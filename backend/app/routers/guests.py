import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.guest_service import GuestService
from app.schemas.guest import GuestCreate, GuestUpdate, GuestOut, GuestListResponse

router = APIRouter(prefix="/api/guests", tags=["Guests"])

@router.get("", response_model=GuestListResponse)
def list_guests(
    search: Optional[str] = Query(None),
    relationship: Optional[str] = Query(None),
    is_unidentified: Optional[bool] = Query(None),
    family_group: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("full_name"),
    sort_order: str = Query("asc"),
    db: Session = Depends(get_db)
):
    items, total = GuestService.get_guests(
        db,
        search=search,
        relationship=relationship,
        is_unidentified=is_unidentified,
        family_group=family_group,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@router.post("", response_model=GuestOut, status_code=status.HTTP_201_CREATED)
def create_guest(guest_in: GuestCreate, db: Session = Depends(get_db)):
    guest = GuestService.create_guest(db, guest_in)
    return GuestOut.model_validate(guest)

@router.get("/{guest_id}", response_model=GuestOut)
def get_guest(guest_id: int, db: Session = Depends(get_db)):
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return GuestOut.model_validate(guest)

@router.put("/{guest_id}", response_model=GuestOut)
def update_guest(guest_id: int, guest_in: GuestUpdate, db: Session = Depends(get_db)):
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    updated = GuestService.update_guest(db, guest, guest_in)
    return GuestOut.model_validate(updated)

@router.delete("/{guest_id}", status_code=status.HTTP_200_OK)
def delete_guest(guest_id: int, db: Session = Depends(get_db)):
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    GuestService.delete_guest(db, guest)
    return {"message": "Guest safely deleted (soft delete applied to preserve historical records)"}
