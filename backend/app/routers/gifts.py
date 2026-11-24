import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.gift_service import GiftService
from app.schemas.gift import GiftCreate, GiftUpdate, GiftOut, GiftListResponse

router = APIRouter(prefix="/api/gifts", tags=["Gifts"])

@router.get("", response_model=GiftListResponse)
def list_gifts(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
    is_cash: Optional[bool] = Query(None),
    guest_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    items, total = GiftService.get_gifts(
        db,
        search=search,
        category=category,
        review_status=review_status,
        is_cash=is_cash,
        guest_id=guest_id,
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

@router.post("", response_model=GiftOut, status_code=status.HTTP_201_CREATED)
def create_gift(gift_in: GiftCreate, db: Session = Depends(get_db)):
    gift = GiftService.create_gift(db, gift_in)
    return GiftService.get_gift_by_id(db, gift.id)

@router.get("/{gift_id}", response_model=GiftOut)
def get_gift(gift_id: int, db: Session = Depends(get_db)):
    gift_out = GiftService.get_gift_by_id(db, gift_id)
    if not gift_out:
        raise HTTPException(status_code=404, detail="Gift record not found")
    return gift_out

@router.put("/{gift_id}", response_model=GiftOut)
def update_gift(gift_id: int, gift_in: GiftUpdate, db: Session = Depends(get_db)):
    gift = db.query(GiftService.get_gift_by_id(db, gift_id))
    raw_gift = db.query(gift_in.__class__).first()  # type check
    from app.models.gift import Gift as GiftModel
    gift_obj = db.query(GiftModel).filter(GiftModel.id == gift_id, GiftModel.is_deleted == False).first()
    if not gift_obj:
        raise HTTPException(status_code=404, detail="Gift record not found")
    GiftService.update_gift(db, gift_obj, gift_in)
    return GiftService.get_gift_by_id(db, gift_id)

@router.delete("/{gift_id}", status_code=status.HTTP_200_OK)
def delete_gift(gift_id: int, db: Session = Depends(get_db)):
    from app.models.gift import Gift as GiftModel
    gift_obj = db.query(GiftModel).filter(GiftModel.id == gift_id, GiftModel.is_deleted == False).first()
    if not gift_obj:
        raise HTTPException(status_code=404, detail="Gift record not found")
    GiftService.delete_gift(db, gift_obj)
    return {"message": "Gift safely deleted"}
