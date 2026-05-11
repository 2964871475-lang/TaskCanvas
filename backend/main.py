from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import users, tasks, vocabulary, habits, stats

Base.metadata.create_all(bind=engine)

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


@app.get("/")
def root():
    return {"message": "TaskCanvas API is running", "docs": "/docs"}
