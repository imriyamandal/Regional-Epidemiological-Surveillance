from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.schemas.analytics import (
    ClimateImpact,
    ComparisonItem,
    DashboardStats,
    DiseaseTrendPoint,
    ForecastResponse,
    MapHotspot,
    RiskScoreItem,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    return await AnalyticsService.get_dashboard_stats(db)


@router.get("/trends", response_model=list[DiseaseTrendPoint])
async def trends(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    disease: Optional[str] = None,
    months: int = Query(12, ge=1, le=60),
):
    return await AnalyticsService.get_disease_trends(db, disease, months)


@router.get("/forecast", response_model=ForecastResponse)
async def forecast(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    disease: str = "DENGUE",
    district: str = "Pune",
    horizon: int = Query(6, ge=1, le=12),
):
    return await AnalyticsService.get_forecasts(db, disease, district, horizon)


@router.get("/risk", response_model=list[RiskScoreItem])
async def risk_scores(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    limit: int = Query(100, ge=1, le=500),
):
    return await AnalyticsService.get_risk_scores(db, limit)


@router.get("/map/hotspots", response_model=list[MapHotspot])
async def map_hotspots(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    return await AnalyticsService.get_map_hotspots(db)


@router.get("/climate-impact", response_model=list[ClimateImpact])
async def climate_impact(_: Annotated[User, Depends(get_current_user)]):
    return AnalyticsService.climate_impact_analysis()


@router.get("/compare/states", response_model=list[ComparisonItem])
async def compare_states(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    return await AnalyticsService.state_comparison(db)
