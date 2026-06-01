"""Seed PostgreSQL with surveillance data, predictions, and alerts."""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

# Load backend .env for database URL
env_path = BACKEND / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

get_settings.cache_clear()
settings = get_settings()
from app.database.base import Base
from app.database.models import Alert, AlertLevel, ClimateData, Disease, Outbreak, Prediction, RiskLevel
from app.services.alert_service import risk_to_alert_level

engine = create_async_engine(settings.database_url)
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def risk_from_cases(cases: int, pop: int) -> tuple[float, RiskLevel]:
    rate = cases / (pop / 100000 + 1)
    score = min(0.99, rate / 50)
    if score >= 0.85:
        return score, RiskLevel.CRITICAL
    if score >= 0.7:
        return score, RiskLevel.HIGH
    if score >= 0.5:
        return score, RiskLevel.MEDIUM
    if score >= 0.3:
        return score, RiskLevel.LOW
    return score, RiskLevel.SAFE


async def seed():
    sys.path.insert(0, str(ROOT))
    from ml.data.ingestion import generate_surveillance_dataset
    from ml.features.engineering import engineer_features

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    df = generate_surveillance_dataset()
    featured = engineer_features(df)

    async with Session() as db:
        diseases = {d.code: d.id for d in (await db.execute(select(Disease))).scalars().all()}
        if not diseases:
            print("Run backend first to create diseases")
            return

        count = 0
        for _, row in df.iterrows():
            code = row["disease_code"]
            if code not in diseases:
                continue
            dt = pd.Timestamp(row["report_date"]).to_pydatetime()
            ob = Outbreak(
                disease_id=diseases[code],
                state=row["state"],
                district=row["district"],
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                case_count=int(row["case_count"]),
                death_count=int(row["death_count"]),
                population=int(row["population"]),
                population_density=float(row["population_density"]),
                incidence_rate=float(row["case_count"]) / (row["population"] / 100000),
                report_date=dt,
                month=dt.month,
                quarter=(dt.month - 1) // 3 + 1,
                year=dt.year,
                season="monsoon" if 6 <= dt.month <= 9 else "other",
                source=row["source"],
            )
            db.add(ob)
            if count % 500 == 0:
                cd = ClimateData(
                    state=row["state"],
                    district=row["district"],
                    report_date=dt,
                    temperature=float(row["temperature"]),
                    rainfall=float(row["rainfall"]),
                    humidity=float(row["humidity"]),
                    precipitation=float(row["precipitation"]),
                    wind_speed=float(row["wind_speed"]),
                    air_quality_index=float(row["air_quality_index"]),
                    leaf_area_index=float(row["leaf_area_index"]),
                )
                db.add(cd)
            count += 1

        latest = featured.groupby(["state", "district", "disease_code"]).tail(1)
        for _, row in latest.iterrows():
            code = row["disease_code"]
            if code not in diseases:
                continue
            score, level = risk_from_cases(int(row["case_count"]), int(row["population"]))
            pred_cases = row["case_count"] * (1 + row.get("growth_rate", 0.1))
            target = pd.Timestamp(row["report_date"]) + pd.DateOffset(months=3)
            db.add(
                Prediction(
                    disease_id=diseases[code],
                    state=row["state"],
                    district=row["district"],
                    horizon_months=3,
                    predicted_cases=float(pred_cases),
                    confidence_lower=float(pred_cases * 0.8),
                    confidence_upper=float(pred_cases * 1.25),
                    risk_level=level,
                    risk_score=score,
                    model_name="stacking_ensemble",
                    model_version="1.0.0",
                    target_date=target.to_pydatetime(),
                )
            )
            alert_level = risk_to_alert_level(level, score)
            if alert_level in (AlertLevel.ORANGE, AlertLevel.RED, AlertLevel.YELLOW):
                db.add(
                    Alert(
                        disease_id=diseases[code],
                        state=row["state"],
                        district=row["district"],
                        level=alert_level,
                        title=f"{level.value.replace('_', ' ').title()} — {row['district']}",
                        message=f"Elevated {code} risk detected. Predicted cases: {pred_cases:.0f}",
                        risk_score=score,
                        predicted_cases=float(pred_cases),
                    )
                )

        await db.commit()
        print(f"Seeded {count} outbreaks")


if __name__ == "__main__":
    asyncio.run(seed())
