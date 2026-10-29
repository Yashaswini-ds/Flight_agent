import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.flight import City, Airport, Airline, Flight, FlightFare, FlightSeat, TravelClass
from datetime import datetime, timedelta, timezone
import uuid

# Use in-memory SQLite database engine strictly for Pytest isolated testing
TEST_ENGINE = create_engine("sqlite:///:memory:", echo=False)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)

@pytest.fixture(scope="function")
def db_session(setup_test_db):
    from app.agents.state import SessionManager
    SessionManager.clear()
    connection = TEST_ENGINE.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
    SessionManager.clear()


@pytest.fixture(scope="function")
def seeded_db(db_session):
    # Seed 5 cities
    cities = [
        City(id=str(uuid.uuid4()), code="BLR", name="Bengaluru", state="Karnataka"),
        City(id=str(uuid.uuid4()), code="MAA", name="Chennai", state="Tamil Nadu"),
        City(id=str(uuid.uuid4()), code="HYD", name="Hyderabad", state="Telangana"),
        City(id=str(uuid.uuid4()), code="BOM", name="Mumbai", state="Maharashtra"),
        City(id=str(uuid.uuid4()), code="DEL", name="Delhi", state="Delhi"),
    ]
    db_session.add_all(cities)

    # Seed Airline
    airline = Airline(id=str(uuid.uuid4()), code="DA", name="Demo Air")
    db_session.add(airline)

    # Seed User & Admin
    user = User(
        id="user-123",
        email="testuser@flightagent.com",
        password_hash=get_password_hash("password123"),
        full_name="Test User",
        role=UserRole.USER
    )
    admin = User(
        id="admin-123",
        email="testadmin@flightagent.com",
        password_hash=get_password_hash("adminpass123"),
        full_name="Test Admin",
        role=UserRole.ADMIN
    )
    db_session.add_all([user, admin])

    # Seed Flight BLR -> DEL
    dep = datetime.now(timezone.utc) + timedelta(days=2)
    flight = Flight(
        id="flight-123",
        flight_number="DA-101",
        airline_code="DA",
        origin_code="BLR",
        destination_code="DEL",
        departure_time=dep,
        arrival_time=dep + timedelta(hours=2, minutes=30),
        duration_minutes=150,
        stops=0,
        status="SCHEDULED"
    )
    db_session.add(flight)

    # Fares
    fare_econ = FlightFare(
        id=str(uuid.uuid4()),
        flight_id=flight.id,
        travel_class=TravelClass.ECONOMY,
 base_fare=4000.0,
        seats_available=20,
        baggage_allowance_kg=15,
        cabin_baggage_kg=7
    )
    fare_biz = FlightFare(
        id=str(uuid.uuid4()),
        flight_id=flight.id,
        travel_class=TravelClass.BUSINESS,
        base_fare=10000.0,
        seats_available=5,
        baggage_allowance_kg=30,
        cabin_baggage_kg=10
    )
    db_session.add_all([fare_econ, fare_biz])

    # Seats
    seat1 = FlightSeat(id=str(uuid.uuid4()), flight_id=flight.id, seat_number="12A", travel_class=TravelClass.ECONOMY, is_booked=False, price_extra=300.0)
    seat2 = FlightSeat(id=str(uuid.uuid4()), flight_id=flight.id, seat_number="12B", travel_class=TravelClass.ECONOMY, is_booked=False, price_extra=0.0)
    db_session.add_all([seat1, seat2])

    db_session.commit()
    return db_session
