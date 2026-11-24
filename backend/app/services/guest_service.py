from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.models.guest import Guest
from app.models.gift import Gift
from app.models.contributor import GiftContributor
from app.models.thank_you import ThankYouMessage
from app.schemas.guest import GuestCreate, GuestUpdate, GuestOut

class GuestService:
    @staticmethod
    def get_guests(
        db: Session,
        search: Optional[str] = None,
        relationship: Optional[str] = None,
        is_unidentified: Optional[bool] = None,
        family_group: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "full_name",
        sort_order: str = "asc"
    ) -> Tuple[List[GuestOut], int]:
        query = db.query(Guest).filter(Guest.is_deleted == False)

        if search:
            search_fmt = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Guest.full_name.ilike(search_fmt),
                    Guest.family_group.ilike(search_fmt),
                    Guest.relationship_type.ilike(search_fmt),
                    Guest.notes.ilike(search_fmt),
                    Guest.phone_number.ilike(search_fmt)
                )
            )

        if relationship and relationship != "all":
            query = query.filter(Guest.relationship_type == relationship)

        if is_unidentified is not None:
            query = query.filter(Guest.is_unidentified == is_unidentified)

        if family_group:
            query = query.filter(Guest.family_group == family_group)

        total = query.count()

        # Sorting
        sort_col = getattr(Guest, sort_by, Guest.full_name)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_col))
        else:
            query = query.order_by(asc(sort_col))

        offset = (page - 1) * page_size
        guests = query.offset(offset).limit(page_size).all()

        results = []
        for g in guests:
            # Calculate total gifts contributed
            contrib_count = db.query(GiftContributor).filter(GiftContributor.guest_id == g.id).count()
            # Calculate thank you status
            ty_msg = db.query(ThankYouMessage).filter(ThankYouMessage.guest_id == g.id).first()
            ty_status = ty_msg.status if ty_msg else "none"

            g_out = GuestOut.model_validate(g)
            g_out.total_gifts_contributed = contrib_count
            g_out.thank_you_status = ty_status
            results.append(g_out)

        return results, total

    @staticmethod
    def get_guest_by_id(db: Session, guest_id: int) -> Optional[Guest]:
        return db.query(Guest).filter(Guest.id == guest_id, Guest.is_deleted == False).first()

    @staticmethod
    def create_guest(db: Session, guest_in: GuestCreate) -> Guest:
        # Check if name indicates unknown or unidentified
        is_unknown = guest_in.is_unidentified
        lower_name = guest_in.full_name.lower()
        if any(term in lower_name for term in ["unknown", "unidentified", "didn't catch", "no name", "anonymous"]):
            is_unknown = True

        guest = Guest(
            full_name=guest_in.full_name.strip(),
            relationship_type=guest_in.relationship_type or "Guest",
            phone_number=guest_in.phone_number,
            email=guest_in.email,
            address=guest_in.address,
            family_group=guest_in.family_group,
            is_unidentified=is_unknown,
            notes=guest_in.notes
        )
        db.add(guest)
        db.commit()
        db.refresh(guest)
        return guest

    @staticmethod
    def update_guest(db: Session, guest: Guest, guest_in: GuestUpdate) -> Guest:
        for field, value in guest_in.model_dump(exclude_unset=True).items():
            setattr(guest, field, value)
        db.commit()
        db.refresh(guest)
        return guest

    @staticmethod
    def delete_guest(db: Session, guest: Guest) -> bool:
        # Safe soft delete
        guest.is_deleted = True
        db.commit()
        return True
