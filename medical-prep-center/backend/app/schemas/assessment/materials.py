from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime

# ========== ТИПЫ И КОНСТАНТЫ ==========

SubjectName = Literal["chemistry", "biology", "химия", "биология"]
FileType = Literal["book", "test_book"]
SearchResultType = Literal["topic", "section", "file"]
Theme = Literal["light", "dark"]
Language = Literal["ru", "en"]

# ========== БАЗОВЫЕ МОДЕЛИ ==========


class DownloadableFileResponse(BaseModel):
    id: int = Field(..., alias="file_id")
    title: str
    author: str
    size: str = Field(..., alias="file_size")
    format: str = Field(default="PDF", alias="file_format")
    download_url: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True
        field_serialization_alias_generator = None


class TopicResponse(BaseModel):
    """Модель для темы в разделе"""

    id: int = Field(alias="topic_id")
    title: str = Field(alias="name")
    homework: List[str] = Field(default_factory=list)
    videoUrl: str = Field(
        default="https://www.youtube.com/embed/dQw4w9WgXcQ", alias="video_url"
    )
    testId: int = Field(alias="test_id")
    block_name: Optional[str] = None

    def __init__(self, **data):
        # Преобразуем homework из строки в список
        if "homework" in data and isinstance(data["homework"], str):
            data["homework"] = data["homework"].split("\n") if data["homework"] else []

        # Генерируем testId если его нет
        if "test_id" not in data and "testId" not in data and "topic_id" in data:
            data["testId"] = data["topic_id"] + 100

        super().__init__(**data)

    class Config:
        from_attributes = True
        populate_by_name = True


class SectionResponse(BaseModel):
    """Модель для раздела (отображается как модуль на фронтенде)"""

    id: int = Field(alias="section_id")
    name: str
    description: Optional[str] = None
    books: List[DownloadableFileResponse] = Field(default_factory=list)
    testBooks: List[DownloadableFileResponse] = Field(default_factory=list)
    topics: List[TopicResponse] = Field(default_factory=list)

    def __init__(self, **data):
        # Форматируем название как "Модуль X" если есть order_number
        if "order_number" in data and data["order_number"]:
            data["name"] = f"Модуль {data['order_number']}"
        super().__init__(**data)

    class Config:
        from_attributes = True
        populate_by_name = True


class MaterialsSubjectResponse(BaseModel):
    """Модель для материалов предмета"""

    modules: List[SectionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
        populate_by_name = True


# ========== ОТВЕТЫ API ==========


class SubjectMaterialsResponse(BaseModel):
    """Ответ API для материалов предмета"""

    materials: Dict[str, MaterialsSubjectResponse]

    class Config:
        from_attributes = True


class TopicDetailResponse(BaseModel):
    """Расширенная информация о теме"""

    topic_id: int = Field(alias="id")
    title: str = Field(alias="topic_name")
    homework: List[str] = Field(default_factory=list)
    number: Optional[int] = Field(alias="topic_number")
    additional_material: Optional[str] = None
    video_url: str = Field(default="https://www.youtube.com/embed/dQw4w9WgXcQ")
    test_id: int = Field(alias="testId")
    block_name: Optional[str] = None
    section_name: Optional[str] = None
    subject_name: Optional[str] = None
    section_id: Optional[int] = None
    subject_id: Optional[int] = None
    questions_count: int = 0
    tests_count: int = 0
    tests: List[Dict[str, Any]] = Field(default_factory=list)

    def __init__(self, **data):
        # Преобразуем homework из строки в список
        if "homework" in data and isinstance(data["homework"], str):
            data["homework"] = data["homework"].split("\n") if data["homework"] else []

        # Генерируем test_id если его нет
        if "test_id" not in data and "testId" not in data and "topic_id" in data:
            data["test_id"] = data["topic_id"] + 100

        super().__init__(**data)

    class Config:
        from_attributes = True
        populate_by_name = True


# ========== ЗАПРОСЫ ==========


class SubjectMaterialsRequest(BaseModel):
    """Запрос материалов по предмету"""

    subject_name: SubjectName = Field(
        ..., description="Название предмета (химия/биология/chemistry/biology)"
    )


class SearchRequest(BaseModel):
    """Запрос поиска по материалам"""

    query: str = Field(..., min_length=1, max_length=100)
    subject_filter: Optional[str] = None
    section_filter: Optional[int] = None
    limit: int = Field(default=20, le=100)


class SearchResult(BaseModel):
    """Результат поиска"""

    type: SearchResultType  # "topic", "section", "file"
    id: int
    title: str
    description: Optional[str] = None
    subject_name: str
    section_name: Optional[str] = None


# ========== СОЗДАНИЕ/ОБНОВЛЕНИЕ ==========
class MaterialsResponseModel(BaseModel):
    """Модель ответа API для материалов"""
    
    materials: Dict[str, MaterialsSubjectResponse]
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "materials": {
                    "chemistry": {
                        "modules": [
                            {
                                "id": 1,
                                "name": "Модуль 1",
                                "books": [],
                                "testBooks": [],
                                "topics": []
                            }
                        ]
                    }
                }
            }
        }

class MaterialFileCreate(BaseModel):
    """Модель для создания файла материала"""

    title: str = Field(..., min_length=1, max_length=300)
    author: str = Field(..., min_length=1, max_length=200)
    size: str = Field(..., max_length=50)
    format: str = Field(default="PDF", max_length=10)
    file_type: FileType = Field(..., description="book или test_book")
    url: Optional[str] = Field(None, max_length=500)


class TopicCreate(BaseModel):
    """Модель для создания темы"""

    block_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=200)
    homework: Optional[str] = None
    number: Optional[int] = None
    additional_material: Optional[str] = None
    video_url: Optional[str] = None


class TopicUpdate(BaseModel):
    """Модель для обновления темы"""

    block_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    homework: Optional[str] = None
    number: Optional[int] = None
    additional_material: Optional[str] = None
    video_url: Optional[str] = None


# ========== СТАТИСТИКА ==========


class MaterialsStatistics(BaseModel):
    """Статистика по материалам"""

    total_subjects: int
    total_sections: int
    total_topics: int
    total_files: int
    subjects_breakdown: Dict[str, int]  # название предмета -> количество разделов


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


# ========== ПОЛЬЗОВАТЕЛЬСКИЕ НАСТРОЙКИ ==========


class UIState(BaseModel):
    """Состояние интерфейса пользователя"""

    selectedSubject: str = "chemistry"
    selectedModule: Optional[Union[int, str]] = None
    expandedSections: Dict[str, bool] = Field(default_factory=dict)
    theme: Theme = "light"
    language: Language = "ru"


class UserPreferences(BaseModel):
    """Пользовательские настройки"""

    theme: Theme = Field(default="light")
    language: Language = Field(default="ru")
    autoplay: bool = False
    notifications: bool = True
    cacheEnabled: bool = True


# ========== ПРОГРЕСС ==========


class HomeworkItem(BaseModel):
    """Элемент домашнего задания"""

    task_number: int
    description: str
    completed: bool = False


class TestInfo(BaseModel):
    """Информация о тесте"""

    test_id: int
    topic_id: int
    questions_count: int
    time_limit: Optional[int] = None  # в минутах
    attempts_allowed: int = 1
    passing_score: float = Field(default=0.6, ge=0.0, le=1.0)  # 60%


class UserProgress(BaseModel):
    """Прогресс пользователя"""

    completedTopics: List[int] = Field(default_factory=list)
    currentTopic: Optional[int] = None
    testResults: Dict[str, Any] = Field(default_factory=dict)
    totalProgress: float = Field(default=0.0, ge=0.0, le=1.0)


# ========== ЗДОРОВЬЕ СЕРВИСА ==========


class HealthCheckResponse(BaseModel):
    """Ответ проверки здоровья сервиса"""

    status: str = "healthy"
    service: str = "materials-api"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
