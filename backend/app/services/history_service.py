from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.history import GiftExchangeHistory
from app.models.guest import Guest
from app.schemas.history import HistoryCreate, HistoryOut, ReciprocityComparisonOut

class HistoryService:
    @staticmethod
    def get_history(
        db: Session,
        guest_id: Optional[int] = None,
        family_group: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[HistoryOut]:
        query = db.query(GiftExchangeHistory)

        if guest_id:
            query = query.filter(GiftExchangeHistory.guest_id == guest_id)
        if family_group:
            query = query.filter(GiftExchangeHistory.family_group == family_group)
        if event_type:
            query = query.filter(GiftExchangeHistory.event_type == event_type)

        records = query.order_by(desc(GiftExchangeHistory.event_date)).all()
        results = []
        for r in records:
            guest = db.query(Guest).filter(Guest.id == r.guest_id).first() if r.guest_id else None
            out = HistoryOut.model_validate(r)
            out.guest_name = guest.full_name if guest else (r.family_group or "Unknown")
            out.relationship_type = guest.relationship_type if guest else "Guest"
            results.append(out)
        return results

    @staticmethod
    def create_exchange_record(db: Session, record_in: HistoryCreate) -> GiftExchangeHistory:
        record = GiftExchangeHistory(
            guest_id=record_in.guest_id,
            family_group=record_in.family_group,
            event_id=record_in.event_id,
            event_name=record_in.event_name,
            event_type=record_in.event_type,
            gift_description=record_in.gift_description,
            category=record_in.category or "Other",
            recorded_value=record_in.recorded_value,
            currency=record_in.currency or "BDT",
            event_date=record_in.event_date,
            reference_gift_id=record_in.reference_gift_id,
            notes=record_in.notes
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_reciprocity_comparison(db: Session, guest_id: int) -> ReciprocityComparisonOut:
        guest = db.query(Guest).filter(Guest.id == guest_id).first()
        guest_name = guest.full_name if guest else "Unknown Guest"
        family_group = guest.family_group if guest else None

        received = HistoryService.get_history(db, guest_id=guest_id, event_type="received")
        given = HistoryService.get_history(db, guest_id=guest_id, event_type="given_return")

        # Also search by family group if applicable
        if family_group:
            family_received = HistoryService.get_history(db, family_group=family_group, event_type="received")
            family_given = HistoryService.get_history(db, family_group=family_group, event_type="given_return")
            # merge unique
            rec_ids = {r.id for r in received}
            for fr in family_received:
                if fr.id not in rec_ids:
                    received.append(fr)
            giv_ids = {g.id for g in given}
            for fg in family_given:
                if fg.id not in giv_ids:
                    given.append(fg)

        has_pending = len(received) > len(given)

        return ReciprocityComparisonOut(
            guest_id=guest_id,
            guest_name=guest_name,
            family_group=family_group,
            gifts_received=received,
            gifts_given_in_return=given,
            has_pending_return=has_pending,
            notes=f"Comparison: {len(received)} gift(s) received, {len(given)} return gift(s) recorded."
        )
