from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import hashlib
import secrets

from ..database import get_db
from ..models import User, Team, TeamMember

router = APIRouter(prefix="/api", tags=["用户与团队"])


class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    bio: str
    created_at: datetime
    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    email: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class TeamCreate(BaseModel):
    name: str
    description: str = ""


class TeamOut(BaseModel):
    id: int
    name: str
    description: str
    invite_code: str
    created_at: datetime
    model_config = {"from_attributes": True}


class TeamMemberOut(BaseModel):
    id: int
    user_id: int
    username: str
    role: str
    joined_at: datetime


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ==================== 用户 ====================

@router.post("/users/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    user = User(username=data.username, email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/login", response_model=UserOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or user.hashed_password != hash_password(data.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return user


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/password")
def change_password(user_id: int, data: PasswordChange, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.hashed_password != hash_password(data.old_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.get("/users/{user_id}/teams", response_model=List[TeamOut])
def get_user_teams(user_id: int, db: Session = Depends(get_db)):
    memberships = db.query(TeamMember).filter(TeamMember.user_id == user_id).all()
    team_ids = [m.team_id for m in memberships]
    return db.query(Team).filter(Team.id.in_(team_ids)).all() if team_ids else []


# ==================== 团队 ====================

@router.post("/users/teams", response_model=TeamOut, status_code=201)
def create_team(data: TeamCreate, owner_id: int, db: Session = Depends(get_db)):
    team = Team(name=data.name, description=data.description, invite_code=secrets.token_hex(6), owner_id=owner_id)
    db.add(team)
    db.commit()
    db.refresh(team)
    member = TeamMember(team_id=team.id, user_id=owner_id, role="owner")
    db.add(member)
    db.commit()
    return team


@router.post("/users/teams/join")
def join_team(invite_code: str, user_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.invite_code == invite_code).first()
    if not team:
        raise HTTPException(status_code=404, detail="邀请码无效")
    existing = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="已经是团队成员")
    member = TeamMember(team_id=team.id, user_id=user_id)
    db.add(member)
    db.commit()
    return {"message": f"成功加入团队 {team.name}", "team_id": team.id}


@router.get("/teams/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    return team


@router.get("/teams/{team_id}/members", response_model=List[TeamMemberOut])
def get_team_members(team_id: int, db: Session = Depends(get_db)):
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    result = []
    for m in members:
        user = db.get(User, m.user_id)
        result.append(TeamMemberOut(
            id=m.id, user_id=m.user_id, username=user.username if user else "未知",
            role=m.role, joined_at=m.joined_at,
        ))
    return result
