from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

# 1. 공공데이터 장소 테이블
class Location(Base):
    __tablename__ = "locations"

    id = Column(String, primary_key=True, index=True) # 공공데이터 ID
    title = Column(String, nullable=False)
    content_type = Column(String, nullable=False) # 관광지, 행사 등
    address = Column(String, nullable=True)
    map_x = Column(Float, nullable=True)
    map_y = Column(Float, nullable=True)
    image_url = Column(String, nullable=True)
    source = Column(String, nullable=True)

# 2. 번개 모임 테이블
class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    category = Column(String, nullable=False)
    meeting_date = Column(String, nullable=False) # 예: "2026-07-15" 또는 "오늘"
    meeting_time = Column(String, nullable=False) # 예: "19:00"
    location_name = Column(String, nullable=False) # 장소명
    max_participants = Column(Integer, default=4)
    current_participants = Column(Integer, default=1)
    content = Column(Text, nullable=True)
    password = Column(String, nullable=False) # 평문 암호화 비교 (요구사항)
    status = Column(String, default="OPEN") # OPEN, CLOSED, END
    location_id = Column(String, ForeignKey("locations.id"), nullable=True) # 공공데이터 연결
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 3. 참여자 테이블
class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    nickname = Column(String, nullable=False)
    password = Column(String, nullable=False) # 참여 취소용 비밀번호
    created_at = Column(DateTime(timezone=True), server_default=func.now())