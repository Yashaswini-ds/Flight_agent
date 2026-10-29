from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.flight_repository import FlightRepository
from app.models.flight import TravelClass, Flight, City, FlightSeat
from app.schemas.flight import FlightResponse, FlightFareResponse, CityResponse, SeatResponse
from app.core.exceptions import NotFoundException, BadRequestException

class FlightService:
    def __init__(self, db: Session):
        self.db = db
        self.flight_repo = FlightRepository(db)

    def get_cities(self) -> List[CityResponse]:
        cities = self.flight_repo.get_cities()
        return [CityResponse.model_validate(c) for c in cities]

    def search_flights(
        self,
        origin: str,
        destination: str,
        travel_date_str: str,
        passenger_count: int,
        travel_class: TravelClass
    ) -> List[FlightResponse]:
        if origin.upper() == destination.upper():
            raise BadRequestException("Source and Destination cities cannot be the same")
        
        try:
            travel_date = datetime.strptime(travel_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise BadRequestException("Invalid travel date format. Expected YYYY-MM-DD")

        flights = self.flight_repo.search_flights(
            origin_code=origin,
            destination_code=destination,
            travel_date=travel_date,
            travel_class=travel_class,
            passenger_count=passenger_count
        )

        results = []
        for flight in flights:
            fares_resp = [
                FlightFareResponse.model_validate(f)
                for f in flight.fares
                if f.travel_class == travel_class
            ]
            results.append(
                FlightResponse(
                    id=flight.id,
                    flight_number=flight.flight_number,
                    airline_code=flight.airline.code,
                    airline_name=flight.airline.name,
                    origin_code=flight.origin.code,
                    origin_city=flight.origin.name,
                    destination_code=flight.destination.code,
                    destination_city=flight.destination.name,
                    departure_time=flight.departure_time,
                    arrival_time=flight.arrival_time,
                    duration_minutes=flight.duration_minutes,
                    stops=flight.stops,
                    status=flight.status,
                    fares=fares_resp
                )
            )
        return results

    def get_flight_details(self, flight_id: str) -> FlightResponse:
        flight = self.flight_repo.get_flight_by_id(flight_id)
        if not flight:
            raise NotFoundException("Flight not found")
        fares_resp = [FlightFareResponse.model_validate(f) for f in flight.fares]
        return FlightResponse(
            id=flight.id,
            flight_number=flight.flight_number,
            airline_code=flight.airline.code,
            airline_name=flight.airline.name,
            origin_code=flight.origin.code,
            origin_city=flight.origin.name,
            destination_code=flight.destination.code,
            destination_city=flight.destination.name,
            departure_time=flight.departure_time,
            arrival_time=flight.arrival_time,
            duration_minutes=flight.duration_minutes,
            stops=flight.stops,
            status=flight.status,
            fares=fares_resp
        )

    def get_flight_by_number(self, flight_number: str) -> Optional[FlightResponse]:
        flight = self.flight_repo.get_flight_by_number(flight_number)
        if not flight:
            return None
        fares_resp = [FlightFareResponse.model_validate(f) for f in flight.fares]
        return FlightResponse(
            id=flight.id,
            flight_number=flight.flight_number,
            airline_code=flight.airline.code,
            airline_name=flight.airline.name,
            origin_code=flight.origin.code,
            origin_city=flight.origin.name,
            destination_code=flight.destination.code,
            destination_city=flight.destination.name,
            departure_time=flight.departure_time,
            arrival_time=flight.arrival_time,
            duration_minutes=flight.duration_minutes,
            stops=flight.stops,
            status=flight.status,
            fares=fares_resp
        )

    def get_flight_seats(self, flight_id: str, travel_class: TravelClass) -> List[SeatResponse]:
        seats = self.flight_repo.get_seats_for_flight(flight_id, travel_class)
        return [SeatResponse.model_validate(s) for s in seats]

