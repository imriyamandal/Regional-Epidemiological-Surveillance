from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.models import Report, User
from app.database.session import get_db
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/generate")
async def generate_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    title: str = "DOPEWIS Health Intelligence Report",
):
    stats = await AnalyticsService.get_dashboard_stats(db)
    risks = await AnalyticsService.get_risk_scores(db, limit=20)
    trends = await AnalyticsService.get_disease_trends(db, months=6)
    report = await ReportService.generate_intelligence_report(
        db,
        current_user.id,
        title,
        stats,
        [r.model_dump() for r in risks],
        [t.model_dump() for t in trends],
    )
    return {"id": report.id, "title": report.title, "file_path": report.file_path}


@router.get("")
async def list_reports(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(Report).where(Report.user_id == current_user.id).order_by(Report.created_at.desc())
    )
    reports = result.scalars().all()
    return [
        {"id": r.id, "title": r.title, "type": r.report_type, "created_at": r.created_at}
        for r in reports
    ]


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    if not report or not report.file_path:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(report.file_path, filename=f"{report.title}.pdf")
