from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.contributor import ContributorOut, ContributorCreate

class GiftBase(BaseModel):
    event_id: int
    gift_name: str
    gift_description: Optional[str] = None
    gift_category: str = "Other"  # Household Items, Clothing, Cash, Jewelry, Electronics, Decorative Items, Other, Unknown
    quantity: int = 1
    gift_date: date = Field(default_factory=date.today)
    is_cash: bool = False
    cash_amount: Optional[Decimal] = None  # Optional!
    currency: str = "BDT"
    original_note: str  # Preserves exact handwritten note
    additional_notes: Optional[str] = None
    review_status: str = "confirmed"  # confirmed, requires_review, unidentified

class GiftCreate(GiftBase):
    contributor_ids: Optional[List[int]] = None
    contributors: Optional[List[ContributorCreate]] = None

class GiftUpdate(BaseModel):
    gift_name: Optional[str] = None
    gift_description: Optional[str] = None
    gift_category: Optional[str] = None
    quantity: Optional[int] = None
    gift_date: Optional[date] = None
    is_cash: Optional[bool] = None
    cash_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    original_note: Optional[str] = None
    additional_notes: Optional[str] = None
    review_status: Optional[str] = None
    contributor_ids: Optional[List[int]] = None

class GiftOut(GiftBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    event_name: Optional[str] = None
    contributors: List[ContributorOut] = []

    class Config:
        from_attributes = True

class GiftListResponse(BaseModel):
    items: List[GiftOut]
    total: int
    page: int
    page_size: int
    total_pages: int
