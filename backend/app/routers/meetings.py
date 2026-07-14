# 모임 생성 라우터
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Location, Meeting
from app.schemas import (
    MeetingCreate,
    MeetingResponse,
)

# URL 설정
router = APIRouter(
    prefix="/api/meetings",
    tags=["meetings"],
)


@router.post(
    "",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_meeting(
    payload: MeetingCreate,
    db: Session = Depends(get_db), # db 세션 받기
):
    # location_id가 전달됐다면 실제 장소인지 확인
    if payload.location_id is not None:
        location = db.get(
            Location,
            payload.location_id,
        )

        if location is None:
            raise HTTPException(
                status_code=404,
                detail="연결할 장소를 찾을 수 없습니다.",
            )

    # Pydantic 객체를 Dictionary로 바꿔 Meeting에 전달
    meeting = Meeting(
        **payload.model_dump(),
        current_participants=1,
        status="OPEN",
    )

    # 데이터 저장
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return meeting