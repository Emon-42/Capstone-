from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ContributorBase(BaseModel):
    guest_id: int
    contribution_note: Optional[str] = None
    is_primary: Optional[bool] = True

class ContributorCreate(ContributorBase):
    pass

class ContributorOut(BaseModel):
    id: int
    gift_id: int
    guest_id: int
    guest_name: Optional[str] = None
    relationship_type: Optional[str] = None
    family_group: Optional[str] = None
    contribution_note: Optional[str] = None
    is_primary: bool
    created_at: datetime

    class Config:
        from_attributes = True
