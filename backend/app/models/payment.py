import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
import app.models.booking
import enum

class PaymentStatus(str, enum.Enum):
    INTENT_CREATED = "INTENT_CREATED"
    AUTHORIZED = "AUTHORIZED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class PaymentMethod(str, enum.Enum):
    UPI = "UPI"
    QR = "QR"
    CARD = "CARD"

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id: Mapped[str] = mapped_column(String(36), ForeignKey("bookings.id"), nullable=False)
    payment_intent_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    transaction_reference: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    ap2_consent_token: Mapped[str] = mapped_column(String(128), nullable=True)
    ap2_mandate_id: Mapped[str] = mapped_column(String(64), nullable=True)
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.INTENT_CREATED, nullable=False)
    payment_details_masked: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    booking = relationship("Booking", back_populates="payment")
