from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth.admin import *
from app.services.content.subject_service import *
from app.services.content.section_service import *
from app.services.content.topic_service import *
from app.services.content.question_service import *

router = APIRouter()

# SUBJECTS
@router.get("/subjects", response_model=AdminSubjectsListResponse)
async def get_subjects(
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка предметов"""
    try:
        if search:
            subjects = await search_subjects_by_name_db(db, search)
        else:
            subjects = await get_all_subjects_db(db)
        
        # Обогащаем данными
        enriched_subjects = []
        for subject in subjects:
            subject_data = AdminSubjectResponse.from_orm(subject)
            subject_data.sections_count = await count_sections_by_subject_db(db, subject.subject_id)
            enriched_subjects.append(subject_data)
        
        total = len(enriched_subjects)
        paginated = enriched_subjects[offset:offset + limit]
        
        return AdminSubjectsListResponse(
            items=paginated,
            total=total,
            limit=limit,
            offset=offset,
            has_next=offset + limit < total,
            has_prev=offset > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subjects", response_model=AdminSubjectResponse)
async def create_subject(
    subject_data: CreateSubjectRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание предмета"""
    try:
        new_subject = await add_subject_db(db, subject_data.name, subject_data.description)
        return AdminSubjectResponse.from_orm(new_subject)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/subjects/{subject_id}", response_model=AdminSubjectResponse)
async def update_subject(
    subject_id: int,
    subject_data: UpdateSubjectRequest,
    db: AsyncSession = Depends(get_db)
):
    """Обновление предмета"""
    try:
        updated_subject = await edit_subject_db(
            db, subject_id, subject_data.name, subject_data.description
        )
        return AdminSubjectResponse.from_orm(updated_subject)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/subjects/{subject_id}")
async def delete_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление предмета"""
    try:
        return await delete_subject_db(db, subject_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SECTIONS
@router.get("/sections", response_model=AdminSectionsListResponse)
async def get_sections(
    subject_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка разделов"""
    try:
        if subject_id:
            sections = await get_sections_by_subject_db(db, subject_id)
        elif search:
            sections = await search_sections_by_name_db(db, search)
        else:
            sections = await get_all_sections_db(db)
        
        # Обогащаем данными
        enriched_sections = []
        for section in sections:
            section_data = AdminSectionResponse.from_orm(section)
            section_data.subject_name = section.subject.name
            enriched_sections.append(section_data)
        
        total = len(enriched_sections)
        paginated = enriched_sections[offset:offset + limit]
        
        return AdminSectionsListResponse(
            items=paginated,
            total=total,
            limit=limit,
            offset=offset,
            has_next=offset + limit < total,
            has_prev=offset > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sections", response_model=AdminSectionResponse)
async def create_section(
    section_data: CreateSectionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание раздела"""
    try:
        new_section = await add_section_db(
            db, section_data.subject_id, section_data.name, section_data.order_number
        )
        return AdminSectionResponse.from_orm(new_section)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sections/{section_id}", response_model=AdminSectionResponse)
async def update_section(
    section_id: int,
    section_data: UpdateSectionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Обновление раздела"""
    try:
        updated_section = await edit_section_db(
            db, section_id, section_data.subject_id, 
            section_data.name, section_data.order_number
        )
        return AdminSectionResponse.from_orm(updated_section)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sections/{section_id}")
async def delete_section(
    section_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление раздела"""
    try:
        return await delete_section_db(db, section_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# TOPICS
@router.get("/topics", response_model=AdminTopicsListResponse)
async def get_topics(
    block_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка тем"""
    try:
        if block_id:
            topics = await get_topics_by_block_db(db, block_id)
        elif search:
            topics = await search_topics_by_name_db(db, search)
        else:
            topics = await get_all_topics_db(db)
        
        # Обогащаем данными
        enriched_topics = []
        for topic in topics:
            topic_data = AdminTopicResponse.from_orm(topic)
            topic_data.block_name = topic.block.name
            topic_data.section_name = topic.block.section.name
            topic_data.subject_name = topic.block.section.subject.name
            topic_data.questions_count = await get_questions_count_by_topic_db(db, topic.topic_id)
            enriched_topics.append(topic_data)
        
        total = len(enriched_topics)
        paginated = enriched_topics[offset:offset + limit]
        
        return AdminTopicsListResponse(
            items=paginated,
            total=total,
            limit=limit,
            offset=offset,
            has_next=offset + limit < total,
            has_prev=offset > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/topics", response_model=AdminTopicResponse)
async def create_topic(
    topic_data: CreateTopicRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание темы"""
    try:
        new_topic = await add_topic_db(
            db=db,
            block_id=topic_data.block_id,
            name=topic_data.name,
            homework=topic_data.homework,
            number=topic_data.number,
            additional_material=topic_data.additional_material
        )
        return AdminTopicResponse.from_orm(new_topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/topics/{topic_id}", response_model=AdminTopicResponse)
async def update_topic(
    topic_id: int,
    topic_data: UpdateTopicRequest,
    db: AsyncSession = Depends(get_db)
):
    """Обновление темы"""
    try:
        updated_topic = await edit_topic_db(
            db=db,
            topic_id=topic_id,
            block_id=topic_data.block_id,
            name=topic_data.name,
            homework=topic_data.homework,
            number=topic_data.number,
            additional_material=topic_data.additional_material
        )
        return AdminTopicResponse.from_orm(updated_topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/topics/{topic_id}")
async def delete_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление темы"""
    try:
        return await delete_topic_db(db, topic_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# QUESTIONS
@router.get("/questions", response_model=AdminQuestionsListResponse)
async def get_questions(
    topic_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка вопросов"""
    try:
        if topic_id:
            questions = await get_questions_by_topic_db(db, topic_id)
        elif search:
            questions = await search_questions_by_text_db(db, search)
        else:
            questions = await get_all_questions_db(db)
        
        # Обогащаем данными
        enriched_questions = []
        for question in questions:
            question_data = AdminQuestionResponse.from_orm(question)
            question_data.topic_name = question.topic.name
            question_data.subject_name = question.topic.block.section.subject.name
            enriched_questions.append(question_data)
        
        total = len(enriched_questions)
        paginated = enriched_questions[offset:offset + limit]
        
        return AdminQuestionsListResponse(
            items=paginated,
            total=total,
            limit=limit,
            offset=offset,
            has_next=offset + limit < total,
            has_prev=offset > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/questions", response_model=AdminQuestionResponse)
async def create_question(
    question_data: CreateQuestionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание вопроса"""
    try:
        new_question = await add_question_db(
            db=db,
            topic_id=question_data.topic_id,
            text=question_data.text,
            correct_answers=question_data.correct_answers,
            answer_1=question_data.answer_1,
            answer_2=question_data.answer_2,
            answer_3=question_data.answer_3,
            answer_4=question_data.answer_4,
            explanation=question_data.explanation,
            category=question_data.category
        )
        return AdminQuestionResponse.from_orm(new_question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/questions/{question_id}", response_model=AdminQuestionResponse)
async def update_question(
    question_id: int,
    question_data: UpdateQuestionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Обновление вопроса"""
    try:
        updated_question = await edit_question_db(
            db=db,
            question_id=question_id,
            topic_id=question_data.topic_id,
            text=question_data.text,
            correct_answers=question_data.correct_answers,
            answer_1=question_data.answer_1,
            answer_2=question_data.answer_2,
            answer_3=question_data.answer_3,
            answer_4=question_data.answer_4,
            explanation=question_data.explanation,
            category=question_data.category
        )
        return AdminQuestionResponse.from_orm(updated_question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление вопроса"""
    try:
        return await delete_question_db(db, question_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))