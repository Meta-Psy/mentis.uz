from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth.admin import *
from app.services.roles.student_service import *

router = APIRouter()

@router.get("/", response_model=AdminUniversitiesListResponse)
async def get_universities(
    university_type: Optional[UniversityTypeEnum] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка университетов"""
    try:
        universities = await get_all_universities_db(db)
        
        # Фильтрация
        if university_type:
            universities = [u for u in universities if u.type == university_type]
        if search:
            universities = [u for u in universities if search.lower() in u.name.lower()]
        
        total = len(universities)
        paginated = universities[offset:offset + limit]
        
        # Обогащаем данными
        enriched_universities = []
        for university in paginated:
            uni_data = AdminUniversityResponse.from_orm(university)
            enriched_universities.append(uni_data)
        
        return AdminUniversitiesListResponse(
            items=enriched_universities,
            total=total,
            limit=limit,
            offset=offset,
            has_next=offset + limit < total,
            has_prev=offset > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=AdminUniversityResponse)
async def create_university(
    university_data: CreateUniversityRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание университета"""
    try:
        new_university = await add_university_db(
            db=db,
            name=university_data.name,
            entrance_score=university_data.entrance_score,
            university_type=university_data.type,
            location=university_data.location,
            website_url=university_data.website_url,
            logo_url=university_data.logo_url,
            contact_phone=university_data.contact_phone
        )
        return AdminUniversityResponse.from_orm(new_university)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))