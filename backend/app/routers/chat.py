import os
import traceback 
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
    # 검색 대상 분류 (모임 모집 vs 순수 장소 추천) 추출 필드 
    target: str = Field(
        ..., 
        description="검색 대상 분류. '할 사람', '구함', '번개', '동료' 등 함께 행위를 할 동료를 구하는 글이면 'MEETING', 단순 정보 탐색/장소 추천 요청이면 'LOCATION'"
    )
    # 모임 카테고리 (description에 공통 데이터 매핑 기준 명시)
    category: Optional[str] = Field(
        None, 
        description="카테고리. 반드시 다음 6개 명칭 중 정확히 하나를 선택해야 함: '관광', '문화생활', '운동·산책', '맛집', '쇼핑', '여행'"
    )
    meeting_date: Optional[str] = Field(
        None, 
        description="YYYY-MM-DD 형식의 모임 날짜. 사용자가 '오늘'이나 '내일'이라고 하면 유추해서 실제 계산된 YYYY-MM-DD 포맷팅으로 채울 것."
    )

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    #  답변 데이터가 모임(MEETING)인지 장소(LOCATION)인지 구분
    target: str 
    # Pydantic이 LocationResponse와 MeetingResponse 규격을 정상적으로 파악하고 직렬화하도록 명시
    matched_data: List[Union[schemas.MeetingResponse, schemas.LocationResponse]] 

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
                    # 모임 검색 조건 추출뿐만 아니라, Target(의도 분류)을 추가로 추출하도록 프롬프트 고도화
                    "content": (
                        f"너는 대화 속에서 사용자의 검색 의도를 'target(MEETING/LOCATION)'으로 분류하고 "
                        f"'category', 'meeting_date'를 추출하는 대전 SSAFY '모여유' 비서야. "
                        f"오늘 날짜는 {today_str}일이야. "
                        f"사용자의 자연어 질문에서 '함께할 사람/번개 구함'이 핵심이면 'MEETING', 단순 '맛집/장소 추천' 요청이면 'LOCATION'으로 target을 분류해줘. "
                        f"특히 사용자가 맛집, 밥집, 음식점, 먹을 곳 등을 언급하면 category 값을 반드시 '음식점'으로 매핑하고, "
                        f"관광, 놀거리, 구경 등을 언급하면 '관광지', 걷기, 조깅, 레저 활동을 언급하면 '레포츠', 전시, 예술, 스터디룸 등을 언급하면 '문화시설', 쇼핑, 옷, 신발을 언급하면 '쇼핑', 여행, 코스, 힐링 등을 언급하면 '여행코스', 축제, 페스티벌, 공연, 파티 등을 언급하면 '축제공연행사'로 최종 분류하여 출력해야 해."
                    )
                },
                {"role": "user", "content": payload.message}
            ],
            response_format=SearchConditions,
        )
        
        extracted_data = completion.choices[0].message.parsed
        # 분류 결과(target) 추출
        target = extracted_data.target 
        category = extracted_data.category
        meeting_date = extracted_data.meeting_date

        # 분류 결과 실시간 터미널 디버깅 로깅
        print(f"[디버깅] 분류 결과 -> Target: {target}, Category: {category}, Date: {meeting_date}")

    except Exception as e:
        # 💡 터미널에 시원하게 에러 이유와 몇 번째 줄에서 터졌는지 다 찍어줍니다.
        print("❌ [OpenAI API 연동 에러 발생 로그]")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OpenAI 분석 중 에러가 발생했습니다: {str(e)}")

    # 하이브리드 분기 처리: GPT가 분석한 target에 따라 다른 DB 테이블 조회
    
    # Case1: 'MEETING'일 때
    if target == "MEETING":
        query = db.query(models.Meeting).filter(models.Meeting.status == "OPEN")

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
            
        # matched_meetings를 matched_data로 변경
        matched_data = query.order_by(models.Meeting.meeting_date.asc(), models.Meeting.meeting_time.asc()).all()
        if not matched_data:
            reply = f"원하시는 {category if category else ''} 조건에 맞는 모집 중인 번개 모임이 아직 없네요. 😢 직접 새로운 번개를 만들어 대망의 첫 주최자가 되어 보시는 건 어떨까요?"
        else:
            conditions_text = []
            if meeting_date: conditions_text.append(f"날짜: {meeting_date}")
            if category: conditions_text.append(f"카테고리: {category}")
            desc = " 및 ".join(conditions_text) if conditions_text else "전체"
            
            reply = f"요청하신 조건({desc})에 매칭되는 번개 모임을 {len(matched_data)}개 찾았어요! 아래 리스트에서 확인해 보세요! 👇"

    # Case2:'LOCATION'일 때 (공공데이터 테이블 서칭)
    else:
        # Location 테이블에서 해당 카테고리(content_type)에 맞는 장소들 조회 
        query = db.query(models.Location)
        
        # GPT가 변환하여 내뱉은 실제 DB 카테고리 값('음식점', '관광지' 등)을 사용해 즉시 쿼리 필터링
        if category:
            query = query.filter(models.Location.content_type == category)
        
        # 5개만 뽑음
        matched_data = query.limit(5).all()
        
        # 장소 검색 결과에 대한 자연어 답변 생성
        if not matched_data:
            reply = f"죄송해요, 캠퍼스 주변의 {category if category else ''} 정보를 아직 DB에 업데이트하지 못했어요. 다른 단어로 물어봐 주시겠어요?"
        else:
            reply = f"캠퍼스 주변의 멋진 {category} 스팟들을 소개해 드릴게요! 마음에 드는 곳이 있다면 카드 안의 버튼을 눌러 번개를 만들어 보세요! 👇"

    return ChatResponse(
        reply=reply,
        #최종 분류 결과(target) 반환
        target=target, 
        # matched_meetings 대신 target에 따라 유동적으로 조회된 matched_data 반환
        matched_data=matched_data 
    )