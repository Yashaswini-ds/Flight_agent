import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
import enum

class TravelClass(str, enum.Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"

class City(Base):
    __tablename__ = "cities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)  # e.g., BLR
    name: Mapped[str] = mapped_column(String(100), nullable=False)                          # e.g., Bengaluru
    state: Mapped[str] = mapped_column(String(100), nullable=False)                         # e.g., Karnataka

class Airport(Base):
    __tablename__ = "airports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)  # e.g., BLR
    name: Mapped[str] = mapped_column(String(150), nullable=False)                         # Kempegowda Intl
    city_code: Mapped[str] = mapped_column(String(10), ForeignKey("cities.code"), nullable=False)

class Airline(Base):
    __tablename__ = "airlines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)  # e.g., DA
    name: Mapped[str] = mapped_column(String(100), nullable=False)                         # Demo Air
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)

class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flight_number: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    airline_code: Mapped[str] = mapped_column(String(10), ForeignKey("airlines.code"), nullable=False)
    origin_code: Mapped[str] = mapped_column(String(10), ForeignKey("cities.code"), nullable=False)
    destination_code: Mapped[str] = mapped_column(String(10), ForeignKey("cities.code"), nullable=False)
    departure_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    stops: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="SCHEDULED", nullable=False)

    airline = relationship("Airline")
    origin = relationship("City", foreign_keys=[origin_code])
    destination = relationship("City", foreign_keys=[destination_code])
    fares = relationship("FlightFare", back_populates="flight", cascade="all, delete-orphan")
    seats = relationship("FlightSeat", back_populates="flight", cascade="all, delete-orphan")

class FlightFare(Base):
    __tablename__ = "flight_fares"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flight_id: Mapped[str] = mapped_column(String(36), ForeignKey("flights.id"), nullable=False)
    travel_class: Mapped[TravelClass] = mapped_column(Enum(TravelClass), nullable=False)
    base_fare: Mapped[float] = mapped_column(Float, nullable=False)
    seats_available: Mapped[int] = mapped_column(Integer, nullable=False)
    baggage_allowance_kg: Mapped[int] = mapped_column(Integer, nullable=False)
    cabin_baggage_kg: Mapped[int] = mapped_column(Integer, nullable=False)

    flight = relationship("Flight", back_populates="fares")

class FlightSeat(Base):
    __tablename__ = "seats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flight_id: Mapped[str] = mapped_column(String(36), ForeignKey("flights.id"), nullable=False)
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False) # e.g., 12A
    travel_class: Mapped[TravelClass] = mapped_column(Enum(TravelClass), nullable=False)
    is_booked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    price_extra: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    flight = relationship("Flight", back_populates="seats")
