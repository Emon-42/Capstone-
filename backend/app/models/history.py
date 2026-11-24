from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class GiftExchangeHistory(Base):
    __tablename__ = "gift_exchange_history"

    id = Column(Integer, primary_key=True, index=True)
    guest_id = Column(Integer, ForeignKey("guests.id", ondelete="SET NULL"), nullable=True, index=True)
    family_group = Column(String(190), nullable=True, index=True)
    event_id = Column(Integer, ForeignKey("wedding_events.id", ondelete="SET NULL"), nullable=True, index=True)
    event_name = Column(String(255), nullable=False)  # e.g., "Farhana's Wedding" or "Rahman Uncle's Son's Wedding"
    event_type = Column(String(50), nullable=False, index=True)  # "received" or "given_return"
    gift_description = Column(Text, nullable=False)
    category = Column(String(50), default="Other")
    recorded_value = Column(Numeric(12, 2), nullable=True)  # Optional! Only when explicitly known
    currency = Column(String(10), default="BDT")
    event_date = Column(Date, default=date.today, nullable=False)
    reference_gift_id = Column(Integer, ForeignKey("gifts.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    guest = relationship("Guest", back_populates="exchanges")
    event = relationship("WeddingEvent", back_populates="exchanges")
    reference_gift = relationship("Gift", back_populates="reciprocity_records")
