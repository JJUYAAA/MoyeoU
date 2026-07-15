import os
import traceback 
from datetime import date
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

class SearchConditions(BaseModel):
    category: Optional[str] = Field(
        None, 
        description="모임 카테고리. 반드시 다음 6개 명칭 중 정확히 하나를 선택해야 함: '관광', '문화생활', '운동·산책', '맛집', '쇼핑', '여행'"
    )
    meeting_date: Optional[str] = Field(
        None, 
        description="YYYY-MM-DD 형식의 모임 날짜. 사용자가 '오늘'이나 '내일'이라고 하면 유추해서 실제 계산된 YYYY-MM-DD 포맷팅으로 채울 것."
    )

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    matched_meetings: List[schemas.MeetingResponse]

@router.post("", response_model=ChatResponse)
def chat_and_search(payload: ChatRequest, db: Session = Depends(get_db)):
    # API 키 상태 실시간 터미널 로깅 추가
    print(f"[디버깅] 로드된 API KEY 앞부분: {str(settings.OPENAI_API_KEY)[:10]}...")

    if not settings.OPENAI_API_KEY or "sk-" not in settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해 주세요."
        )

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    today_str = str(date.today()) 

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        f"너는 대화 속에서 모임 검색을 위한 'category'와 'meeting_date'를 추출하는 대전 SSAFY '모여유' 비서야. "
                        f"오늘 날짜는 {today_str}일이야. 사용자의 자연어 질문에서 날짜나 카테고리를 면밀히 분석해서 구조화된 데이터로 추출해줘. "
                        f"특히 카테고리는 사용자의 요구(맛있는 거 먹기, 밥 먹기 등 -> '맛집', 놀러가기, 구경하기 등 -> '관광')를 파악하여 지정된 분류명으로 매핑해줘."
                    )
                },
                {"role": "user", "content": payload.message}
            ],
            response_format=SearchConditions,
        )
        
        extracted_data = completion.choices[0].message.parsed
        category = extracted_data.category
        meeting_date = extracted_data.meeting_date

    except Exception as e:
        # 💡 터미널에 시원하게 에러 이유와 몇 번째 줄에서 터졌는지 다 찍어줍니다.
        print("❌ [OpenAI API 연동 에러 발생 로그]")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OpenAI 분석 중 에러가 발생했습니다: {str(e)}")

    query = db.query(models.Meeting).filter(models.Meeting.status == "OPEN")
    
    if category:
        query = query.filter(models.Meeting.category == category)
    if meeting_date:
        query = query.filter(models.Meeting.meeting_date == meeting_date)
        
    matched_meetings = query.order_by(models.Meeting.meeting_date.asc(), models.Meeting.meeting_time.asc()).all()

    if not matched_meetings:
        reply = f"원하시는 {category if category else ''} 조건에 맞는 모집 중인 번개 모임이 아직 없네요. 😢 직접 새로운 번개를 만들어 대망의 첫 주최자가 되어 보시는 건 어떨까요?"
    else:
        conditions_text = []
        if meeting_date: conditions_text.append(f"날짜: {meeting_date}")
        if category: conditions_text.append(f"카테고리: {category}")
        desc = " 및 ".join(conditions_text) if conditions_text else "전체"
        
        reply = f"요청하신 조건({desc})에 매칭되는 번개 모임을 {len(matched_meetings)}개 찾았어요! 아래 리스트에서 확인해 보세요! 👇"

    return ChatResponse(
        reply=reply,
        matched_meetings=matched_meetings
    )