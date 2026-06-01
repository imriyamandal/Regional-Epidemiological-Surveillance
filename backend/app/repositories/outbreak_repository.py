from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Disease, Outbreak


class OutbreakRepository:
    @staticmethod
    async def total_cases(db: AsyncSession) -> int:
        return int(await db.scalar(select(func.coalesce(func.sum(Outbreak.case_count), 0))) or 0)

    @staticmethod
    async def district_count(db: AsyncSession) -> int:
        return int(await db.scalar(select(func.count(func.distinct(Outbreak.district)))) or 0)

    @staticmethod
    async def latest_by_district(
        db: AsyncSession, disease_code: str, district: str, limit: int = 24
    ):
        query = (
            select(Outbreak, Disease)
            .join(Disease, Outbreak.disease_id == Disease.id)
            .where(Disease.code == disease_code, Outbreak.district == district)
            .order_by(Outbreak.report_date.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return result.all()
