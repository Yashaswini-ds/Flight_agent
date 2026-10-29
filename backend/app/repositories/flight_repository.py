from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.flight import Flight, City, Airport, Airline, FlightFare, FlightSeat, TravelClass

class FlightRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_cities(self) -> List[City]:
        return self.db.query(City).all()

    def get_flight_by_id(self, flight_id: str) -> Optional[Flight]:
        return self.db.query(Flight).filter(Flight.id == flight_id).first()

    def search_flights(
        self,
        origin_code: str,
        destination_code: str,
        travel_date: date,
        travel_class: TravelClass,
        passenger_count: int
    ) -> List[Flight]:
        # Search flights matching origin, destination, class and passenger count
        start_of_day = datetime.combine(travel_date, datetime.min.time())
        end_of_day = datetime.combine(travel_date, datetime.max.time())

        flights = (
            self.db.query(Flight)
            .join(FlightFare, Flight.id == FlightFare.flight_id)
            .filter(
                Flight.origin_code == origin_code.upper(),
                Flight.destination_code == destination_code.upper(),
                Flight.departure_time >= start_of_day,
                Flight.departure_time <= end_of_day,
                FlightFare.travel_class == travel_class,
                FlightFare.seats_available >= passenger_count
            )
            .all()
        )
        return flights

    def get_flight_by_number(self, flight_number: str) -> Optional[Flight]:
        return (
            self.db.query(Flight)
            .filter(func.upper(Flight.flight_number) == flight_number.upper())
            .first()
        )

    def get_seats_for_flight(self, flight_id: str, travel_class: TravelClass) -> List[FlightSeat]:
        return (
            self.db.query(FlightSeat)
            .filter(FlightSeat.flight_id == flight_id, FlightSeat.travel_class == travel_class)
            .all()
        )

