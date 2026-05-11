from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


# ==================== 模块1: 用户与团队 ====================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    avatar = Column(String(255), default="")
    bio = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tasks = relationship("Task", back_populates="owner")
    team_memberships = relationship("TeamMember", back_populates="user")
    study_records = relationship("StudyRecord", back_populates="user")
    habit_records = relationship("HabitRecord", back_populates="user")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    invite_code = Column(String(20), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    owner_id = Column(Integer, ForeignKey("users.id"))

    members = relationship("TeamMember", back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String(20), default="member")  # owner / admin / member
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ==================== 模块2: 智能任务看板 ====================

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    category = Column(String(20), default="daily")  # daily / longterm / mistake
    subject = Column(String(50), default="其他")
    priority = Column(Integer, default=2)  # 1=高 2=中 3=低
    status = Column(String(20), default="pending")  # pending / in_progress / done
    difficulty = Column(Integer, default=3)  # 1-5
    estimated_minutes = Column(Integer, default=60)
    deadline = Column(DateTime, nullable=True)
    sort_order = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)  # 连续打卡天数
    last_checkin = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    owner = relationship("User", back_populates="tasks")
    study_records = relationship("StudyRecord", back_populates="task")


# ==================== 模块3: 单词学习 ====================

class WordBook(Base):
    __tablename__ = "word_books"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    words = relationship("Word", back_populates="book")


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("word_books.id"))
    english = Column(String(100), nullable=False)
    chinese = Column(String(200), nullable=False)
    phonetic = Column(String(100), default="")
    example = Column(Text, default="")
    mastery = Column(Float, default=0.0)  # 掌握度 0-100
    next_review = Column(DateTime, nullable=True)  # 下次复习时间
    review_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)  # 错误次数
    is_starred = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("WordBook", back_populates="words")
    records = relationship("WordStudyRecord", back_populates="word")


class WordStudyRecord(Base):
    __tablename__ = "word_study_records"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    is_correct = Column(Boolean, nullable=False)
    studied_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    word = relationship("Word", back_populates="records")


# ==================== 模块4: 习惯与番茄钟 ====================

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(10), default="✓")
    frequency = Column(String(20), default="daily")  # daily / weekly
    target_count = Column(Integer, default=1)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    records = relationship("HabitRecord", back_populates="habit")


class HabitRecord(Base):
    __tablename__ = "habit_records"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    count = Column(Integer, default=1)

    habit = relationship("Habit", back_populates="records")
    user = relationship("User", back_populates="habit_records")


class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    duration_minutes = Column(Integer, default=25)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)


# ==================== 模块5: 学习记录（用于统计） ====================

class StudyRecord(Base):
    __tablename__ = "study_records"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=0)
    focus_score = Column(Float, default=0.0)
    note = Column(Text, default="")

    task = relationship("Task", back_populates="study_records")
    user = relationship("User", back_populates="study_records")
