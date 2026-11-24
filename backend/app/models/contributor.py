from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class GiftContributor(Base):
    __tablename__ = "gift_contributors"

    id = Column(Integer, primary_key=True, index=True)
    gift_id = Column(Integer, ForeignKey("gifts.id", ondelete="CASCADE"), nullable=False, index=True)
    guest_id = Column(Integer, ForeignKey("guests.id", ondelete="RESTRICT"), nullable=False, index=True)
    contribution_note = Column(String(255), nullable=True)  # e.g., "Joint gift with Shilpi Khala"
    is_primary = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    gift = relationship("Gift", back_populates="contributors")
    guest = relationship("Guest", back_populates="contributions")

    __table_args__ = (
        UniqueConstraint('gift_id', 'guest_id', name='uq_gift_guest_contributor'),
    )
