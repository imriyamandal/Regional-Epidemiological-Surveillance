from typing import Annotated, Optional

import pandas as pd
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.models import Disease, Outbreak, User
from app.database.session import get_db
from app.schemas.analytics import ExplainabilityResponse
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/explainability", tags=["Explainable AI"])


@router.get("", response_model=ExplainabilityResponse)
async def explain(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    disease: str = Query("DENGUE"),
    district: str = Query("Pune"),
    state: Optional[str] = None,
):
    query = (
        select(Outbreak, Disease)
        .join(Disease, Outbreak.disease_id == Disease.id)
        .where(Disease.code == disease, Outbreak.district == district)
        .order_by(Outbreak.report_date.desc())
        .limit(24)
    )
    if state:
        query = query.where(Outbreak.state == state)
    result = await db.execute(query)
    rows = result.all()
    if not rows:
        features = pd.DataFrame([{"case_count": 50, "lag_1": 40, "rainfall": 120, "temperature": 28}])
    else:
        records = []
        for ob, _ in rows:
            records.append(
                {
                    "case_count": ob.case_count,
                    "lag_1": ob.case_count * 0.9,
                    "rainfall": 100,
                    "temperature": 28,
                    "rolling_mean_3": ob.case_count,
                    "growth_rate": 0.1,
                }
            )
        features = pd.DataFrame(records).tail(1)
    return PredictionService.explain_prediction(features, disease, district)
