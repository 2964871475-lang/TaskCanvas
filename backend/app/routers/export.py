import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from ..database import get_db
from ..models import Task, Word, WordBook, WordStudyRecord, PomodoroSession

router = APIRouter(prefix="/api/export", tags=["导出"])


def ensure_utc(dt):
    """确保 datetime 有时区信息"""
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


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
    tasks = db.query(Task).filter(Task.owner_id == user_id, Task.status == "done").all()
    daily_tasks = {(today - timedelta(days=6 - i)).strftime("%m-%d"): 0 for i in range(7)}
    for t in tasks:
        completed_at = ensure_utc(t.completed_at)
        if completed_at and completed_at >= week_ago:
            day = completed_at.strftime("%m-%d")
            if day in daily_tasks:
                daily_tasks[day] += 1

    # 单词数据
    word_records = db.query(WordStudyRecord).filter(WordStudyRecord.user_id == user_id).all()
    daily_words = {(today - timedelta(days=6 - i)).strftime("%m-%d"): 0 for i in range(7)}
    for r in word_records:
        studied_at = ensure_utc(r.studied_at)
        if studied_at and studied_at >= week_ago:
            day = studied_at.strftime("%m-%d")
            if day in daily_words:
                daily_words[day] += 1

    # 统计
    total_tasks = db.query(func.count(Task.id)).filter(Task.owner_id == user_id).scalar()
    done_tasks = db.query(func.count(Task.id)).filter(Task.owner_id == user_id, Task.status == "done").scalar()
    total_words = db.query(func.count(Word.id)).join(WordBook).filter(WordBook.user_id == user_id).scalar()
    mastered = db.query(func.count(Word.id)).join(WordBook).filter(WordBook.user_id == user_id, Word.mastery >= 80).scalar()
    pomodoro_sessions = db.query(PomodoroSession).filter(
        PomodoroSession.user_id == user_id, PomodoroSession.is_completed == True
    ).all()
    pomodoro_min = sum(s.duration_minutes for s in pomodoro_sessions if ensure_utc(s.started_at) and ensure_utc(s.started_at) >= week_ago)

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
