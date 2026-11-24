from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.models.gift import Gift
from app.models.event import WeddingEvent
from app.models.guest import Guest
from app.models.contributor import GiftContributor
from app.models.thank_you import ThankYouMessage
from app.models.history import GiftExchangeHistory
from app.schemas.gift import GiftCreate, GiftUpdate, GiftOut
from app.services.contributor_service import ContributorService

class GiftService:
    @staticmethod
    def get_gifts(
        db: Session,
        search: Optional[str] = None,
        category: Optional[str] = None,
        review_status: Optional[str] = None,
        is_cash: Optional[bool] = None,
        guest_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[GiftOut], int]:
        query = db.query(Gift).filter(Gift.is_deleted == False)

        if search:
            search_fmt = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Gift.gift_name.ilike(search_fmt),
                    Gift.gift_description.ilike(search_fmt),
                    Gift.original_note.ilike(search_fmt),
                    Gift.gift_category.ilike(search_fmt)
                )
            )

        if category and category != "all":
            query = query.filter(Gift.gift_category == category)

        if review_status and review_status != "all":
            query = query.filter(Gift.review_status == review_status)

        if is_cash is not None:
            query = query.filter(Gift.is_cash == is_cash)

        if guest_id:
            query = query.join(GiftContributor).filter(GiftContributor.guest_id == guest_id)

        total = query.count()

        sort_col = getattr(Gift, sort_by, Gift.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        offset = (page - 1) * page_size
        gifts = query.offset(offset).limit(page_size).all()

        results = []
        for g in gifts:
            event = db.query(WeddingEvent).filter(WeddingEvent.id == g.event_id).first()
            event_name = event.event_name if event else "Wedding Event"
            contributors = ContributorService.get_contributors_for_gift(db, g.id)

            g_out = GiftOut.model_validate(g)
            g_out.event_name = event_name
            g_out.contributors = contributors
            results.append(g_out)

        return results, total

    @staticmethod
    def get_gift_by_id(db: Session, gift_id: int) -> Optional[GiftOut]:
        g = db.query(Gift).filter(Gift.id == gift_id, Gift.is_deleted == False).first()
        if not g:
            return None
        event = db.query(WeddingEvent).filter(WeddingEvent.id == g.event_id).first()
        contributors = ContributorService.get_contributors_for_gift(db, g.id)
        g_out = GiftOut.model_validate(g)
        g_out.event_name = event.event_name if event else "Wedding Event"
        g_out.contributors = contributors
        return g_out

    @staticmethod
    def create_gift(db: Session, gift_in: GiftCreate) -> Gift:
        # Check if review required
        review_status = gift_in.review_status
        lower_note = gift_in.original_note.lower()
        if any(term in lower_note for term in ["?", "no card", "didn't catch", "unknown", "unclear"]):
            if review_status == "confirmed":
                review_status = "requires_review"

        gift = Gift(
            event_id=gift_in.event_id,
            gift_name=gift_in.gift_name.strip(),
            gift_description=gift_in.gift_description,
            gift_category=gift_in.gift_category or "Other",
            quantity=gift_in.quantity or 1,
            gift_date=gift_in.gift_date,
            is_cash=gift_in.is_cash,
            cash_amount=gift_in.cash_amount if gift_in.is_cash else None,
            currency=gift_in.currency or "BDT",
            original_note=gift_in.original_note.strip(),  # Preserved as entered
            additional_notes=gift_in.additional_notes,
            review_status=review_status
        )
        db.add(gift)
        db.commit()
        db.refresh(gift)

        # Associate contributors
        contributor_ids = gift_in.contributor_ids or []
        if gift_in.contributors:
            for c in gift_in.contributors:
                ContributorService.add_contributor(
                    db,
                    gift_id=gift.id,
                    guest_id=c.guest_id,
                    contribution_note=c.contribution_note,
                    is_primary=c.is_primary if c.is_primary is not None else True
                )
                if c.guest_id not in contributor_ids:
                    contributor_ids.append(c.guest_id)
        elif contributor_ids:
            for idx, g_id in enumerate(contributor_ids):
                ContributorService.add_contributor(
                    db,
                    gift_id=gift.id,
                    guest_id=g_id,
                    contribution_note="Gift Contributor",
                    is_primary=(idx == 0)
                )

        # Create ThankYou messages and GiftExchangeHistory records for each contributor
        event = db.query(WeddingEvent).filter(WeddingEvent.id == gift.event_id).first()
        event_name = event.event_name if event else "Wedding"

        for g_id in contributor_ids:
            guest = db.query(Guest).filter(Guest.id == g_id).first()
            if guest:
                # 1. Automatic pending thank-you record
                existing_ty = db.query(ThankYouMessage).filter(
                    ThankYouMessage.gift_id == gift.id,
                    ThankYouMessage.guest_id == g_id
                ).first()
                if not existing_ty:
                    ty = ThankYouMessage(
                        gift_id=gift.id,
                        guest_id=g_id,
                        status="pending",
                        tone="warm",
                        message_text=f"Dear {guest.full_name},\n\nThank you so much for the wonderful {gift.gift_name}. We truly appreciate your thoughtful gesture and blessings.\n\nWith love,\nFarhana and Family"
                    )
                    db.add(ty)

                # 2. Reciprocity record (received)
                reciprocity = GiftExchangeHistory(
                    guest_id=g_id,
                    family_group=guest.family_group,
                    event_id=gift.event_id,
                    event_name=event_name,
                    event_type="received",
                    gift_description=gift.gift_name,
                    category=gift.gift_category,
                    recorded_value=gift.cash_amount if gift.is_cash else None,
                    currency=gift.currency,
                    event_date=gift.gift_date,
                    reference_gift_id=gift.id,
                    notes=f"Original note: {gift.original_note}"
                )
                db.add(reciprocity)

        db.commit()
        db.refresh(gift)
        return gift

    @staticmethod
    def update_gift(db: Session, gift: Gift, gift_in: GiftUpdate) -> Gift:
        data = gift_in.model_dump(exclude_unset=True)
        # Note: editing structured fields does not modify original_note unless explicitly sent
        contributor_ids = data.pop("contributor_ids", None)

        for field, value in data.items():
            setattr(gift, field, value)

        if contributor_ids is not None:
            # Sync contributors
            db.query(GiftContributor).filter(GiftContributor.gift_id == gift.id).delete()
            for idx, g_id in enumerate(contributor_ids):
                ContributorService.add_contributor(
                    db,
                    gift_id=gift.id,
                    guest_id=g_id,
                    contribution_note="Gift Contributor",
                    is_primary=(idx == 0)
                )

        db.commit()
        db.refresh(gift)
        return gift

    @staticmethod
    def delete_gift(db: Session, gift: Gift) -> bool:
        gift.is_deleted = True
        db.commit()
        return True
