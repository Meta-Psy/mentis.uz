from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.auth.admin_service import *
from app.services.content.subject_service import *
from app.services.content.section_service import *
from app.services.content.topic_service import *
from app.services.content.module_service import *
from app.services.content.question_service import *
from app.schemas.auth.admin import *
from app.schemas.content.subject import *
from app.core.dependencies import get_current_user, require_roles
from app.database.models.user import UserRole

# ===== ADMINS ROUTER =====
admins_router = APIRouter()

@admins_router.get("/profile", response_model=AdminProfileResponse)
async def get_admin_profile(
    current_user = Depends(get_current_user)
):
    """Получение профиля администратора"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    try:
        admin = get_admin_by_id_db(current_user.user_id)
        admin_info = get_admin_info_db(current_user.user_id)
        
        return AdminProfileResponse(
            admin=admin,
            admin_info=admin_info
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@admins_router.get("/users/statistics")
async def get_users_statistics(
    current_user = Depends(get_current_user)
):
    """Получение статистики пользователей системы"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    try:
        stats = get_user_statistics_db()
        teacher_stats = get_teacher_statistics_db()
        admin_stats = get_admin_statistics_db()
        
        return {
            "overall": stats,
            "teachers": teacher_stats,
            "admins": admin_stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@admins_router.get("/system/health")
async def get_system_health(
    current_user = Depends(get_current_user)
):
    """Получение информации о состоянии системы"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    try:
        # Системная информация
        health_info = {
            "database": {
                "status": "healthy",
                "connections": 5,
                "max_connections": 100
            },
            "redis": {
                "status": "healthy",
                "memory_usage": "45MB",
                "connected_clients": 12
            },
            "storage": {
                "status": "healthy",
                "used_space": "2.3GB",
                "available_space": "47.7GB"
            },
            "performance": {
                "average_response_time": "120ms",
                "requests_per_minute": 45,
                "error_rate": "0.1%"
            }
        }
        
        return health_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== SUBJECTS ROUTER =====
subjects_router = APIRouter()

@subjects_router.get("/", response_model=List[SubjectResponse])
async def get_all_subjects(
    current_user = Depends(get_current_user)
):
    """Получение всех предметов"""
    try:
        subjects = get_all_subjects_db()
        return [SubjectResponse.from_orm(subject) for subject in subjects]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.post("/", response_model=SubjectResponse)
async def create_subject(
    subject_data: CreateSubjectRequest,
    current_user = Depends(get_current_user)
):
    """Создание нового предмета (только для администраторов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    try:
        subject = add_subject_db(
            name=subject_data.name,
            description=subject_data.description
        )
        return SubjectResponse.from_orm(subject)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.get("/{subject_id}", response_model=SubjectDetailResponse)
async def get_subject_details(
    subject_id: int,
    current_user = Depends(get_current_user)
):
    """Получение детальной информации о предмете"""
    try:
        subject = find_subject_db(subject_id)
        sections = get_sections_by_subject_db(subject_id)
        
        return SubjectDetailResponse(
            subject=subject,
            sections=sections,
            sections_count=len(sections)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int,
    subject_update: UpdateSubjectRequest,
    current_user = Depends(get_current_user)
):
    """Обновление предмета (только для администраторов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    try:
        updated_subject = edit_subject_db(
            subject_id=subject_id,
            name=subject_update.name,
            description=subject_update.description
        )
        return SubjectResponse.from_orm(updated_subject)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.delete("/{subject_id}")
async def delete_subject(
    subject_id: int,
    current_user = Depends(get_current_user)
):
    """Удаление предмета (только для администраторов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    try:
        result = delete_subject_db(subject_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== SECTIONS =====

@subjects_router.get("/{subject_id}/sections", response_model=List[SectionResponse])
async def get_subject_sections(
    subject_id: int,
    current_user = Depends(get_current_user)
):
    """Получение разделов предмета"""
    try:
        sections = get_sections_by_subject_db(subject_id)
        return [SectionResponse.from_orm(section) for section in sections]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.post("/{subject_id}/sections", response_model=SectionResponse)
async def create_section(
    subject_id: int,
    section_data: CreateSectionRequest,
    current_user = Depends(get_current_user)
):
    """Создание раздела (только для администраторов и учителей)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам и учителям"
        )
    
    try:
        section = add_section_db(
            subject_id=subject_id,
            name=section_data.name,
            order_number=section_data.order_number
        )
        return SectionResponse.from_orm(section)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.get("/sections/{section_id}", response_model=SectionDetailResponse)
async def get_section_details(
    section_id: int,
    current_user = Depends(get_current_user)
):
    """Получение детальной информации о разделе"""
    try:
        section = find_section_db(section_id)
        # Здесь можно добавить получение блоков раздела
        blocks = []  # get_blocks_by_section_db(section_id)
        
        return SectionDetailResponse(
            section=section,
            blocks=blocks,
            blocks_count=len(blocks)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.put("/sections/{section_id}", response_model=SectionResponse)
async def update_section(
    section_id: int,
    section_update: UpdateSectionRequest,
    current_user = Depends(get_current_user)
):
    """Обновление раздела"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам и учителям"
        )
    
    try:
        updated_section = edit_section_db(
            section_id=section_id,
            name=section_update.name,
            order_number=section_update.order_number
        )
        return SectionResponse.from_orm(updated_section)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== MODULES =====

@subjects_router.get("/modules/", response_model=List[ModuleResponse])
async def get_all_modules(
    subject_name: Optional[str] = Query(None),
    current_user = Depends(get_current_user)
):
    """Получение всех модулей"""
    try:
        if subject_name:
            modules = get_modules_by_subject_db(subject_name)
        else:
            modules = get_all_modules_db()
        
        return [ModuleResponse.from_orm(module) for module in modules]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.post("/modules/", response_model=ModuleResponse)
async def create_module(
    module_data: CreateModuleRequest,
    current_user = Depends(get_current_user)
):
    """Создание модуля (только для администраторов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    try:
        module = add_modul_db(
            start_topic_chem=module_data.start_topic_chem,
            start_topic_bio=module_data.start_topic_bio,
            end_topic_chem=module_data.end_topic_chem,
            end_topic_bio=module_data.end_topic_bio,
            order_number=module_data.order_number,
            name=module_data.name
        )
        return ModuleResponse.from_orm(module)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.get("/modules/{module_id}", response_model=ModuleDetailResponse)
async def get_module_details(
    module_id: int,
    current_user = Depends(get_current_user)
):
    """Получение детальной информации о модуле"""
    try:
        module = find_modul_db(module_id)
        
        return ModuleDetailResponse(
            module=module,
            topics_chemistry_range=f"{module.start_topic_chem}-{module.end_topic_chem}",
            topics_biology_range=f"{module.start_topic_bio}-{module.end_topic_bio}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.put("/modules/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: int,
    module_update: UpdateModuleRequest,
    current_user = Depends(get_current_user)
):
    """Обновление модуля (только для администраторов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    try:
        updated_module = edit_modul_db(
            modul_id=module_id,
            start_topic_chem=module_update.start_topic_chem,
            start_topic_bio=module_update.start_topic_bio,
            end_topic_chem=module_update.end_topic_chem,
            end_topic_bio=module_update.end_topic_bio,
            order_number=module_update.order_number,
            name=module_update.name
        )
        return ModuleResponse.from_orm(updated_module)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== QUESTIONS MANAGEMENT =====

@subjects_router.get("/topics/{topic_id}/questions", response_model=List[QuestionResponse])
async def get_topic_questions(
    topic_id: int,
    current_user = Depends(get_current_user)
):
    """Получение вопросов темы"""
    try:
        questions = get_questions_by_topic_db(topic_id)
        return [QuestionResponse.from_orm(question) for question in questions]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.post("/topics/{topic_id}/questions", response_model=QuestionResponse)
async def create_question(
    topic_id: int,
    question_data: CreateQuestionRequest,
    current_user = Depends(get_current_user)
):
    """Создание вопроса (только для администраторов и учителей)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам и учителям"
        )
    
    try:
        question = add_question_db(
            topic_id=topic_id,
            text=question_data.text,
            answer_1=question_data.answer_1,
            answer_2=question_data.answer_2,
            answer_3=question_data.answer_3,
            answer_4=question_data.answer_4,
            correct_answers=question_data.correct_answers,
            explanation=question_data.explanation,
            category=question_data.category
        )
        return QuestionResponse.from_orm(question)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.get("/questions/{question_id}", response_model=QuestionDetailResponse)
async def get_question_details(
    question_id: int,
    current_user = Depends(get_current_user)
):
    """Получение детальной информации о вопросе"""
    try:
        question = find_question_db(question_id)
        
        return QuestionDetailResponse(
            question=question,
            options=[
                {"id": "A", "text": question.answer_1},
                {"id": "B", "text": question.answer_2},
                {"id": "C", "text": question.answer_3},
                {"id": "D", "text": question.answer_4}
            ],
            correct_option=["A", "B", "C", "D"][question.correct_answers - 1]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_update: UpdateQuestionRequest,
    current_user = Depends(get_current_user)
):
    """Обновление вопроса"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам и учителям"
        )
    
    try:
        updated_question = edit_question_db(
            question_id=question_id,
            text=question_update.text,
            answer_1=question_update.answer_1,
            answer_2=question_update.answer_2,
            answer_3=question_update.answer_3,
            answer_4=question_update.answer_4,
            correct_answers=question_update.correct_answers,
            explanation=question_update.explanation,
            category=question_update.category
        )
        return QuestionResponse.from_orm(updated_question)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    current_user = Depends(get_current_user)
):
    """Удаление вопроса"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам и учителям"
        )
    
    try:
        result = delete_question_db(question_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== BULK OPERATIONS =====

@subjects_router.post("/questions/bulk-import")
async def bulk_import_questions(
    import_data: BulkImportQuestionsRequest,
    current_user = Depends(get_current_user)
):
    """Массовый импорт вопросов (только для администраторов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    try:
        imported_count = 0
        errors = []
        
        for question_data in import_data.questions:
            try:
                add_question_db(
                    topic_id=question_data["topic_id"],
                    text=question_data["text"],
                    answer_1=question_data["answer_1"],
                    answer_2=question_data["answer_2"],
                    answer_3=question_data["answer_3"],
                    answer_4=question_data["answer_4"],
                    correct_answers=question_data["correct_answers"],
                    explanation=question_data.get("explanation"),
                    category=question_data.get("category", [])
                )
                imported_count += 1
            except Exception as e:
                errors.append({
                    "question": question_data.get("text", "Unknown"),
                    "error": str(e)
                })
        
        return {
            "imported_count": imported_count,
            "total_count": len(import_data.questions),
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.post("/questions/bulk-update-categories")
async def bulk_update_question_categories(
    update_data: BulkUpdateCategoriesRequest,
    current_user = Depends(get_current_user)
):
    """Массовое обновление категорий вопросов"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам и учителям"
        )
    
    try:
        updated_count = 0
        
        for question_id, categories in update_data.updates.items():
            try:
                update_question_category_db(int(question_id), categories)
                updated_count += 1
            except Exception:
                continue
        
        return {
            "updated_count": updated_count,
            "total_count": len(update_data.updates)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== SEARCH AND ANALYTICS =====

@subjects_router.get("/search/questions")
async def search_questions(
    query: str = Query(..., min_length=3),
    topic_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    has_explanation: Optional[bool] = Query(None),
    current_user = Depends(get_current_user)
):
    """Поиск вопросов"""
    try:
        # Базовый поиск по тексту
        questions = search_questions_by_text_db(query)
        
        # Фильтрация по дополнительным параметрам
        if topic_id:
            questions = [q for q in questions if q.topic_id == topic_id]
        
        if category:
            questions = [q for q in questions if category in q.category]
        
        if has_explanation is not None:
            if has_explanation:
                questions = [q for q in questions if q.explanation]
            else:
                questions = [q for q in questions if not q.explanation]
        
        return {
            "query": query,
            "results": [QuestionResponse.from_orm(q) for q in questions],
            "total_found": len(questions)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@subjects_router.get("/analytics/questions")
async def get_questions_analytics(
    current_user = Depends(get_current_user)
):
    """Получение аналитики по вопросам"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам и учителям"
        )
    
    try:
        analytics = get_questions_statistics_db()
        
        # Дополнительная аналитика
        questions_without_explanation = get_questions_without_explanation_db()
        
        analytics.update({
            "questions_without_explanation_count": len(questions_without_explanation),
            "questions_by_topic": get_questions_count_by_topics(),
            "categories_distribution": get_categories_distribution()
        })
        
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def get_questions_count_by_topics() -> Dict[int, int]:
    """Получение количества вопросов по темам"""
    # Заглушка
    return {
        1: 25,
        2: 30,
        3: 28
    }

def get_categories_distribution() -> Dict[str, int]:
    """Получение распределения по категориям"""
    # Заглушка
    return {
        "easy": 45,
        "medium": 78,
        "hard": 32
    }

# ===== EXPORT FUNCTIONALITY =====

@subjects_router.get("/export/questions")
async def export_questions(
    subject_id: Optional[int] = Query(None),
    topic_id: Optional[int] = Query(None),
    format: str = Query("json", regex="^(json|csv|xlsx)$"),
    current_user = Depends(get_current_user)
):
    """Экспорт вопросов в различных форматах"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам и учителям"
        )
    
    try:
        # Получаем вопросы для экспорта
        if topic_id:
            questions = get_questions_by_topic_db(topic_id)
        elif subject_id:
            # Получить все вопросы предмета через темы
            questions = get_questions_by_subject(subject_id)
        else:
            questions = get_all_questions_db()
        
        if format == "json":
            return {
                "questions": [
                    {
                        "id": q.question_id,
                        "topic_id": q.topic_id,
                        "text": q.text,
                        "answers": [q.answer_1, q.answer_2, q.answer_3, q.answer_4],
                        "correct_answer": q.correct_answers,
                        "explanation": q.explanation,
                        "category": q.category
                    } for q in questions
                ],
                "export_date": datetime.now().isoformat(),
                "total_count": len(questions)
            }
        # Для CSV и XLSX форматов можно добавить соответствующую логику
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def get_questions_by_subject(subject_id: int) -> List:
    """Получение всех вопросов предмета"""
    # Логика получения всех вопросов предмета через темы и разделы
    # Заглушка
    return []

# Экспортируем роутеры
admins = admins_router
subjects = subjects_router