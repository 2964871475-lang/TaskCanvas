from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from ..database import get_db
from ..models import Task, StudyRecord

router = APIRouter(prefix="/api/tasks", tags=["任务看板"])


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    category: str = "daily"
    subject: str = "其他"
    priority: int = 2
    difficulty: int = 3
    estimated_minutes: int = 60
    deadline: Optional[datetime] = None
    owner_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subject: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    difficulty: Optional[int] = None
    estimated_minutes: Optional[int] = None
    deadline: Optional[datetime] = None
    sort_order: Optional[int] = None


class BatchSortItem(BaseModel):
    id: int
    sort_order: int


class StudyRecordCreate(BaseModel):
    task_id: Optional[int] = None
    user_id: int
    duration_minutes: int
    focus_score: float = 0.0
    note: str = ""


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    subject: str
    priority: int
    status: str
    difficulty: int
    estimated_minutes: int
    deadline: Optional[datetime]
    sort_order: int
    streak_days: int
    created_at: datetime
    completed_at: Optional[datetime]
    model_config = {"from_attributes": True}


@router.get("/", response_model=List[TaskOut])
def list_tasks(owner_id: int, status: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Task).filter(Task.owner_id == owner_id)
    if status:
        query = query.filter(Task.status == status)
    if category:
        query = query.filter(Task.category == category)
    return query.order_by(Task.sort_order, Task.created_at.desc()).all()


@router.post("/", response_model=TaskOut, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task_data = data.model_dump()
    # 如果创建时状态为 done，自动设置 completed_at
    if task_data.get("status") == "done":
        task_data["completed_at"] = datetime.now(timezone.utc)
    task = Task(**task_data)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    update_data = data.model_dump(exclude_unset=True)

    # 处理 completed_at 生命周期
    new_status = update_data.get("status")
    if new_status == "done" and task.status != "done":
        update_data["completed_at"] = datetime.now(timezone.utc)
    elif new_status and new_status != "done" and task.status == "done":
        update_data["completed_at"] = None

    for key, value in update_data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/batch-sort")
def batch_sort(items: List[BatchSortItem], db: Session = Depends(get_db)):
    for item in items:
        task = db.get(Task, item.id)
        if task:
            task.sort_order = item.sort_order
    db.commit()
    return {"message": "排序更新成功"}


@router.post("/study-record")
def create_study_record(data: StudyRecordCreate, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    record = StudyRecord(
        task_id=data.task_id, user_id=data.user_id,
        start_time=now, end_time=now, duration_minutes=data.duration_minutes,
        focus_score=data.focus_score, note=data.note,
    )
    db.add(record)
    db.commit()
    return {"message": "学习记录已保存"}


@router.post("/{task_id}/checkin", response_model=TaskOut)
def checkin_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    now = datetime.now(timezone.utc)
    if task.last_checkin:
        # 确保 last_checkin 有时区信息
        last_checkin = task.last_checkin
        if last_checkin.tzinfo is None:
            last_checkin = last_checkin.replace(tzinfo=timezone.utc)
        days_diff = (now - last_checkin).days
        # 防止同一天重复签到
        if days_diff == 0:
            return task
        task.streak_days = task.streak_days + 1 if days_diff == 1 else 1
    else:
        task.streak_days = 1
    task.last_checkin = now
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()
