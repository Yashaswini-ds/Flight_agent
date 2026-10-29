import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.flight import TravelClass

class BookingStatus(str, enum.Enum):
    BOOKED = "BOOKED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    PARTIALLY_CANCELLED = "PARTIALLY_CANCELLED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"
    COMPLETED = "COMPLETED"

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_reference: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    pnr: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    flight_id: Mapped[str] = mapped_column(String(36), ForeignKey("flights.id"), nullable=False)
    travel_class: Mapped[TravelClass] = mapped_column(Enum(TravelClass), nullable=False)
    travel_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    passenger_count: Mapped[int] = mapped_column(Integer, nullable=False)
    base_fare: Mapped[float] = mapped_column(Float, nullable=False)
    seat_addons_fee: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    baggage_addons_fee: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    taxes: Mapped[float] = mapped_column(Float, nullable=False)
    total_fare: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.PAYMENT_PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="bookings")
    flight = relationship("Flight")
    passengers = relationship("BookingPassenger", back_populates="booking", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    refund = relationship("Refund", back_populates="booking", uselist=False, cascade="all, delete-orphan")

class BookingPassenger(Base):
    __tablename__ = "booking_passengers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id: Mapped[str] = mapped_column(String(36), ForeignKey("bookings.id"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    seat_number: Mapped[str] = mapped_column(String(10), nullable=True)
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    booking = relationship("Booking", back_populates="passengers")
