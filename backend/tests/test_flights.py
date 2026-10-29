import pytest
from app.services.flight_service import FlightService
from app.models.flight import TravelClass
from app.core.exceptions import BadRequestException, NotFoundException
from datetime import datetime, timedelta

def test_get_predefined_cities(seeded_db):
    service = FlightService(seeded_db)
    cities = service.get_cities()

    assert len(cities) == 5
    codes = [c.code for c in cities]
    assert "BLR" in codes
    assert "MAA" in codes
    assert "HYD" in codes
    assert "BOM" in codes
    assert "DEL" in codes

def test_search_flights_valid(seeded_db):
    service = FlightService(seeded_db)
    target_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

    results = service.search_flights(
        origin="BLR",
        destination="DEL",
        travel_date_str=target_date,
        passenger_count=1,
        travel_class=TravelClass.ECONOMY
    )

    assert len(results) >= 1
    assert results[0].origin_code == "BLR"
    assert results[0].destination_code == "DEL"

def test_search_flights_same_origin_destination_fails(seeded_db):
    service = FlightService(seeded_db)
    target_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

    with pytest.raises(BadRequestException):
        service.search_flights(
            origin="BLR",
            destination="BLR",
            travel_date_str=target_date,
            passenger_count=1,
            travel_class=TravelClass.ECONOMY
        )

def test_get_flight_seats(seeded_db):
    service = FlightService(seeded_db)
    seats = service.get_flight_seats("flight-123", TravelClass.ECONOMY)

    assert len(seats) == 2
    seat_numbers = [s.seat_number for s in seats]
    assert "12A" in seat_numbers
    assert "12B" in seat_numbers
