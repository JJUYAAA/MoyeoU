from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)
from typing import Optional, List, Literal
from datetime import date, datetime, time

# 모집 카테고리
Category = Literal[
    "모각코·공부",
    "식사·카페",
    "운동",
    "문화·행사",
    "나들이",
]

# 모집 상태
MeetingStatus = Literal[
    "OPEN",
    "CLOSED",
    "END",
]

# --- Location (공공데이터 장소) ---
class LocationBase(BaseModel):
    id: str
    title: str
    content_type: str
    address: Optional[str] = None
    map_x: Optional[float] = None
    map_y: Optional[float] = None
    image_url: Optional[str] = None
    source: Optional[str] = None

class LocationResponse(LocationBase):
    class Config:
        from_attributes = True

# 생성·수정·응답에서 공통으로 사용하는 모임 필드
class MeetingBase(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=100,
    )
    category: Category
    meeting_date: date
    meeting_time: time
    location_name: str = Field(
        min_length=1,
        max_length=150,
    )
    max_participants: int = Field(
        ge=2,
        le=100,
    )
    content: str = Field(
        min_length=1,
        max_length=3000,
    )
    location_id: str | None = Field(
        default=None,
        max_length=100,
    )

    @field_validator(
        "title",
        "location_name",
        "content",
    )
    @classmethod
    def remove_surrounding_spaces(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "공백만 입력할 수 없습니다."
            )

        return value
    
# 모임 생성 요청
class MeetingCreate(MeetingBase):
    password: str = Field(
        min_length=4,
        max_length=100,
    )

    @field_validator("meeting_date")
    @classmethod
    def meeting_date_cannot_be_past(
        cls,
        value: date,
    ) -> date:
        if value < date.today():
            raise ValueError(
                "과거 날짜로 모임을 만들 수 없습니다."
            )

        return value

class MeetingResponse(MeetingBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    current_participants: int
    status: MeetingStatus
    created_at: datetime
    updated_at: datetime

# 참여 신청 요청
class ParticipantJoin(BaseModel):
    nickname: str = Field(
        min_length=1,
        max_length=30,
    )
    password: str = Field(
        min_length=4,
        max_length=100,
    )
    
# 참여 응답
class ParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    nickname: str
    created_at: datetime