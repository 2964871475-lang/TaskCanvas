from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, timezone

from ..database import get_db
from ..models import Comment, User

router = APIRouter(prefix="/api/comments", tags=["评论"])


class CommentCreate(BaseModel):
    content: str
    task_id: int
    user_id: int


class CommentOut(BaseModel):
    id: int
    content: str
    task_id: int
    user_id: int
    username: str
    created_at: datetime


@router.post("/", response_model=CommentOut, status_code=201)
def create_comment(data: CommentCreate, db: Session = Depends(get_db)):
    comment = Comment(content=data.content, task_id=data.task_id, user_id=data.user_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    user = db.get(User, data.user_id)
    return CommentOut(
        id=comment.id, content=comment.content, task_id=comment.task_id,
        user_id=comment.user_id, username=user.username if user else "未知",
        created_at=comment.created_at,
    )


@router.get("/task/{task_id}", response_model=List[CommentOut])
def list_comments(task_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at).all()
    result = []
    for c in comments:
        user = db.get(User, c.user_id)
        result.append(CommentOut(
            id=c.id, content=c.content, task_id=c.task_id,
            user_id=c.user_id, username=user.username if user else "未知",
            created_at=c.created_at,
        ))
    return result


@router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    db.delete(comment)
    db.commit()
