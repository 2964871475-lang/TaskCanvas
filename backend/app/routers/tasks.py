from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from ..database import get_db
from ..models import Task

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
def list_tasks(
    owner_id: int,
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Task).filter(Task.owner_id == owner_id)
    if status:
        query = query.filter(Task.status == status)
    if category:
        query = query.filter(Task.category == category)
    return query.order_by(Task.sort_order, Task.created_at.desc()).all()


@router.post("/", response_model=TaskOut, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    update_data = data.model_dump(exclude_unset=True)
    if update_data.get("status") == "done" and task.status != "done":
        update_data["completed_at"] = datetime.now(timezone.utc)
    for key, value in update_data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/checkin", response_model=TaskOut)
def checkin_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    now = datetime.now(timezone.utc)
    if task.last_checkin:
        days_diff = (now - task.last_checkin).days
        task.streak_days = task.streak_days + 1 if days_diff <= 1 else 1
    else:
        task.streak_days = 1
    task.last_checkin = now
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()
