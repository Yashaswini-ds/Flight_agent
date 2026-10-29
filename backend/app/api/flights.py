from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.flight_service import FlightService
from app.schemas.flight import FlightResponse, CityResponse, SeatResponse
from app.models.flight import TravelClass

router = APIRouter(prefix="/api/flights", tags=["Flights"])

@router.get("/cities", response_model=List[CityResponse])
def get_cities(db: Session = Depends(get_db)):
    service = FlightService(db)
    return service.get_cities()

@router.get("/search", response_model=List[FlightResponse])
def search_flights(
    origin: str = Query(..., description="Origin city code (e.g., BLR)"),
    destination: str = Query(..., description="Destination city code (e.g., DEL)"),
    travel_date: str = Query(..., description="Date YYYY-MM-DD"),
    passenger_count: int = Query(1, ge=1, le=9),
    travel_class: TravelClass = Query(TravelClass.ECONOMY),
    db: Session = Depends(get_db)
):
    service = FlightService(db)
    return service.search_flights(
        origin=origin,
        destination=destination,
        travel_date_str=travel_date,
        passenger_count=passenger_count,
        travel_class=travel_class
    )

@router.get("/{flight_id}", response_model=FlightResponse)
def get_flight_by_id(flight_id: str, db: Session = Depends(get_db)):
    service = FlightService(db)
    return service.get_flight_details(flight_id)

@router.get("/{flight_id}/seats", response_model=List[SeatResponse])
def get_flight_seats(
    flight_id: str,
    travel_class: TravelClass = Query(TravelClass.ECONOMY),
    db: Session = Depends(get_db)
):
    service = FlightService(db)
    return service.get_flight_seats(flight_id, travel_class)
