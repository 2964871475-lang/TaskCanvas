from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

from ..database import get_db
from ..models import Habit, HabitRecord, PomodoroSession, User

router = APIRouter(prefix="/api/habits", tags=["习惯与番茄钟"])


class HabitCreate(BaseModel):
    name: str
    icon: str = "✓"
    frequency: str = "daily"
    target_count: int = 1
    user_id: int


class HabitOut(BaseModel):
    id: int
    name: str
    icon: str
    frequency: str
    target_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PomodoroCreate(BaseModel):
    user_id: int
    duration_minutes: int = 25


class PomodoroOut(BaseModel):
    id: int
    duration_minutes: int
    started_at: datetime
    ended_at: Optional[datetime]
    is_completed: bool

    model_config = {"from_attributes": True}


@router.post("/", response_model=HabitOut, status_code=201)
def create_habit(data: HabitCreate, db: Session = Depends(get_db)):
    habit = Habit(**data.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("/", response_model=List[HabitOut])
def list_habits(user_id: int, db: Session = Depends(get_db)):
    return db.query(Habit).filter(Habit.user_id == user_id).all()


@router.post("/{habit_id}/checkin")
def checkin_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(Habit).get(habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="习惯不存在")
    record = HabitRecord(habit_id=habit_id, user_id=habit.user_id)
    db.add(record)
    db.commit()
    today_count = (
        db.query(func.count(HabitRecord.id))
        .filter(
            HabitRecord.habit_id == habit_id,
            HabitRecord.completed_at >= datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0
            ),
        )
        .scalar()
    )
    return {"message": "打卡成功", "today_count": today_count, "target": habit.target_count}


@router.post("/pomodoro/start", response_model=PomodoroOut, status_code=201)
def start_pomodoro(data: PomodoroCreate, db: Session = Depends(get_db)):
    session = PomodoroSession(
        user_id=data.user_id,
        duration_minutes=data.duration_minutes,
        started_at=datetime.now(timezone.utc),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.patch("/pomodoro/{session_id}/complete", response_model=PomodoroOut)
def complete_pomodoro(session_id: int, db: Session = Depends(get_db)):
    session = db.query(PomodoroSession).get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="番茄钟会话不存在")
    session.ended_at = datetime.now(timezone.utc)
    session.is_completed = True
    db.commit()
    db.refresh(session)
    return session


@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    result = (
        db.query(
            User.username,
            func.sum(PomodoroSession.duration_minutes).label("total_minutes"),
        )
        .join(PomodoroSession, PomodoroSession.user_id == User.id)
        .filter(PomodoroSession.started_at >= week_ago, PomodoroSession.is_completed == True)
        .group_by(User.username)
        .order_by(func.sum(PomodoroSession.duration_minutes).desc())
        .limit(10)
        .all()
    )
    return [{"username": r[0], "total_minutes": r[1] or 0} for r in result]
