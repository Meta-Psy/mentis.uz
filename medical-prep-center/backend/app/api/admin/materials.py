from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth.admin import *
from app.services.content.topic_service import *

router = APIRouter()

@router.get("/files", response_model=AdminMaterialFilesListResponse)
async def get_material_files(
    section_id: Optional[int] = None,
    file_type: Optional[MaterialFileTypeEnum] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка файлов материалов"""
    try:
        # Логика получения файлов материалов
        # Используем существующие функции для работы с MaterialFile
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files", response_model=AdminMaterialFileResponse)
async def create_material_file(
    file_data: CreateMaterialFileRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание файла материала"""
    try:
        new_file = await add_material_file_db(
            db=db,
            section_id=file_data.section_id,
            file_type=file_data.file_type,
            title=file_data.title,
            author=file_data.author,
            file_size=file_data.file_size,
            file_format=file_data.file_format,
            download_url=file_data.download_url
        )
        return AdminMaterialFileResponse.from_orm(new_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))