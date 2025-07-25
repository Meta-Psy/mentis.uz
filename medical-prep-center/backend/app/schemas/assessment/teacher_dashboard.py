from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime

# ========== ТИПЫ И КОНСТАНТЫ ==========

CommentType = Literal["positive", "negative", "neutral"]
AttendanceStatus = Literal["present", "absent", "late"]
StudentStatus = Literal["active", "inactive"]

# ========== БАЗОВЫЕ МОДЕЛИ ==========

class StudentSkillAnalysis(BaseModel):
    """Анализ навыков студента по 8 критериям"""
    
    correct_answers: List[int] = Field(default_factory=lambda: [0] * 8, description="Правильные ответы по каждому критерию")
    incorrect_answers: List[int] = Field(default_factory=lambda: [0] * 8, description="Неправильные ответы по каждому критерию")
    
    def get_criterion_accuracy(self, criterion_index: int) -> float:
        """Получить точность по критерию (0-1)"""
        if criterion_index < 0 or criterion_index >= 8:
            return 0.0
        
        correct = self.correct_answers[criterion_index]
        incorrect = self.incorrect_answers[criterion_index]
        total = correct + incorrect
        
        return correct / total if total > 0 else 0.0
    
    def get_total_accuracy(self) -> float:
        """Получить общую точность"""
        total_correct = sum(self.correct_answers)
        total_incorrect = sum(self.incorrect_answers)
        total = total_correct + total_incorrect
        
        return total_correct / total if total > 0 else 0.0


class StudentAttendanceInfo(BaseModel):
    """Информация о посещаемости студента"""
    
    total_lessons: int = 0
    present_count: int = 0
    absent_count: int = 0
    late_count: int = 0
    attendance_rate: float = 0.0
    last_attendance_date: Optional[datetime] = None


class StudentTestStatistics(BaseModel):
    """Статистика тестов студента"""
    
    total_tests: int = 0
    completed_tests: int = 0
    pending_tests: int = 0
    average_score: float = 0.0
    best_score: float = 0.0
    dtm_score: Optional[float] = None
    last_test_date: Optional[datetime] = None


class StudentCommentInfo(BaseModel):
    """Информация о комментариях студента"""
    
    comment_id: Optional[int] = None
    comment_text: str = ""
    comment_type: CommentType = "neutral"
    last_updated: Optional[datetime] = None


class StudentDetailInfo(BaseModel):
    """Детальная информация о студенте для преподавателя"""
    
    student_id: int = Field(alias="id")
    name: str = Field(alias="full_name")
    photo: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    # Статистика
    test_statistics: StudentTestStatistics
    attendance_info: StudentAttendanceInfo
    skill_analysis: StudentSkillAnalysis
    comment_info: StudentCommentInfo
    
    # Статусы
    student_status: StudentStatus = "active"
    last_seen: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True


class GroupScheduleInfo(BaseModel):
    """Информация о расписании группы"""
    
    group_id: int
    group_name: str
    days: List[str] = Field(default_factory=list)
    start_time: str = "00:00"
    student_count: int = 0
    subject_name: str = ""


class TeacherProfileInfo(BaseModel):
    """Профиль преподавателя"""
    
    teacher_id: int
    name: str = Field(alias="full_name")
    surname: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    photo: Optional[str] = None
    
    # Дополнительная информация
    education_background: Optional[str] = None
    years_experience: Optional[int] = None
    certifications: Optional[str] = None
    languages: Optional[str] = None
    
    # Предметы и группы
    subjects: List[str] = Field(default_factory=list)
    schedule: List[GroupScheduleInfo] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
        populate_by_name = True


# ========== ОТВЕТЫ API ==========

class GroupStudentsResponse(BaseModel):
    """Ответ со студентами группы"""
    
    group_id: int
    group_name: str
    students: List[StudentDetailInfo]
    total_count: int
    
    class Config:
        from_attributes = True


class TeacherGroupsResponse(BaseModel):
    """Ответ с группами преподавателя"""
    
    teacher_id: int
    groups: List[GroupScheduleInfo]
    total_groups: int
    total_students: int
    
    class Config:
        from_attributes = True


class TeacherDashboardResponse(BaseModel):
    """Основной ответ дашборда преподавателя"""
    
    teacher_profile: TeacherProfileInfo
    groups: List[GroupScheduleInfo]
    total_students: int
    
    class Config:
        from_attributes = True


# ========== ЗАПРОСЫ ==========

class UpdateCommentRequest(BaseModel):
    """Запрос на обновление комментария"""
    
    student_id: int = Field(..., gt=0)
    comment_text: str = Field(..., max_length=1000)
    comment_type: CommentType = "neutral"


class GetGroupStudentsRequest(BaseModel):
    """Запрос на получение студентов группы"""
    
    group_id: int = Field(..., gt=0)
    include_inactive: bool = False
    sort_by: Optional[str] = Field(None, pattern="^(name|score|attendance|last_seen)$")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$")


# ========== СТАТИСТИКА ==========

class CriterionAnalysis(BaseModel):
    """Анализ по критерию"""
    
    criterion_number: int = Field(..., ge=1, le=8)
    correct_count: int = 0
    incorrect_count: int = 0
    total_count: int = 0
    accuracy_percentage: float = 0.0


class StudentAnalyticsResponse(BaseModel):
    """Аналитика студента"""
    
    student_id: int
    criteria_analysis: List[CriterionAnalysis]
    overall_accuracy: float = 0.0
    total_questions: int = 0
    last_updated: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class GroupAnalyticsResponse(BaseModel):
    """Аналитика группы"""
    
    group_id: int
    average_score: float = 0.0
    attendance_rate: float = 0.0
    students_analytics: List[StudentAnalyticsResponse]
    criteria_averages: List[CriterionAnalysis]
    
    class Config:
        from_attributes = True


# ========== ОБНОВЛЕНИЯ ==========

class UpdateStudentStatusRequest(BaseModel):
    """Запрос на обновление статуса студента"""
    
    student_id: int = Field(..., gt=0)
    new_status: StudentStatus


class BulkUpdateCommentsRequest(BaseModel):
    """Массовое обновление комментариев"""
    
    comments: List[UpdateCommentRequest] = Field(..., max_items=50)


# ========== ФИЛЬТРЫ И ПОИСК ==========

class StudentFilters(BaseModel):
    """Фильтры для студентов"""
    
    status: Optional[StudentStatus] = None
    min_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    max_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    attendance_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    has_pending_tests: Optional[bool] = None
    last_seen_days: Optional[int] = Field(None, ge=0, le=365)


class SearchStudentsRequest(BaseModel):
    """Поиск студентов"""
    
    query: str = Field(..., min_length=1, max_length=100)
    group_id: Optional[int] = None
    filters: Optional[StudentFilters] = None
    limit: int = Field(20, le=100)


# ========== ОШИБКИ ==========

class TeacherErrorResponse(BaseModel):
    """Ошибка API преподавателя"""
    
    error: str
    detail: str
    status_code: int
    teacher_id: Optional[int] = None


# ========== ЗДОРОВЬЕ СЕРВИСА ==========

class TeacherAPIHealthResponse(BaseModel):
    """Ответ проверки здоровья API преподавателя"""
    
    status: str = "healthy"
    service: str = "teacher-api"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    active_teachers: int = 0
    total_groups: int = 0