from fastapi import APIRouter

from app.api.v1 import admin, alerts, analytics, auth, explainability, reports

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(analytics.router)
api_router.include_router(alerts.router)
api_router.include_router(explainability.router)
api_router.include_router(reports.router)
api_router.include_router(admin.router)
