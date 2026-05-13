from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
import json

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
    scheduled_date: Optional[datetime] = None
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
    scheduled_date: Optional[datetime] = None
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
    scheduled_date: Optional[datetime]
    sort_order: int
    streak_days: int
    created_at: datetime
    completed_at: Optional[datetime]
    model_config = {"from_attributes": True}


@router.get("/", response_model=List[TaskOut])
def list_tasks(owner_id: int, status: Optional[str] = None, category: Optional[str] = None, scheduled_date: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Task).filter(Task.owner_id == owner_id)
    if status:
        query = query.filter(Task.status == status)
    if category:
        query = query.filter(Task.category == category)
    if scheduled_date:
        query = query.filter(func.date(Task.scheduled_date) == scheduled_date)
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
    if update_data.get("status") == "done" and task.status != "done":
        update_data["completed_at"] = datetime.now(timezone.utc)
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


class BatchDeleteItem(BaseModel):
    ids: List[int]


@router.post("/batch-delete")
def batch_delete(data: BatchDeleteItem, db: Session = Depends(get_db)):
    deleted = db.query(Task).filter(Task.id.in_(data.ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"已删除 {deleted} 条任务", "deleted": deleted}


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
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()


@router.get("/export/{user_id}")
def export_tasks(user_id: int, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.owner_id == user_id).order_by(Task.sort_order, Task.created_at.desc()).all()
    result = []
    for t in tasks:
        result.append({
            "title": t.title,
            "description": t.description or "",
            "category": t.category,
            "subject": t.subject,
            "priority": t.priority,
            "difficulty": t.difficulty,
            "estimated_minutes": t.estimated_minutes,
            "deadline": t.deadline.isoformat() if t.deadline else None,
            "scheduled_date": t.scheduled_date.strftime("%Y-%m-%d") if t.scheduled_date else None,
            "status": t.status,
        })
    return JSONResponse(content={"tasks": result, "count": len(result)})


@router.post("/import/{user_id}")
async def import_tasks(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="请上传 JSON 文件")
    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="文件格式错误，无法解析 JSON")

    task_list = data if isinstance(data, list) else data.get("tasks", [])
    if not task_list:
        raise HTTPException(status_code=400, detail="未找到有效的任务数据")

    imported = 0
    skipped = 0
    for item in task_list:
        title = item.get("title", "").strip()
        if not title:
            skipped += 1
            continue
        category = item.get("category", "daily")
        if category not in ("daily", "longterm", "mistake"):
            category = "daily"
        priority = item.get("priority", 2)
        if priority not in (1, 2, 3):
            priority = 2
        scheduled = item.get("scheduled_date")
        deadline_val = datetime.fromisoformat(item["deadline"]) if item.get("deadline") else None
        if not scheduled and deadline_val:
            scheduled = deadline_val.strftime("%Y-%m-%d")
        task = Task(
            title=title,
            description=item.get("description", ""),
            category=category,
            subject=item.get("subject", "其他"),
            priority=priority,
            difficulty=item.get("difficulty", 3),
            estimated_minutes=item.get("estimated_minutes", 60),
            deadline=deadline_val,
            scheduled_date=datetime.strptime(scheduled, "%Y-%m-%d") if scheduled else datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"),
            status=item.get("status", "pending"),
            owner_id=user_id,
        )
        db.add(task)
        imported += 1

    db.commit()
    return {"message": f"导入完成：成功 {imported} 条，跳过 {skipped} 条", "imported": imported, "skipped": skipped}
