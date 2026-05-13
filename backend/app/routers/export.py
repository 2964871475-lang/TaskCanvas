import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from ..database import get_db
from ..models import Task, Word, WordBook, WordStudyRecord, PomodoroSession, StudyRecord, StudyGoal

router = APIRouter(prefix="/api/export", tags=["导出"])


@router.get("/weekly-report")
def weekly_report(user_id: int, db: Session = Depends(get_db)):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
    matplotlib.rcParams["axes.unicode_minus"] = False

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)

    # 任务数据
    tasks = db.query(Task).filter(Task.owner_id == user_id, Task.completed_at >= week_ago).all()
    daily_tasks = {(today - timedelta(days=6 - i)).strftime("%m-%d"): 0 for i in range(7)}
    for t in tasks:
        if t.completed_at:
            day = t.completed_at.strftime("%m-%d")
            if day in daily_tasks:
                daily_tasks[day] += 1

    # 单词数据
    word_records = db.query(WordStudyRecord).filter(WordStudyRecord.user_id == user_id, WordStudyRecord.studied_at >= week_ago).all()
    daily_words = {(today - timedelta(days=6 - i)).strftime("%m-%d"): 0 for i in range(7)}
    for r in word_records:
        day = r.studied_at.strftime("%m-%d")
        if day in daily_words:
            daily_words[day] += 1

    # 统计
    total_tasks = db.query(func.count(Task.id)).filter(Task.owner_id == user_id).scalar()
    done_tasks = db.query(func.count(Task.id)).filter(Task.owner_id == user_id, Task.status == "done").scalar()
    total_words = db.query(func.count(Word.id)).join(WordBook).filter(WordBook.user_id == user_id).scalar()
    mastered = db.query(func.count(Word.id)).join(WordBook).filter(WordBook.user_id == user_id, Word.mastery >= 80).scalar()
    pomodoro_min = db.query(func.sum(PomodoroSession.duration_minutes)).filter(
        PomodoroSession.user_id == user_id, PomodoroSession.started_at >= week_ago, PomodoroSession.is_completed == True
    ).scalar() or 0

    # 绘图
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("TaskCanvas 周学习报告", fontsize=16, fontweight="bold")

    dates = list(daily_tasks.keys())
    axes[0, 0].bar(dates, list(daily_tasks.values()), color="#409eff")
    axes[0, 0].set_title("每日任务完成数")
    axes[0, 0].set_ylabel("个")

    axes[0, 1].plot(dates, list(daily_words.values()), marker="o", color="#67c23a", linewidth=2)
    axes[0, 1].set_title("每日单词学习量")
    axes[0, 1].set_ylabel("个")

    labels = ["已完成", "进行中/待办"]
    values = [done_tasks, total_tasks - done_tasks]
    axes[1, 0].pie(values, labels=labels, autopct="%1.1f%%", colors=["#67c23a", "#909399"])
    axes[1, 0].set_title(f"任务完成率 ({done_tasks}/{total_tasks})")

    summary = f"本周学习总结\n\n完成任务: {done_tasks} 个\n学习单词: {sum(daily_words.values())} 个\n掌握单词: {mastered}/{total_words}\n番茄钟专注: {pomodoro_min} 分钟"
    axes[1, 1].text(0.5, 0.5, summary, transform=axes[1, 1].transAxes, fontsize=12, ha="center", va="center",
                    bbox=dict(boxstyle="round", facecolor="#f0f9eb", alpha=0.8))
    axes[1, 1].set_title("学习概览")
    axes[1, 1].axis("off")

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png", headers={"Content-Disposition": "attachment; filename=weekly_report.png"})


@router.get("/daily-report")
def daily_report(user_id: int, db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    # 今日完成任务
    done_tasks = db.query(Task).filter(
        Task.owner_id == user_id, Task.status == "done", Task.completed_at >= today
    ).all()
    task_list = [{"id": t.id, "title": t.title, "subject": t.subject, "category": t.category} for t in done_tasks]

    # 学习时长
    study_minutes = db.query(func.sum(StudyRecord.duration_minutes)).filter(
        StudyRecord.user_id == user_id, StudyRecord.start_time >= today
    ).scalar() or 0

    # 单词学习数
    words_studied = db.query(func.count(WordStudyRecord.id)).filter(
        WordStudyRecord.user_id == user_id, WordStudyRecord.studied_at >= today
    ).scalar()

    # 番茄钟数
    pomodoro_count = db.query(func.count(PomodoroSession.id)).filter(
        PomodoroSession.user_id == user_id, PomodoroSession.is_completed == True, PomodoroSession.started_at >= today
    ).scalar()

    # 各科目任务分布
    all_tasks = db.query(Task).filter(Task.owner_id == user_id).all()
    subject_stats = {}
    for t in all_tasks:
        s = t.subject or "其他"
        if s not in subject_stats:
            subject_stats[s] = {"total": 0, "done": 0}
        subject_stats[s]["total"] += 1
        if t.status == "done":
            subject_stats[s]["done"] += 1

    # 薄弱科目（完成率最低）
    weak_subjects = []
    for s, v in subject_stats.items():
        rate = round(v["done"] / v["total"] * 100, 1) if v["total"] else 0
        weak_subjects.append({"subject": s, "total": v["total"], "done": v["done"], "rate": rate})
    weak_subjects.sort(key=lambda x: x["rate"])

    # 目标完成情况
    goals = db.query(StudyGoal).filter(StudyGoal.user_id == user_id).all()
    goal_progress = []
    for g in goals:
        actual = 0
        if g.goal_type == "tasks":
            actual = len(done_tasks)
        elif g.goal_type == "minutes":
            actual = study_minutes
        elif g.goal_type == "words":
            actual = words_studied
        goal_progress.append({
            "type": g.goal_type, "target": g.target_value, "actual": actual,
            "achieved": actual >= g.target_value,
        })

    return {
        "date": today.strftime("%Y-%m-%d"),
        "tasks_completed": task_list,
        "study_minutes": study_minutes,
        "words_studied": words_studied,
        "pomodoro_count": pomodoro_count,
        "subject_analysis": weak_subjects[:5],
        "goal_progress": goal_progress,
    }


@router.get("/monthly-report")
def monthly_report(user_id: int, db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    month_ago = today - timedelta(days=30)

    # 30天趋势
    tasks = db.query(Task).filter(Task.owner_id == user_id, Task.completed_at >= month_ago).all()
    words = db.query(WordStudyRecord).filter(WordStudyRecord.user_id == user_id, WordStudyRecord.studied_at >= month_ago).all()
    pomodoros = db.query(PomodoroSession).filter(
        PomodoroSession.user_id == user_id, PomodoroSession.started_at >= month_ago, PomodoroSession.is_completed == True
    ).all()

    daily_tasks = {}
    daily_words = {}
    daily_pomo = {}
    for i in range(30):
        day = (today - timedelta(days=29 - i)).strftime("%m-%d")
        daily_tasks[day] = 0
        daily_words[day] = 0
        daily_pomo[day] = 0

    for t in tasks:
        if t.completed_at:
            day = t.completed_at.strftime("%m-%d")
            if day in daily_tasks:
                daily_tasks[day] += 1
    for w in words:
        day = w.studied_at.strftime("%m-%d")
        if day in daily_words:
            daily_words[day] += 1
    for p in pomodoros:
        day = p.started_at.strftime("%m-%d")
        if day in daily_pomo:
            daily_pomo[day] += p.duration_minutes

    # 汇总
    total_tasks_done = sum(daily_tasks.values())
    total_words_studied = sum(daily_words.values())
    total_pomo_min = sum(daily_pomo.values())
    total_words = db.query(func.count(Word.id)).join(WordBook).filter(WordBook.user_id == user_id).scalar()
    mastered = db.query(func.count(Word.id)).join(WordBook).filter(WordBook.user_id == user_id, Word.mastery >= 80).scalar()

    # 目标达成率
    goals = db.query(StudyGoal).filter(StudyGoal.user_id == user_id).all()
    goal_achievement = []
    for g in goals:
        achieved_days = 0
        for t in tasks:
            if g.goal_type == "tasks" and t.completed_at:
                day_count = sum(1 for tt in tasks if tt.completed_at and tt.completed_at.strftime("%m-%d") == t.completed_at.strftime("%m-%d"))
                if day_count >= g.target_value:
                    achieved_days += 1
                    break
        goal_achievement.append({"type": g.goal_type, "target": g.target_value})

    return {
        "period": f"{month_ago.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}",
        "daily_tasks": [{"date": k, "count": v} for k, v in daily_tasks.items()],
        "daily_words": [{"date": k, "count": v} for k, v in daily_words.items()],
        "daily_pomodoro": [{"date": k, "minutes": v} for k, v in daily_pomo.items()],
        "summary": {
            "tasks_completed": total_tasks_done,
            "words_studied": total_words_studied,
            "pomodoro_minutes": total_pomo_min,
            "mastered_words": mastered,
            "total_words": total_words,
        },
    }
