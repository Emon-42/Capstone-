from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.contributor import GiftContributor
from app.models.guest import Guest
from app.schemas.contributor import ContributorCreate, ContributorOut

class ContributorService:
    @staticmethod
    def get_contributors_for_gift(db: Session, gift_id: int) -> List[ContributorOut]:
        contributors = (
            db.query(GiftContributor, Guest)
            .join(Guest, GiftContributor.guest_id == Guest.id)
            .filter(GiftContributor.gift_id == gift_id)
            .all()
        )
        results = []
        for c, g in contributors:
            c_out = ContributorOut(
                id=c.id,
                gift_id=c.gift_id,
                guest_id=c.guest_id,
                guest_name=g.full_name,
                relationship_type=g.relationship_type,
                family_group=g.family_group,
                contribution_note=c.contribution_note,
                is_primary=c.is_primary,
                created_at=c.created_at
            )
            results.append(c_out)
        return results

    @staticmethod
    def add_contributor(
        db: Session,
        gift_id: int,
        guest_id: int,
        contribution_note: Optional[str] = None,
        is_primary: bool = True
    ) -> GiftContributor:
        # Check if already exists
        existing = db.query(GiftContributor).filter(
            GiftContributor.gift_id == gift_id,
            GiftContributor.guest_id == guest_id
        ).first()

        if existing:
            existing.contribution_note = contribution_note
            existing.is_primary = is_primary
            db.commit()
            db.refresh(existing)
            return existing

        contributor = GiftContributor(
            gift_id=gift_id,
            guest_id=guest_id,
            contribution_note=contribution_note,
            is_primary=is_primary
        )
        db.add(contributor)
        db.commit()
        db.refresh(contributor)
        return contributor

    @staticmethod
    def remove_contributor(db: Session, gift_id: int, guest_id: int) -> bool:
        contributor = db.query(GiftContributor).filter(
            GiftContributor.gift_id == gift_id,
            GiftContributor.guest_id == guest_id
        ).first()
        if contributor:
            db.delete(contributor)
            db.commit()
            return True
        return False
