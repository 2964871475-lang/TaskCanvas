from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import openpyxl
import io
import csv

from ..database import get_db
from ..models import WordBook, Word, WordStudyRecord, WordGameRecord

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


@router.post("/books/{book_id}/import-file", status_code=201)
async def import_file(book_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """从 Excel(.xlsx) 或 CSV 文件批量导入单词
    格式要求：第一行为表头，列顺序为 英文, 中文, 音标(可选), 例句(可选)
    表头名称可以自定义，但顺序必须正确
    """
    book = db.get(WordBook, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="词书不存在")

    filename = file.filename.lower()
    rows = []

    if filename.endswith(".xlsx"):
        content = await file.read()
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True)
        ws = wb.active
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i == 0:  # 跳过表头
                continue
            rows.append([str(c) if c is not None else "" for c in row])
        wb.close()
    elif filename.endswith(".csv"):
        content = await file.read()
        text = content.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(text))
        for i, row in enumerate(reader):
            if i == 0:
                continue
            rows.append(row)
    else:
        raise HTTPException(status_code=400, detail="仅支持 .xlsx 和 .csv 文件")

    count = 0
    for row in rows:
        if len(row) < 2 or not row[0].strip() or not row[1].strip():
            continue
        word = Word(
            book_id=book_id,
            english=row[0].strip(),
            chinese=row[1].strip(),
            phonetic=row[2].strip() if len(row) > 2 else "",
            example=row[3].strip() if len(row) > 3 else "",
        )
        db.add(word)
        count += 1

    db.commit()
    return {"message": f"成功导入 {count} 个单词", "count": count}


class GameSaveIn(BaseModel):
    user_id: int
    username: str
    score: int
    accuracy: float
    total_pairs: int
    correct_count: int
    time_seconds: int


class GameRecordOut(BaseModel):
    id: int
    username: str
    score: int
    accuracy: float
    total_pairs: int
    correct_count: int
    time_seconds: int
    created_at: datetime
    model_config = {"from_attributes": True}


@router.post("/game/save", response_model=GameRecordOut, status_code=201)
def save_game_record(data: GameSaveIn, db: Session = Depends(get_db)):
    record = WordGameRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/game/leaderboard", response_model=List[GameRecordOut])
def game_leaderboard(limit: int = 20, db: Session = Depends(get_db)):
    return (
        db.query(WordGameRecord)
        .order_by(WordGameRecord.score.desc(), WordGameRecord.time_seconds.asc())
        .limit(limit)
        .all()
    )
