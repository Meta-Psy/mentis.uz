from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime

# ========== ТИПЫ И КОНСТАНТЫ ==========

SubjectName = Literal["chemistry", "biology", "химия", "биология"]
StatisticType = Literal["current_grades", "tests", "dtm", "section_exams", "block_exams"]
TableType = Literal["all_groups_average", "my_group_average", "dtm_all_time", "dtm_last_month"]
MetricPeriod = Literal["monthly", "weekly", "daily"]

# ========== БАЗОВЫЕ МОДЕЛИ ==========

class GradePoint(BaseModel):
    """Точка данных для графика оценок"""
    month: str
    value: float
    
    class Config:
        from_attributes = True


class StudentRankingInfo(BaseModel):
    """Информация о студенте для рейтинга"""
    student_id: int
    name: str = Field(alias="full_name")
    group_id: int
    group_name: Optional[str] = None
    
    # Оценки
    chemistry_avg: Optional[float] = None
    biology_avg: Optional[float] = None
    overall_avg: Optional[float] = None
    
    # ДТМ баллы
    chemistry_dtm: Optional[float] = None
    biology_dtm: Optional[float] = None
    general_dtm: Optional[float] = None
    total_dtm: Optional[float] = None
    
    # Последние ДТМ результаты
    last_chemistry_dtm: Optional[float] = None
    last_biology_dtm: Optional[float] = None
    last_general_dtm: Optional[float] = None
    last_total_dtm: Optional[float] = None
    
    # Рейтинг
    rank: int = 0
    
    class Config:
        from_attributes = True
        populate_by_name = True


class SubjectStatistics(BaseModel):
    """Статистика по предмету"""
    subject_id: int
    subject_name: str
    
    # Графики данных
    current_grades: List[GradePoint] = Field(default_factory=list)
    tests: List[GradePoint] = Field(default_factory=list)
    dtm: List[GradePoint] = Field(default_factory=list)
    section_exams: List[GradePoint] = Field(default_factory=list)
    block_exams: List[GradePoint] = Field(default_factory=list)
    
    # Средние значения
    avg_current_grade: float = 0.0
    avg_test_score: float = 0.0
    avg_dtm_score: float = 0.0
    avg_section_score: float = 0.0
    avg_block_score: float = 0.0
    
    class Config:
        from_attributes = True


class OverallStatistics(BaseModel):
    """Общая статистика студента"""
    student_id: int
    
    # Общие показатели
    total_subjects: int = 0
    completed_tests: int = 0
    pending_tests: int = 0
    overdue_tests: int = 0
    
    # Средние баллы
    overall_average: float = 0.0
    chemistry_average: float = 0.0
    biology_average: float = 0.0
    
    # ДТМ статистика
    total_dtm_attempts: int = 0
    best_dtm_score: float = 0.0
    latest_dtm_score: float = 0.0
    
    # Посещаемость
    total_lessons: int = 0
    attended_lessons: int = 0
    attendance_rate: float = 0.0
    
    class Config:
        from_attributes = True


class TournamentTable(BaseModel):
    """Турнирная таблица"""
    table_type: TableType
    title: str
    students: List[StudentRankingInfo]
    current_student_rank: int = 0
    total_participants: int = 0
    
    class Config:
        from_attributes = True


# ========== ОТВЕТЫ API ==========

class StudentStatisticsResponse(BaseModel):
    """Полная статистика студента"""
    student_id: int
    student_name: str
    group_id: int
    group_name: str
    
    # Статистика по предметам
    chemistry: SubjectStatistics
    biology: SubjectStatistics
    
    # Общая статистика
    overall: OverallStatistics
    
    # Турнирные таблицы
    tournament_tables: List[TournamentTable] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class SubjectProgressResponse(BaseModel):
    """Прогресс по конкретному предмету"""
    subject_id: int
    subject_name: str
    student_id: int
    
    # Данные для графика
    progress_data: Dict[str, List[GradePoint]]
    
    # Сводная информация
    current_average: float = 0.0
    improvement_trend: float = 0.0  # положительное значение = улучшение
    last_month_average: float = 0.0
    
    class Config:
        from_attributes = True


class RankingResponse(BaseModel):
    """Ответ с рейтингом студентов"""
    table_type: TableType
    title: str
    students: List[StudentRankingInfo]
    current_student: Optional[StudentRankingInfo] = None
    current_student_rank: int = 0
    total_participants: int = 0
    group_filter: Optional[int] = None
    
    class Config:
        from_attributes = True


# ========== ЗАПРОСЫ ==========

class StatisticsRequest(BaseModel):
    """Запрос статистики студента"""
    student_id: int = Field(..., gt=0, description="ID студента")
    period: MetricPeriod = Field(default="monthly", description="Период для статистики")
    include_tournaments: bool = Field(default=True, description="Включить турнирные таблицы")


class SubjectProgressRequest(BaseModel):
    """Запрос прогресса по предмету"""
    student_id: int = Field(..., gt=0, description="ID студента")
    subject_name: SubjectName = Field(..., description="Название предмета")
    metric_type: StatisticType = Field(default="current_grades", description="Тип метрики")
    period: MetricPeriod = Field(default="monthly", description="Период")


class RankingRequest(BaseModel):
    """Запрос рейтинга"""
    table_type: TableType = Field(..., description="Тип турнирной таблицы")
    student_id: int = Field(..., gt=0, description="ID текущего студента")
    group_id: Optional[int] = Field(None, description="Фильтр по группе")
    limit: int = Field(default=50, le=200, description="Максимальное количество записей")


# ========== СОЗДАНИЕ/ОБНОВЛЕНИЕ ==========

class DTMResultCreate(BaseModel):
    """Создание результата ДТМ"""
    student_id: int = Field(..., gt=0)
    subject_id: int = Field(..., gt=0)
    common_subject_correct_answers: float = Field(..., ge=0, le=189)
    second_subject_correct_answers: float = Field(..., ge=0, le=189) 
    first_subject_correct_answers: float = Field(..., ge=0, le=189)
    total_correct_answers: float = Field(..., ge=0, le=189)
    exam_date: Optional[datetime] = None
    category_correct: Optional[List[int]] = Field(default_factory=list)
    category_mistake: Optional[List[int]] = Field(default_factory=list)
    attempt_number: Optional[int] = None


class CurrentRatingCreate(BaseModel):
    """Создание текущей оценки"""
    student_id: int = Field(..., gt=0)
    subject_id: int = Field(..., gt=0)
    topic_id: int = Field(..., gt=0)
    current_correct_answers: float = Field(..., ge=0)
    second_current_correct_answers: float = Field(..., ge=0)


# ========== СТАТИСТИКА И АНАЛИТИКА ==========

class TrendAnalysis(BaseModel):
    """Анализ тенденций"""
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    trend: Literal["improving", "declining", "stable"]
    
    class Config:
        from_attributes = True


class PerformanceInsights(BaseModel):
    """Аналитические выводы о производительности"""
    student_id: int
    
    # Сильные стороны
    strengths: List[str] = Field(default_factory=list)
    
    # Области для улучшения
    areas_for_improvement: List[str] = Field(default_factory=list)
    
    # Рекомендации
    recommendations: List[str] = Field(default_factory=list)
    
    # Тренды
    trends: List[TrendAnalysis] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class DetailedStatisticsResponse(BaseModel):
    """Детальная статистика с аналитикой"""
    student_statistics: StudentStatisticsResponse
    performance_insights: PerformanceInsights
    comparison_data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


# ========== ОШИБКИ ==========

class StatisticsError(BaseModel):
    """Ошибка статистики"""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ValidationErrorDetail(BaseModel):
    """Детали ошибки валидации"""
    field: str
    message: str
    value: Any


class ValidationErrorResponse(BaseModel):
    """Ответ с ошибками валидации"""
    detail: List[ValidationErrorDetail]


# ========== УТИЛИТЫ ==========

class DateRange(BaseModel):
    """Диапазон дат"""
    start_date: datetime
    end_date: datetime
    
    class Config:
        from_attributes = True


class StatisticsFilter(BaseModel):
    """Фильтр для статистики"""
    date_range: Optional[DateRange] = None
    subject_ids: Optional[List[int]] = None
    group_id: Optional[int] = None
    metric_types: Optional[List[StatisticType]] = None
    
    class Config:
        from_attributes = True


# ========== ЗДОРОВЬЕ СЕРВИСА ==========

class StatisticsHealthResponse(BaseModel):
    """Проверка здоровья сервиса статистики"""
    status: str = "healthy"
    service: str = "statistics-api"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    active_calculations: int = 0
    cache_status: str = "operational"
    
    class Config:
        from_attributes = True