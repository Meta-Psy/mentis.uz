from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.content.subject_service import *
from app.services.content.section_service import *
from app.services.content.topic_service import *
from app.services.content.module_service import *
from app.schemas.content.materials import *
from app.core.dependencies import get_current_user
from app.database.models.user import UserRole
import os
from pathlib import Path

router = APIRouter()

# Директория для хранения файлов
UPLOAD_DIR = Path("uploads/materials")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ===== ПОЛУЧЕНИЕ МАТЕРИАЛОВ ПО ПРЕДМЕТАМ =====

@router.get("/subjects/{subject_name}")
async def get_subject_materials(
    subject_name: str,
    module_id: Optional[int] = Query(None),
    current_user = Depends(get_current_user)
):
    """Получение материалов по предмету"""
    try:
        # Проверяем, что предмет существует
        if subject_name.lower() not in ["chemistry", "biology", "химия", "биология"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверное название предмета"
            )
        
        # Получаем структуру материалов согласно frontend
        materials_structure = {
            "modules": []
        }
        
        # Получаем модули
        if subject_name.lower() in ["chemistry", "химия"]:
            modules = get_modules_by_subject_db("химия")
        else:
            modules = get_modules_by_subject_db("биология")
        
        for module in modules:
            if module_id and module.modul_id != module_id:
                continue
                
            module_data = {
                "id": module.modul_id,
                "name": module.name or f"Модуль {module.order_number}",
                "books": get_module_books(module.modul_id, "main"),
                "testBooks": get_module_books(module.modul_id, "test"),
                "topics": get_module_topics_with_materials(module.modul_id, subject_name)
            }
            materials_structure["modules"].append(module_data)
        
        return materials_structure
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def get_module_books(module_id: int, book_type: str) -> List[dict]:
    """Получение книг модуля"""
    # Заглушка - в реальности будет получать из базы данных
    if book_type == "main":
        return [
            {
                "id": f"{module_id}_book_1",
                "title": "Основы химии",
                "author": "Петров А.И.",
                "size": "15.2 МБ",
                "format": "PDF",
                "download_url": f"/api/v1/materials/download/{module_id}_book_1"
            }
        ]
    else:  # test books
        return [
            {
                "id": f"{module_id}_test_1",
                "title": "Сборник тестов",
                "author": "Иванова М.К.",
                "size": "8.4 МБ", 
                "format": "PDF",
                "download_url": f"/api/v1/materials/download/{module_id}_test_1"
            }
        ]

def get_module_topics_with_materials(module_id: int, subject: str) -> List[dict]:
    """Получение тем модуля с материалами"""
    # Заглушка согласно frontend структуре
    return [
        {
            "id": 1,
            "title": "Тема 3. Строение атома",
            "homework": [
                "Решить тесты по теме 3",
                "Химия 10 кл. Выучить параграфы 4 - 7",
                "Конспект по строению атома"
            ],
            "videoUrl": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "testId": 103
        }
    ]

# ===== РАБОТА С ТЕМАМИ =====

@router.get("/topics/{topic_id}")
async def get_topic_materials(
    topic_id: int,
    current_user = Depends(get_current_user)
):
    """Получение материалов конкретной темы"""
    try:
        # Здесь будет логика получения материалов темы из topic_service
        topic_data = {
            "id": topic_id,
            "title": f"Тема {topic_id}",
            "homework": [
                "Пример домашнего задания 1",
                "Пример домашнего задания 2"
            ],
            "videoUrl": "https://www.youtube.com/embed/example",
            "testId": topic_id + 100,
            "additional_materials": []
        }
        
        return topic_data
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/topics/{topic_id}/homework")
async def update_topic_homework(
    topic_id: int,
    homework_update: UpdateHomeworkRequest,
    current_user = Depends(get_current_user)
):
    """Обновление домашнего задания темы (только для учителей)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям и администраторам"
        )
    
    try:
        # Логика обновления домашнего задания через topic_service
        # edit_topic_db(topic_id, homework=homework_update.homework)
        
        return {"message": "Домашнее задание обновлено"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== ЗАГРУЗКА И СКАЧИВАНИЕ ФАЙЛОВ =====

@router.post("/upload")
async def upload_material_file(
    file: UploadFile = File(...),
    category: str = Query(..., regex="^(book|test|video|other)$"),
    module_id: Optional[int] = Query(None),
    topic_id: Optional[int] = Query(None),
    current_user = Depends(get_current_user)
):
    """Загрузка файла материала (только для учителей и администраторов)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям и администраторам"
        )
    
    try:
        # Проверяем тип файла
        allowed_extensions = {".pdf", ".doc", ".docx", ".mp4", ".avi", ".mkv"}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неподдерживаемый тип файла"
            )
        
        # Создаем уникальное имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Сохраняем информацию о файле в базе данных
        file_info = {
            "filename": safe_filename,
            "original_name": file.filename,
            "size": len(content),
            "category": category,
            "module_id": module_id,
            "topic_id": topic_id,
            "uploaded_by": current_user.user_id,
            "upload_date": datetime.now()
        }
        
        # Здесь должна быть логика сохранения в базу данных
        # save_material_file_info(file_info)
        
        return {
            "message": "Файл успешно загружен",
            "file_id": safe_filename,
            "download_url": f"/api/v1/materials/download/{safe_filename}"
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )

@router.get("/download/{file_id}")
async def download_material_file(
    file_id: str,
    current_user = Depends(get_current_user)
):
    """Скачивание файла материала"""
    try:
        file_path = UPLOAD_DIR / file_id
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Файл не найден"
            )
        
        # Получаем оригинальное имя файла из базы данных
        # file_info = get_material_file_info(file_id)
        # original_name = file_info.original_name if file_info else file_id
        
        return FileResponse(
            path=file_path,
            filename=file_id,  # В реальности использовать original_name
            media_type='application/octet-stream'
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/files/{file_id}")
async def delete_material_file(
    file_id: str,
    current_user = Depends(get_current_user)
):
    """Удаление файла материала (только для учителей и администраторов)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям и администраторам"
        )
    
    try:
        file_path = UPLOAD_DIR / file_id
        
        if file_path.exists():
            os.remove(file_path)
        
        # Удаляем информацию из базы данных
        # delete_material_file_info(file_id)
        
        return {"message": "Файл успешно удален"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== УПРАВЛЕНИЕ ВИДЕОУРОКАМИ =====

@router.post("/videos")
async def add_video_lesson(
    video_data: AddVideoLessonRequest,
    current_user = Depends(get_current_user)
):
    """Добавление видеоурока к теме (только для учителей и администраторов)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям и администраторам"
        )
    
    try:
        # Логика добавления видеоурока через topic_service
        # update_topic_video(video_data.topic_id, video_data.video_url)
        
        return {"message": "Видеоурок добавлен"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/videos/{topic_id}")
async def update_video_lesson(
    topic_id: int,
    video_update: UpdateVideoLessonRequest,
    current_user = Depends(get_current_user)
):
    """Обновление видеоурока темы (только для учителей и администраторов)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям и администраторам"
        )
    
    try:
        # Логика обновления видеоурока
        # update_topic_video(topic_id, video_update.video_url)
        
        return {"message": "Видеоурок обновлен"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== МАТЕРИАЛЫ ДЛЯ РАЗДЕЛОВ =====

@router.get("/sections/{section_id}/materials")
async def get_section_materials(
    section_id: int,
    current_user = Depends(get_current_user)
):
    """Получение материалов раздела"""
    try:
        # Логика получения материалов раздела через section_service
        section = find_section_db(section_id)
        
        # Получаем связанные материалы
        section_materials = {
            "section_id": section_id,
            "section_name": section.name,
            "materials": get_section_material_links(section_id)
        }
        
        return section_materials
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def get_section_material_links(section_id: int) -> List[dict]:
    """Получение ссылок на материалы раздела"""
    # Заглушка - в реальности получать из SectionMaterial модели
    return [
        {
            "id": 1,
            "title": "Дополнительные материалы",
            "links": [
                "https://example.com/material1",
                "https://example.com/material2"
            ]
        }
    ]

@router.post("/sections/{section_id}/materials")
async def add_section_materials(
    section_id: int,
    materials_data: AddSectionMaterialsRequest,
    current_user = Depends(get_current_user)
):
    """Добавление материалов к разделу (только для учителей и администраторов)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям и администраторам"
        )
    
    try:
        # Логика добавления материалов через section_service
        # add_section_material_links(section_id, materials_data.links)
        
        return {"message": "Материалы добавлены к разделу"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== ПОИСК МАТЕРИАЛОВ =====

@router.get("/search")
async def search_materials(
    query: str = Query(..., min_length=3),
    material_type: Optional[str] = Query(None, regex="^(book|test|video|all)$"),
    subject: Optional[str] = Query(None),
    current_user = Depends(get_current_user)
):
    """Поиск материалов по запросу"""
    try:
        # Логика поиска материалов
        search_results = {
            "query": query,
            "results": [
                {
                    "id": 1,
                    "title": f"Результат поиска для '{query}'",
                    "type": "book",
                    "subject": "chemistry",
                    "description": "Описание найденного материала"
                }
            ],
            "total_found": 1
        }
        
        return search_results
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== СТАТИСТИКА ИСПОЛЬЗОВАНИЯ =====

@router.get("/statistics/usage")
async def get_materials_usage_statistics(
    period: str = Query("month", regex="^(week|month|semester|year)$"),
    current_user = Depends(get_current_user)
):
    """Получение статистики использования материалов"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям и администраторам"
        )
    
    try:
        # Статистика использования материалов
        usage_stats = {
            "period": period,
            "total_downloads": 150,
            "most_popular": [
                {"title": "Общая химия", "downloads": 45},
                {"title": "Биология клетки", "downloads": 38}
            ],
            "by_subject": {
                "chemistry": 85,
                "biology": 65
            }
        }
        
        return usage_stats
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )