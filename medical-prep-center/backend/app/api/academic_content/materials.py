from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

# Импорты базы данных и моделей
from app.database import get_db
from app.database.models.academic import MaterialFileType

# Импорты сервисов
from app.services.content.topic_service import (
    get_topic_with_details_db,
    add_material_file_db,
    search_materials_db
)
from app.services.content.subject_service import (
    get_subject_materials_db, 
    get_materials_statistics_db
)
from app.services.content.section_service import get_section_with_materials_db

# Импорты схем
from app.schemas.assessment.materials import (
    MaterialsResponseModel,
    SectionResponse,
    TopicDetailResponse,
    MaterialFileCreate,
    SearchResult,
    MaterialsStatistics
)

# Создание роутера
router = APIRouter()

# ===========================================
# ПОЛУЧЕНИЕ МАТЕРИАЛОВ ПО ПРЕДМЕТУ
# ===========================================

@router.get("/{subject_name}", 
            response_model=MaterialsResponseModel,
            summary="Получить материалы предмета",
            description="Получение всех материалов по предмету (chemistry/biology)")
async def get_materials_by_subject(
    subject_name: str = Path(..., description="Название предмета"),
    db: AsyncSession = Depends(get_db)
) -> MaterialsResponseModel:
    """
    Получение всех материалов по предмету
    
    - **subject_name**: Название предмета (chemistry или biology)
    
    Возвращает структуру материалов со всеми разделами, темами и файлами
    """
    try:
        # Валидация названия предмета
        valid_subjects = ['chemistry', 'biology', 'химия', 'биология']
        if subject_name.lower() not in valid_subjects:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недопустимое название предмета. Используйте: chemistry или biology"
            )
        
        # Получение данных
        subject_data = await get_subject_materials_db(db, subject_name)
        
        # Формирование ответа в нужном формате
        materials_data = {
            subject_name.lower(): subject_data
        }
        
        return MaterialsResponseModel(materials=materials_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

# ===========================================
# ПОЛУЧЕНИЕ МАТЕРИАЛОВ РАЗДЕЛА
# ===========================================

@router.get("/section/{section_id}", 
            response_model=SectionResponse,
            summary="Получить материалы раздела",
            description="Получение всех материалов конкретного раздела")
async def get_section_materials(
    section_id: int,
    db: AsyncSession = Depends(get_db)
) -> SectionResponse:
    """
    Получение материалов конкретного раздела
    
    - **section_id**: ID раздела
    
    Возвращает все файлы, темы и информацию о разделе
    """
    try:
        if section_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID раздела должен быть положительным числом"
            )
        
        section_data = await get_section_with_materials_db(db, section_id)
        return SectionResponse(**section_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения материалов раздела: {str(e)}"
        )

# ===========================================
# ПОЛУЧЕНИЕ ДЕТАЛЕЙ ТЕМЫ
# ===========================================

@router.get("/topic/{topic_id}", 
            response_model=TopicDetailResponse,
            summary="Получить детали темы",
            description="Получение подробной информации о теме")
async def get_topic_details(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
) -> TopicDetailResponse:
    """
    Получение деталей конкретной темы
    
    - **topic_id**: ID темы
    
    Возвращает все детали темы включая домашнее задание, видео и тесты
    """
    try:
        if topic_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID темы должен быть положительным числом"
            )
        
        topic_data = await get_topic_with_details_db(db, topic_id)
        return TopicDetailResponse(**topic_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения темы: {str(e)}"
        )

# ===========================================
# ДОБАВЛЕНИЕ ФАЙЛА К РАЗДЕЛУ
# ===========================================

@router.post("/section/{section_id}/files",
             summary="Добавить файл к разделу",
             description="Добавление нового файла материала к разделу")
async def add_section_file(
    section_id: int,
    file_data: MaterialFileCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Добавление файла к разделу
    
    - **section_id**: ID раздела
    - **file_data**: Данные файла (название, автор, размер, тип)
    
    Возвращает подтверждение создания файла
    """
    try:
        if section_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID раздела должен быть положительным числом"
            )
        
        # Валидация типа файла
        if file_data.file_type not in ['book', 'test_book']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тип файла должен быть 'book' или 'test_book'"
            )
        
        # Создание файла
        material_file = await add_material_file_db(
            db=db, 
            section_id=section_id,
            file_type=MaterialFileType(file_data.file_type),
            title=file_data.title,
            author=file_data.author,
            file_size=file_data.size,
            file_format=file_data.format,
            download_url=file_data.url
        )
        
        return {
            "status": "success", 
            "message": "Файл успешно добавлен",
            "file_id": material_file.file_id,
            "data": {
                "id": material_file.file_id,
                "title": material_file.title,
                "author": material_file.author,
                "size": material_file.file_size,
                "format": material_file.file_format
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка добавления файла: {str(e)}"
        )

# ===========================================
# ПОИСК ПО МАТЕРИАЛАМ
# ===========================================

@router.get("/search", 
            response_model=List[SearchResult],
            summary="Поиск материалов",
            description="Поиск по всем материалам с фильтрацией")
async def search_materials(
    query: str = Query(..., min_length=2, max_length=100, description="Поисковый запрос"),
    subject_filter: Optional[str] = Query(None, description="Фильтр по предмету"),
    section_filter: Optional[int] = Query(None, description="Фильтр по разделу"),
    limit: Optional[int] = Query(20, le=100, description="Лимит результатов"),
    db: AsyncSession = Depends(get_db)
) -> List[SearchResult]:
    """
    Поиск по материалам
    
    - **query**: Поисковый запрос (минимум 2 символа)
    - **subject_filter**: Фильтр по предмету (опционально)
    - **section_filter**: Фильтр по разделу (опционально)
    - **limit**: Максимальное количество результатов (по умолчанию 20)
    
    Возвращает список найденных материалов
    """
    try:
        # Валидация параметров
        if not query or len(query.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поисковый запрос должен содержать минимум 2 символа"
            )
        
        if subject_filter and subject_filter.lower() not in ['chemistry', 'biology', 'химия', 'биология']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недопустимый фильтр по предмету"
            )
        
        if section_filter and section_filter <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID раздела должен быть положительным числом"
            )
        
        # Выполнение поиска
        results = await search_materials_db(
            db=db, 
            query=query.strip(), 
            subject_filter=subject_filter, 
            section_filter=section_filter
        )
        
        # Ограничение результатов
        limited_results = results[:limit] if limit else results
        
        return [SearchResult(**result) for result in limited_results]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка поиска: {str(e)}"
        )

# ===========================================
# СТАТИСТИКА МАТЕРИАЛОВ
# ===========================================

@router.get("/statistics", 
            response_model=MaterialsStatistics,
            summary="Статистика материалов",
            description="Получение общей статистики по материалам")
async def get_statistics(
    db: AsyncSession = Depends(get_db)
) -> MaterialsStatistics:
    """
    Получение статистики материалов
    
    Возвращает общую информацию о количестве предметов, разделов, тем и файлов
    """
    try:
        stats = await get_materials_statistics_db(db)
        return MaterialsStatistics(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики: {str(e)}"
        )

# ===========================================
# ПРОВЕРКА ЗДОРОВЬЯ API
# ===========================================

@router.get("/health",
            summary="Проверка здоровья API",
            description="Простая проверка работоспособности API материалов")
async def health_check():
    """
    Проверка здоровья API материалов
    """
    return {
        "status": "healthy",
        "service": "materials-api",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

