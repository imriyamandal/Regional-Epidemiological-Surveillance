from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.database.models import Disease, ModelRegistry, Outbreak, User, UserRole
from app.database.session import get_db
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return list(result.scalars().all())


@router.get("/datasets/stats")
async def dataset_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
):
    outbreaks = await db.scalar(select(func.count(Outbreak.id))) or 0
    diseases = await db.scalar(select(func.count(Disease.id))) or 0
    return {
        "outbreak_records": outbreaks,
        "diseases": diseases,
        "sources": ["IDSP India", "WHO", "Open-Meteo Climate", "Census Population"],
    }


@router.get("/models")
async def list_models(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
):
    result = await db.execute(select(ModelRegistry).order_by(ModelRegistry.created_at.desc()))
    models = result.scalars().all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "version": m.version,
            "type": m.model_type,
            "metrics": m.metrics,
            "is_active": m.is_active,
            "mlflow_run_id": m.mlflow_run_id,
        }
        for m in models
    ]
