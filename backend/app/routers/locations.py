import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/api/locations",
    tags=["Locations"]
)

# JSON 파일들이 위치한 경로
JSON_FILES = [
    "대전_충청권_관광지.json",
    "대전_충청권_레포츠.json",
    "대전_충청권_문화시설.json",
    "대전_충청권_쇼핑.json",
    "대전_충청권_숙박.json",
    "대전_충청권_여행코스.json",
    "대전_충청권_음식점.json",
    "대전_충청권_축제공연행사.json"
]

@router.post("/init-data")
def initialize_locations_data(db: Session = Depends(get_db)):
    """
    로컬 JSON 파일들을 읽어서 SQLite DB에 초기 데이터를 밀어 넣습니다. (중복 없이 적재)
    """
    inserted_count = 0
    for file_name in JSON_FILES:
        if not os.path.exists(file_name):
            continue
            
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data.get("items", [])
            content_type = data.get("contentType", "기타")
            
            for item in items:
                # 중복 등록 방지 (contentid 기준)
                content_id = str(item.get("contentid"))
                exists = db.query(models.Location).filter(models.Location.id == content_id).first()
                if exists:
                    continue
                
                # DB 모델 생성 및 삽입
                db_location = models.Location(
                    id=content_id,
                    title=item.get("title", "이름 없음"),
                    content_type=content_type,
                    address=item.get("addr1", ""),
                    map_x=float(item.get("mapx")) if item.get("mapx") else None,
                    map_y=float(item.get("mapy")) if item.get("mapy") else None,
                    image_url=item.get("firstimage", ""),
                    source="한국관광공사 국문 관광정보 서비스"
                )
                db.add(db_location)
                inserted_count += 1
                
    db.commit()
    return {"status": "success", "message": f"총 {inserted_count}개의 대전/충청 장소 데이터가 성공적으로 적재되었습니다."}


# 장소 목록 조회 API (필터 가능)
@router.get("/", response_model=List[schemas.LocationResponse])
def get_locations(
    content_type: Optional[str] = None, 
    keyword: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(models.Location)
    if content_type:
        query = query.filter(models.Location.content_type == content_type)
    if keyword:
        query = query.filter(models.Location.title.contains(keyword))
    return query.limit(50).all() # 과부하 방지를 위해 50개 제한


# 장소 상세 조회 API
@router.get("/{id}", response_model=schemas.LocationResponse)
def get_location_detail(id: str, db: Session = Depends(get_db)):
    location = db.query(models.Location).filter(models.Location.id == id).first()
    if not location:
        raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다.")
    return location