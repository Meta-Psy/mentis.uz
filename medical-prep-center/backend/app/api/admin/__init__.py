from fastapi import APIRouter
from app.api.admin.user import router as users_router
from app.api.admin.academic import router as content_router  
from app.api.admin.group import router as groups_router
from app.api.admin.university import router as universities_router
from app.api.admin.statistic import router as statistics_router
from app.api.admin.materials import router as materials_router

admin_router = APIRouter(prefix="/admin", tags=["admin"])

admin_router.include_router(users_router, prefix="/users", tags=["admin-users"])
admin_router.include_router(content_router, prefix="/content", tags=["admin-content"])
admin_router.include_router(groups_router, prefix="/groups", tags=["admin-groups"])
admin_router.include_router(universities_router, prefix="/universities", tags=["admin-universities"])
admin_router.include_router(materials_router, prefix="/materials", tags=["admin-materials"])
admin_router.include_router(statistics_router, prefix="/statistics", tags=["admin-statistics"])
