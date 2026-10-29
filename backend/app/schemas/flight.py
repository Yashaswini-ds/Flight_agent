from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.flight import TravelClass

class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    state: str

class FlightFareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    travel_class: TravelClass
    base_fare: float
    seats_available: int
    baggage_allowance_kg: int
    cabin_baggage_kg: int

class SeatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    seat_number: str
    travel_class: TravelClass
    is_booked: bool
    price_extra: float

class FlightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    flight_number: str
    airline_code: str
    airline_name: str
    origin_code: str
    origin_city: str
    destination_code: str
    destination_city: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    stops: int
    status: str
    fares: List[FlightFareResponse]

class FlightSearchRequest(BaseModel):
    origin: str
    destination: str
    travel_date: str  # YYYY-MM-DD
    passenger_count: int = Field(1, ge=1, le=9)
    travel_class: TravelClass = TravelClass.ECONOMY
