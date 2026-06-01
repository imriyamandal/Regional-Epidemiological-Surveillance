from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.database.models import User, UserRole
from app.database.session import get_db
from app.schemas.analytics import AlertResponse
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 50,
):
    return await AlertService.list_alerts(db, current_user.id, limit)


@router.patch("/{alert_id}/read", response_model=AlertResponse)
async def mark_alert_read(
    alert_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    alert = await AlertService.mark_read(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/test-email")
async def test_email(
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
):
    sent = AlertService.send_email_alert(
        current_user.email,
        "DOPEWIS Test Alert",
        "This is a test alert from the Disease Outbreak Prediction platform.",
    )
    return {"sent": sent, "message": "Email sent" if sent else "SMTP not configured"}
