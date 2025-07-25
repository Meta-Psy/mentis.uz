from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime
from enum import Enum

# ========== ЭНУМЫ ==========

class AttendanceTypeEnum(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"

class CommentTypeEnum(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class TestTypeEnum(str, Enum):
    TRAINING = "training"
    CONTROL = "control"
    FINAL = "final"

# ========== БАЗОВЫЕ МОДЕЛИ ==========

class AttendanceResponse(BaseModel):
    """Модель записи посещаемости"""
    attendance_id: int
    student_id: int
    lesson_date_time: datetime
    att_status: AttendanceTypeEnum
    subject_id: int
    topic_id: int
    excuse_reason: Optional[str] = None
    extra_lesson: Optional[str] = None
    
    # Связанные данные
    topic_name: Optional[str] = None
    subject_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class AttendanceDay(BaseModel):
    """День в календаре посещаемости"""
    date: int
    status: Literal["present", "absent", "late", "exam", "holiday", "future"]
    lesson: str
    topic_id: Optional[int] = None
    attendance_id: Optional[int] = None

class AttendanceMonth(BaseModel):
    """Месяц в календаре посещаемости"""
    name: str
    year: int
    month: int
    days: List[AttendanceDay]

class AttendanceCalendarResponse(BaseModel):
    """Календарь посещаемости"""
    student_id: int
    subject_id: int
    months: List[AttendanceMonth]
    
    class Config:
        from_attributes = True

class CurrentRatingResponse(BaseModel):
    """Модель текущего рейтинга"""
    rating_id: int
    student_id: int
    subject_id: int
    topic_id: int
    current_correct_answers: float
    second_current_correct_answers: float
    last_updated: datetime
    
    # Связанные данные
    topic_name: Optional[str] = None
    topic_number: Optional[int] = None
    
    class Config:
        from_attributes = True

class PerformanceTopic(BaseModel):
    """Тема в таблице успеваемости"""
    number: int
    topic_id: int
    topic_name: str
    listened: bool
    first_try: Optional[float] = None
    second_try: Optional[float] = None
    average: float
    
    class Config:
        from_attributes = True

class PerformanceModuleResponse(BaseModel):
    """Успеваемость по модулю"""
    module_id: int
    module_name: str
    topics: List[PerformanceTopic]
    
    class Config:
        from_attributes = True

class CommentResponse(BaseModel):
    """Модель комментария"""
    comment_id: int
    teacher_id: int
    student_id: int
    comment_text: str
    comment_date: datetime
    comment_type: CommentTypeEnum
    
    # Связанные данные
    teacher_name: Optional[str] = None
    teacher_surname: Optional[str] = None
    
    class Config:
        from_attributes = True

class FinalGradeResponse(BaseModel):
    """Итоговая оценка"""
    student_id: int
    subject_id: int
    section_average: float
    block_average: float
    current_average: float  
    topic_average: float
    final_grade: float
    counts: Dict[str, int]
    
    class Config:
        from_attributes = True

# ========== СТАТИСТИКА ==========

class AttendanceStatistics(BaseModel):
    """Статистика посещаемости"""
    student_id: int
    subject_id: Optional[int] = None
    total_lessons: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_rate: float

class StudentStatistics(BaseModel):
    """Общая статистика студента"""
    student_id: int
    attendance_stats: Dict[str, AttendanceStatistics]
    performance_stats: Dict[str, FinalGradeResponse]
    comments_count: Dict[str, int]
    
    class Config:
        from_attributes = True

# ========== ЗАПРОСЫ ==========

class AttendanceRequest(BaseModel):
    """Запрос создания записи посещаемости"""
    student_id: int = Field(..., gt=0)
    lesson_date_time: datetime
    att_status: AttendanceTypeEnum
    subject_id: int = Field(..., gt=0)
    topic_id: int = Field(..., gt=0)
    excuse_reason: Optional[str] = None
    extra_lesson: Optional[str] = None

class AttendanceUpdateRequest(BaseModel):
    """Запрос обновления посещаемости"""
    att_status: Optional[AttendanceTypeEnum] = None
    excuse_reason: Optional[str] = None
    extra_lesson: Optional[str] = None

class CommentRequest(BaseModel):
    """Запрос создания комментария"""
    teacher_id: int = Field(..., gt=0)
    student_id: int = Field(..., gt=0)
    comment_text: str = Field(..., min_length=1, max_length=1000)
    comment_type: CommentTypeEnum

class CommentUpdateRequest(BaseModel):
    """Запрос обновления комментария"""
    comment_text: Optional[str] = Field(None, min_length=1, max_length=1000)
    comment_type: Optional[CommentTypeEnum] = None

class CurrentRatingRequest(BaseModel):
    """Запрос создания текущего рейтинга"""
    student_id: int = Field(..., gt=0)
    subject_id: int = Field(..., gt=0)
    topic_id: int = Field(..., gt=0)
    current_correct_answers: float = Field(..., ge=0.0)
    second_current_correct_answers: float = Field(..., ge=0.0)

class CurrentRatingUpdateRequest(BaseModel):
    """Запрос обновления текущего рейтинга"""
    current_correct_answers: Optional[float] = Field(None, ge=0.0)
    second_current_correct_answers: Optional[float] = Field(None, ge=0.0)

# ========== ФИЛЬТРЫ ==========

class AttendanceFilterRequest(BaseModel):
    """Фильтры для посещаемости"""
    subject_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[AttendanceTypeEnum] = None

class PerformanceFilterRequest(BaseModel):
    """Фильтры для успеваемости"""
    subject_name: Literal["chemistry", "biology", "химия", "биология"]
    module_filter: Optional[int] = None

class CommentsFilterRequest(BaseModel):
    """Фильтры для комментариев"""
    comment_type: Optional[CommentTypeEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_text: Optional[str] = None

# ========== ОТВЕТЫ API ==========

class StudentDetailsResponse(BaseModel):
    """Полная информация о студенте для родительской страницы"""
    student_id: int
    student_name: str
    student_surname: str
    
    # Данные по предметам
    subjects_data: Dict[str, Dict[str, Any]]  # subject_name -> {attendance: {}, performance: {}, final_grades: {}}
    
    class Config:
        from_attributes = True

class ModuleAttendanceResponse(BaseModel):
    """Посещаемость по модулю"""
    module_id: int
    module_name: str
    months: List[AttendanceMonth]
    statistics: AttendanceStatistics
    
    class Config:
        from_attributes = True

class ModulePerformanceResponse(BaseModel):
    """Успеваемость по модулю"""
    module_id: int
    module_name: str
    topics: List[PerformanceTopic]
    average_grade: float
    
    class Config:
        from_attributes = True

# ========== ОШИБКИ ==========

class ErrorResponse(BaseModel):
    """Стандартная модель ошибки"""
    error: str
    detail: str
    status_code: int

class ValidationErrorDetail(BaseModel):
    """Детали ошибки валидации"""
    field: str
    message: str
    value: Any

class ValidationErrorResponse(BaseModel):
    """Ответ с ошибками валидации"""
    detail: List[ValidationErrorDetail]

# ========== ЗДОРОВЬЕ СЕРВИСА ==========

class AssessmentHealthResponse(BaseModel):
    """Ответ проверки здоровья сервиса оценок"""
    status: str = "healthy"
    service: str = "assessment-api"
    version: str = "1.0.0" 
    timestamp: datetime = Field(default_factory=datetime.now)
    active_students: Optional[int] = None