from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.report_service import ReportService
from app.schemas.report import DashboardStats, ReportSummary

router = APIRouter(prefix="/api/reports", tags=["Reports & Analytics"])

@router.get("/summary", response_model=ReportSummary)
def get_report_summary(db: Session = Depends(get_db)):
    stats = ReportService.get_dashboard_stats(db)
    cat_dist = ReportService.get_category_distribution(db)
    activities = ReportService.get_recent_activities(db)
    monthly = [{"month": "Nov 2026", "count": stats.total_gift_records}]
    return {
        "stats": stats,
        "category_distribution": cat_dist,
        "monthly_statistics": monthly,
        "recent_activities": activities
    }

@router.get("/gifts")
def get_gift_analytics(db: Session = Depends(get_db)):
    cat_dist = ReportService.get_category_distribution(db)
    stats = ReportService.get_dashboard_stats(db)
    return {
        "total_gifts": stats.total_gift_records,
        "total_cash_gifts": stats.total_cash_gifts,
        "unidentified_gifts": stats.unidentified_gifts,
        "categories": cat_dist
    }

@router.get("/thank-you")
def get_thank_you_analytics(db: Session = Depends(get_db)):
    stats = ReportService.get_dashboard_stats(db)
    return {
        "sent": stats.thank_you_sent,
        "pending": stats.thank_you_pending,
        "draft": stats.thank_you_draft,
        "completion_rate": stats.completion_rate_percentage
    }

@router.get("/export/csv")
def export_csv(
    type: str = Query("gifts", regex="^(guests|gifts|thank_you|history)$"),
    db: Session = Depends(get_db)
):
    csv_data = ReportService.export_csv(db, type)
    filename = f"wedding_gift_ledger_{type}_export.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
