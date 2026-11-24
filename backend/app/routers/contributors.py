from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.contributor_service import ContributorService
from app.schemas.contributor import ContributorCreate, ContributorOut
from app.models.gift import Gift

router = APIRouter(prefix="/api", tags=["Contributors"])

@router.get("/gifts/{gift_id}/contributors", response_model=List[ContributorOut])
def get_gift_contributors(gift_id: int, db: Session = Depends(get_db)):
    return ContributorService.get_contributors_for_gift(db, gift_id)

@router.post("/gifts/{gift_id}/contributors", response_model=ContributorOut, status_code=status.HTTP_201_CREATED)
def add_gift_contributor(gift_id: int, contrib_in: ContributorCreate, db: Session = Depends(get_db)):
    gift = db.query(Gift).filter(Gift.id == gift_id, Gift.is_deleted == False).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    c = ContributorService.add_contributor(
        db,
        gift_id=gift_id,
        guest_id=contrib_in.guest_id,
        contribution_note=contrib_in.contribution_note,
        is_primary=contrib_in.is_primary if contrib_in.is_primary is not None else True
    )
    contributors = ContributorService.get_contributors_for_gift(db, gift_id)
    for item in contributors:
        if item.id == c.id:
            return item
    return contributors[0]

@router.delete("/gifts/{gift_id}/contributors/{guest_id}", status_code=status.HTTP_200_OK)
def remove_gift_contributor(gift_id: int, guest_id: int, db: Session = Depends(get_db)):
    success = ContributorService.remove_contributor(db, gift_id, guest_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contributor association not found")
    return {"message": "Contributor removed successfully"}
