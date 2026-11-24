from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class ThankYouGenerateRequest(BaseModel):
    guest_id: int
    gift_id: int
    tone: Optional[str] = "warm"  # formal, warm, friendly, short, detailed
    custom_note: Optional[str] = None

class ThankYouCreate(BaseModel):
    gift_id: int
    guest_id: int
    tone: str = "warm"
    message_text: str
    status: str = "pending"
    sent_via: Optional[str] = None
    notes: Optional[str] = None

class ThankYouUpdate(BaseModel):
    message_text: Optional[str] = None
    status: Optional[str] = None
    tone: Optional[str] = None
    sent_via: Optional[str] = None
    notes: Optional[str] = None

class ThankYouStatusHistoryOut(BaseModel):
    id: int
    previous_status: str
    new_status: str
    changed_at: datetime
    change_reason: Optional[str] = None

    class Config:
        from_attributes = True

class ThankYouOut(BaseModel):
    id: int
    gift_id: int
    guest_id: int
    guest_name: Optional[str] = None
    gift_name: Optional[str] = None
    relationship_type: Optional[str] = None
    status: str
    tone: str
    message_text: str
    sent_date: Optional[datetime] = None
    sent_via: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    status_history: List[ThankYouStatusHistoryOut] = []

    class Config:
        from_attributes = True

class ThankYouListResponse(BaseModel):
    items: List[ThankYouOut]
    total: int
    page: int
    page_size: int
    total_pages: int
