from datetime import datetime, timedelta
from typing import List, Optional, Any, Dict
from app.database import get_db
from app.database.models.assessment import (
    DtmExam, SectionExam, BlockExam, ModulExam, TopicTest, CurrentRating
)
from app.database.models.academic import Section, Block, Subject, Topic, Moduls
from app.database.models.user import Student
from fastapi import HTTPException, status
from sqlalchemy import func

# ===========================================
# DTM EXAM OPERATIONS
# ===========================================

def add_dtm_exam_db(student_id: int, subject_id: int, common_subject_correct_answers: float,
                   second_subject_correct_answers: float, first_subject_correct_answers: float,
                   total_correct_answers: float, exam_date: Optional[datetime] = None,
                   category_correct: Optional[List[int]] = None, 
                   category_mistake: Optional[List[int]] = None,
                   attempt_number: Optional[int] = None) -> DtmExam:
    """Добавление DTM экзамена"""
    with next(get_db()) as db:
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
            attempt_number=attempt_number
        )
        db.add(new_exam)
        db.commit()
        db.refresh(new_exam)
        return new_exam

def delete_dtm_exam_db(exam_id: int, student_id: int, subject_id: int) -> dict:
    """Удаление DTM экзамена"""
    with next(get_db()) as db:
        exam = (db.query(DtmExam)
               .filter_by(exam_id=exam_id, student_id=student_id, subject_id=subject_id)
               .first())
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экзамен id={exam_id} для студента {student_id} по предмету {subject_id} не найден"
            )
        db.delete(exam)
        db.commit()
        return {"status": "Удалён"}

def edit_dtm_exam_db(exam_id: int, student_id: int, subject_id: int,
                    common_subject_correct_answers: Optional[float] = None,
                    second_subject_correct_answers: Optional[float] = None,
                    first_subject_correct_answers: Optional[float] = None,
                    total_correct_answers: Optional[float] = None,
                    exam_date: Optional[datetime] = None,
                    category_correct: Optional[List[int]] = None,
                    category_mistake: Optional[List[int]] = None,
                    attempt_number: Optional[int] = None) -> DtmExam:
    """Редактирование DTM экзамена"""
    with next(get_db()) as db:
        exam = (db.query(DtmExam)
               .filter_by(exam_id=exam_id, student_id=student_id, subject_id=subject_id)
               .first())
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экзамен id={exam_id} для студента {student_id} по предмету {subject_id} не найден"
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
            
        db.commit()
        db.refresh(exam)
        return exam

def get_dtm_exam_scores_by_student_and_date_db(student_id: int, exam_date: datetime) -> Dict[str, float]:
    """Получение всех оценок DTM экзамена по студенту и дате"""
    with next(get_db()) as db:
        exam = (db.query(DtmExam)
               .filter(DtmExam.student_id == student_id, DtmExam.exam_date == exam_date)
               .first())
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"DTM экзамен не найден для студента {student_id} на дату {exam_date}"
            )
        return {
            "common_subject_correct_answers": exam.common_subject_correct_answers,
            "second_subject_correct_answers": exam.second_subject_correct_answers,
            "first_subject_correct_answers": exam.first_subject_correct_answers,
            "total_correct_answers": exam.total_correct_answers
        }

def get_all_dtm_scores_by_student_db(student_id: int) -> List[DtmExam]:
    """Получение всех DTM экзаменов студента"""
    with next(get_db()) as db:
        exams = (db.query(DtmExam)
                .filter(DtmExam.student_id == student_id)
                .order_by(DtmExam.exam_date)
                .all())
        return exams

def get_average_dtm_score_for_student_db(student_id: int) -> Dict[str, float]:
    """Получение средних оценок DTM экзаменов студента"""
    with next(get_db()) as db:
        result = (db.query(
            func.avg(DtmExam.common_subject_correct_answers).label('avg_common'),
            func.avg(DtmExam.second_subject_correct_answers).label('avg_second'),
            func.avg(DtmExam.first_subject_correct_answers).label('avg_first'),
            func.avg(DtmExam.total_correct_answers).label('avg_total')
        ).filter(DtmExam.student_id == student_id).first())
        
        if not result or result.avg_total is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"DTM экзамены для студента {student_id} не найдены"
            )
            
        return {
            "avg_common_subject": float(result.avg_common),
            "avg_second_subject": float(result.avg_second),
            "avg_first_subject": float(result.avg_first),
            "avg_total": float(result.avg_total)
        }

# ===========================================
# SECTION EXAM OPERATIONS
# ===========================================

def add_section_exam_db(student_id: int, section_id: int, correct_answers: float,
                       exam_date: datetime, category_correct: Optional[List[int]] = None,
                       category_mistake: Optional[List[int]] = None,
                       time_spent: Optional[str] = None, passed: Optional[bool] = None,
                       max_correct_answers: Optional[float] = None,
                       attempt_count: Optional[str] = None) -> SectionExam:
    """Создание новой записи SectionExam"""
    with next(get_db()) as db:
        if not db.query(Student).get(student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Студент id={student_id} не найден"
            )
        if not db.query(Section).get(section_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Раздел id={section_id} не найден"
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
            attempt_count=attempt_count
        )
        db.add(exam)
        db.commit()
        db.refresh(exam)
        return exam

def delete_section_exam_db(section_exam_id: int) -> None:
    """Удаление SectionExam"""
    with next(get_db()) as db:
        exam = db.query(SectionExam).get(section_exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экзамен по разделу id={section_exam_id} не найден"
            )
        db.delete(exam)
        db.commit()

def update_section_exam_db(section_exam_id: int, correct_answers: Optional[float] = None,
                          section_id: Optional[int] = None, student_id: Optional[int] = None,
                          exam_date: Optional[datetime] = None, time_spent: Optional[str] = None,
                          passed: Optional[bool] = None, max_correct_answers: Optional[float] = None,
                          attempt_count: Optional[str] = None) -> SectionExam:
    """Обновление полей SectionExam"""
    with next(get_db()) as db:
        exam = db.query(SectionExam).get(section_exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экзамен по разделу id={section_exam_id} не найден"
            )
            
        if student_id is not None:
            if not db.query(Student).get(student_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Студент id={student_id} не найден"
                )
            exam.student_id = student_id
            
        if section_id is not None:
            if not db.query(Section).get(section_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Раздел id={section_id} не найден"
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

        db.commit()
        db.refresh(exam)
        return exam

def get_section_exam_score_db(student_id: int, exam_date: datetime) -> float:
    """Получение оценки за экзамен по разделу"""
    with next(get_db()) as db:
        exam = (db.query(SectionExam)
               .filter(SectionExam.student_id == student_id, SectionExam.exam_date == exam_date)
               .first())
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экзамен по разделу для студента {student_id} на дату {exam_date} не найден"
            )
        return exam.correct_answers

def get_avg_score_by_student_subject_db(student_id: int, subject_id: int) -> float:
    """Средний балл студента по предмету (через связь Section → Subject)"""
    with next(get_db()) as db:
        avg_score = (db.query(func.avg(SectionExam.correct_answers))
                    .join(SectionExam.section)
                    .filter(SectionExam.student_id == student_id, Section.subject_id == subject_id)
                    .scalar())
        if avg_score is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экзамены по разделам для студента {student_id} по предмету {subject_id} не найдены"
            )
        return float(avg_score)

def get_avg_score_for_subject_db(subject_id: int) -> float:
    """Средний балл по предмету среди всех студентов"""
    with next(get_db()) as db:
        avg_score = (db.query(func.avg(SectionExam.correct_answers))
                    .join(SectionExam.section)
                    .filter(Section.subject_id == subject_id)
                    .scalar())
        if avg_score is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экзамены по разделам для предмета {subject_id} не найдены"
            )
        return float(avg_score)

# ===========================================
# BLOCK EXAM OPERATIONS
# ===========================================

def add_block_exam_db(student_id: int, block_id: int, subject_id: int,
                     correct_answers: float, exam_date: datetime,
                     category_correct: Optional[List[Any]] = None,
                     category_mistake: Optional[List[Any]] = None,
                     time_spent: Optional[str] = None, passed: Optional[bool] = None,
                     max_correct_answers: Optional[float] = None,
                     attempt_count: Optional[str] = None,
                     time_limit: Optional[str] = None) -> BlockExam:
    """Создание новой записи BlockExam"""
    with next(get_db()) as db:
        if not db.query(Student).get(student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Студент id={student_id} не найден"
            )
        if not db.query(Block).get(block_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Блок id={block_id} не найден"
            )
        if not db.query(Subject).get(subject_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Предмет id={subject_id} не найден"
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
            time_limit=time_limit
        )
        db.add(exam)
        db.commit()
        db.refresh(exam)
        return exam

def delete_block_exam_db(block_exam_id: int) -> None:
    """Удаление записи BlockExam"""
    with next(get_db()) as db:
        exam = db.query(BlockExam).get(block_exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экзамен по блоку id={block_exam_id} не найден"
            )
        db.delete(exam)
        db.commit()

def update_block_exam_db(block_exam_id: int, student_id: Optional[int] = None,
                        block_id: Optional[int] = None, subject_id: Optional[int] = None,
                        correct_answers: Optional[float] = None, exam_date: Optional[datetime] = None,
                        time_spent: Optional[str] = None, passed: Optional[bool] = None,
                        max_correct_answers: Optional[float] = None,
                        attempt_count: Optional[str] = None,
                        time_limit: Optional[str] = None) -> BlockExam:
    """Обновление полей BlockExam"""
    with next(get_db()) as db:
        exam = db.query(BlockExam).get(block_exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экзамен по блоку id={block_exam_id} не найден"
            )

        if student_id is not None:
            if not db.query(Student).get(student_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Студент id={student_id} не найден"
                )
            exam.student_id = student_id

        if block_id is not None:
            if not db.query(Block).get(block_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Блок id={block_id} не найден"
                )
            exam.block_id = block_id

        if subject_id is not None:
            if not db.query(Subject).get(subject_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Предмет id={subject_id} не найден"
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

        db.commit()
        db.refresh(exam)
        return exam

def get_all_block_scores_by_student_subject_db(student_id: int, subject_id: int) -> List[float]:
    """Получение всех оценок по блокам для студента и предмета"""
    with next(get_db()) as db:
        rows = (db.query(BlockExam.correct_answers)
               .filter(BlockExam.student_id == student_id, BlockExam.subject_id == subject_id)
               .order_by(BlockExam.exam_date)
               .all())
        return [r[0] for r in rows]

def get_block_score_by_student_date_subject_db(student_id: int, subject_id: int, exam_date: datetime) -> float:
    """Получение оценки по блоку для студента на конкретную дату"""
    with next(get_db()) as db:
        exam = (db.query(BlockExam)
               .filter_by(student_id=student_id, subject_id=subject_id, exam_date=exam_date)
               .first())
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экзамен по блоку для студента {student_id} по предмету {subject_id} на дату {exam_date} не найден"
            )
        return exam.correct_answers

def get_avg_block_score_by_student_subject_db(student_id: int, subject_id: int) -> float:
    """Средний балл по блокам для студента и предмета"""
    with next(get_db()) as db:
        avg_score = (db.query(func.avg(BlockExam.correct_answers))
                    .filter(BlockExam.student_id == student_id, BlockExam.subject_id == subject_id)
                    .scalar())
        if avg_score is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экзамены по блокам для студента {student_id} по предмету {subject_id} не найдены"
            )
        return float(avg_score)

def get_avg_block_score_for_subject_db(subject_id: int) -> Dict[int, float]:
    """Средний балл по блокам для каждого студента по предмету"""
    with next(get_db()) as db:
        rows = (db.query(BlockExam.student_id, func.avg(BlockExam.correct_answers).label("avg_score"))
               .filter(BlockExam.subject_id == subject_id)
               .group_by(BlockExam.student_id)
               .all())
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Экзамены по блокам для предмета {subject_id} не найдены"
            )
        return {student_id: float(avg_score) for student_id, avg_score in rows}

# ===========================================
# MODULE EXAM OPERATIONS
# ===========================================

def add_modul_exam_db(modul_id: int, student_id: int, chem_correct_answers: float,
                     bio_correct_answers: float, exam_date: datetime,
                     category_correct: Optional[List[Any]] = None,
                     category_mistake: Optional[List[Any]] = None,
                     total_questions_chem: Optional[int] = None,
                     total_questions_bio: Optional[int] = None,
                     time_spent_chem: Optional[str] = None,
                     time_spent_bio: Optional[str] = None) -> ModulExam:
    """Добавление нового модульного экзамена"""
    with next(get_db()) as db:
        if not db.query(Moduls).get(modul_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Модуль id={modul_id} не найден"
            )
        if not db.query(Student).get(student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Студент id={student_id} не найден"
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
            time_spent_bio=time_spent_bio
        )
        db.add(exam)
        db.commit()
        db.refresh(exam)
        return exam

def delete_modul_exam_db(modul_exam_id: int) -> None:
    """Удаление модульного экзамена"""
    with next(get_db()) as db:
        exam = db.query(ModulExam).get(modul_exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Модульный экзамен id={modul_exam_id} не найден"
            )
        db.delete(exam)
        db.commit()

def update_modul_exam_db(modul_exam_id: int, chem_correct_answers: Optional[float] = None,
                        bio_correct_answers: Optional[float] = None,
                        exam_date: Optional[datetime] = None,
                        total_questions_chem: Optional[int] = None,
                        total_questions_bio: Optional[int] = None,
                        time_spent_chem: Optional[str] = None,
                        time_spent_bio: Optional[str] = None) -> ModulExam:
    """Обновление модульного экзамена"""
    with next(get_db()) as db:
        exam = db.query(ModulExam).get(modul_exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Модульный экзамен id={modul_exam_id} не найден"
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

        db.commit()
        db.refresh(exam)
        return exam

def get_modul_exam_scores_db(student_id: int, modul_id: int, exam_date: datetime) -> Dict[str, float]:
    """Получение оценок модульного экзамена"""
    with next(get_db()) as db:
        exam = (db.query(ModulExam.chem_correct_answers, ModulExam.bio_correct_answers)
               .filter_by(student_id=student_id, modul_id=modul_id, exam_date=exam_date)
               .first())
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Оценки модульного экзамена не найдены"
            )
        chem, bio = exam
        return {"chem_correct_answers": chem, "bio_correct_answers": bio}

def get_avg_bio_score_for_student_db(student_id: int) -> float:
    """Средний балл по биологии для студента"""
    with next(get_db()) as db:
        avg_bio = (db.query(func.avg(ModulExam.bio_correct_answers))
                  .filter(ModulExam.student_id == student_id)
                  .scalar())
        return avg_bio or 0.0

def get_avg_chem_score_for_student_db(student_id: int) -> float:
    """Средний балл по химии для студента"""
    with next(get_db()) as db:
        avg_chem = (db.query(func.avg(ModulExam.chem_correct_answers))
                   .filter(ModulExam.student_id == student_id)
                   .scalar())
        return avg_chem or 0.0

def get_all_chem_scores_db(modul_id: int, exam_date: datetime) -> Dict[int, float]:
    """Получение всех оценок по химии для модуля на дату"""
    with next(get_db()) as db:
        rows = (db.query(ModulExam.student_id, ModulExam.chem_correct_answers)
               .filter_by(modul_id=modul_id, exam_date=exam_date)
               .all())
        return {sid: score for sid, score in rows}

def get_all_bio_scores_db(modul_id: int, exam_date: datetime) -> Dict[int, float]:
    """Получение всех оценок по биологии для модуля на дату"""
    with next(get_db()) as db:
        rows = (db.query(ModulExam.student_id, ModulExam.bio_correct_answers)
               .filter_by(modul_id=modul_id, exam_date=exam_date)
               .all())
        return {sid: score for sid, score in rows}

# ===========================================
# TOPIC TEST OPERATIONS
# ===========================================

def add_topic_test_db(student_id: int, topic_id: int, question_count: int,
                     correct_answers: float, attempt_date: datetime,
                     time_spent: Optional[str] = None) -> TopicTest:
    """Добавление теста по теме"""
    with next(get_db()) as db:
        if not db.query(Student).get(student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Студент id={student_id} не найден"
            )
        if not db.query(Topic).get(topic_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тема id={topic_id} не найдена"
            )
            
        tt = TopicTest(
            student_id=student_id,
            topic_id=topic_id,
            question_count=question_count,
            correct_answers=correct_answers,
            attempt_date=attempt_date,
            time_spent=time_spent
        )
        db.add(tt)
        db.commit()
        db.refresh(tt)
        return tt

def update_topic_test_score_db(student_id: int, topic_id: int, topic_test_id: int,
                              new_correct_answers: float) -> TopicTest:
    """Изменение оценки в TopicTest"""
    with next(get_db()) as db:
        tt = (db.query(TopicTest)
             .filter_by(topic_test_id=topic_test_id, student_id=student_id, topic_id=topic_id)
             .first())
        if not tt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тест по теме не найден для обновления"
            )
        tt.correct_answers = new_correct_answers
        db.commit()
        db.refresh(tt)
        return tt

def delete_topic_test_db(topic_test_id: int) -> None:
    """Удаление теста по теме"""
    with next(get_db()) as db:
        tt = db.query(TopicTest).get(topic_test_id)
        if not tt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тест по теме id={topic_test_id} не найден"
            )
        db.delete(tt)
        db.commit()

def get_topic_test_score_db(student_id: int, topic_id: int, topic_test_id: int) -> float:
    """Получение оценки теста по теме"""
    with next(get_db()) as db:
        score = (db.query(TopicTest.correct_answers)
                .filter_by(topic_test_id=topic_test_id, student_id=student_id, topic_id=topic_id)
                .scalar())
        if score is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Оценка теста не найдена"
            )
        return score

def get_all_topic_scores_by_topic_db(topic_id: int) -> Dict[int, float]:
    """Получение всех оценок по теме"""
    with next(get_db()) as db:
        rows = (db.query(TopicTest.student_id, TopicTest.correct_answers)
               .filter(TopicTest.topic_id == topic_id)
               .all())
        return {sid: sc for sid, sc in rows}

def get_avg_topic_score_for_student_db(student_id: int, topic_id: int) -> float:
    """Средний балл студента по теме"""
    with next(get_db()) as db:
        avg = (db.query(func.avg(TopicTest.correct_answers))
              .filter(TopicTest.student_id == student_id, TopicTest.topic_id == topic_id)
              .scalar())
        return avg or 0.0

# ===========================================
# CURRENT RATING OPERATIONS
# ===========================================

def add_current_rating_db(student_id: int, subject_id: int, topic_id: int,
                         current_correct_answers: float, second_current_correct_answers: float) -> CurrentRating:
    """Добавление текущего рейтинга"""
    with next(get_db()) as db:
        if not db.query(Topic).get(topic_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тема id={topic_id} не найдена"
            )
            
        rating = CurrentRating(
            student_id=student_id,
            subject_id=subject_id,
            topic_id=topic_id,
            current_correct_answers=current_correct_answers,
            second_current_correct_answers=second_current_correct_answers,
            last_updated=datetime.now()
        )
        db.add(rating)
        db.commit()
        db.refresh(rating)
        return rating

def delete_current_rating_db(rating_id: int) -> None:
    """Удаление текущего рейтинга"""
    with next(get_db()) as db:
        rating = db.query(CurrentRating).filter_by(rating_id=rating_id).first()
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Текущий рейтинг id={rating_id} не найден"
            )
        db.delete(rating)
        db.commit()

def update_current_rating_db(rating_id: int, current_correct_answers: Optional[float] = None,
                            second_current_correct_answers: Optional[float] = None) -> CurrentRating:
    """Обновление текущего рейтинга"""
    with next(get_db()) as db:
        rating = db.query(CurrentRating).filter_by(rating_id=rating_id).first()
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Текущий рейтинг id={rating_id} не найден"
            )
            
        if current_correct_answers is not None:
            rating.current_correct_answers = current_correct_answers
        if second_current_correct_answers is not None:
            rating.second_current_correct_answers = second_current_correct_answers
        rating.last_updated = datetime.now()
        
        db.commit()
        db.refresh(rating)
        return rating

def get_current_score_db(student_id: int, subject_id: int, topic_id: int) -> float:
    """Получение текущего балла"""
    with next(get_db()) as db:
        rating = db.query(CurrentRating).filter_by(
            student_id=student_id,
            subject_id=subject_id,
            topic_id=topic_id
        ).first()
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Текущий рейтинг не найден"
            )
        return rating.current_correct_answers

def get_second_current_score_db(student_id: int, subject_id: int, topic_id: int) -> float:
    """Получение второго текущего балла"""
    with next(get_db()) as db:
        rating = db.query(CurrentRating).filter_by(
            student_id=student_id,
            subject_id=subject_id,
            topic_id=topic_id
        ).first()
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Текущий рейтинг не найден"
            )
        return rating.second_current_correct_answers

def get_avg_sum_scores_by_block_for_student_db(student_id: int, block_id: int) -> float:
    """Средняя сумма баллов по блоку для студента"""
    with next(get_db()) as db:
        avg_sum = (db.query(func.avg(
            func.coalesce(CurrentRating.current_correct_answers, 0) +
            func.coalesce(CurrentRating.second_current_correct_answers, 0)
        )).join(Topic, CurrentRating.topic_id == Topic.topic_id)
        .filter(CurrentRating.student_id == student_id, Topic.block_id == block_id)
        .scalar())

        return float(avg_sum) if avg_sum is not None else 0.0

def get_avg_current_rating_for_block_db(block_id: int) -> Dict[int, float]:
    """Средний текущий рейтинг по блоку для всех студентов"""
    with next(get_db()) as db:
        block = db.query(Block).filter_by(block_id=block_id).first()
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Блок id={block_id} не найден"
            )
            
        subject_id = block.section.subject_id
        rows = (db.query(
            CurrentRating.student_id,
            func.avg(CurrentRating.current_correct_answers + CurrentRating.second_current_correct_answers).label("avg_score")
        ).join(CurrentRating.topic)
        .filter(Topic.block_id == block_id, CurrentRating.subject_id == subject_id)
        .group_by(CurrentRating.student_id)
        .all())

        return {student_id: avg_score for student_id, avg_score in rows}

# ===========================================
# CALCULATE FINAL GRADE
# ===========================================

def calculate_final_grade_db(student_id: int, subject_id: int) -> Dict[str, Any]:
    """Вычисление итоговой оценки студента по предмету"""
    with next(get_db()) as db:
        # Получаем средние баллы по разным типам экзаменов
        section_avg = (db.query(func.avg(SectionExam.correct_answers))
                      .join(SectionExam.section)
                      .filter(SectionExam.student_id == student_id, Section.subject_id == subject_id)
                      .scalar()) or 0
                      
        block_avg = (db.query(func.avg(BlockExam.correct_answers))
                    .filter(BlockExam.student_id == student_id, BlockExam.subject_id == subject_id)
                    .scalar()) or 0
                    
        current_avg = (db.query(func.avg(CurrentRating.current_correct_answers + CurrentRating.second_current_correct_answers))
                      .filter(CurrentRating.student_id == student_id, CurrentRating.subject_id == subject_id)
                      .scalar()) or 0
                      
        topic_avg = (db.query(func.avg(TopicTest.correct_answers))
                    .join(TopicTest.topic)
                    .join(Topic.block)
                    .join(Block.section)
                    .filter(TopicTest.student_id == student_id, Section.subject_id == subject_id)
                    .scalar()) or 0

        # Получаем количество записей для весового коэффициента
        section_count = (db.query(SectionExam)
                        .join(SectionExam.section)
                        .filter(SectionExam.student_id == student_id, Section.subject_id == subject_id)
                        .count())
                        
        block_count = (db.query(BlockExam)
                      .filter(BlockExam.student_id == student_id, BlockExam.subject_id == subject_id)
                      .count())
                      
        current_count = (db.query(CurrentRating)
                        .filter(CurrentRating.student_id == student_id, CurrentRating.subject_id == subject_id)
                        .count())
                        
        topic_count = (db.query(TopicTest)
                      .join(TopicTest.topic)
                      .join(Topic.block)
                      .join(Block.section)
                      .filter(TopicTest.student_id == student_id, Section.subject_id == subject_id)
                      .count())

        # Вычисляем итоговую оценку с весовыми коэффициентами
        weights = {
            'section': 0.3,
            'block': 0.3,
            'current': 0.25,
            'topic': 0.15
        }
        
        total_weight = 0
        weighted_sum = 0
        
        if section_count > 0:
            weighted_sum += section_avg * weights['section']
            total_weight += weights['section']
            
        if block_count > 0:
            weighted_sum += block_avg * weights['block']
            total_weight += weights['block']
            
        if current_count > 0:
            weighted_sum += current_avg * weights['current']
            total_weight += weights['current']
            
        if topic_count > 0:
            weighted_sum += topic_avg * weights['topic']
            total_weight += weights['topic']

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
                "topic_tests": topic_count
            }
        }