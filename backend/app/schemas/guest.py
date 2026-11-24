from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class GuestBase(BaseModel):
    full_name: str
    relationship_type: Optional[str] = "Guest"
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    family_group: Optional[str] = None
    is_unidentified: Optional[bool] = False
    notes: Optional[str] = None

class GuestCreate(GuestBase):
    pass

class GuestUpdate(BaseModel):
    full_name: Optional[str] = None
    relationship_type: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    family_group: Optional[str] = None
    is_unidentified: Optional[bool] = None
    notes: Optional[str] = None

class GuestOut(GuestBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    total_gifts_contributed: Optional[int] = 0
    thank_you_status: Optional[str] = None  # "none", "pending", "sent"

    class Config:
        from_attributes = True

class GuestListResponse(BaseModel):
    items: List[GuestOut]
    total: int
    page: int
    page_size: int
    total_pages: int
