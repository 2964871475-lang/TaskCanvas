from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

from ..database import get_db
from ..models import WordBook, Word, WordStudyRecord

router = APIRouter(prefix="/api/vocabulary", tags=["单词学习"])

# 艾宾浩斯复习间隔（小时）
EBBINGHAUS_INTERVALS = [1, 2, 4, 8, 24, 48, 168, 336]


class WordBookCreate(BaseModel):
    name: str
    description: str = ""
    user_id: int


class WordCreate(BaseModel):
    english: str
    chinese: str
    phonetic: str = ""
    example: str = ""


class WordOut(BaseModel):
    id: int
    book_id: int
    english: str
    chinese: str
    phonetic: str
    example: str
    mastery: float
    next_review: Optional[datetime]
    review_count: int
    error_count: int
    is_starred: bool

    model_config = {"from_attributes": True}


class WordBookOut(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StudyAnswer(BaseModel):
    is_correct: bool


def calc_next_review(review_count: int) -> datetime:
    idx = min(review_count, len(EBBINGHAUS_INTERVALS) - 1)
    hours = EBBINGHAUS_INTERVALS[idx]
    return datetime.now(timezone.utc) + timedelta(hours=hours)


@router.post("/books", response_model=WordBookOut, status_code=201)
def create_book(data: WordBookCreate, db: Session = Depends(get_db)):
    book = WordBook(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("/books", response_model=List[WordBookOut])
def list_books(user_id: int, db: Session = Depends(get_db)):
    return db.query(WordBook).filter(WordBook.user_id == user_id).all()


@router.post("/books/{book_id}/words", response_model=WordOut, status_code=201)
def add_word(book_id: int, data: WordCreate, db: Session = Depends(get_db)):
    word = Word(book_id=book_id, **data.model_dump())
    db.add(word)
    db.commit()
    db.refresh(word)
    return word


@router.post("/books/{book_id}/words/batch", response_model=List[WordOut], status_code=201)
def batch_add_words(book_id: int, words: List[WordCreate], db: Session = Depends(get_db)):
    result = []
    for w in words:
        word = Word(book_id=book_id, **w.model_dump())
        db.add(word)
        result.append(word)
    db.commit()
    for w in result:
        db.refresh(w)
    return result


@router.get("/books/{book_id}/words", response_model=List[WordOut])
def list_words(book_id: int, db: Session = Depends(get_db)):
    return db.query(Word).filter(Word.book_id == book_id).all()


@router.get("/review", response_model=List[WordOut])
def get_review_words(user_id: int, limit: int = 20, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    words = (
        db.query(Word)
        .join(WordBook)
        .filter(WordBook.user_id == user_id, Word.next_review <= now)
        .order_by(Word.next_review)
        .limit(limit)
        .all()
    )
    return words


@router.get("/review-count")
def get_review_count(user_id: int, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    count = (
        db.query(Word)
        .join(WordBook)
        .filter(WordBook.user_id == user_id, Word.next_review <= now)
        .count()
    )
    return {"count": count}


@router.post("/words/{word_id}/answer", response_model=WordOut)
def answer_word(word_id: int, data: StudyAnswer, user_id: int = 0, db: Session = Depends(get_db)):
    word = db.query(Word).get(word_id)
    if not word:
        raise HTTPException(status_code=404, detail="单词不存在")
    record = WordStudyRecord(word_id=word_id, user_id=user_id, is_correct=data.is_correct)
    db.add(record)
    if data.is_correct:
        word.review_count += 1
        word.mastery = min(100, word.mastery + 15)
    else:
        word.error_count += 1
        word.mastery = max(0, word.mastery - 20)
        word.review_count = max(0, word.review_count - 1)
    word.next_review = calc_next_review(word.review_count)
    db.commit()
    db.refresh(word)
    return word


@router.post("/words/{word_id}/star", response_model=WordOut)
def toggle_star(word_id: int, db: Session = Depends(get_db)):
    word = db.get(Word, word_id)
    if not word:
        raise HTTPException(status_code=404, detail="单词不存在")
    word.is_starred = not word.is_starred
    db.commit()
    db.refresh(word)
    return word


@router.get("/error-words", response_model=List[WordOut])
def get_error_words(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Word)
        .join(WordBook)
        .filter(WordBook.user_id == user_id, Word.error_count > 0)
        .order_by(Word.error_count.desc())
        .all()
    )
