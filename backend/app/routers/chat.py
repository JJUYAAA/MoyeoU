import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from app.database import get_db
from app import models, schemas
from app.config import settings
from openai import OpenAI

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)

# --- OpenAI가 추출할 검색 조건의 규격을 정의하는 Pydantic 스키마 ---
class SearchConditions(BaseModel):
    category: Optional[str] = Field(
        None, 
        description="모임 카테고리. 다음 5개 중 하나여야 함: '모각코·공부', '식사·카페', '운동', '문화·행사', '나들이'"
    )
    meeting_date: Optional[str] = Field(
        None, 
        description="YYYY-MM-DD 형식의 모임 날짜. 사용자가 '오늘'이나 '내일'이라고 하면 유추해서 포맷팅할 것."
    )

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    matched_meetings: List[schemas.MeetingResponse]


# --- 💬 OpenAI 연동 실시간 챗봇 및 검색 API ---
@router.post("/", response_model=ChatResponse)
def chat_and_search(payload: ChatRequest, db: Session = Depends(get_db)):
    # 🚨 .env에 OPENAI_API_KEY가 등록되어 있지 않으면 미리 에러 핸들링을 합니다.
    if not settings.OPENAI_API_KEY or "sk-" not in settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해 주세요."
        )

    # 1. OpenAI 클라이언트 초기화
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        # 2. System Prompt를 통해 자연어 질문에서 카테고리와 날짜 추출 지시
        # GPT-4o-mini 모델을 사용하여 구조화된 JSON 데이터로 바로 받아옵니다.
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 대화 속에서 모임 검색을 위한 'category'와 'meeting_date'를 추출하는 AI 비서야. 오늘 날짜는 2026-07-14일이야. 사용자의 질문에서 날짜나 카테고리를 찾아서 구조화된 데이터로 채워줘."},
                {"role": "user", "content": payload.message}
            ],
            response_format=SearchConditions, # Pydantic 모델을 응답 포맷으로 직접 주입
        )
        
        # 구조화된 추출 데이터 가져오기
        extracted_data = completion.choices[0].message.parsed
        category = extracted_data.category
        meeting_date = extracted_data.meeting_date

    except Exception as e:
        # API 오류 등이 발생했을 때의 예외 처리
        raise HTTPException(status_code=500, detail=f"OpenAI 분석 중 에러가 발생했습니다: {str(e)}")

    # 3. 추출된 조건으로 SQLite DB 조회
    query = db.query(models.Meeting).filter(models.Meeting.status == "OPEN")
    
    if category:
        query = query.filter(models.Meeting.category == category)
    if meeting_date:
        query = query.filter(models.Meeting.meeting_date == meeting_date)
        
    matched_meetings = query.all()

    # 4. 자연어 답변 생성
    if not matched_meetings:
        reply = "원하시는 조건에 맞는 모집 중인 번개 모임이 아직 없네요. 😢 직접 새로운 번개를 만들어 첫 주최자가 되어 보시는 건 어떨까요?"
    else:
        conditions_text = []
        if meeting_date: conditions_text.append(f"날짜: {meeting_date}")
        if category: conditions_text.append(f"카테고리: {category}")
        desc = " 및 ".join(conditions_text) if conditions_text else "전체"
        
        reply = f"요청하신 조건({desc})에 매칭되는 번개 모임을 {len(matched_meetings)}개 찾았어요! 아래 카드 리스트에서 지금 바로 확인해 보세요! 👇"

    return ChatResponse(
        reply=reply,
        matched_meetings=matched_meetings
    )