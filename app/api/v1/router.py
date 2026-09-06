from __future__ import annotations
from fastapi import APIRouter
from app.config import settings
from app.api.v1.alerts import router as alerts_router
from app.api.v1.auth import router as auth_router
from app.api.v1.barangays import router as barangays_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.heatmap import router as heatmap_router
from app.api.v1.chat import router as chat_router
from app.api.v1.municipalities import router as municipalities_router
from app.api.v1.reports import router as reports_router
from app.api.v1.scanner import router as scanner_router
from app.api.v1.schools import router as schools_router
from app.api.v1.users import router as users_router
from app.api.v1.weather import router as weather_router

api_router = APIRouter(prefix=settings.API_V1_PREFIX)

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(reports_router)
api_router.include_router(scanner_router)
api_router.include_router(alerts_router)
api_router.include_router(weather_router)
api_router.include_router(heatmap_router)
api_router.include_router(barangays_router)
api_router.include_router(municipalities_router)
api_router.include_router(dashboard_router)
api_router.include_router(schools_router)
api_router.include_router(chat_router)

