from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import engine, Base, SessionLocal
from app.routers import users, tasks, vocabulary, habits, stats, comments, export
from app.models import User, StudyGoal
import hashlib

Base.metadata.create_all(bind=engine)


def migrate_db():
    """为已有数据库添加新列"""
    db = SessionLocal()
    try:
        # tasks表迁移
        result = db.execute(text("PRAGMA table_info(tasks)")).fetchall()
        columns = [row[1] for row in result]
        if "scheduled_date" not in columns:
            db.execute(text("ALTER TABLE tasks ADD COLUMN scheduled_date DATETIME"))
            db.commit()

        # users表迁移
        result = db.execute(text("PRAGMA table_info(users)")).fetchall()
        columns = [row[1] for row in result]
        if "is_admin" not in columns:
            db.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
            db.commit()
        if "is_disabled" not in columns:
            db.execute(text("ALTER TABLE users ADD COLUMN is_disabled BOOLEAN DEFAULT 0"))
            db.commit()

        # pomodoro_sessions表迁移
        result = db.execute(text("PRAGMA table_info(pomodoro_sessions)")).fetchall()
        columns = [row[1] for row in result]
        if "task_id" not in columns:
            db.execute(text("ALTER TABLE pomodoro_sessions ADD COLUMN task_id INTEGER"))
            db.commit()
    except Exception:
        pass
    finally:
        db.close()


def create_admin():
    """如果没有管理员账户，自动创建默认管理员"""
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.is_admin == True).first():
            admin = User(
                username="admin",
                email="admin@taskcanvas.com",
                hashed_password=hashlib.sha256("admin123".encode()).hexdigest(),
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            print("✅ 已创建默认管理员: admin / admin123")
    except Exception:
        pass
    finally:
        db.close()


migrate_db()
create_admin()

app = FastAPI(title="TaskCanvas API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(vocabulary.router)
app.include_router(habits.router)
app.include_router(stats.router)
app.include_router(comments.router)
app.include_router(export.router)


@app.get("/")
def root():
    return {"message": "TaskCanvas API is running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
