from fastapi import APIRouter
from app.api.v1.routers import (
    auth,
    students,
    teachers,
    admins,
    parents,
    subjects,
    tests,
    materials,
    statistics,
    dashboard
)

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# User management routes
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
api_router.include_router(admins.router, prefix="/admins", tags=["admins"])
api_router.include_router(parents.router, prefix="/parents", tags=["parents"])

# Academic content routes
api_router.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])

# Analytics and reporting routes
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])