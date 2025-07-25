from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime, date

# ========== ТИПЫ И КОНСТАНТЫ ==========

AttendanceStatus = Literal["present", "absent", "late"]
CommentType = Literal["positive", "negative", "neutral"]
TestType = Literal["training", "control", "final"]
StudentStatus = Literal["active", "inactive"]
SubjectName = Literal["chemistry", "biology", "химия", "биология"]

# ========== БАЗОВЫЕ МОДЕЛИ ==========

class StudentInfoResponse(BaseModel):
    """Основная информация о студенте"""
    
    student_id: int
    name: str
    surname: str
    phone: Optional[str] = None
    email: Optional[str] = None
    photo: Optional[str] = None
    direction: Optional[str] = None
    goal: Optional[str] = None
    group_id: Optional[int] = None
    student_status: StudentStatus
    last_login: Optional[datetime] = None
    
    # Дополнительная информация
    hobby: Optional[str] = None
    sex: Optional[str] = None
    address: Optional[str] = None
    birthday: Optional[date] = None
    
    class Config:
        from_attributes = True


class UniversityResponse(BaseModel):
    """Информация об университете"""
    
    university_id: int
    name: str
    type: str = Field(alias="university_type")
    entrance_score: Optional[float] = None
    location: str
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    contact_phone: Optional[str] = None
    priority_order: Optional[int] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True


class FacultyResponse(BaseModel):
    """Информация о факультете"""
    
    faculty_id: int
    name: str
    annual_cost: Optional[str] = None
    available_place: Optional[str] = None
    description: Optional[str] = None
    entrance_score: Optional[float] = None
    code: Optional[str] = None
    
    class Config:
        from_attributes = True


class TestResultResponse(BaseModel):
    """Результат теста"""
    
    test_id: int
    test_type: TestType
    topic_name: str
    subject_name: str
    score_percentage: float
    correct_answers: int
    total_questions: int
    attempt_date: datetime
    time_spent: Optional[str] = None
    passed: bool
    
    class Config:
        from_attributes = True


class AttendanceResponse(BaseModel):
    """Информация о посещаемости"""
    
    attendance_id: int
    lesson_date_time: datetime
    att_status: AttendanceStatus
    topic_name: Optional[str] = None
    subject_name: str
    excuse_reason: Optional[str] = None
    extra_lesson: Optional[str] = None
    
    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Комментарий учителя"""
    
    comment_id: int
    teacher_name: str
    comment_text: str
    comment_date: datetime
    comment_type: CommentType
    
    class Config:
        from_attributes = True


class ExamScoreResponse(BaseModel):
    """Оценка за экзамен"""
    
    exam_type: str  # "dtm", "section", "block", "module"
    subject_name: Optional[str] = None
    section_name: Optional[str] = None
    block_name: Optional[str] = None
    score: float
    max_score: Optional[float] = None
    exam_date: datetime
    passed: Optional[bool] = None
    
    class Config:
        from_attributes = True


class StudentStatisticsResponse(BaseModel):
    """Статистика студента"""
    
    # Общая статистика
    total_tests_completed: int
    average_score: float
    total_time_studied_hours: float
    
    # Посещаемость
    attendance_rate: float
    total_lessons: int
    present_count: int
    absent_count: int
    late_count: int
    
    # Оценки по предметам
    subject_averages: Dict[str, float] = Field(default_factory=dict)
    
    # Прогресс
    completed_topics: int
    total_topics: int
    progress_percentage: float
    
    class Config:
        from_attributes = True


class StudentProgressResponse(BaseModel):
    """Прогресс студента по темам"""
    
    topic_id: int
    topic_name: str
    subject_name: str
    section_name: str
    block_name: str
    is_completed: bool
    test_score: Optional[float] = None
    attendance: Optional[AttendanceStatus] = None
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class StudentAnalyticsResponse(BaseModel):
    """Аналитика студента по категориям"""
    
    # Правильные и неправильные ответы по категориям
    correct_by_category: Dict[str, int] = Field(default_factory=dict)
    mistakes_by_category: Dict[str, int] = Field(default_factory=dict)
    
    # Общие показатели
    total_correct: int
    total_mistakes: int
    accuracy_percentage: float
    
    # Слабые места
    weak_categories: List[str] = Field(default_factory=list)
    strong_categories: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class StudentProfileResponse(BaseModel):
    """Полный профиль студента"""
    
    student_info: StudentInfoResponse
    universities: List[UniversityResponse] = Field(default_factory=list)
    recent_tests: List[TestResultResponse] = Field(default_factory=list)
    attendance_summary: Dict[str, Any] = Field(default_factory=dict)
    recent_comments: List[CommentResponse] = Field(default_factory=list)
    exam_scores: List[ExamScoreResponse] = Field(default_factory=list)
    statistics: StudentStatisticsResponse
    analytics: StudentAnalyticsResponse
    progress: List[StudentProgressResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


# ========== ЗАПРОСЫ ==========

class UpdateStudentInfoRequest(BaseModel):
    """Запрос на обновление информации студента"""
    
    hobby: Optional[str] = None
    sex: Optional[str] = None
    address: Optional[str] = None
    birthday: Optional[date] = None
    goal: Optional[str] = None
    
    class Config:
        validate_assignment = True


class AddUniversityRequest(BaseModel):
    """Запрос на добавление университета в список"""
    
    university_id: int = Field(..., gt=0)
    priority_order: int = Field(..., ge=1, le=10)


class UpdateUniversityPriorityRequest(BaseModel):
    """Запрос на изменение приоритета университета"""
    
    universities: List[Dict[str, int]] = Field(
        ..., 
        description="Список с university_id и priority_order"
    )


class StudentGoalRequest(BaseModel):
    """Запрос на обновление цели студента"""
    
    goal: str = Field(..., min_length=1, max_length=500)


# ========== ФИЛЬТРЫ ==========

class StudentTestsFilter(BaseModel):
    """Фильтры для тестов студента"""
    
    subject_name: Optional[SubjectName] = None
    test_type: Optional[TestType] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    passed_only: Optional[bool] = None
    limit: int = Field(default=20, le=100)


class StudentAttendanceFilter(BaseModel):
    """Фильтры для посещаемости студента"""
    
    subject_name: Optional[SubjectName] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[AttendanceStatus] = None
    limit: int = Field(default=50, le=200)


class StudentCommentsFilter(BaseModel):
    """Фильтры для комментариев студента"""
    
    comment_type: Optional[CommentType] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=20, le=100)


# ========== ОТВЕТЫ API ==========

class StudentTestsResponse(BaseModel):
    """Ответ со списком тестов студента"""
    
    tests: List[TestResultResponse] = Field(default_factory=list)
    total_count: int
    average_score: float
    passed_count: int
    failed_count: int
    
    class Config:
        from_attributes = True


class StudentAttendanceResponse(BaseModel):
    """Ответ с посещаемостью студента"""
    
    attendance_records: List[AttendanceResponse] = Field(default_factory=list)
    total_count: int
    attendance_rate: float
    present_count: int
    absent_count: int
    late_count: int
    
    class Config:
        from_attributes = True


class StudentCommentsResponse(BaseModel):
    """Ответ с комментариями о студенте"""
    
    comments: List[CommentResponse] = Field(default_factory=list)
    total_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    
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

class StudentProfileHealthResponse(BaseModel):
    """Ответ проверки здоровья API профиля студента"""
    
    status: str = "healthy"
    service: str = "student-profile-api"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    active_students: Optional[int] = None