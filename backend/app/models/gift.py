from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Gift(Base):
    __tablename__ = "gifts"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("wedding_events.id"), nullable=False, index=True)
    gift_name = Column(String(190), nullable=False, index=True)
    gift_description = Column(Text, nullable=True)
    gift_category = Column(
        String(50),
        nullable=False,
        default="Other"
    )  # Household Items, Clothing, Cash, Jewelry, Electronics, Decorative Items, Other, Unknown
    quantity = Column(Integer, default=1)
    gift_date = Column(Date, default=date.today)
    is_cash = Column(Boolean, default=False)
    cash_amount = Column(Numeric(12, 2), nullable=True)  # Optional! Never assume missing cash amounts
    currency = Column(String(10), default="BDT")
    original_note = Column(Text, nullable=False)  # Mandatory: preserves exact handwritten text
    additional_notes = Column(Text, nullable=True)
    review_status = Column(
        String(50),
        default="confirmed",
        index=True
    )  # confirmed, requires_review, unidentified
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event = relationship("WeddingEvent", back_populates="gifts")
    contributors = relationship("GiftContributor", back_populates="gift", cascade="all, delete-orphan")
    thank_you_messages = relationship("ThankYouMessage", back_populates="gift", cascade="all, delete-orphan")
    reciprocity_records = relationship("GiftExchangeHistory", back_populates="reference_gift")
