from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.flight import TravelClass
from app.models.booking import BookingStatus

class PassengerInput(BaseModel):
    first_name: str
    last_name: str
    age: int = Field(..., ge=1, le=120)
    gender: str
    seat_number: Optional[str] = None

class CreateBookingRequest(BaseModel):
    flight_id: str
    travel_class: TravelClass
    travel_date: str # YYYY-MM-DD
    passengers: List[PassengerInput]
    extra_baggage_kg: int = 0

class PassengerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    first_name: str
    last_name: str
    age: int
    gender: str
    seat_number: Optional[str]

class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    booking_reference: str
    pnr: str
    user_id: str
    flight_id: str
    airline_name: str
    flight_number: str
    origin_code: str
    origin_city: str
    destination_code: str
    destination_city: str
    departure_time: datetime
    arrival_time: datetime
    travel_class: TravelClass
    travel_date: datetime
    passenger_count: int
    base_fare: float
    seat_addons_fee: float
    baggage_addons_fee: float
    taxes: float
    total_fare: float
    status: BookingStatus
    created_at: datetime
    passengers: List[PassengerResponse]

class ModifyBookingRequest(BaseModel):
    new_travel_date: Optional[str] = None # YYYY-MM-DD
    new_travel_class: Optional[TravelClass] = None

class CancelBookingRequest(BaseModel):
    reason: Optional[str] = "Customer requested cancellation"
