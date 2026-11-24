from decimal import Decimal
from typing import Optional, List, Dict
from pydantic import BaseModel

class DashboardStats(BaseModel):
    total_guests: int
    total_gift_records: int
    total_contributors: int
    thank_you_sent: int
    thank_you_pending: int
    thank_you_draft: int
    unidentified_gifts: int
    gifts_requiring_review: int
    total_cash_gifts: int
    total_recorded_cash_value: Decimal
    completion_rate_percentage: float

class CategoryStat(BaseModel):
    category: str
    count: int
    percentage: float

class MonthlyStat(BaseModel):
    month: str
    count: int

class RecentActivityItem(BaseModel):
    id: int
    type: str  # "gift", "thank_you", "guest", "reciprocity"
    title: str
    description: str
    timestamp: str
    status: Optional[str] = None

class ReportSummary(BaseModel):
    stats: DashboardStats
    category_distribution: List[CategoryStat]
    monthly_statistics: List[MonthlyStat]
    recent_activities: List[RecentActivityItem]
