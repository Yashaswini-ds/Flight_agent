import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
import enum

class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class TicketCategory(str, enum.Enum):
    BOOKING = "BOOKING"
    PAYMENT = "PAYMENT"
    CANCELLATION = "CANCELLATION"
    GENERAL = "GENERAL"

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    booking_reference: Mapped[str] = mapped_column(String(20), nullable=True)
    category: Mapped[TicketCategory] = mapped_column(Enum(TicketCategory), default=TicketCategory.GENERAL, nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    admin_response: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="support_tickets")
