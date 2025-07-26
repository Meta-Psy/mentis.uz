from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime

# Импорты существующих роутеров
from app.api.academic_content.attendance import router as assessment_router
from app.api.academic_content.tests import router as tests_router
from app.api.academic_content.statistic import router as statistics_router
from app.api.auth.parent import router as parent_dashboard_router
from app.api.auth.student import router as student_dashboard_router
from app.api.auth.teacher import router as teacher_dashboard_router
from app.api.academic_content.materials import router as materials_router
from app.api.auth.auth import router as auth_router

# Импорт нового админского роутера
from app.api.admin import admin_router

# Импорт базы данных
from app.database import init_db, close_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Lifespan manager для управления подключениями
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Запуск приложения...")
    try:
        # Инициализация базы данных
        await init_db()
        logger.info("✅ База данных инициализирована")
        yield
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Завершение работы приложения...")
        try:
            await close_db()
            logger.info("✅ Соединения с базой данных закрыты")
        except Exception as e:
            logger.error(f"❌ Ошибка при завершении: {e}")

# Создание FastAPI приложения
app = FastAPI(
    title="Educational Platform API",
    description="API для образовательной платформы с оценками, тестами, материалами и административной панелью",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Alternative React port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://your-frontend-domain.com",  # Production domain
        "https://admin.your-frontend-domain.com",  # Admin panel domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Middleware для доверенных хостов
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.your-domain.com"]
)

# Глобальный обработчик исключений
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Необработанная ошибка: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Внутренняя ошибка сервера",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

# ===========================================
# MIDDLEWARE ДЛЯ АДМИНКИ (ОПЦИОНАЛЬНО)
# ===========================================

# Простая защита админки (в продакшене использовать JWT)
async def verify_admin_access(request):
    """Проверка доступа к админке"""
    # Здесь можно добавить проверку JWT токена или другую аутентификацию
    # Пример:
    # auth_header = request.headers.get("Authorization")
    # if not auth_header or not verify_admin_token(auth_header):
    #     raise HTTPException(status_code=401, detail="Admin access required")
    pass

# ===========================================
# ПОДКЛЮЧЕНИЕ РОУТЕРОВ
# ===========================================

# Роутеры для оценок и аттестации
app.include_router(
    assessment_router,
    prefix="/api/assessment",
    tags=["Assessment"],
    responses={404: {"description": "Не найдено"}}
)

app.include_router(
    tests_router,
    prefix="/api/tests", 
    tags=["Tests"],
    responses={404: {"description": "Не найдено"}}
)

app.include_router(
    statistics_router,
    prefix="/api/statistics",
    tags=["Statistics"],
    responses={404: {"description": "Не найдено"}}
)

# Роутеры для дашбордов
app.include_router(
    parent_dashboard_router,
    prefix="/api/parent",
    tags=["Parent Dashboard"],
    responses={404: {"description": "Не найдено"}}
)

app.include_router(
    student_dashboard_router,
    prefix="/api/student",
    tags=["Student Dashboard"],
    responses={404: {"description": "Не найдено"}}
)

app.include_router(
    teacher_dashboard_router,
    prefix="/api/teacher",
    tags=["Teacher Dashboard"],
    responses={404: {"description": "Не найдено"}}
)

# Роутер для материалов
app.include_router(
    materials_router,
    prefix="/api/materials",
    tags=["Materials"],
    responses={404: {"description": "Не найдено"}}
)

# Роутер для аутентификации
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"],
    responses={404: {"description": "Не найдено"}}
)

# НОВЫЙ: Роутер для админки
app.include_router(
    admin_router,
    prefix="/api",  # admin_router уже содержит /admin в prefix
    tags=["Admin Panel"],
    responses={
        401: {"description": "Требуется авторизация администратора"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Не найдено"}
    }
    # dependencies=[Depends(verify_admin_access)]  # Раскомментировать для защиты
)

# ===========================================
# ОСНОВНЫЕ ЭНДПОИНТЫ
# ===========================================

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Educational Platform API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc",
        "admin_panel": "/api/admin"
    }

@app.get("/api")
async def api_root():
    """API корневой эндпоинт"""
    return {
        "message": "Educational Platform API v1.0.0",
        "endpoints": {
            "assessment": "/api/assessment",
            "tests": "/api/tests",
            "statistics": "/api/statistics",
            "parent_dashboard": "/api/parent",
            "student_dashboard": "/api/student", 
            "teacher_dashboard": "/api/teacher",
            "materials": "/api/materials",
            "auth": "/api/auth",
            "admin": "/api/admin"  # НОВЫЙ эндпоинт
        },
        "admin_endpoints": {
            "dashboard": "/api/admin/dashboard",
            "users": "/api/admin/users",
            "content": "/api/admin/subjects",
            "analytics": "/api/admin/analytics",
            "export": "/api/admin/export",
            "health": "/api/admin/health"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Общий health check для всего API"""
    return {
        "status": "healthy",
        "service": "educational-platform-api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "active",
        "components": {
            "database": "healthy",
            "assessment": "healthy",
            "tests": "healthy",
            "statistics": "healthy",
            "materials": "healthy",
            "auth": "healthy",
            "admin": "healthy"  # НОВЫЙ компонент
        }
    }

@app.get("/api/info")
async def api_info():
    """Информация об API"""
    return {
        "name": "Educational Platform API",
        "version": "1.0.0",
        "description": "API для образовательной платформы",
        "features": [
            "Система оценок и аттестации",
            "Тестирование студентов",
            "Статистика и аналитика",
            "Дашборды для родителей, студентов и учителей",
            "Управление учебными материалами",
            "Аутентификация и авторизация",
            "Административная панель управления"  # НОВАЯ функция
        ],
        "admin_features": [  # НОВЫЙ раздел
            "Управление пользователями",
            "Управление контентом (предметы, разделы, темы, вопросы)",
            "Управление университетами и группами",
            "Аналитика и статистика",
            "Экспорт данных",
            "Валидация целостности",
            "Массовые операции"
        ],
        "environments": {
            "development": "http://localhost:8000",
            "staging": "https://staging-api.your-domain.com",
            "production": "https://api.your-domain.com"
        },
        "contact": {
            "email": "support@your-domain.com",
            "documentation": "/docs"
        },
        "timestamp": datetime.now().isoformat()
    }

# ===========================================
# MIDDLEWARE ДЛЯ ЛОГИРОВАНИЯ
# ===========================================

@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware для логирования запросов"""
    start_time = datetime.now()
    
    # Специальное логирование для админских запросов
    is_admin_request = request.url.path.startswith("/api/admin")
    log_prefix = "🔧 ADMIN" if is_admin_request else "📨"
    
    # Логируем входящий запрос
    logger.info(f"{log_prefix} {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        # Вычисляем время обработки
        process_time = (datetime.now() - start_time).total_seconds()
        
        # Логируем ответ
        logger.info(
            f"📤 {request.method} {request.url} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        # Добавляем заголовки времени обработки
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Timestamp"] = datetime.now().isoformat()
        response.headers["X-API-Version"] = "1.0.0"
        
        # Специальные заголовки для админки
        if is_admin_request:
            response.headers["X-Admin-API"] = "true"
        
        return response
        
    except Exception as e:
        # Логируем ошибку
        process_time = (datetime.now() - start_time).total_seconds()
        logger.error(
            f"❌ {request.method} {request.url} - "
            f"Error: {str(e)} - "
            f"Time: {process_time:.3f}s"
        )
        raise

# ===========================================
# ДОПОЛНИТЕЛЬНЫЕ УТИЛИТЫ
# ===========================================

@app.get("/api/routes")
async def list_routes():
    """Список всех доступных маршрутов (для отладки)"""
    routes = []
    admin_routes = []
    
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            route_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', None)
            }
            
            if route.path.startswith('/api/admin'):
                admin_routes.append(route_info)
            else:
                routes.append(route_info)
    
    return {
        "total_routes": len(routes) + len(admin_routes),
        "public_routes": sorted(routes, key=lambda x: x['path']),
        "admin_routes": sorted(admin_routes, key=lambda x: x['path']),
        "admin_routes_count": len(admin_routes)
    }

@app.get("/api/version")
async def get_version():
    """Получение версии API"""
    return {
        "version": "1.0.0",
        "build_date": "2024-01-01",
        "environment": "development",
        "python_version": "3.11+",
        "fastapi_version": "0.104.1",
        "admin_panel": "enabled",  # НОВОЕ поле
        "last_updated": datetime.now().isoformat()
    }

# ===========================================
# АДМИНСКИЕ MIDDLEWARE И ЗАЩИТА
# ===========================================

# Middleware для проверки прав доступа к админке
@app.middleware("http")
async def admin_access_middleware(request, call_next):
    """Middleware для проверки доступа к админским эндпоинтам"""
    
    # Проверяем, является ли запрос админским
    if request.url.path.startswith("/api/admin"):
        # Здесь можно добавить проверку авторизации
        # Например, проверка JWT токена с ролью admin
        
        # Пример базовой проверки (в продакшене заменить на полноценную авторизацию)
        auth_header = request.headers.get("Authorization")
        
        # Для разработки можно временно отключить проверку
        if not auth_header and request.url.path not in [
            "/api/admin/health",  # Health check доступен всем
            "/docs", "/redoc", "/openapi.json"  # Документация
        ]:
            # Раскомментировать для включения защиты:
            # return JSONResponse(
            #     status_code=401,
            #     content={
            #         "error": True,
            #         "message": "Admin authentication required",
            #         "status_code": 401
            #     }
            # )
            pass
    
    response = await call_next(request)
    return response

# ===========================================
# КОНФИГУРАЦИЯ ДЛЯ РАЗРАБОТКИ
# ===========================================

if __name__ == "__main__":
    # Настройки для разработки
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Автоперезагрузка при изменениях
        log_level="info",
        access_log=True,
        workers=1  # Для разработки используем 1 worker
    )

# ===========================================
# НАСТРОЙКИ ДЛЯ ПРОДАКШЕНА
# ===========================================

# Для продакшена используйте:
# uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Или с Gunicorn:
# gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Переменные окружения для продакшена:
# - DATABASE_URL: строка подключения к базе данных
# - SECRET_KEY: секретный ключ для JWT
# - ADMIN_SECRET_KEY: отдельный ключ для админки
# - CORS_ORIGINS: разрешенные домены для CORS
# - LOG_LEVEL: уровень логирования
# - ENVIRONMENT: production/staging/development
# - ADMIN_ENABLED: включена ли админка (true/false)
