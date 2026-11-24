from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.history_service import HistoryService
from app.schemas.history import HistoryCreate, HistoryOut, ReciprocityComparisonOut

router = APIRouter(prefix="/api/gift-history", tags=["Gift History & Reciprocity"])

@router.get("", response_model=List[HistoryOut])
def list_history(
    guest_id: Optional[int] = Query(None),
    family_group: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),  # "received" or "given_return"
    db: Session = Depends(get_db)
):
    return HistoryService.get_history(db, guest_id=guest_id, family_group=family_group, event_type=event_type)

@router.post("", response_model=HistoryOut, status_code=status.HTTP_201_CREATED)
def record_exchange(record_in: HistoryCreate, db: Session = Depends(get_db)):
    rec = HistoryService.create_exchange_record(db, record_in)
    history_items = HistoryService.get_history(db)
    for it in history_items:
        if it.id == rec.id:
            return it
    return history_items[0]

@router.get("/reciprocity/{guest_id}", response_model=ReciprocityComparisonOut)
def get_reciprocity_comparison(guest_id: int, db: Session = Depends(get_db)):
    return HistoryService.get_reciprocity_comparison(db, guest_id)
