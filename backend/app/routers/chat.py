import os
import traceback 
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, Field
from typing import Optional, List, Union 
from app.database import get_db
from app import models, schemas
from app.config import settings
from openai import OpenAI

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)

class SearchConditions(BaseModel):
    target: str = Field(
        ..., 
        description="검색 대상 분류. '할 사람', '구함', '번개', '동료' 등 함께 행위를 할 동료를 구하는 글이면 'MEETING', 단순 정보 탐색/장소 추천 요청이면 'LOCATION'"
    )
    category: Optional[str] = Field(
        None, 
        description="카테고리. 반드시 다음 7개 명칭 중 정확히 하나를 선택해야 함: '관광지', '음식점', '문화시설', '레포츠', '쇼핑', '여행코스', '축제공연행사'"
    )
    meeting_date: Optional[str] = Field(
        None, 
        description="YYYY-MM-DD 형식의 모임 날짜. 사용자가 '오늘'이나 '내일'이라고 하면 유추해서 실제 계산된 YYYY-MM-DD 포맷팅으로 채울 것."
    )
    offset: int = Field(
        default=0,
        description="데이터를 건너뛸 개수(offset). 추가적인 제안이나 다음 페이지의 탐색 의도가 드러나면 이 값을 5씩 누적하여 증가시킵니다."
    )

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    target: str 
    matched_data: List[Union[schemas.MeetingResponse, schemas.LocationResponse]] 

@router.post("", response_model=ChatResponse)
def chat_and_search(payload: ChatRequest, db: Session = Depends(get_db)):
    print(f"[디버깅] 실제 로드된 API KEY 글자수: {len(settings.OPENAI_API_KEY)}자")
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
                        f"너는 대화 속에서 사용자의 검색 의도를 'target(MEETING/LOCATION)'으로 분류하고 "
                        f"'category', 'meeting_date' 및 'offset'을 추출하는 대전 SSAFY '모여유' 비서야. "
                        f"오늘 날짜는 {today_str}일이야. \n\n"
                        f"1. 의도 분류(target): 함께 모여서 행위를 할 동료나 사람을 구하는 '번개' 목적의 글이면 'MEETING', 단순 장소나 맛집 추천 요령이면 'LOCATION'으로 분류해.\n"
                        f"2. 카테고리 매핑(category): 사용자의 자연어 질문에서 핵심 단어를 포착하여 다음 7개 명칭 중 '정확히 하나'만 선택해서 출력해.\n"
                        f"- 맛집, 밥집, 음식점, 카페, 먹을 곳 -> '음식점'\n"
                        f"- 관광, 놀거리, 구경, 명소 -> '관광지'\n"
                        f"- 운동, 걷기, 조깅, 산책, 레저 -> '레포츠'\n"
                        f"- 전시, 극장, 영화, 예술, 스터디룸 -> '문화시설'\n"
                        f"- 쇼핑, 옷, 마트 -> '쇼핑'\n"
                        f"- 여행, 드라이브, 코스, 힐링 -> '여행코스'\n"
                        f"- 축제, 페스티벌, 공연, 파티 -> '축제공연행사'\n\n"
                        f"3. 페이징(offset): 다른 거 추천해줘, 다음 등 기존과 다른 정보 제안 요구 시 5 단위로 할당해."
                    )
                },
                {"role": "user", "content": payload.message}
            ],
            response_format=SearchConditions,
        )
        
        extracted_data = completion.choices[0].message.parsed
        target = extracted_data.target 
        category = extracted_data.category
        meeting_date = extracted_data.meeting_date
        offset = extracted_data.offset

        print(f"[디버깅] 분류 결과 -> Target: {target}, Category: {category}, Date: {meeting_date}, Offset: {offset}")

    except Exception as e:
        print("❌ [OpenAI API 연동 에러 발생 로그]")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OpenAI 분석 중 에러가 발생했습니다: {str(e)}")

    if target == "MEETING":
        # ⚡ [개선] 스키마 검증 에러(N+1) 방지를 위해 joinedload로 댓글(comments) 목록을 즉시 강제 로드
        query = db.query(models.Meeting).options(joinedload(models.Meeting.comments)).filter(models.Meeting.status == "OPEN")

        meeting_category_map = {
            "관광지": "관광",
            "음식점": "맛집",
            "문화시설": "문화생활",
            "레포츠": "운동·산책",
            "쇼핑": "쇼핑",
            "여행코스": "여행",
            "축제공연행사": "문화생활"
        }
        search_category = meeting_category_map.get(category, category) if category else None
        
        if search_category:
            query = query.filter(models.Meeting.category == search_category)
        if meeting_date:
            query = query.filter(models.Meeting.meeting_date == meeting_date)
            
        matched_data = query.order_by(models.Meeting.meeting_date.asc(), models.Meeting.meeting_time.asc()).all()
        
        if not matched_data:
            reply = f"원하시는 {category if category else ''} 조건에 맞는 모집 중인 번개 모임이 아직 없네요. 😢 직접 새로운 번개를 만들어 대망의 첫 주최자가 되어 보시는 건 어떨까요?"
        else:
            conditions_text = []
            if meeting_date: conditions_text.append(f"날짜: {meeting_date}")
            if category: conditions_text.append(f"카테고리: {category}")
            desc = " 및 ".join(conditions_text) if conditions_text else "전체"
            
            reply = f"요청하신 조건({desc})에 매칭되는 번개 모임을 {len(matched_data)}개 찾았어요! 아래 리스트에서 확인해 보세요! 👇"

    else:
        query = db.query(models.Location)
        
        if category:
            query = query.filter(models.Location.content_type == category)
        
        matched_data = query.offset(offset).limit(5).all()
        
        if not matched_data:
            if offset > 0:
                reply = f"죄송해요, {category if category else '해당 카테고리'}에 대해 더 이상 보여드릴 장소가 없어요. 처음 추천한 곳들 중에서 마음에 드는 스팟이 없는지 다시 확인해 보시겠어요?"
            else:
                reply = f"죄송해요, 캠퍼스 주변의 {category if category else ''} 정보를 아직 DB에 업데이트하지 못했어요. 다른 단어로 물어봐 주시겠어요?"
        else:
            if offset > 0:
                reply = f"새로운 주변 {category} 핫스팟들을 더 찾아왔어요! 이곳들은 어떠신가요? 👇"
            else:
                reply = f"캠퍼스 주변의 멋진 {category} 스팟들을 소개해 드릴게요! 마음에 드는 곳이 있다면 카드 안의 버튼을 눌러 번개를 만들어 보세요! 👇"

    return ChatResponse(
        reply=reply,
        target=target, 
        matched_data=matched_data 
    )