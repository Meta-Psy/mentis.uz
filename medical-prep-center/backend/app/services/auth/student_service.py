from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import and_, or_
from app.database import get_db
from app.database.models.academic import GroupProgress, University, Faculty, UniversityType
from app.database.models.assessment import TopicTest, ModulExam, BlockExam, SectionExam
from app.database.models.user import Student, StudentInfo, StudentStatus, User, UserRole

# ===========================================
# STUDENT OPERATIONS (Updated - without create)
# ===========================================

def get_student_by_id_db(student_id: int) -> Student:
    """Получение студента по ID"""
    with next(get_db()) as db:
        student = db.query(Student).filter_by(student_id=student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )
        return student

def update_student_db(student_id: int, direction: Optional[str] = None,
                     group_id: Optional[int] = None, goal: Optional[str] = None,
                     student_status: Optional[StudentStatus] = None) -> Student:
    """Обновление данных студента"""
    with next(get_db()) as db:
        student = db.query(Student).filter_by(student_id=student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )

        if direction is not None:
            student.direction = direction
        if group_id is not None:
            student.group_id = group_id
        if goal is not None:
            student.goal = goal
        if student_status is not None:
            student.student_status = student_status

        db.commit()
        db.refresh(student)
        return student

def delete_student_db(student_id: int) -> dict:
    """Удаление студента"""
    with next(get_db()) as db:
        student = db.query(Student).filter_by(student_id=student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )
        db.delete(student)
        db.commit()
        return {"status": "Удален"}

# ===========================================
# STUDENT INFO OPERATIONS
# ===========================================

def create_student_info_db(student_id: int, hobby: Optional[str] = None,
                          sex: Optional[str] = None, address: Optional[str] = None,
                          birthday: Optional[datetime] = None) -> StudentInfo:
    """Создание дополнительной информации о студенте"""
    with next(get_db()) as db:
        # Проверяем, что студент существует
        student = db.query(Student).filter_by(student_id=student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )

        # Проверяем, что информация еще не создана
        existing_info = db.query(StudentInfo).filter_by(student_id=student_id).first()
        if existing_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Информация о студенте уже существует"
            )

        student_info = StudentInfo(
            student_id=student_id,
            hobby=hobby,
            sex=sex,
            address=address,
            birthday=birthday
        )
        db.add(student_info)
        db.commit()
        db.refresh(student_info)
        return student_info

def update_student_info_db(student_id: int, hobby: Optional[str] = None,
                          sex: Optional[str] = None, address: Optional[str] = None,
                          birthday: Optional[datetime] = None) -> StudentInfo:
    """Обновление дополнительной информации о студенте"""
    with next(get_db()) as db:
        student_info = db.query(StudentInfo).filter_by(student_id=student_id).first()
        if not student_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Информация о студенте не найдена"
            )

        if hobby is not None:
            student_info.hobby = hobby
        if sex is not None:
            student_info.sex = sex
        if address is not None:
            student_info.address = address
        if birthday is not None:
            student_info.birthday = birthday

        db.commit()
        db.refresh(student_info)
        return student_info

# ===========================================
# GROUP PROGRESS OPERATIONS
# ===========================================

def add_group_progress_db(group_id: int, topic_id: int, data: str,
                         average_score: Optional[float] = None,
                         notes: Optional[str] = None) -> GroupProgress:
    """Добавление прогресса группы по конкретному уроку"""
    with next(get_db()) as db:
        # Проверяем, существует ли уже запись для данной группы и урока
        existing_progress = db.query(GroupProgress).filter_by(
            group_id=group_id, topic_id=topic_id
        ).first()

        if existing_progress:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Прогресс для группы {group_id} по уроку {topic_id} уже существует"
            )

        new_progress = GroupProgress(
            group_id=group_id,
            topic_id=topic_id,
            data=data,
            average_score=average_score,
            notes=notes
        )
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)
        return new_progress

def update_group_progress_db(group_progress_id: int, data: Optional[str] = None,
                           average_score: Optional[float] = None,
                           notes: Optional[str] = None) -> GroupProgress:
    """Изменение прогресса группы по конкретному уроку"""
    with next(get_db()) as db:
        progress = db.query(GroupProgress).filter_by(
            group_progress_id=group_progress_id
        ).first()

        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Прогресс группы не найден"
            )

        if data is not None:
            progress.data = data
        if average_score is not None:
            progress.average_score = average_score
        if notes is not None:
            progress.notes = notes

        db.commit()
        db.refresh(progress)
        return progress

def delete_group_progress_db(group_progress_id: int) -> dict:
    """Удаление прогресса группы по конкретному уроку"""
    with next(get_db()) as db:
        progress = db.query(GroupProgress).filter_by(
            group_progress_id=group_progress_id
        ).first()

        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Прогресс группы не найден"
            )

        db.delete(progress)
        db.commit()
        return {"status": "Удален"}

def get_group_progress_by_lesson_db(group_id: int, topic_id: int) -> GroupProgress:
    """Получение прогресса группы по конкретному уроку"""
    with next(get_db()) as db:
        progress = db.query(GroupProgress).filter_by(
            group_id=group_id, topic_id=topic_id
        ).first()

        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Прогресс группы {group_id} по уроку {topic_id} не найден"
            )

        return progress

# ===========================================
# STUDENT EXAM STATUS OPERATIONS
# ===========================================

def get_overdue_exams_db(student_id: int) -> dict:
    """Получение всех просроченных тестов конкретного ученика"""
    with next(get_db()) as db:
        today = datetime.now().date()

        # Получаем все экзамены студента, где дата экзамена меньше сегодняшней
        overdue_topic_tests = db.query(TopicTest).filter(
            and_(
                TopicTest.student_id == student_id,
                TopicTest.attempt_date < today
            )
        ).all()

        overdue_module_exams = db.query(ModulExam).filter(
            and_(
                ModulExam.student_id == student_id,
                ModulExam.exam_date < today
            )
        ).all()

        overdue_block_exams = db.query(BlockExam).filter(
            and_(
                BlockExam.student_id == student_id,
                BlockExam.exam_date < today
            )
        ).all()

        overdue_section_exams = db.query(SectionExam).filter(
            and_(
                SectionExam.student_id == student_id,
                SectionExam.exam_date < today
            )
        ).all()

        return {
            "student_id": student_id,
            "overdue_topic_tests": overdue_topic_tests,
            "overdue_module_exams": overdue_module_exams,
            "overdue_block_exams": overdue_block_exams,
            "overdue_section_exams": overdue_section_exams,
            "total_overdue": (len(overdue_topic_tests) + len(overdue_module_exams) +
                              len(overdue_block_exams) + len(overdue_section_exams))
        }

def get_upcoming_exams_db(student_id: int) -> dict:
    """Получение актуальных тестов (в ближайшие 2 дня) конкретного ученика"""
    with next(get_db()) as db:
        today = datetime.now().date()
        two_days_later = today + timedelta(days=2)

        # Получаем все экзамены студента на ближайшие 2 дня
        upcoming_topic_tests = db.query(TopicTest).filter(
            and_(
                TopicTest.student_id == student_id,
                TopicTest.attempt_date >= today,
                TopicTest.attempt_date <= two_days_later
            )
        ).all()

        upcoming_module_exams = db.query(ModulExam).filter(
            and_(
                ModulExam.student_id == student_id,
                ModulExam.exam_date >= today,
                ModulExam.exam_date <= two_days_later
            )
        ).all()

        upcoming_block_exams = db.query(BlockExam).filter(
            and_(
                BlockExam.student_id == student_id,
                BlockExam.exam_date >= today,
                BlockExam.exam_date <= two_days_later
            )
        ).all()

        upcoming_section_exams = db.query(SectionExam).filter(
            and_(
                SectionExam.student_id == student_id,
                SectionExam.exam_date >= today,
                SectionExam.exam_date <= two_days_later
            )
        ).all()

        return {
            "student_id": student_id,
            "upcoming_topic_tests": upcoming_topic_tests,
            "upcoming_module_exams": upcoming_module_exams,
            "upcoming_block_exams": upcoming_block_exams,
            "upcoming_section_exams": upcoming_section_exams,
            "total_upcoming": (len(upcoming_topic_tests) + len(upcoming_module_exams) +
                               len(upcoming_block_exams) + len(upcoming_section_exams))
        }

# ===========================================
# UNIVERSITY OPERATIONS
# ===========================================

def add_university_db(name: str, entrance_score: Optional[float],
                      university_type: UniversityType, location: str, website_url: str,
                      logo_url: Optional[str] = None, contact_phone: Optional[str] = None) -> University:
    """Добавление нового университета"""
    with next(get_db()) as db:
        # Проверяем, существует ли уже университет с таким именем
        existing_university = db.query(University).filter_by(name=name).first()
        if existing_university:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Университет с именем '{name}' уже существует"
            )

        new_university = University(
            name=name,
            entrance_score=entrance_score,
            type=university_type,
            location=location,
            website_url=website_url,
            logo_url=logo_url,
            contact_phone=contact_phone
        )
        db.add(new_university)
        db.commit()
        db.refresh(new_university)
        return new_university

def update_university_db(university_id: int, name: Optional[str] = None,
                         entrance_score: Optional[float] = None,
                         university_type: Optional[UniversityType] = None,
                         location: Optional[str] = None,
                         website_url: Optional[str] = None,
                         logo_url: Optional[str] = None,
                         contact_phone: Optional[str] = None) -> University:
    """Изменение информации о университете"""
    with next(get_db()) as db:
        university = db.query(University).filter_by(university_id=university_id).first()

        if not university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Университет не найден"
            )

        if name is not None:
            university.name = name
        if entrance_score is not None:
            university.entrance_score = entrance_score
        if university_type is not None:
            university.type = university_type
        if location is not None:
            university.location = location
        if website_url is not None:
            university.website_url = website_url
        if logo_url is not None:
            university.logo_url = logo_url
        if contact_phone is not None:
            university.contact_phone = contact_phone

        db.commit()
        db.refresh(university)
        return university

def delete_university_db(university_id: int) -> dict:
    """Удаление университета"""
    with next(get_db()) as db:
        university = db.query(University).filter_by(university_id=university_id).first()

        if not university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Университет не найден"
            )

        db.delete(university)
        db.commit()
        return {"status": "Удален"}

def get_university_by_id_db(university_id: int) -> University:
    """Получение университета по ID"""
    with next(get_db()) as db:
        university = db.query(University).filter_by(university_id=university_id).first()

        if not university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Университет не найден"
            )

        return university

def get_all_universities_db() -> List[University]:
    """Получение всех университетов"""
    with next(get_db()) as db:
        universities = db.query(University).all()
        return universities

# ===========================================
# FACULTY OPERATIONS
# ===========================================

def add_faculty_db(university_id: int, name: str, description: Optional[str] = None,
                   entrance_score: Optional[float] = None, annual_cost: Optional[str] = None,
                   available_place: Optional[str] = None, code: Optional[str] = None) -> Faculty:
    """Добавление нового факультета"""
    with next(get_db()) as db:
        # Проверяем, существует ли университет
        university = db.query(University).filter_by(university_id=university_id).first()
        if not university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Университет не найден"
            )

        # Проверяем, существует ли уже факультет с таким именем в данном университете
        existing_faculty = db.query(Faculty).filter_by(
            university_id=university_id, name=name
        ).first()
        if existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Факультет '{name}' уже существует в данном университете"
            )

        new_faculty = Faculty(
            university_id=university_id,
            name=name,
            description=description,
            entrance_score=entrance_score,
            annual_cost=annual_cost,
            available_place=available_place,
            code=code
        )
        db.add(new_faculty)
        db.commit()
        db.refresh(new_faculty)
        return new_faculty

def update_faculty_db(faculty_id: int, name: Optional[str] = None,
                      description: Optional[str] = None,
                      entrance_score: Optional[float] = None,
                      annual_cost: Optional[str] = None,
                      available_place: Optional[str] = None,
                      code: Optional[str] = None) -> Faculty:
    """Изменение информации о факультете"""
    with next(get_db()) as db:
        faculty = db.query(Faculty).filter_by(faculty_id=faculty_id).first()

        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Факультет не найден"
            )

        if name is not None:
            faculty.name = name
        if description is not None:
            faculty.description = description
        if entrance_score is not None:
            faculty.entrance_score = entrance_score
        if annual_cost is not None:
            faculty.annual_cost = annual_cost
        if available_place is not None:
            faculty.available_place = available_place
        if code is not None:
            faculty.code = code

        db.commit()
        db.refresh(faculty)
        return faculty

def delete_faculty_db(faculty_id: int) -> dict:
    """Удаление факультета"""
    with next(get_db()) as db:
        faculty = db.query(Faculty).filter_by(faculty_id=faculty_id).first()

        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Факультет не найден"
            )

        db.delete(faculty)
        db.commit()
        return {"status": "Удален"}

def get_faculty_by_id_db(faculty_id: int) -> Faculty:
    """Получение факультета по ID"""
    with next(get_db()) as db:
        faculty = db.query(Faculty).filter_by(faculty_id=faculty_id).first()

        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Факультет не найден"
            )

        return faculty

def get_faculties_by_university_db(university_id: int) -> List[Faculty]:
    """Получение всех факультетов конкретного университета"""
    with next(get_db()) as db:
        faculties = db.query(Faculty).filter_by(university_id=university_id).all()

        if not faculties:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Факультеты для университета {university_id} не найдены"
            )

        return faculties

def get_all_faculties_db() -> List[Faculty]:
    """Получение всех факультетов"""
    with next(get_db()) as db:
        faculties = db.query(Faculty).all()
        return faculties

# ===========================================
# HELPER FUNCTIONS
# ===========================================

def get_students_by_group_db(group_id: int) -> List[Student]:
    """Получение всех студентов группы"""
    with next(get_db()) as db:
        students = db.query(Student).filter_by(group_id=group_id).all()
        if not students:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Студенты группы {group_id} не найдены"
            )
        return students

def get_active_students_db() -> List[Student]:
    """Получение всех активных студентов"""
    with next(get_db()) as db:
        students = db.query(Student).filter_by(student_status=StudentStatus.ACTIVE).all()
        return students

def get_inactive_students_db() -> List[Student]:
    """Получение всех неактивных студентов"""
    with next(get_db()) as db:
        students = db.query(Student).filter_by(student_status=StudentStatus.INACTIVE).all()
        return students

def activate_student_db(student_id: int) -> Student:
    """Активация студента"""
    with next(get_db()) as db:
        student = db.query(Student).filter_by(student_id=student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )
        
        student.student_status = StudentStatus.ACTIVE
        db.commit()
        db.refresh(student)
        return student

def deactivate_student_db(student_id: int) -> Student:
    """Деактивация студента"""
    with next(get_db()) as db:
        student = db.query(Student).filter_by(student_id=student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )
        
        student.student_status = StudentStatus.INACTIVE
        db.commit()
        db.refresh(student)
        return student