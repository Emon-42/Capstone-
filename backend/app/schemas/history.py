from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel

class HistoryBase(BaseModel):
    guest_id: Optional[int] = None
    family_group: Optional[str] = None
    event_id: Optional[int] = None
    event_name: str
    event_type: str  # "received" or "given_return"
    gift_description: str
    category: str = "Other"
    recorded_value: Optional[Decimal] = None  # Optional! Never guessed
    currency: str = "BDT"
    event_date: date
    reference_gift_id: Optional[int] = None
    notes: Optional[str] = None

class HistoryCreate(HistoryBase):
    pass

class HistoryUpdate(BaseModel):
    event_name: Optional[str] = None
    event_type: Optional[str] = None
    gift_description: Optional[str] = None
    category: Optional[str] = None
    recorded_value: Optional[Decimal] = None
    currency: Optional[str] = None
    event_date: Optional[date] = None
    notes: Optional[str] = None

class HistoryOut(HistoryBase):
    id: int
    guest_name: Optional[str] = None
    relationship_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReciprocityComparisonOut(BaseModel):
    guest_id: Optional[int] = None
    guest_name: Optional[str] = None
    family_group: Optional[str] = None
    gifts_received: List[HistoryOut] = []
    gifts_given_in_return: List[HistoryOut] = []
    has_pending_return: bool = False
    notes: Optional[str] = None
