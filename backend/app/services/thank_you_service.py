from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.models.thank_you import ThankYouMessage, ThankYouStatusHistory
from app.models.gift import Gift
from app.models.guest import Guest
from app.schemas.thank_you import ThankYouOut, ThankYouStatusHistoryOut

class ThankYouService:
    @staticmethod
    def generate_message(
        guest_name: str,
        gift_name: str,
        relationship: Optional[str] = "Guest",
        is_cash: bool = False,
        tone: str = "warm",
        custom_note: Optional[str] = None
    ) -> str:
        """
        Generates culturally appropriate, personalized thank you message.
        CRITICAL BUSINESS RULE:
        Never mention a cash amount, even if recorded in database!
        """
        # Salutation
        if any(term in guest_name.lower() for term in ["uncle", "khala", "chachi", "fupu", "mami"]):
            salutation = f"Dear {guest_name}"
        elif "family" in guest_name.lower():
            salutation = f"Dear {guest_name}"
        else:
            salutation = f"Dear {guest_name}"

        # Clean gift reference: NEVER show cash amount!
        if is_cash or "envelope" in gift_name.lower() or "cash" in gift_name.lower():
            gift_ref = "thoughtful gift and kind blessings"
        else:
            gift_ref = f"beautiful {gift_name}"

        # Tones
        if tone == "formal":
            msg = (
                f"{salutation},\n\n"
                f"We express our sincerest gratitude for your gracious presence at our wedding and for the {gift_ref}. "
                f"Your warm wishes and generosity mean a great deal to both of our families.\n\n"
                f"Sincerely with respect,\nFarhana and Family"
            )
        elif tone == "friendly":
            msg = (
                f"{salutation}!\n\n"
                f"It was so amazing having you celebrate with us! Thank you so much for the {gift_ref}. "
                f"We absolutely love it and appreciate having you in our lives.\n\n"
                f"Cheers and love,\nFarhana and Tanvir"
            )
        elif tone == "short":
            msg = (
                f"{salutation},\n\n"
                f"Thank you very much for the wonderful {gift_ref} and for celebrating our wedding with us!\n\n"
                f"With love, Farhana & Family."
            )
        elif tone == "detailed":
            msg = (
                f"{salutation},\n\n"
                f"Our wedding was made truly complete by your presence, prayers, and heartfelt joy. "
                f"Thank you so much for the {gift_ref}. It will always remain a cherished memory in our home. "
                f"We look forward to visiting you soon.\n\n"
                f"With deep gratitude and love,\nFarhana and Family"
            )
        else:  # "warm" default
            msg = (
                f"{salutation},\n\n"
                f"Thank you so much for the {gift_ref}. We truly appreciate your thoughtful gesture and your presence at our wedding.\n\n"
                f"With love and warm regards,\nFarhana and Family"
            )

        if custom_note:
            msg += f"\n\nP.S. {custom_note}"

        return msg

    @staticmethod
    def get_messages(
        db: Session,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[ThankYouOut], int]:
        query = db.query(ThankYouMessage)

        if status and status != "all":
            query = query.filter(ThankYouMessage.status == status)

        if search:
            search_fmt = f"%{search.strip()}%"
            query = query.join(Guest).filter(
                or_(
                    Guest.full_name.ilike(search_fmt),
                    ThankYouMessage.message_text.ilike(search_fmt)
                )
            )

        total = query.count()

        sort_col = getattr(ThankYouMessage, sort_by, ThankYouMessage.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        offset = (page - 1) * page_size
        messages = query.offset(offset).limit(page_size).all()

        results = []
        for m in messages:
            guest = db.query(Guest).filter(Guest.id == m.guest_id).first()
            gift = db.query(Gift).filter(Gift.id == m.gift_id).first()
            history = db.query(ThankYouStatusHistory).filter(ThankYouStatusHistory.message_id == m.id).order_by(desc(ThankYouStatusHistory.changed_at)).all()

            m_out = ThankYouOut(
                id=m.id,
                gift_id=m.gift_id,
                guest_id=m.guest_id,
                guest_name=guest.full_name if guest else "Unknown Guest",
                gift_name=gift.gift_name if gift else "Gift",
                relationship_type=guest.relationship_type if guest else "Guest",
                status=m.status,
                tone=m.tone,
                message_text=m.message_text,
                sent_date=m.sent_date,
                sent_via=m.sent_via,
                notes=m.notes,
                created_at=m.created_at,
                updated_at=m.updated_at,
                status_history=[ThankYouStatusHistoryOut.model_validate(h) for h in history]
            )
            results.append(m_out)

        return results, total

    @staticmethod
    def update_message(
        db: Session,
        message: ThankYouMessage,
        message_text: Optional[str] = None,
        tone: Optional[str] = None,
        sent_via: Optional[str] = None,
        notes: Optional[str] = None
    ) -> ThankYouMessage:
        if message_text is not None:
            message.message_text = message_text
        if tone is not None:
            message.tone = tone
        if sent_via is not None:
            message.sent_via = sent_via
        if notes is not None:
            message.notes = notes

        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def mark_status(
        db: Session,
        message: ThankYouMessage,
        new_status: str,
        sent_via: Optional[str] = None,
        reason: Optional[str] = None
    ) -> ThankYouMessage:
        prev_status = message.status
        message.status = new_status
        if new_status == "sent":
            message.sent_date = datetime.utcnow()
            if sent_via:
                message.sent_via = sent_via

        # Log history
        history = ThankYouStatusHistory(
            message_id=message.id,
            previous_status=prev_status,
            new_status=new_status,
            change_reason=reason or f"Status changed from {prev_status} to {new_status}"
        )
        db.add(history)
        db.commit()
        db.refresh(message)
        return message
