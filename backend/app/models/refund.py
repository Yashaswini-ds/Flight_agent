import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
import enum

class RefundStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

class Refund(Base):
    __tablename__ = "refunds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id: Mapped[str] = mapped_column(String(36), ForeignKey("bookings.id"), nullable=False)
    refund_reference: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    gross_amount: Mapped[float] = mapped_column(Float, nullable=False)
    cancellation_fee: Mapped[float] = mapped_column(Float, nullable=False)
    net_refund_amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[RefundStatus] = mapped_column(Enum(RefundStatus), default=RefundStatus.PENDING, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    booking = relationship("Booking", back_populates="refund")
