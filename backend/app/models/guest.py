from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Guest(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(190), nullable=False, index=True)  # e.g., "Rahman Uncle", "Unknown Guest"
    relationship_type = Column(String(100), default="Guest")  # e.g., "Uncle", "Khala", "Friend", "Unknown"
    phone_number = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    family_group = Column(String(190), nullable=True, index=True)  # e.g., "Chittagong Family", "Rahman Family"
    is_unidentified = Column(Boolean, default=False, index=True)  # True for unidentified guests
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False)  # Soft deletion to preserve reciprocity records
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contributions = relationship("GiftContributor", back_populates="guest")
    thank_you_messages = relationship("ThankYouMessage", back_populates="guest")
    exchanges = relationship("GiftExchangeHistory", back_populates="guest")
