from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ThankYouMessage(Base):
    __tablename__ = "thank_you_messages"

    id = Column(Integer, primary_key=True, index=True)
    gift_id = Column(Integer, ForeignKey("gifts.id", ondelete="CASCADE"), nullable=False, index=True)
    guest_id = Column(Integer, ForeignKey("guests.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = Column(String(50), default="pending", index=True)  # draft, pending, sent
    tone = Column(String(50), default="warm")  # formal, warm, friendly, short, detailed
    message_text = Column(Text, nullable=False)
    sent_date = Column(DateTime, nullable=True)
    sent_via = Column(String(50), nullable=True)  # WhatsApp, SMS, Printed Card, In Person
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    gift = relationship("Gift", back_populates="thank_you_messages")
    guest = relationship("Guest", back_populates="thank_you_messages")
    status_history = relationship("ThankYouStatusHistory", back_populates="message", cascade="all, delete-orphan")

class ThankYouStatusHistory(Base):
    __tablename__ = "thank_you_status_history"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("thank_you_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    change_reason = Column(Text, nullable=True)

    # Relationship
    message = relationship("ThankYouMessage", back_populates="status_history")
