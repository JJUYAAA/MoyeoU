from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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

# --- Meeting (번개 모임) ---
class MeetingCreate(BaseModel):
    title: str
    category: str
    meeting_date: str
    meeting_time: str
    location_name: str
    max_participants: int
    content: Optional[str] = None
    password: str
    location_id: Optional[str] = None

class MeetingResponse(BaseModel):
    id: int
    title: str
    category: str
    meeting_date: str
    meeting_time: str
    location_name: str
    max_participants: int
    current_participants: int
    content: Optional[str] = None
    status: str
    location_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Participant (참여자) ---
class ParticipantJoin(BaseModel):
    nickname: str
    password: str

class ParticipantResponse(BaseModel):
    id: int
    meeting_id: int
    nickname: str
    created_at: datetime

    class Config:
        from_attributes = True