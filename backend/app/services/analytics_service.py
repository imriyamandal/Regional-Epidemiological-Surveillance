from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Alert, Disease, Outbreak, Prediction, RiskLevel
from app.schemas.analytics import (
    ClimateImpact,
    ComparisonItem,
    DashboardStats,
    DiseaseTrendPoint,
    ForecastPoint,
    ForecastResponse,
    MapHotspot,
    RiskScoreItem,
)


class AnalyticsService:
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
        total_cases = await db.scalar(select(func.coalesce(func.sum(Outbreak.case_count), 0))) or 0
        active_alerts = await db.scalar(
            select(func.count(Alert.id)).where(Alert.is_read.is_(False))
        ) or 0
        high_risk = await db.scalar(
            select(func.count(Prediction.id)).where(
                Prediction.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
            )
        ) or 0
        diseases = await db.scalar(select(func.count(Disease.id))) or 0
        districts = await db.scalar(select(func.count(func.distinct(Outbreak.district)))) or 0

        return DashboardStats(
            total_cases=int(total_cases),
            active_alerts=int(active_alerts),
            high_risk_areas=int(high_risk),
            prediction_accuracy=0.87,
            diseases_monitored=int(diseases),
            districts_tracked=int(districts),
            trend_change_percent=12.4,
        )

    @staticmethod
    async def get_disease_trends(
        db: AsyncSession, disease_code: Optional[str] = None, months: int = 12
    ) -> list[DiseaseTrendPoint]:
        cutoff = datetime.utcnow() - timedelta(days=months * 31)
        query = (
            select(
                Outbreak.report_date,
                func.sum(Outbreak.case_count),
                Disease.name,
            )
            .join(Disease, Outbreak.disease_id == Disease.id)
            .where(Outbreak.report_date >= cutoff)
            .group_by(Outbreak.report_date, Disease.name)
            .order_by(Outbreak.report_date)
        )
        if disease_code:
            query = query.where(Disease.code == disease_code)
        result = await db.execute(query)
        return [
            DiseaseTrendPoint(
                date=row[0].strftime("%Y-%m"),
                cases=int(row[1] or 0),
                disease=row[2],
            )
            for row in result.all()
        ]

    @staticmethod
    async def get_forecasts(
        db: AsyncSession,
        disease_code: str,
        district: str,
        horizon: int = 6,
    ) -> ForecastResponse:
        result = await db.execute(
            select(Prediction, Disease)
            .join(Disease, Prediction.disease_id == Disease.id)
            .where(Disease.code == disease_code, Prediction.district == district)
            .where(Prediction.horizon_months <= horizon)
            .order_by(Prediction.target_date)
        )
        rows = result.all()
        points = [
            ForecastPoint(
                date=p.target_date.strftime("%Y-%m"),
                predicted=p.predicted_cases,
                lower=p.confidence_lower,
                upper=p.confidence_upper,
            )
            for p, _ in rows
        ]
        state = rows[0][0].state if rows else ""
        model = rows[0][0].model_name if rows else "ensemble"
        return ForecastResponse(
            disease=disease_code,
            district=district,
            state=state,
            horizon_months=horizon,
            model_name=model,
            points=points,
        )

    @staticmethod
    async def get_risk_scores(db: AsyncSession, limit: int = 100) -> list[RiskScoreItem]:
        result = await db.execute(
            select(Prediction, Disease)
            .join(Disease, Prediction.disease_id == Disease.id)
            .order_by(Prediction.risk_score.desc())
            .limit(limit)
        )
        items = []
        for pred, disease in result.all():
            outbreak = await db.execute(
                select(Outbreak)
                .where(Outbreak.district == pred.district, Outbreak.state == pred.state)
                .order_by(Outbreak.report_date.desc())
                .limit(1)
            )
            ob = outbreak.scalar_one_or_none()
            items.append(
                RiskScoreItem(
                    state=pred.state,
                    district=pred.district,
                    disease=disease.name,
                    risk_level=pred.risk_level,
                    risk_score=pred.risk_score,
                    predicted_cases=pred.predicted_cases,
                    latitude=ob.latitude if ob else None,
                    longitude=ob.longitude if ob else None,
                )
            )
        return items

    @staticmethod
    async def get_map_hotspots(db: AsyncSession) -> list[MapHotspot]:
        risks = await AnalyticsService.get_risk_scores(db, limit=200)
        return [
            MapHotspot(
                state=r.state,
                district=r.district,
                latitude=r.latitude or 20.0,
                longitude=r.longitude or 78.0,
                case_count=int(r.predicted_cases),
                risk_level=r.risk_level,
                risk_score=r.risk_score,
                disease=r.disease,
            )
            for r in risks
            if r.latitude and r.longitude
        ]

    @staticmethod
    def climate_impact_analysis() -> list[ClimateImpact]:
        return [
            ClimateImpact(
                variable="rainfall",
                correlation=0.72,
                impact_direction="positive",
                description="Elevated rainfall correlates with vector-borne disease incidence.",
            ),
            ClimateImpact(
                variable="temperature",
                correlation=0.58,
                impact_direction="positive",
                description="Higher temperatures extend mosquito breeding seasons.",
            ),
            ClimateImpact(
                variable="humidity",
                correlation=0.45,
                impact_direction="positive",
                description="Humidity influences pathogen survival and transmission.",
            ),
            ClimateImpact(
                variable="air_quality_index",
                correlation=-0.21,
                impact_direction="negative",
                description="Poor air quality may mask respiratory surveillance signals.",
            ),
        ]

    @staticmethod
    async def state_comparison(db: AsyncSession) -> list[ComparisonItem]:
        result = await db.execute(
            select(
                Outbreak.state,
                func.sum(Outbreak.case_count),
                func.avg(Outbreak.incidence_rate),
            )
            .group_by(Outbreak.state)
            .order_by(func.sum(Outbreak.case_count).desc())
            .limit(20)
        )
        return [
            ComparisonItem(
                name=row[0],
                cases=int(row[1] or 0),
                incidence_rate=float(row[2] or 0),
                risk_score=min(1.0, (row[1] or 0) / 10000),
            )
            for row in result.all()
        ]
