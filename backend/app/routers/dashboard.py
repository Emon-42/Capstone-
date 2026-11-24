from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.report_service import ReportService
from app.schemas.report import DashboardStats, ReportSummary

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    return ReportService.get_dashboard_stats(db)

@router.get("/summary", response_model=ReportSummary)
def get_summary(db: Session = Depends(get_db)):
    stats = ReportService.get_dashboard_stats(db)
    cat_dist = ReportService.get_category_distribution(db)
    activities = ReportService.get_recent_activities(db)
    # Generate simple monthly grouping
    monthly = [
        {"month": "Nov 2026", "count": stats.total_gift_records}
    ]
    return {
        "stats": stats,
        "category_distribution": cat_dist,
        "monthly_statistics": monthly,
        "recent_activities": activities
    }

@router.get("/recent-activity")
def get_recent_activity(db: Session = Depends(get_db)):
    return ReportService.get_recent_activities(db)
