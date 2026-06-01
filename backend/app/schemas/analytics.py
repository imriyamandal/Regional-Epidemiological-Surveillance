from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.database.models import AlertLevel, RiskLevel


class DashboardStats(BaseModel):
    total_cases: int
    active_alerts: int
    high_risk_areas: int
    prediction_accuracy: float
    diseases_monitored: int
    districts_tracked: int
    trend_change_percent: float


class DiseaseTrendPoint(BaseModel):
    date: str
    cases: int
    disease: str


class ForecastPoint(BaseModel):
    date: str
    predicted: float
    lower: Optional[float] = None
    upper: Optional[float] = None
    actual: Optional[float] = None


class ForecastResponse(BaseModel):
    disease: str
    district: str
    state: str
    horizon_months: int
    model_name: str
    points: list[ForecastPoint]
    confidence_level: float = 0.95


class RiskScoreItem(BaseModel):
    state: str
    district: str
    disease: str
    risk_level: RiskLevel
    risk_score: float
    predicted_cases: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class MapHotspot(BaseModel):
    state: str
    district: str
    latitude: float
    longitude: float
    case_count: int
    risk_level: RiskLevel
    risk_score: float
    disease: str


class ExplainabilityResponse(BaseModel):
    disease: str
    district: str
    prediction: float
    risk_level: RiskLevel
    top_features: list[dict[str, Any]]
    shap_summary: list[dict[str, Any]]
    shap_waterfall: list[dict[str, Any]]


class AlertResponse(BaseModel):
    id: int
    level: AlertLevel
    title: str
    message: str
    state: str
    district: str
    risk_score: float
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ClimateImpact(BaseModel):
    variable: str
    correlation: float
    impact_direction: str
    description: str


class ComparisonItem(BaseModel):
    name: str
    cases: int
    incidence_rate: float
    risk_score: float
