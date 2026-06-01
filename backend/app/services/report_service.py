import io
import json
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Report
from app.schemas.analytics import DashboardStats


class ReportService:
    @staticmethod
    async def generate_intelligence_report(
        db: AsyncSession,
        user_id: int,
        title: str,
        stats: DashboardStats,
        risk_summary: list[dict],
        trends: list[dict],
    ) -> Report:
        content = {
            "generated_at": datetime.utcnow().isoformat(),
            "stats": stats.model_dump(),
            "risk_summary": risk_summary,
            "trends": trends,
        }
        reports_dir = Path("artifacts/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        filename = f"report_{user_id}_{int(datetime.utcnow().timestamp())}.pdf"
        filepath = reports_dir / filename
        ReportService._write_pdf(filepath, title, content)

        report = Report(
            user_id=user_id,
            title=title,
            report_type="intelligence",
            content_json=content,
            file_path=str(filepath),
        )
        db.add(report)
        await db.flush()
        await db.refresh(report)
        return report

    @staticmethod
    def _write_pdf(path: Path, title: str, content: dict) -> None:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=18, spaceAfter=12)
        elements = [
            Paragraph(title, title_style),
            Paragraph(
                f"Generated: {content.get('generated_at', '')}",
                styles["Normal"],
            ),
            Spacer(1, 12),
            Paragraph("Executive Summary", styles["Heading2"]),
        ]
        stats = content.get("stats", {})
        table_data = [
            ["Metric", "Value"],
            ["Total Cases", str(stats.get("total_cases", 0))],
            ["Active Alerts", str(stats.get("active_alerts", 0))],
            ["High Risk Areas", str(stats.get("high_risk_areas", 0))],
            ["Prediction Accuracy", f"{stats.get('prediction_accuracy', 0):.1%}"],
        ]
        t = Table(table_data, colWidths=[200, 200])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        elements.append(t)
        doc.build(elements)
        path.write_bytes(buffer.getvalue())
