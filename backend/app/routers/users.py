from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import hashlib
import secrets

from ..database import get_db
from ..models import User, Team, TeamMember

router = APIRouter(prefix="/api/users", tags=["用户与团队"])


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


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=UserOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or user.hashed_password != hash_password(data.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/teams", response_model=TeamOut, status_code=201)
def create_team(data: TeamCreate, owner_id: int, db: Session = Depends(get_db)):
    team = Team(
        name=data.name,
        description=data.description,
        invite_code=secrets.token_hex(6),
        owner_id=owner_id,
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    member = TeamMember(team_id=team.id, user_id=owner_id, role="owner")
    db.add(member)
    db.commit()
    return team


@router.post("/teams/join")
def join_team(invite_code: str, user_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.invite_code == invite_code).first()
    if not team:
        raise HTTPException(status_code=404, detail="邀请码无效")
    existing = db.query(TeamMember).filter(
        TeamMember.team_id == team.id, TeamMember.user_id == user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="已经是团队成员")
    member = TeamMember(team_id=team.id, user_id=user_id)
    db.add(member)
    db.commit()
    return {"message": f"成功加入团队 {team.name}"}
