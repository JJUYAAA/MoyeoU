from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings

# 서버 시작 시 SQLite 테이블 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

# CORS 허용 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: 추후 개발 완료 시 각 라우터를 이곳에 포함시킵니다.
# from app.routers import meetings, locations, chat
# app.include_router(meetings.router)
# app.include_router(locations.router)
# app.include_router(chat.router)

@app.get("/")
def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}