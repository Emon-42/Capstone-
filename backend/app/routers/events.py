from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.event import WeddingEvent
from app.schemas.event import EventCreate, EventUpdate, EventOut

router = APIRouter(prefix="/api/events", tags=["Wedding Events"])

@router.get("", response_model=List[EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(WeddingEvent).order_by(WeddingEvent.event_date.desc()).all()

@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(event_in: EventCreate, db: Session = Depends(get_db)):
    event = WeddingEvent(
        event_name=event_in.event_name,
        event_date=event_in.event_date,
        venue=event_in.venue,
        host_family=event_in.host_family or "Farhana's Family",
        is_primary=event_in.is_primary or False,
        notes=event_in.notes
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return EventOut.model_validate(event)

@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(WeddingEvent).filter(WeddingEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventOut.model_validate(event)
