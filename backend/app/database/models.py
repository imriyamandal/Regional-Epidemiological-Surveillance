import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    HEALTH_OFFICER = "health_officer"


class RiskLevel(str, enum.Enum):
    SAFE = "safe"
    LOW = "low_risk"
    MEDIUM = "medium_risk"
    HIGH = "high_risk"
    CRITICAL = "critical_risk"


class AlertLevel(str, enum.Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.ANALYST)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    alerts: Mapped[list["Alert"]] = relationship(back_populates="user")
    reports: Mapped[list["Report"]] = relationship(back_populates="user")


class Disease(Base):
    __tablename__ = "diseases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_notifiable: Mapped[bool] = mapped_column(Boolean, default=True)

    outbreaks: Mapped[list["Outbreak"]] = relationship(back_populates="disease")
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="disease")


class Outbreak(Base):
    __tablename__ = "outbreaks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    disease_id: Mapped[int] = mapped_column(ForeignKey("diseases.id"), index=True)
    state: Mapped[str] = mapped_column(String(100), index=True)
    district: Mapped[str] = mapped_column(String(100), index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    case_count: Mapped[int] = mapped_column(Integer, default=0)
    death_count: Mapped[int] = mapped_column(Integer, default=0)
    population: Mapped[Optional[int]] = mapped_column(Integer)
    population_density: Mapped[Optional[float]] = mapped_column(Float)
    incidence_rate: Mapped[Optional[float]] = mapped_column(Float)
    report_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    month: Mapped[int] = mapped_column(Integer)
    quarter: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer, index=True)
    season: Mapped[str] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(50), default="IDSP")
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)

    disease: Mapped["Disease"] = relationship(back_populates="outbreaks")


class ClimateData(Base):
    __tablename__ = "climate_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(String(100), index=True)
    district: Mapped[str] = mapped_column(String(100), index=True)
    report_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    temperature: Mapped[Optional[float]] = mapped_column(Float)
    rainfall: Mapped[Optional[float]] = mapped_column(Float)
    humidity: Mapped[Optional[float]] = mapped_column(Float)
    precipitation: Mapped[Optional[float]] = mapped_column(Float)
    wind_speed: Mapped[Optional[float]] = mapped_column(Float)
    air_quality_index: Mapped[Optional[float]] = mapped_column(Float)
    leaf_area_index: Mapped[Optional[float]] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(50), default="ERA5")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    disease_id: Mapped[int] = mapped_column(ForeignKey("diseases.id"), index=True)
    state: Mapped[str] = mapped_column(String(100), index=True)
    district: Mapped[str] = mapped_column(String(100), index=True)
    horizon_months: Mapped[int] = mapped_column(Integer)
    predicted_cases: Mapped[float] = mapped_column(Float)
    confidence_lower: Mapped[Optional[float]] = mapped_column(Float)
    confidence_upper: Mapped[Optional[float]] = mapped_column(Float)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel))
    risk_score: Mapped[float] = mapped_column(Float)
    model_name: Mapped[str] = mapped_column(String(100))
    model_version: Mapped[str] = mapped_column(String(50))
    feature_importance: Mapped[Optional[dict]] = mapped_column(JSON)
    shap_values: Mapped[Optional[dict]] = mapped_column(JSON)
    prediction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    target_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    disease: Mapped["Disease"] = relationship(back_populates="predictions")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    disease_id: Mapped[Optional[int]] = mapped_column(ForeignKey("diseases.id"))
    state: Mapped[str] = mapped_column(String(100))
    district: Mapped[str] = mapped_column(String(100))
    level: Mapped[AlertLevel] = mapped_column(Enum(AlertLevel))
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    risk_score: Mapped[float] = mapped_column(Float)
    predicted_cases: Mapped[Optional[float]] = mapped_column(Float)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[Optional["User"]] = relationship(back_populates="alerts")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    report_type: Mapped[str] = mapped_column(String(50))
    content_json: Mapped[dict] = mapped_column(JSON)
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="reports")


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    version: Mapped[str] = mapped_column(String(50))
    model_type: Mapped[str] = mapped_column(String(50))
    metrics: Mapped[dict] = mapped_column(JSON)
    artifact_path: Mapped[str] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    mlflow_run_id: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
