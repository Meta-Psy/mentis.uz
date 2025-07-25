from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime, date

# ========== ТИПЫ И КОНСТАНТЫ ==========

AttendanceStatus = Literal["present", "absent", "late"]
CommentType = Literal["positive", "negative", "neutral"]
UserRole = Literal["student", "teacher", "admin", "parent"]
StudentStatus = Literal["active", "inactive"]

# ========== БАЗОВЫЕ МОДЕЛИ ==========

class AttendanceRecord(BaseModel):
    """Запись о посещаемости"""
    attendance_id: int
    student_id: int
    lesson_date_time: datetime
    att_status: AttendanceStatus
    subject_id: int
    topic_id: int
    excuse_reason: Optional[str] = None
    extra_lesson: Optional[str] = None
    
    class Config:
        from_attributes = True


class CommentRecord(BaseModel):
    """Комментарий учителя"""
    comment_id: int
    teacher_id: int
    student_id: int
    comment_text: str
    comment_date: datetime
    comment_type: CommentType
    
    class Config:
        from_attributes = True


class GradeRecord(BaseModel):
    """Оценка студента"""
    score: float
    max_score: float
    percentage: float
    exam_date: datetime
    exam_type: str
    subject_name: str
    
    @property
    def formatted_score(self) -> str:
        return f"{self.score}/{self.max_score}"
    
    class Config:
        from_attributes = True


class SubjectGrades(BaseModel):
    """Оценки по предмету"""
    subject_name: str
    average_score: float
    total_assessments: int
    passed_assessments: int
    failed_assessments: int
    status: Literal["отлично", "хорошо", "удовлетворительно", "плохо"]
    
    # Детализация по типам оценок
    polls_score: float = 0.0  # Опросы
    tests_score: float = 0.0  # Тесты
    control_works_score: float = 0.0  # Контрольные работы
    
    polls_total: int = 0
    tests_total: int = 0
    control_works_total: int = 0
    
    class Config:
        from_attributes = True


class StudentInfo(BaseModel):
    """Информация о студенте"""
    student_id: int
    name: str
    surname: str
    photo: Optional[str] = None
    direction: str
    goal: Optional[str] = None
    group_id: Optional[int] = None
    
    # Дополнительная информация
    hobby: Optional[str] = None
    sex: Optional[str] = None
    address: Optional[str] = None
    birthday: Optional[date] = None
    
    class Config:
        from_attributes = True


class TeacherInfo(BaseModel):
    """Информация об учителе"""
    teacher_id: int
    name: str
    surname: str
    subjects: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


# ========== СТАТИСТИКА ПОСЕЩАЕМОСТИ ==========

class AttendanceStatistics(BaseModel):
    """Статистика посещаемости"""
    student_id: int
    subject_id: Optional[int] = None
    total_lessons: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_rate: float
    
    class Config:
        from_attributes = True


class DisciplineStatistics(BaseModel):
    """Статистика дисциплины"""
    student_id: int
    total_absences: int
    total_lessons: int
    missed_homeworks: int
    total_homeworks: int
    missed_polls: int
    total_polls: int
    teacher_remarks: int
    status: Literal["отлично", "хорошо", "удовлетворительно", "плохо"]
    
    @property
    def absence_percentage(self) -> float:
        if self.total_lessons == 0:
            return 0.0
        return (self.total_absences / self.total_lessons) * 100
    
    @property
    def homework_completion_rate(self) -> float:
        if self.total_homeworks == 0:
            return 100.0
        completed = self.total_homeworks - self.missed_homeworks
        return (completed / self.total_homeworks) * 100
    
    class Config:
        from_attributes = True


# ========== DTM И ЭКЗАМЕНЫ ==========

class DtmScore(BaseModel):
    """DTM балл"""
    current_score: float
    max_score: float = 189.0
    required_score: float
    exam_date: Optional[datetime] = None
    
    @property
    def formatted_current(self) -> str:
        return f"{self.current_score}/{self.max_score}"
    
    @property
    def formatted_required(self) -> str:
        return f"{self.required_score}/{self.max_score}"
    
    @property
    def is_passing(self) -> bool:
        return self.current_score >= self.required_score
    
    class Config:
        from_attributes = True


class ExamStatistics(BaseModel):
    """Статистика экзаменов"""
    student_id: int
    
    # Последние результаты
    last_monthly_exam: Optional[GradeRecord] = None
    last_final_control: Optional[GradeRecord] = None
    last_intermediate_control: Optional[GradeRecord] = None
    
    # Общая статистика
    total_exams: int = 0
    passed_exams: int = 0
    average_score: float = 0.0
    status: Literal["отлично", "хорошо", "удовлетворительно", "плохо"]
    
    class Config:
        from_attributes = True


class AdmissionChance(BaseModel):
    """Шанс поступления"""
    student_id: int
    probability_percentage: float
    target_university: Optional[str] = None
    current_score: float
    required_score: float
    recommendations: List[str] = Field(default_factory=list)
    
    @property
    def status_text(self) -> str:
        if self.probability_percentage >= 80:
            return "Высокий шанс"
        elif self.probability_percentage >= 60:
            return "Средний шанс"
        elif self.probability_percentage >= 40:
            return "Низкий шанс"
        else:
            return "Очень низкий шанс"
    
    class Config:
        from_attributes = True


# ========== РАСПИСАНИЕ ==========

class ScheduleItem(BaseModel):
    """Элемент расписания"""
    subject_name: str
    days: List[str]  # ["Пн", "Ср", "Пт"]
    time: str  # "16:00-17:30"
    teacher_name: Optional[str] = None
    
    @property
    def formatted_schedule(self) -> str:
        days_str = ", ".join(self.days)
        return f"{days_str} - {self.time}"
    
    class Config:
        from_attributes = True


class StudentSchedule(BaseModel):
    """Расписание студента"""
    student_id: int
    chemistry_schedule: Optional[ScheduleItem] = None
    biology_schedule: Optional[ScheduleItem] = None
    
    class Config:
        from_attributes = True


# ========== ОСНОВНОЙ ОТВЕТ ==========

class ParentStatisticsResponse(BaseModel):
    """Основной ответ статистики для родителей"""
    
    # Информация о студенте
    student_info: StudentInfo
    
    # Расписание
    schedule: StudentSchedule
    
    # DTM баллы
    dtm_score: DtmScore
    
    # Успеваемость
    performance: Dict[str, SubjectGrades]
    overall_performance_status: Literal["отлично", "хорошо", "удовлетворительно", "плохо"]
    
    # Дисциплина
    discipline: DisciplineStatistics
    
    # Экзамены
    exams: ExamStatistics
    
    # Шанс поступления
    admission_chance: AdmissionChance
    
    # Последние комментарии
    recent_comments: List[CommentRecord] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


# ========== ЗАПРОСЫ ==========

class ParentStatisticsRequest(BaseModel):
    """Запрос статистики для родителей"""
    student_id: int = Field(..., gt=0, description="ID студента")
    include_comments: bool = Field(default=True, description="Включить комментарии")
    comments_limit: int = Field(default=5, le=20, description="Лимит комментариев")


class AttendanceFilterRequest(BaseModel):
    """Фильтр для посещаемости"""
    student_id: int = Field(..., gt=0)
    subject_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class GradesFilterRequest(BaseModel):
    """Фильтр для оценок"""
    student_id: int = Field(..., gt=0)
    subject_id: Optional[int] = None
    exam_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ========== ДЕТАЛЬНЫЕ ОТВЕТЫ ==========

class DetailedPerformanceResponse(BaseModel):
    """Детальная информация об успеваемости"""
    student_id: int
    subjects: List[SubjectGrades]
    recent_grades: List[GradeRecord]
    grade_trends: Dict[str, List[float]]  # subject_name -> [scores]
    
    class Config:
        from_attributes = True


class DetailedDisciplineResponse(BaseModel):
    """Детальная информация о дисциплине"""
    student_id: int
    attendance_records: List[AttendanceRecord]
    attendance_statistics: AttendanceStatistics
    missed_assignments: List[Dict[str, Any]]
    teacher_comments: List[CommentRecord]
    
    class Config:
        from_attributes = True


class DetailedExamsResponse(BaseModel):
    """Детальная информация об экзаменах"""
    student_id: int
    dtm_exams: List[GradeRecord]
    section_exams: List[GradeRecord]
    block_exams: List[GradeRecord]
    module_exams: List[GradeRecord]
    exam_trends: Dict[str, List[float]]
    
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

class ParentStatisticsHealthResponse(BaseModel):
    """Ответ проверки здоровья сервиса родительской статистики"""
    status: str = "healthy"
    service: str = "parent-statistics-api"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    active_students: int = 0


# ========== УВЕДОМЛЕНИЯ ==========

class NotificationItem(BaseModel):
    """Уведомление для родителей"""
    notification_id: str
    type: Literal["warning", "info", "success", "error"]
    title: str
    message: str
    created_at: datetime
    is_read: bool = False
    priority: Literal["low", "medium", "high"] = "medium"
    
    class Config:
        from_attributes = True


class ParentNotificationsResponse(BaseModel):
    """Ответ с уведомлениями"""
    student_id: int
    notifications: List[NotificationItem]
    unread_count: int
    
    class Config:
        from_attributes = True