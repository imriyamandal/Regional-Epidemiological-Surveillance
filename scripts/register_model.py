"""Register trained model metadata in the database."""

import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

env_path = BACKEND / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import joblib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.database.models import ModelRegistry

get_settings.cache_clear()
settings = get_settings()
engine = create_async_engine(settings.database_url, connect_args={"check_same_thread": False})
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

ARTIFACTS = BACKEND / "artifacts"


async def register():
    meta_path = ARTIFACTS / "model_meta.joblib"
    results_path = ARTIFACTS / "training_results.json"
    if not meta_path.exists():
        print("No model_meta.joblib — run ML pipeline first.")
        return

    meta = joblib.load(meta_path)
    results = json.loads(results_path.read_text()) if results_path.exists() else {}

    async with Session() as db:
        existing = await db.execute(
            select(ModelRegistry).where(ModelRegistry.name == meta.get("best_model_name", "ensemble"))
        )
        for row in existing.scalars().all():
            row.is_active = False

        db.add(
            ModelRegistry(
                name=meta.get("best_model_name", "stacking_ensemble"),
                version="1.0.0",
                model_type="classification",
                metrics={
                    "roc_auc": meta.get("best_roc_auc", 0),
                    "all_results": results,
                },
                artifact_path=str(ARTIFACTS / "best_model.joblib"),
                is_active=True,
                mlflow_run_id="local",
            )
        )
        await db.commit()
        print(f"Registered model: {meta.get('best_model_name')} (AUC={meta.get('best_roc_auc', 0):.4f})")


if __name__ == "__main__":
    asyncio.run(register())
