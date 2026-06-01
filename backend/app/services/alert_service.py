import smtplib
from email.mime.text import MIMEText

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.models import Alert, AlertLevel, RiskLevel

settings = get_settings()


def risk_to_alert_level(risk_level: RiskLevel, risk_score: float) -> AlertLevel:
    if risk_level == RiskLevel.CRITICAL or risk_score >= 0.85:
        return AlertLevel.RED
    if risk_level == RiskLevel.HIGH or risk_score >= 0.7:
        return AlertLevel.ORANGE
    if risk_level in (RiskLevel.MEDIUM, RiskLevel.LOW) or risk_score >= 0.45:
        return AlertLevel.YELLOW
    return AlertLevel.GREEN


class AlertService:
    @staticmethod
    async def create_alert(
        db: AsyncSession,
        *,
        state: str,
        district: str,
        title: str,
        message: str,
        risk_score: float,
        risk_level: RiskLevel,
        disease_id: int | None = None,
        predicted_cases: float | None = None,
        user_id: int | None = None,
    ) -> Alert:
        level = risk_to_alert_level(risk_level, risk_score)
        alert = Alert(
            user_id=user_id,
            disease_id=disease_id,
            state=state,
            district=district,
            level=level,
            title=title,
            message=message,
            risk_score=risk_score,
            predicted_cases=predicted_cases,
        )
        db.add(alert)
        await db.flush()
        await db.refresh(alert)
        return alert

    @staticmethod
    async def list_alerts(db: AsyncSession, user_id: int | None = None, limit: int = 50) -> list[Alert]:
        query = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
        if user_id:
            query = query.where((Alert.user_id == user_id) | (Alert.user_id.is_(None)))
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def mark_read(db: AsyncSession, alert_id: int) -> Alert | None:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        if alert:
            alert.is_read = True
            await db.flush()
        return alert

    @staticmethod
    def send_email_alert(to_email: str, subject: str, body: str) -> bool:
        if not settings.smtp_host or not settings.smtp_user:
            return False
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = settings.alert_from_email
            msg["To"] = to_email
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
            return True
        except Exception:
            return False
