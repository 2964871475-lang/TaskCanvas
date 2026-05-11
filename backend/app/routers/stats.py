from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from ..database import get_db
from ..models import (Task, StudyRecord, Word, WordBook, WordStudyRecord,
                      PomodoroSession, Habit, HabitRecord, TeamMember, User)

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
    mastered_words = db.query(func.count(Word.id)).join(WordBook).filter(WordBook.user_id == user_id, Word.mastery >= 80).scalar()

    return {
        "total_tasks": total, "done": done, "in_progress": in_progress, "pending": pending,
        "completion_rate": round(done / total * 100, 1) if total else 0,
        "today_study_minutes": today_study, "total_words": total_words, "mastered_words": mastered_words,
    }


@router.get("/weekly-tasks")
def weekly_tasks(user_id: int, db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    tasks = db.query(Task).filter(Task.owner_id == user_id, Task.completed_at >= week_ago).all()
    daily = {(today - timedelta(days=6 - i)).strftime("%m-%d"): 0 for i in range(7)}
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
    records = db.query(WordStudyRecord).filter(WordStudyRecord.user_id == user_id, WordStudyRecord.studied_at >= week_ago).all()
    daily = {(today - timedelta(days=6 - i)).strftime("%m-%d"): 0 for i in range(7)}
    for r in records:
        day = r.studied_at.strftime("%m-%d")
        if day in daily:
            daily[day] += 1
    return [{"date": k, "count": v} for k, v in daily.items()]


@router.get("/weekly-pomodoro")
def weekly_pomodoro(user_id: int, db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    sessions = db.query(PomodoroSession).filter(
        PomodoroSession.user_id == user_id, PomodoroSession.started_at >= week_ago, PomodoroSession.is_completed == True
    ).all()
    daily = {(today - timedelta(days=6 - i)).strftime("%m-%d"): 0 for i in range(7)}
    for s in sessions:
        day = s.started_at.strftime("%m-%d")
        if day in daily:
            daily[day] += s.duration_minutes
    return [{"date": k, "minutes": v} for k, v in daily.items()]


@router.get("/word-mastery-heatmap")
def word_mastery_heatmap(user_id: int, db: Session = Depends(get_db)):
    words = db.query(Word).join(WordBook).filter(WordBook.user_id == user_id).all()
    buckets = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
    for w in words:
        m = w.mastery
        if m < 20: buckets["0-20"] += 1
        elif m < 40: buckets["20-40"] += 1
        elif m < 60: buckets["40-60"] += 1
        elif m < 80: buckets["60-80"] += 1
        else: buckets["80-100"] += 1
    return [{"range": k, "count": v} for k, v in buckets.items()]


@router.get("/team-comparison/{team_id}")
def team_comparison(team_id: int, db: Session = Depends(get_db)):
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    result = []
    for m in members:
        user = db.get(User, m.user_id)
        if not user: continue
        tasks_done = db.query(func.count(Task.id)).filter(Task.owner_id == m.user_id, Task.status == "done", Task.completed_at >= week_ago).scalar()
        pomodoro_min = db.query(func.sum(PomodoroSession.duration_minutes)).filter(
            PomodoroSession.user_id == m.user_id, PomodoroSession.started_at >= week_ago, PomodoroSession.is_completed == True
        ).scalar() or 0
        words_learned = db.query(func.count(WordStudyRecord.id)).filter(
            WordStudyRecord.user_id == m.user_id, WordStudyRecord.studied_at >= week_ago
        ).scalar()
        result.append({"username": user.username, "tasks_done": tasks_done, "pomodoro_minutes": pomodoro_min, "words_learned": words_learned})
    return result


@router.get("/habit-streak")
def habit_streak(user_id: int, db: Session = Depends(get_db)):
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = []
    for h in habits:
        today_count = db.query(func.count(HabitRecord.id)).filter(
            HabitRecord.habit_id == h.id, HabitRecord.completed_at >= today
        ).scalar()
        total = db.query(func.count(HabitRecord.id)).filter(HabitRecord.habit_id == h.id).scalar()
        result.append({"habit_id": h.id, "name": h.name, "icon": h.icon, "today_count": today_count, "target": h.target_count, "total_records": total})
    return result
