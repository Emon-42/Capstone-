from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class WeddingEvent(Base):
    __tablename__ = "wedding_events"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(255), nullable=False)  # e.g., "Farhana & Tanvir's Wedding"
    event_date = Column(Date, nullable=False, default=date.today)
    venue = Column(String(255), nullable=True)
    host_family = Column(String(255), default="Farhana's Family")
    is_primary = Column(Boolean, default=False)  # Primary wedding event
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    gifts = relationship("Gift", back_populates="event", cascade="all, delete-orphan")
    exchanges = relationship("GiftExchangeHistory", back_populates="event")
