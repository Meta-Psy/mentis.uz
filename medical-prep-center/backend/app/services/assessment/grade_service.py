from datetime import datetime, timedelta
from typing import List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models.assessment import (
    DtmExam,
    SectionExam,
    BlockExam,
    ModulExam,
    TopicTest,
    CurrentRating,
)
from app.database.models.academic import Section, Block, Subject, Topic, Moduls
from app.database.models.user import Student
from fastapi import HTTPException, status

# ===========================================
# DTM EXAM OPERATIONS
# ===========================================


async def add_dtm_exam_db(
    db: AsyncSession,
    student_id: int,
    subject_id: int,
    common_subject_correct_answers: float,
    second_subject_correct_answers: float,
    first_subject_correct_answers: float,
    total_correct_answers: float,
    exam_date: Optional[datetime] = None,
    category_correct: Optional[List[int]] = None,
    category_mistake: Optional[List[int]] = None,
    attempt_number: Optional[int] = None,
) -> DtmExam:
    """Добавление DTM экзамена"""

    new_exam = DtmExam(
        student_id=student_id,
        subject_id=subject_id,
        common_subject_correct_answers=common_subject_correct_answers,
        second_subject_correct_answers=second_subject_correct_answers,
        first_subject_correct_answers=first_subject_correct_answers,
        total_correct_answers=total_correct_answers,
        exam_date=exam_date or datetime.now(),
        category_correct=category_correct or [],
        category_mistake=category_mistake or [],
        attempt_number=attempt_number,
    )
    db.add(new_exam)
    await db.commit()
    await db.refresh(new_exam)
    return new_exam


async def delete_dtm_exam_db(
    db: AsyncSession, exam_id: int, student_id: int, subject_id: int
) -> dict:
    """Удаление DTM экзамена"""

    result = await db.execute(
        select(DtmExam).filter(
            DtmExam.exam_id == exam_id,
            DtmExam.student_id == student_id,
            DtmExam.subject_id == subject_id,
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен id={exam_id} для студента {student_id} по предмету {subject_id} не найден",
        )
    await db.delete(exam)
    await db.commit()
    return {"status": "Удалён"}


async def edit_dtm_exam_db(
    db: AsyncSession,
    exam_id: int,
    student_id: int,
    subject_id: int,
    common_subject_correct_answers: Optional[float] = None,
    second_subject_correct_answers: Optional[float] = None,
    first_subject_correct_answers: Optional[float] = None,
    total_correct_answers: Optional[float] = None,
    exam_date: Optional[datetime] = None,
    category_correct: Optional[List[int]] = None,
    category_mistake: Optional[List[int]] = None,
    attempt_number: Optional[int] = None,
) -> DtmExam:
    """Редактирование DTM экзамена"""

    result = await db.execute(
        select(DtmExam).filter(
            DtmExam.exam_id == exam_id,
            DtmExam.student_id == student_id,
            DtmExam.subject_id == subject_id,
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен id={exam_id} для студента {student_id} по предмету {subject_id} не найден",
        )

    if common_subject_correct_answers is not None:
        exam.common_subject_correct_answers = common_subject_correct_answers
    if second_subject_correct_answers is not None:
        exam.second_subject_correct_answers = second_subject_correct_answers
    if first_subject_correct_answers is not None:
        exam.first_subject_correct_answers = first_subject_correct_answers
    if total_correct_answers is not None:
        exam.total_correct_answers = total_correct_answers
    if exam_date is not None:
        exam.exam_date = exam_date
    if category_correct is not None:
        exam.category_correct = category_correct
    if category_mistake is not None:
        exam.category_mistake = category_mistake
    if attempt_number is not None:
        exam.attempt_number = attempt_number

    await db.commit()
    await db.refresh(exam)
    return exam


async def get_dtm_exam_scores_by_student_and_date_db(
    db: AsyncSession, student_id: int, exam_date: datetime
) -> Dict[str, float]:
    """Получение всех оценок DTM экзамена по студенту и дате"""

    result = await db.execute(
        select(DtmExam).filter(
            DtmExam.student_id == student_id,
            func.date(DtmExam.exam_date) == exam_date.date(),
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DTM экзамен не найден для студента {student_id} на дату {exam_date}",
        )
    return {
        "common_subject_correct_answers": exam.common_subject_correct_answers,
        "second_subject_correct_answers": exam.second_subject_correct_answers,
        "first_subject_correct_answers": exam.first_subject_correct_answers,
        "total_correct_answers": exam.total_correct_answers,
    }


async def get_all_dtm_scores_by_student_db(
    db: AsyncSession, student_id: int
) -> List[DtmExam]:
    """Получение всех DTM экзаменов студента"""

    result = await db.execute(
        select(DtmExam)
        .filter(DtmExam.student_id == student_id)
        .order_by(DtmExam.exam_date)
    )
    exams = result.scalars().all()
    return exams


async def get_average_dtm_score_for_student_db(
    db: AsyncSession, student_id: int
) -> Dict[str, float]:
    """Получение средних оценок DTM экзаменов студента"""

    result = await db.execute(
        select(
            func.avg(DtmExam.common_subject_correct_answers).label("avg_common"),
            func.avg(DtmExam.second_subject_correct_answers).label("avg_second"),
            func.avg(DtmExam.first_subject_correct_answers).label("avg_first"),
            func.avg(DtmExam.total_correct_answers).label("avg_total"),
        ).filter(DtmExam.student_id == student_id)
    )
    row = result.first()

    if not row or row.avg_total is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DTM экзамены для студента {student_id} не найдены",
        )

    return {
        "avg_common_subject": float(row.avg_common),
        "avg_second_subject": float(row.avg_second),
        "avg_first_subject": float(row.avg_first),
        "avg_total": float(row.avg_total),
    }


# ===========================================
# SECTION EXAM OPERATIONS
# ===========================================


async def add_section_exam_db(
    db: AsyncSession,
    student_id: int,
    section_id: int,
    correct_answers: float,
    exam_date: datetime,
    category_correct: Optional[List[int]] = None,
    category_mistake: Optional[List[int]] = None,
    time_spent: Optional[str] = None,
    passed: Optional[bool] = None,
    max_correct_answers: Optional[float] = None,
    attempt_count: Optional[str] = None,
) -> SectionExam:
    """Создание новой записи SectionExam"""

    # Проверяем существование студента
    student_result = await db.execute(
        select(Student).filter(Student.student_id == student_id)
    )
    if not student_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент id={student_id} не найден",
        )

    # Проверяем существование раздела
    section_result = await db.execute(
        select(Section).filter(Section.section_id == section_id)
    )
    if not section_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Раздел id={section_id} не найден",
        )

    exam = SectionExam(
        student_id=student_id,
        section_id=section_id,
        correct_answers=correct_answers,
        exam_date=exam_date,
        category_correct=category_correct or [],
        category_mistake=category_mistake or [],
        time_spent=time_spent,
        passed=passed,
        max_correct_answers=max_correct_answers,
        attempt_count=attempt_count,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam


async def delete_section_exam_db(db: AsyncSession, section_exam_id: int) -> None:
    """Удаление SectionExam"""

    result = await db.execute(
        select(SectionExam).filter(SectionExam.section_exam_id == section_exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен по разделу id={section_exam_id} не найден",
        )
    await db.delete(exam)
    await db.commit()


async def update_section_exam_db(
    db: AsyncSession,
    section_exam_id: int,
    correct_answers: Optional[float] = None,
    section_id: Optional[int] = None,
    student_id: Optional[int] = None,
    exam_date: Optional[datetime] = None,
    time_spent: Optional[str] = None,
    passed: Optional[bool] = None,
    max_correct_answers: Optional[float] = None,
    attempt_count: Optional[str] = None,
) -> SectionExam:
    """Обновление полей SectionExam"""

    result = await db.execute(
        select(SectionExam).filter(SectionExam.section_exam_id == section_exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен по разделу id={section_exam_id} не найден",
        )

    if student_id is not None:
        student_result = await db.execute(
            select(Student).filter(Student.student_id == student_id)
        )
        if not student_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Студент id={student_id} не найден",
            )
        exam.student_id = student_id

    if section_id is not None:
        section_result = await db.execute(
            select(Section).filter(Section.section_id == section_id)
        )
        if not section_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Раздел id={section_id} не найден",
            )
        exam.section_id = section_id

    if correct_answers is not None:
        exam.correct_answers = correct_answers
    if exam_date is not None:
        exam.exam_date = exam_date
    if time_spent is not None:
        exam.time_spent = time_spent
    if passed is not None:
        exam.passed = passed
    if max_correct_answers is not None:
        exam.max_correct_answers = max_correct_answers
    if attempt_count is not None:
        exam.attempt_count = attempt_count

    await db.commit()
    await db.refresh(exam)
    return exam


async def get_section_exam_score_db(
    db: AsyncSession, student_id: int, exam_date: datetime
) -> float:
    """Получение оценки за экзамен по разделу"""

    result = await db.execute(
        select(SectionExam).filter(
            SectionExam.student_id == student_id, SectionExam.exam_date == exam_date
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен по разделу для студента {student_id} на дату {exam_date} не найден",
        )
    return exam.correct_answers


async def get_avg_score_by_student_subject_db(
    db: AsyncSession, student_id: int, subject_id: int
) -> float:
    """Средний балл студента по предмету (через связь Section → Subject)"""

    result = await db.execute(
        select(func.avg(SectionExam.correct_answers))
        .join(SectionExam.section)
        .filter(SectionExam.student_id == student_id, Section.subject_id == subject_id)
    )
    avg_score = result.scalar()
    if avg_score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамены по разделам для студента {student_id} по предмету {subject_id} не найдены",
        )
    return float(avg_score)


async def get_avg_score_for_subject_db(db: AsyncSession, subject_id: int) -> float:
    """Средний балл по предмету среди всех студентов"""

    result = await db.execute(
        select(func.avg(SectionExam.correct_answers))
        .join(SectionExam.section)
        .filter(Section.subject_id == subject_id)
    )
    avg_score = result.scalar()
    if avg_score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамены по разделам для предмета {subject_id} не найдены",
        )
    return float(avg_score)


# ===========================================
# BLOCK EXAM OPERATIONS
# ===========================================


async def add_block_exam_db(
    db: AsyncSession,
    student_id: int,
    block_id: int,
    subject_id: int,
    correct_answers: float,
    exam_date: datetime,
    category_correct: Optional[List[Any]] = None,
    category_mistake: Optional[List[Any]] = None,
    time_spent: Optional[str] = None,
    passed: Optional[bool] = None,
    max_correct_answers: Optional[float] = None,
    attempt_count: Optional[str] = None,
    time_limit: Optional[str] = None,
) -> BlockExam:
    """Создание новой записи BlockExam"""

    # Проверяем существование студента
    student_result = await db.execute(
        select(Student).filter(Student.student_id == student_id)
    )
    if not student_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент id={student_id} не найден",
        )

    # Проверяем существование блока
    block_result = await db.execute(select(Block).filter(Block.block_id == block_id))
    if not block_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Блок id={block_id} не найден",
        )

    # Проверяем существование предмета
    subject_result = await db.execute(
        select(Subject).filter(Subject.subject_id == subject_id)
    )
    if not subject_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Предмет id={subject_id} не найден",
        )

    exam = BlockExam(
        student_id=student_id,
        block_id=block_id,
        subject_id=subject_id,
        correct_answers=correct_answers,
        exam_date=exam_date,
        category_correct=category_correct or [],
        category_mistake=category_mistake or [],
        time_spent=time_spent,
        passed=passed,
        max_correct_answers=max_correct_answers,
        attempt_count=attempt_count,
        time_limit=time_limit,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam


async def delete_block_exam_db(db: AsyncSession, block_exam_id: int) -> None:
    """Удаление записи BlockExam"""

    result = await db.execute(
        select(BlockExam).filter(BlockExam.block_exam_id == block_exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен по блоку id={block_exam_id} не найден",
        )
    await db.delete(exam)
    await db.commit()


async def update_block_exam_db(
    db: AsyncSession,
    block_exam_id: int,
    student_id: Optional[int] = None,
    block_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    correct_answers: Optional[float] = None,
    exam_date: Optional[datetime] = None,
    time_spent: Optional[str] = None,
    passed: Optional[bool] = None,
    max_correct_answers: Optional[float] = None,
    attempt_count: Optional[str] = None,
    time_limit: Optional[str] = None,
) -> BlockExam:
    """Обновление полей BlockExam"""

    result = await db.execute(
        select(BlockExam).filter(BlockExam.block_exam_id == block_exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен по блоку id={block_exam_id} не найден",
        )

    if student_id is not None:
        student_result = await db.execute(
            select(Student).filter(Student.student_id == student_id)
        )
        if not student_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Студент id={student_id} не найден",
            )
        exam.student_id = student_id

    if block_id is not None:
        block_result = await db.execute(
            select(Block).filter(Block.block_id == block_id)
        )
        if not block_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Блок id={block_id} не найден",
            )
        exam.block_id = block_id

    if subject_id is not None:
        subject_result = await db.execute(
            select(Subject).filter(Subject.subject_id == subject_id)
        )
        if not subject_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Предмет id={subject_id} не найден",
            )
        exam.subject_id = subject_id

    if correct_answers is not None:
        exam.correct_answers = correct_answers
    if exam_date is not None:
        exam.exam_date = exam_date
    if time_spent is not None:
        exam.time_spent = time_spent
    if passed is not None:
        exam.passed = passed
    if max_correct_answers is not None:
        exam.max_correct_answers = max_correct_answers
    if attempt_count is not None:
        exam.attempt_count = attempt_count
    if time_limit is not None:
        exam.time_limit = time_limit

    await db.commit()
    await db.refresh(exam)
    return exam


async def get_all_block_scores_by_student_subject_db(
    db: AsyncSession, student_id: int, subject_id: int
) -> List[float]:
    """Получение всех оценок по блокам для студента и предмета"""

    result = await db.execute(
        select(BlockExam.correct_answers)
        .filter(BlockExam.student_id == student_id, BlockExam.subject_id == subject_id)
        .order_by(BlockExam.exam_date)
    )
    rows = result.scalars().all()
    return list(rows)


async def get_block_score_by_student_date_subject_db(
    db: AsyncSession, student_id: int, subject_id: int, exam_date: datetime
) -> float:
    """Получение оценки по блоку для студента на конкретную дату"""

    result = await db.execute(
        select(BlockExam).filter(
            BlockExam.student_id == student_id,
            BlockExam.subject_id == subject_id,
            BlockExam.exam_date == exam_date,
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен по блоку для студента {student_id} по предмету {subject_id} на дату {exam_date} не найден",
        )
    return exam.correct_answers


async def get_avg_block_score_by_student_subject_db(
    db: AsyncSession, student_id: int, subject_id: int
) -> float:
    """Средний балл по блокам для студента и предмета"""

    result = await db.execute(
        select(func.avg(BlockExam.correct_answers)).filter(
            BlockExam.student_id == student_id, BlockExam.subject_id == subject_id
        )
    )
    avg_score = result.scalar()
    if avg_score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамены по блокам для студента {student_id} по предмету {subject_id} не найдены",
        )
    return float(avg_score)


async def get_avg_block_score_for_subject_db(
    db: AsyncSession, subject_id: int
) -> Dict[int, float]:
    """Средний балл по блокам для каждого студента по предмету"""

    result = await db.execute(
        select(
            BlockExam.student_id, func.avg(BlockExam.correct_answers).label("avg_score")
        )
        .filter(BlockExam.subject_id == subject_id)
        .group_by(BlockExam.student_id)
    )
    rows = result.all()
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамены по блокам для предмета {subject_id} не найдены",
        )
    return {student_id: float(avg_score) for student_id, avg_score in rows}


# ===========================================
# MODULE EXAM OPERATIONS
# ===========================================


async def add_modul_exam_db(
    db: AsyncSession,
    modul_id: int,
    student_id: int,
    chem_correct_answers: float,
    bio_correct_answers: float,
    exam_date: datetime,
    category_correct: Optional[List[Any]] = None,
    category_mistake: Optional[List[Any]] = None,
    total_questions_chem: Optional[int] = None,
    total_questions_bio: Optional[int] = None,
    time_spent_chem: Optional[str] = None,
    time_spent_bio: Optional[str] = None,
) -> ModulExam:
    """Добавление нового модульного экзамена"""

    # Проверяем существование модуля
    modul_result = await db.execute(select(Moduls).filter(Moduls.modul_id == modul_id))
    if not modul_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модуль id={modul_id} не найден",
        )

    # Проверяем существование студента
    student_result = await db.execute(
        select(Student).filter(Student.student_id == student_id)
    )
    if not student_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент id={student_id} не найден",
        )

    exam = ModulExam(
        modul_id=modul_id,
        student_id=student_id,
        chem_correct_answers=chem_correct_answers,
        bio_correct_answers=bio_correct_answers,
        exam_date=exam_date,
        category_correct=category_correct or [],
        category_mistake=category_mistake or [],
        total_questions_chem=total_questions_chem,
        total_questions_bio=total_questions_bio,
        time_spent_chem=time_spent_chem,
        time_spent_bio=time_spent_bio,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam


async def delete_modul_exam_db(db: AsyncSession, modul_exam_id: int) -> None:
    """Удаление модульного экзамена"""

    result = await db.execute(
        select(ModulExam).filter(ModulExam.modul_exam_id == modul_exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модульный экзамен id={modul_exam_id} не найден",
        )
    await db.delete(exam)
    await db.commit()


async def update_modul_exam_db(
    db: AsyncSession,
    modul_exam_id: int,
    chem_correct_answers: Optional[float] = None,
    bio_correct_answers: Optional[float] = None,
    exam_date: Optional[datetime] = None,
    total_questions_chem: Optional[int] = None,
    total_questions_bio: Optional[int] = None,
    time_spent_chem: Optional[str] = None,
    time_spent_bio: Optional[str] = None,
) -> ModulExam:
    """Обновление модульного экзамена"""

    result = await db.execute(
        select(ModulExam).filter(ModulExam.modul_exam_id == modul_exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модульный экзамен id={modul_exam_id} не найден",
        )

    if chem_correct_answers is not None:
        exam.chem_correct_answers = chem_correct_answers
    if bio_correct_answers is not None:
        exam.bio_correct_answers = bio_correct_answers
    if exam_date is not None:
        exam.exam_date = exam_date
    if total_questions_chem is not None:
        exam.total_questions_chem = total_questions_chem
    if total_questions_bio is not None:
        exam.total_questions_bio = total_questions_bio
    if time_spent_chem is not None:
        exam.time_spent_chem = time_spent_chem
    if time_spent_bio is not None:
        exam.time_spent_bio = time_spent_bio

    await db.commit()
    await db.refresh(exam)
    return exam


async def get_modul_exam_scores_db(
    db: AsyncSession, student_id: int, modul_id: int, exam_date: datetime
) -> Dict[str, float]:
    """Получение оценок модульного экзамена"""

    result = await db.execute(
        select(ModulExam.chem_correct_answers, ModulExam.bio_correct_answers).filter(
            ModulExam.student_id == student_id,
            ModulExam.modul_id == modul_id,
            ModulExam.exam_date == exam_date,
        )
    )
    exam = result.first()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Оценки модульного экзамена не найдены",
        )
    chem, bio = exam
    return {"chem_correct_answers": chem, "bio_correct_answers": bio}


async def get_avg_bio_score_for_student_db(db: AsyncSession, student_id: int) -> float:
    """Средний балл по биологии для студента"""

    result = await db.execute(
        select(func.avg(ModulExam.bio_correct_answers)).filter(
            ModulExam.student_id == student_id
        )
    )
    avg_bio = result.scalar()
    return avg_bio or 0.0


async def get_avg_chem_score_for_student_db(db: AsyncSession, student_id: int) -> float:
    """Средний балл по химии для студента"""

    result = await db.execute(
        select(func.avg(ModulExam.chem_correct_answers)).filter(
            ModulExam.student_id == student_id
        )
    )
    avg_chem = result.scalar()
    return avg_chem or 0.0


async def get_all_chem_scores_db(
    db: AsyncSession, modul_id: int, exam_date: datetime
) -> Dict[int, float]:
    """Получение всех оценок по химии для модуля на дату"""

    result = await db.execute(
        select(ModulExam.student_id, ModulExam.chem_correct_answers).filter(
            ModulExam.modul_id == modul_id, ModulExam.exam_date == exam_date
        )
    )
    rows = result.all()
    return {sid: score for sid, score in rows}


async def get_all_bio_scores_db(
    db: AsyncSession, modul_id: int, exam_date: datetime
) -> Dict[int, float]:
    """Получение всех оценок по биологии для модуля на дату"""

    result = await db.execute(
        select(ModulExam.student_id, ModulExam.bio_correct_answers).filter(
            ModulExam.modul_id == modul_id, ModulExam.exam_date == exam_date
        )
    )
    rows = result.all()
    return {sid: score for sid, score in rows}


# ===========================================
# TOPIC TEST OPERATIONS
# ===========================================


async def add_topic_test_db(
    db: AsyncSession,
    student_id: int,
    topic_id: int,
    question_count: int,
    correct_answers: float,
    attempt_date: datetime,
    time_spent: Optional[str] = None,
) -> TopicTest:
    """Добавление теста по теме"""

    # Проверяем существование студента
    student_result = await db.execute(
        select(Student).filter(Student.student_id == student_id)
    )
    if not student_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент id={student_id} не найден",
        )

    # Проверяем существование темы
    topic_result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    if not topic_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тема id={topic_id} не найдена",
        )

    tt = TopicTest(
        student_id=student_id,
        topic_id=topic_id,
        question_count=question_count,
        correct_answers=correct_answers,
        attempt_date=attempt_date,
        time_spent=time_spent,
    )
    db.add(tt)
    await db.commit()
    await db.refresh(tt)
    return tt


async def update_topic_test_score_db(
    db: AsyncSession,
    student_id: int,
    topic_id: int,
    topic_test_id: int,
    new_correct_answers: float,
) -> TopicTest:
    """Изменение оценки в TopicTest"""

    result = await db.execute(
        select(TopicTest).filter(
            TopicTest.topic_test_id == topic_test_id,
            TopicTest.student_id == student_id,
            TopicTest.topic_id == topic_id,
        )
    )
    tt = result.scalar_one_or_none()
    if not tt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тест по теме не найден для обновления",
        )
    tt.correct_answers = new_correct_answers
    await db.commit()
    await db.refresh(tt)
    return tt


async def delete_topic_test_db(db: AsyncSession, topic_test_id: int) -> None:
    """Удаление теста по теме"""

    result = await db.execute(
        select(TopicTest).filter(TopicTest.topic_test_id == topic_test_id)
    )
    tt = result.scalar_one_or_none()
    if not tt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тест по теме id={topic_test_id} не найден",
        )
    await db.delete(tt)
    await db.commit()


async def get_topic_test_score_db(
    db: AsyncSession, student_id: int, topic_id: int, topic_test_id: int
) -> float:
    """Получение оценки теста по теме"""

    result = await db.execute(
        select(TopicTest.correct_answers).filter(
            TopicTest.topic_test_id == topic_test_id,
            TopicTest.student_id == student_id,
            TopicTest.topic_id == topic_id,
        )
    )
    score = result.scalar()
    if score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Оценка теста не найдена"
        )
    return score


async def get_all_topic_scores_by_topic_db(
    db: AsyncSession, topic_id: int
) -> Dict[int, float]:
    """Получение всех оценок по теме"""

    result = await db.execute(
        select(TopicTest.student_id, TopicTest.correct_answers).filter(
            TopicTest.topic_id == topic_id
        )
    )
    rows = result.all()
    return {sid: sc for sid, sc in rows}


async def get_avg_topic_score_for_student_db(
    db: AsyncSession, student_id: int, topic_id: int
) -> float:
    """Средний балл студента по теме"""

    result = await db.execute(
        select(func.avg(TopicTest.correct_answers)).filter(
            TopicTest.student_id == student_id, TopicTest.topic_id == topic_id
        )
    )
    avg = result.scalar()
    return avg or 0.0


# ===========================================
# CURRENT RATING OPERATIONS
# ===========================================


async def add_current_rating_db(
    db: AsyncSession,
    student_id: int,
    subject_id: int,
    topic_id: int,
    current_correct_answers: float,
    second_current_correct_answers: float,
) -> CurrentRating:
    """Добавление текущего рейтинга"""

    # Проверяем существование темы
    topic_result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    if not topic_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тема id={topic_id} не найдена",
        )

    rating = CurrentRating(
        student_id=student_id,
        subject_id=subject_id,
        topic_id=topic_id,
        current_correct_answers=current_correct_answers,
        second_current_correct_answers=second_current_correct_answers,
        last_updated=datetime.now(),
    )
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating


async def delete_current_rating_db(db: AsyncSession, rating_id: int) -> None:
    """Удаление текущего рейтинга"""

    result = await db.execute(
        select(CurrentRating).filter(CurrentRating.rating_id == rating_id)
    )
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Текущий рейтинг id={rating_id} не найден",
        )
    await db.delete(rating)
    await db.commit()


async def update_current_rating_db(
    db: AsyncSession,
    rating_id: int,
    current_correct_answers: Optional[float] = None,
    second_current_correct_answers: Optional[float] = None,
) -> CurrentRating:
    """Обновление текущего рейтинга"""

    result = await db.execute(
        select(CurrentRating).filter(CurrentRating.rating_id == rating_id)
    )
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Текущий рейтинг id={rating_id} не найден",
        )

    if current_correct_answers is not None:
        rating.current_correct_answers = current_correct_answers
    if second_current_correct_answers is not None:
        rating.second_current_correct_answers = second_current_correct_answers
    rating.last_updated = datetime.now()

    await db.commit()
    await db.refresh(rating)
    return rating


async def get_current_score_db(
    db: AsyncSession, student_id: int, subject_id: int, topic_id: int
) -> float:
    """Получение текущего балла"""

    result = await db.execute(
        select(CurrentRating).filter(
            CurrentRating.student_id == student_id,
            CurrentRating.subject_id == subject_id,
            CurrentRating.topic_id == topic_id,
        )
    )
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Текущий рейтинг не найден"
        )
    return rating.current_correct_answers


async def get_second_current_score_db(
    db: AsyncSession, student_id: int, subject_id: int, topic_id: int
) -> float:
    """Получение второго текущего балла"""

    result = await db.execute(
        select(CurrentRating).filter(
            CurrentRating.student_id == student_id,
            CurrentRating.subject_id == subject_id,
            CurrentRating.topic_id == topic_id,
        )
    )
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Текущий рейтинг не найден"
        )
    return rating.second_current_correct_answers


async def get_avg_sum_scores_by_block_for_student_db(
    db: AsyncSession, student_id: int, block_id: int
) -> float:
    """Средняя сумма баллов по блоку для студента"""

    result = await db.execute(
        select(
            func.avg(
                func.coalesce(CurrentRating.current_correct_answers, 0)
                + func.coalesce(CurrentRating.second_current_correct_answers, 0)
            )
        )
        .join(Topic, CurrentRating.topic_id == Topic.topic_id)
        .filter(CurrentRating.student_id == student_id, Topic.block_id == block_id)
    )
    avg_sum = result.scalar()
    return float(avg_sum) if avg_sum is not None else 0.0


async def get_avg_current_rating_for_block_db(
    db: AsyncSession, block_id: int
) -> Dict[int, float]:
    """Средний текущий рейтинг по блоку для всех студентов"""

    # Проверяем существование блока
    block_result = await db.execute(select(Block).filter(Block.block_id == block_id))
    block = block_result.scalar_one_or_none()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Блок id={block_id} не найден",
        )

    subject_id = block.section.subject_id
    result = await db.execute(
        select(
            CurrentRating.student_id,
            func.avg(
                CurrentRating.current_correct_answers
                + CurrentRating.second_current_correct_answers
            ).label("avg_score"),
        )
        .join(CurrentRating.topic)
        .filter(Topic.block_id == block_id, CurrentRating.subject_id == subject_id)
        .group_by(CurrentRating.student_id)
    )
    rows = result.all()
    return {student_id: avg_score for student_id, avg_score in rows}


# ===========================================
# CALCULATE FINAL GRADE
# ===========================================


async def calculate_final_grade_db(
    db: AsyncSession, student_id: int, subject_id: int
) -> Dict[str, Any]:
    """Вычисление итоговой оценки студента по предмету"""

    # Получаем средние баллы по разным типам экзаменов
    section_avg_result = await db.execute(
        select(func.avg(SectionExam.correct_answers))
        .join(SectionExam.section)
        .filter(SectionExam.student_id == student_id, Section.subject_id == subject_id)
    )
    section_avg = section_avg_result.scalar() or 0

    block_avg_result = await db.execute(
        select(func.avg(BlockExam.correct_answers)).filter(
            BlockExam.student_id == student_id, BlockExam.subject_id == subject_id
        )
    )
    block_avg = block_avg_result.scalar() or 0

    current_avg_result = await db.execute(
        select(
            func.avg(
                CurrentRating.current_correct_answers
                + CurrentRating.second_current_correct_answers
            )
        ).filter(
            CurrentRating.student_id == student_id,
            CurrentRating.subject_id == subject_id,
        )
    )
    current_avg = current_avg_result.scalar() or 0

    topic_avg_result = await db.execute(
        select(func.avg(TopicTest.correct_answers))
        .join(TopicTest.topic)
        .join(Topic.block)
        .join(Block.section)
        .filter(TopicTest.student_id == student_id, Section.subject_id == subject_id)
    )
    topic_avg = topic_avg_result.scalar() or 0

    # Получаем количество записей для весового коэффициента
    section_count_result = await db.execute(
        select(func.count(SectionExam.section_exam_id))
        .join(SectionExam.section)
        .filter(SectionExam.student_id == student_id, Section.subject_id == subject_id)
    )
    section_count = section_count_result.scalar()

    block_count_result = await db.execute(
        select(func.count(BlockExam.block_exam_id)).filter(
            BlockExam.student_id == student_id, BlockExam.subject_id == subject_id
        )
    )
    block_count = block_count_result.scalar()

    current_count_result = await db.execute(
        select(func.count(CurrentRating.rating_id)).filter(
            CurrentRating.student_id == student_id,
            CurrentRating.subject_id == subject_id,
        )
    )
    current_count = current_count_result.scalar()

    topic_count_result = await db.execute(
        select(func.count(TopicTest.topic_test_id))
        .join(TopicTest.topic)
        .join(Topic.block)
        .join(Block.section)
        .filter(TopicTest.student_id == student_id, Section.subject_id == subject_id)
    )
    topic_count = topic_count_result.scalar()

    # Вычисляем итоговую оценку с весовыми коэффициентами
    weights = {"section": 0.3, "block": 0.3, "current": 0.25, "topic": 0.15}

    total_weight = 0
    weighted_sum = 0

    if section_count > 0:
        weighted_sum += section_avg * weights["section"]
        total_weight += weights["section"]

    if block_count > 0:
        weighted_sum += block_avg * weights["block"]
        total_weight += weights["block"]

    if current_count > 0:
        weighted_sum += current_avg * weights["current"]
        total_weight += weights["current"]

    if topic_count > 0:
        weighted_sum += topic_avg * weights["topic"]
        total_weight += weights["topic"]

    final_grade = (weighted_sum / total_weight) if total_weight > 0 else 0

    return {
        "student_id": student_id,
        "subject_id": subject_id,
        "section_average": round(float(section_avg), 2),
        "block_average": round(float(block_avg), 2),
        "current_average": round(float(current_avg), 2),
        "topic_average": round(float(topic_avg), 2),
        "final_grade": round(float(final_grade), 2),
        "counts": {
            "section_exams": section_count,
            "block_exams": block_count,
            "current_ratings": current_count,
            "topic_tests": topic_count,
        },
    }
