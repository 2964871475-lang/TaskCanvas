from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime, timezone
import hashlib
import re
import secrets

from ..database import get_db
from ..models import User, Team, TeamMember, Task, Word, Habit, StudyRecord, Announcement, AuditLog, PomodoroSession, WordBook

router = APIRouter(prefix="/api", tags=["用户与团队"])


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 20:
            raise ValueError("用户名长度需在 2-20 个字符之间")
        if not re.match(r'^[a-zA-Z0-9_一-鿿]+$', v):
            raise ValueError("用户名只能包含字母、数字、下划线或中文")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6 or len(v) > 50:
            raise ValueError("密码长度需在 6-50 个字符之间")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    bio: str
    is_admin: bool = False
    is_disabled: bool = False
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
    owner_id: Optional[int] = None
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
    if user.is_disabled:
        raise HTTPException(status_code=403, detail="账户已被禁用，请联系管理员")
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
    if not data.old_password or not data.new_password:
        raise HTTPException(status_code=400, detail="旧密码和新密码不能为空")
    if user.hashed_password != hash_password(data.old_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    if len(data.new_password) < 6 or len(data.new_password) > 50:
        raise HTTPException(status_code=400, detail="新密码长度需在 6-50 个字符之间")
    if data.old_password == data.new_password:
        raise HTTPException(status_code=400, detail="新密码不能与旧密码相同")
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


@router.delete("/teams/{team_id}")
def delete_team(team_id: int, user_id: int, db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    if team.owner_id != user_id:
        raise HTTPException(status_code=403, detail="只有团队创建者可以删除团队")
    db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
    db.delete(team)
    db.commit()
    return {"message": "团队已删除"}


@router.delete("/teams/{team_id}/members/{member_user_id}")
def remove_member(team_id: int, member_user_id: int, operator_id: int, db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    if team.owner_id != operator_id and operator_id != member_user_id:
        raise HTTPException(status_code=403, detail="无权操作")
    membership = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == member_user_id
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="该用户不是团队成员")
    if membership.role == "owner":
        raise HTTPException(status_code=400, detail="团队创建者不能被移除")
    db.delete(membership)
    db.commit()
    return {"message": "已移除成员"}


# ==================== 管理后台 ====================

def check_admin(user_id: int, db: Session):
    user = db.get(User, user_id)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


def log_action(db: Session, operator_id: int, action: str, target_type: str, target_id: int = None, detail: str = ""):
    log = AuditLog(operator_id=operator_id, action=action, target_type=target_type, target_id=target_id, detail=detail)
    db.add(log)
    db.commit()


# ---------- Pydantic Models ----------

class AdminUserOut(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    is_disabled: bool
    created_at: datetime
    task_count: int = 0
    model_config = {"from_attributes": True}


class AdminTeamOut(BaseModel):
    id: int
    name: str
    description: str
    invite_code: str
    owner_id: Optional[int] = None
    owner_name: str = ""
    member_count: int = 0
    created_at: datetime
    model_config = {"from_attributes": True}


class TeamMemberDetail(BaseModel):
    id: int
    user_id: int
    username: str
    role: str
    joined_at: datetime


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    team_id: Optional[int] = None


class AnnouncementOut(BaseModel):
    id: int
    title: str
    content: str
    team_id: Optional[int]
    team_name: str = ""
    publisher_name: str = ""
    created_at: datetime
    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    id: int
    operator_name: str = ""
    action: str
    target_type: str
    target_id: Optional[int]
    detail: str
    created_at: datetime
    model_config = {"from_attributes": True}


# ==================== 用户管理 ====================

@router.get("/admin/users", response_model=List[AdminUserOut])
def admin_list_users(operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        task_count = db.query(Task).filter(Task.owner_id == u.id).count()
        result.append(AdminUserOut(
            id=u.id, username=u.username, email=u.email,
            is_admin=u.is_admin, is_disabled=u.is_disabled,
            created_at=u.created_at, task_count=task_count,
        ))
    return result


@router.patch("/admin/users/{user_id}/toggle-disable")
def admin_toggle_disable(user_id: int, operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="不能禁用管理员账户")
    user.is_disabled = not user.is_disabled
    status = "已禁用" if user.is_disabled else "已启用"
    log_action(db, operator_id, "toggle_disable", "user", user_id, f"用户 {user.username} {status}")
    return {"message": f"用户 {user.username} {status}"}


@router.post("/admin/users/{user_id}/reset-password")
def admin_reset_password(user_id: int, operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="不能重置管理员密码")
    new_pw = "888888"
    user.hashed_password = hash_password(new_pw)
    log_action(db, operator_id, "reset_password", "user", user_id, f"重置用户 {user.username} 密码")
    return {"message": f"用户 {user.username} 密码已重置为 {new_pw}"}


@router.delete("/admin/users/{user_id}")
def admin_delete_user(user_id: int, operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="不能删除管理员账户")
    username = user.username
    db.query(Task).filter(Task.owner_id == user_id).delete()
    db.query(StudyRecord).filter(StudyRecord.user_id == user_id).delete()
    db.query(TeamMember).filter(TeamMember.user_id == user_id).delete()
    db.delete(user)
    log_action(db, operator_id, "delete_user", "user", user_id, f"删除用户 {username} 及其数据")
    return {"message": f"用户 {username} 及其数据已删除"}


# ==================== 团队审核 ====================

@router.get("/admin/teams", response_model=List[AdminTeamOut])
def admin_list_teams(operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    teams = db.query(Team).order_by(Team.created_at.desc()).all()
    result = []
    for t in teams:
        owner = db.get(User, t.owner_id) if t.owner_id else None
        member_count = db.query(TeamMember).filter(TeamMember.team_id == t.id).count()
        result.append(AdminTeamOut(
            id=t.id, name=t.name, description=t.description, invite_code=t.invite_code,
            owner_id=t.owner_id, owner_name=owner.username if owner else "无",
            member_count=member_count, created_at=t.created_at,
        ))
    return result


@router.get("/admin/teams/{team_id}/members", response_model=List[TeamMemberDetail])
def admin_team_members(team_id: int, operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    result = []
    for m in members:
        user = db.get(User, m.user_id)
        result.append(TeamMemberDetail(
            id=m.id, user_id=m.user_id, username=user.username if user else "未知",
            role=m.role, joined_at=m.joined_at,
        ))
    return result


@router.patch("/admin/teams/{team_id}/transfer")
def admin_transfer_owner(team_id: int, new_owner_id: int, operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    new_owner = db.get(User, new_owner_id)
    if not new_owner:
        raise HTTPException(status_code=404, detail="目标用户不存在")
    membership = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == new_owner_id).first()
    if not membership:
        raise HTTPException(status_code=400, detail="目标用户不是团队成员")
    old_owner_member = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.role == "owner").first()
    if old_owner_member:
        old_owner_member.role = "member"
    membership.role = "owner"
    team.owner_id = new_owner_id
    log_action(db, operator_id, "transfer_owner", "team", team_id, f"团队 {team.name} 组长转移给 {new_owner.username}")
    return {"message": f"团队 {team.name} 组长已转移给 {new_owner.username}"}


@router.delete("/admin/teams/{team_id}/members/{user_id}")
def admin_remove_member(team_id: int, user_id: int, operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    membership = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="该用户不是团队成员")
    if membership.role == "owner":
        raise HTTPException(status_code=400, detail="不能移除组长，请先转移组长权限")
    user = db.get(User, user_id)
    db.delete(membership)
    log_action(db, operator_id, "remove_member", "team", team_id, f"从团队 {team.name} 移除成员 {user.username if user else user_id}")
    return {"message": "已移除成员"}


@router.delete("/admin/teams/{team_id}")
def admin_dissolve_team(team_id: int, operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    team_name = team.name
    db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
    db.query(Announcement).filter(Announcement.team_id == team_id).delete()
    db.delete(team)
    log_action(db, operator_id, "dissolve_team", "team", team_id, f"解散团队 {team_name}")
    return {"message": f"团队 {team_name} 已解散"}


@router.get("/admin/teams/{team_id}/stats")
def admin_team_stats(team_id: int, operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    member_stats = []
    for m in members:
        user = db.get(User, m.user_id)
        if not user:
            continue
        tasks_done = db.query(Task).filter(Task.owner_id == m.user_id, Task.status == "done").count()
        tasks_total = db.query(Task).filter(Task.owner_id == m.user_id).count()
        study_minutes = db.query(StudyRecord).filter(StudyRecord.user_id == m.user_id).with_entities(
            func.sum(StudyRecord.duration_minutes)
        ).scalar() or 0
        words_learned = db.query(Word).join(WordBook).filter(WordBook.user_id == m.user_id, Word.mastery >= 60).count()
        words_total = db.query(Word).join(WordBook).filter(WordBook.user_id == m.user_id).count()
        pomodoro_count = db.query(PomodoroSession).filter(PomodoroSession.user_id == m.user_id, PomodoroSession.is_completed == True).count()
        member_stats.append({
            "user_id": m.user_id,
            "username": user.username,
            "role": m.role,
            "tasks_done": tasks_done,
            "tasks_total": tasks_total,
            "study_minutes": study_minutes,
            "words_learned": words_learned,
            "words_total": words_total,
            "pomodoro_count": pomodoro_count,
        })
    return {"team_name": team.name, "members": member_stats}


# ==================== 公告管理 ====================

@router.post("/admin/announcements", response_model=AnnouncementOut, status_code=201)
def admin_create_announcement(data: AnnouncementCreate, operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    ann = Announcement(title=data.title, content=data.content, team_id=data.team_id, publisher_id=operator_id)
    db.add(ann)
    db.commit()
    db.refresh(ann)
    team_name = ""
    if ann.team_id:
        team = db.get(Team, ann.team_id)
        team_name = team.name if team else ""
    publisher = db.get(User, operator_id)
    log_action(db, operator_id, "publish_announcement", "announcement", ann.id, f"发布公告: {ann.title}")
    return AnnouncementOut(
        id=ann.id, title=ann.title, content=ann.content, team_id=ann.team_id,
        team_name=team_name, publisher_name=publisher.username if publisher else "", created_at=ann.created_at,
    )


@router.get("/admin/announcements", response_model=List[AnnouncementOut])
def admin_list_announcements(operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    anns = db.query(Announcement).order_by(Announcement.created_at.desc()).all()
    result = []
    for a in anns:
        team_name = ""
        if a.team_id:
            team = db.get(Team, a.team_id)
            team_name = team.name if team else "已解散"
        publisher = db.get(User, a.publisher_id)
        result.append(AnnouncementOut(
            id=a.id, title=a.title, content=a.content, team_id=a.team_id,
            team_name=team_name, publisher_name=publisher.username if publisher else "", created_at=a.created_at,
        ))
    return result


@router.delete("/admin/announcements/{ann_id}")
def admin_delete_announcement(ann_id: int, operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    ann = db.get(Announcement, ann_id)
    if not ann:
        raise HTTPException(status_code=404, detail="公告不存在")
    title = ann.title
    db.delete(ann)
    log_action(db, operator_id, "delete_announcement", "announcement", ann_id, f"删除公告: {title}")
    return {"message": f"公告 {title} 已删除"}


# ==================== 数据导出 ====================

@router.get("/admin/export")
def admin_export_data(operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    log_action(db, operator_id, "export_data", "system", detail="导出全量数据")
    users = []
    for u in db.query(User).all():
        users.append({"id": u.id, "username": u.username, "email": u.email, "is_admin": u.is_admin, "is_disabled": u.is_disabled, "created_at": u.created_at.isoformat()})
    tasks = []
    for t in db.query(Task).all():
        tasks.append({"id": t.id, "title": t.title, "category": t.category, "subject": t.subject, "priority": t.priority, "status": t.status, "owner_id": t.owner_id, "created_at": t.created_at.isoformat()})
    teams = []
    for t in db.query(Team).all():
        member_count = db.query(TeamMember).filter(TeamMember.team_id == t.id).count()
        teams.append({"id": t.id, "name": t.name, "owner_id": t.owner_id, "member_count": member_count, "created_at": t.created_at.isoformat()})
    words_count = db.query(Word).count()
    habits_count = db.query(Habit).count()
    study_records_count = db.query(StudyRecord).count()
    return {
        "export_time": datetime.now(timezone.utc).isoformat(),
        "users": users,
        "tasks": tasks,
        "teams": teams,
        "summary": {"total_words": words_count, "total_habits": habits_count, "total_study_records": study_records_count},
    }


# ==================== 操作日志 ====================

@router.get("/admin/logs", response_model=List[AuditLogOut])
def admin_list_logs(operator_id: int, page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    query = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    total = query.count()
    logs = query.offset((page - 1) * size).limit(size).all()
    result = []
    for l in logs:
        operator = db.get(User, l.operator_id)
        result.append(AuditLogOut(
            id=l.id, operator_name=operator.username if operator else "未知",
            action=l.action, target_type=l.target_type, target_id=l.target_id,
            detail=l.detail, created_at=l.created_at,
        ))
    return result


@router.get("/admin/logs/count")
def admin_logs_count(operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    return {"total": db.query(AuditLog).count()}


# ==================== 公开接口（普通用户查看公告） ====================

@router.get("/announcements")
def list_announcements(user_id: int = 0, db: Session = Depends(get_db)):
    query = db.query(Announcement).filter(Announcement.team_id == None)
    if user_id:
        team_ids = [m.team_id for m in db.query(TeamMember).filter(TeamMember.user_id == user_id).all()]
        if team_ids:
            query = db.query(Announcement).filter(
                (Announcement.team_id == None) | (Announcement.team_id.in_(team_ids))
            )
    anns = query.order_by(Announcement.created_at.desc()).limit(20).all()
    result = []
    for a in anns:
        team_name = ""
        if a.team_id:
            team = db.get(Team, a.team_id)
            team_name = team.name if team else ""
        publisher = db.get(User, a.publisher_id)
        result.append({
            "id": a.id, "title": a.title, "content": a.content,
            "team_id": a.team_id, "team_name": team_name,
            "publisher_name": publisher.username if publisher else "",
            "created_at": a.created_at.isoformat(),
        })
    return result


# ==================== 系统统计 ====================

@router.get("/admin/stats")
def admin_stats(operator_id: int, db: Session = Depends(get_db)):
    check_admin(operator_id, db)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_active = db.query(StudyRecord).filter(func.date(StudyRecord.start_time) == today).distinct(StudyRecord.user_id).count()
    return {
        "total_users": db.query(User).count(),
        "active_users": db.query(User).filter(User.is_disabled == False).count(),
        "today_active": today_active,
        "total_tasks": db.query(Task).count(),
        "completed_tasks": db.query(Task).filter(Task.status == "done").count(),
        "total_teams": db.query(Team).count(),
        "total_words": db.query(Word).count(),
        "total_habits": db.query(Habit).count(),
        "total_study_records": db.query(StudyRecord).count(),
        "total_announcements": db.query(Announcement).count(),
    }
