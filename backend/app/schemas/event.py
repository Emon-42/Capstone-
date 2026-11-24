from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

class EventBase(BaseModel):
    event_name: str
    event_date: date
    venue: Optional[str] = None
    host_family: Optional[str] = "Farhana's Family"
    is_primary: Optional[bool] = False
    notes: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    event_name: Optional[str] = None
    event_date: Optional[date] = None
    venue: Optional[str] = None
    host_family: Optional[str] = None
    is_primary: Optional[bool] = None
    notes: Optional[str] = None

class EventOut(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
