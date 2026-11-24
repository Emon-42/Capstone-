import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.thank_you import ThankYouMessage
from app.models.guest import Guest
from app.models.gift import Gift
from app.services.thank_you_service import ThankYouService
from app.schemas.thank_you import (
    ThankYouOut,
    ThankYouListResponse,
    ThankYouGenerateRequest,
    ThankYouUpdate
)

router = APIRouter(prefix="/api/thank-you", tags=["Thank You Messages"])

@router.get("", response_model=ThankYouListResponse)
def list_thank_you_messages(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    items, total = ThankYouService.get_messages(
        db,
        status=status,
        search=search,
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

@router.post("/generate")
def generate_thank_you_message(req: ThankYouGenerateRequest, db: Session = Depends(get_db)):
    guest = db.query(Guest).filter(Guest.id == req.guest_id).first()
    gift = db.query(Gift).filter(Gift.id == req.gift_id).first()

    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")

    message_text = ThankYouService.generate_message(
        guest_name=guest.full_name,
        gift_name=gift.gift_name,
        relationship=guest.relationship_type,
        is_cash=gift.is_cash,
        tone=req.tone or "warm",
        custom_note=req.custom_note
    )

    return {
        "guest_id": guest.id,
        "gift_id": gift.id,
        "guest_name": guest.full_name,
        "gift_name": gift.gift_name,
        "tone": req.tone or "warm",
        "message_text": message_text,
        "is_cash": gift.is_cash,
        "disclaimer": "Never mentions monetary amounts even for cash gifts. Culturally appropriate."
    }

@router.put("/{message_id}", response_model=ThankYouOut)
def update_thank_you_message(message_id: int, update_in: ThankYouUpdate, db: Session = Depends(get_db)):
    msg = db.query(ThankYouMessage).filter(ThankYouMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Thank you message not found")

    updated = ThankYouService.update_message(
        db,
        msg,
        message_text=update_in.message_text,
        tone=update_in.tone,
        sent_via=update_in.sent_via,
        notes=update_in.notes
    )
    if update_in.status and update_in.status != msg.status:
        updated = ThankYouService.mark_status(db, updated, update_in.status, update_in.sent_via)

    items, _ = ThankYouService.get_messages(db)
    for it in items:
        if it.id == message_id:
            return it
    return items[0]

@router.post("/{message_id}/mark-sent", response_model=ThankYouOut)
def mark_message_as_sent(message_id: int, sent_via: Optional[str] = Query("WhatsApp"), db: Session = Depends(get_db)):
    msg = db.query(ThankYouMessage).filter(ThankYouMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Thank you message not found")

    ThankYouService.mark_status(db, msg, "sent", sent_via=sent_via, reason="Marked as sent by user")

    items, _ = ThankYouService.get_messages(db)
    for it in items:
        if it.id == message_id:
            return it
    return items[0]
