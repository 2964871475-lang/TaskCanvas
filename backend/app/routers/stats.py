from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from ..database import get_db
from ..models import Task, StudyRecord, Word, WordBook, WordStudyRecord, PomodoroSession

router = APIRouter(prefix="/api/stats", tags=["数据可视化"])


@router.get("/overview")
def overview(user_id: int, db: Session = Depends(get_db)):
    total = db.query(func.count(Task.id)).filter(Task.owner_id == user_id).scalar()
    done = db.query(func.count(Task.id)).filter(Task.owner_id == user_id, Task.status == "done").scalar()
    in_progress = db.query(func.count(Task.id)).filter(Task.owner_id == user_id, Task.status == "in_progress").scalar()
    pending = db.query(func.count(Task.id)).filter(Task.owner_id == user_id, Task.status == "pending").scalar()

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_study = db.query(func.sum(StudyRecord.duration_minutes)).filter(
        StudyRecord.user_id == user_id, StudyRecord.start_time >= today
    ).scalar() or 0

    total_words = db.query(func.count(Word.id)).join(WordBook).filter(WordBook.user_id == user_id).scalar()
    mastered_words = db.query(func.count(Word.id)).join(WordBook).filter(
        WordBook.user_id == user_id, Word.mastery >= 80
    ).scalar()

    return {
        "total_tasks": total,
        "done": done,
        "in_progress": in_progress,
        "pending": pending,
        "completion_rate": round(done / total * 100, 1) if total else 0,
        "today_study_minutes": today_study,
        "total_words": total_words,
        "mastered_words": mastered_words,
    }


@router.get("/weekly-tasks")
def weekly_tasks(user_id: int, db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    tasks = db.query(Task).filter(
        Task.owner_id == user_id, Task.completed_at >= week_ago
    ).all()

    daily = {}
    for i in range(7):
        day = (today - timedelta(days=6 - i)).strftime("%m-%d")
        daily[day] = 0
    for t in tasks:
        if t.completed_at:
            day = t.completed_at.strftime("%m-%d")
            if day in daily:
                daily[day] += 1
    return [{"date": k, "count": v} for k, v in daily.items()]


@router.get("/weekly-words")
def weekly_words(user_id: int, db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    records = db.query(WordStudyRecord).filter(
        WordStudyRecord.user_id == user_id, WordStudyRecord.studied_at >= week_ago
    ).all()

    daily = {}
    for i in range(7):
        day = (today - timedelta(days=6 - i)).strftime("%m-%d")
        daily[day] = 0
    for r in records:
        day = r.studied_at.strftime("%m-%d")
        if day in daily:
            daily[day] += 1
    return [{"date": k, "count": v} for k, v in daily.items()]


@router.get("/word-mastery-heatmap")
def word_mastery_heatmap(user_id: int, db: Session = Depends(get_db)):
    words = db.query(Word).join(WordBook).filter(WordBook.user_id == user_id).all()
    buckets = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
    for w in words:
        m = w.mastery
        if m < 20:
            buckets["0-20"] += 1
        elif m < 40:
            buckets["20-40"] += 1
        elif m < 60:
            buckets["40-60"] += 1
        elif m < 80:
            buckets["60-80"] += 1
        else:
            buckets["80-100"] += 1
    return [{"range": k, "count": v} for k, v in buckets.items()]
