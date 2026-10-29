import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User, UserRole
from app.models.flight import City, Airport, Airline, Flight, FlightFare, FlightSeat, TravelClass
from app.core.security import get_password_hash

def seed_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        print("Seeding Database with predefined cities, multiple daily flights per route, and demo accounts...")

        # 1. Cities
        cities_data = [
            {"code": "BLR", "name": "Bengaluru", "state": "Karnataka"},
            {"code": "MAA", "name": "Chennai", "state": "Tamil Nadu"},
            {"code": "HYD", "name": "Hyderabad", "state": "Telangana"},
            {"code": "BOM", "name": "Mumbai", "state": "Maharashtra"},
            {"code": "DEL", "name": "Delhi", "state": "Delhi"}
        ]
        for c in cities_data:
            db.add(City(id=str(uuid.uuid4()), code=c["code"], name=c["name"], state=c["state"]))

        # 2. Airports
        airports_data = [
            {"code": "BLR", "name": "Kempegowda International Airport", "city_code": "BLR"},
            {"code": "MAA", "name": "Chennai International Airport", "city_code": "MAA"},
            {"code": "HYD", "name": "Rajiv Gandhi International Airport", "city_code": "HYD"},
            {"code": "BOM", "name": "Chhatrapati Shivaji Maharaj Intl Airport", "city_code": "BOM"},
            {"code": "DEL", "name": "Indira Gandhi International Airport", "city_code": "DEL"}
        ]
        for a in airports_data:
            db.add(Airport(id=str(uuid.uuid4()), code=a["code"], name=a["name"], city_code=a["city_code"]))

        # 3. Airlines
        airlines_data = [
            {"code": "DA", "name": "Demo Air"},
            {"code": "SE", "name": "SkyExpress"},
            {"code": "IF", "name": "IndiaFly"}
        ]
        for al in airlines_data:
            db.add(Airline(id=str(uuid.uuid4()), code=al["code"], name=al["name"]))

        db.flush()

        # 4. Demo Users
        user_demo = User(
            id=str(uuid.uuid4()),
            email="user@flightagent.com",
            password_hash=get_password_hash("user123"),
            full_name="Rahul Sharma",
            phone="+91 9876543210",
            role=UserRole.USER
        )
        admin_demo = User(
            id=str(uuid.uuid4()),
            email="admin@flightagent.com",
            password_hash=get_password_hash("admin123"),
            full_name="System Admin",
            phone="+91 9999999999",
            role=UserRole.ADMIN
        )
        db.add_all([user_demo, admin_demo])

        # 5. Flights across next 30 days - 4 flights per route per day
        city_codes = ["BLR", "MAA", "HYD", "BOM", "DEL"]
        airline_codes = ["DA", "SE", "IF"]
        flight_slots = [
            {"dep_hour": 6, "dep_min": 15, "airline_idx": 0, "fare_mult": 1.0},
            {"dep_hour": 11, "dep_min": 30, "airline_idx": 1, "fare_mult": 1.15},
            {"dep_hour": 16, "dep_min": 45, "airline_idx": 2, "fare_mult": 1.25},
            {"dep_hour": 21, "dep_min": 0, "airline_idx": 0, "fare_mult": 0.95},
        ]
        
        now = datetime.now(timezone.utc)
        flight_count = 0

        for day_offset in range(0, 30):
            target_date = now + timedelta(days=day_offset)
            for i, src in enumerate(city_codes):
                for j, dst in enumerate(city_codes):
                    if src == dst:
                        continue

                    for slot_idx, slot in enumerate(flight_slots):
                        airline_code = airline_codes[(slot["airline_idx"] + i + j) % len(airline_codes)]
                        flight_num = f"{airline_code}-{100 + (slot_idx * 100) + (i * 10) + j}"

                        dep_dt = target_date.replace(hour=slot["dep_hour"], minute=slot["dep_min"], second=0, microsecond=0)
                        duration = 90 + ((i + j + slot_idx) * 15) % 105
                        arr_dt = dep_dt + timedelta(minutes=duration)

                        flight = Flight(
                            id=str(uuid.uuid4()),
                            flight_number=flight_num,
                            airline_code=airline_code,
                            origin_code=src,
                            destination_code=dst,
                            departure_time=dep_dt,
                            arrival_time=arr_dt,
                            duration_minutes=duration,
                            stops=0,
                            status="SCHEDULED"
                        )
                        db.add(flight)

                        # Fares
                        base_econ = round((3200.0 + ((i + j) * 350)) * slot["fare_mult"], 2)
                        fare_econ = FlightFare(
                            id=str(uuid.uuid4()),
                            flight_id=flight.id,
                            travel_class=TravelClass.ECONOMY,
                            base_fare=base_econ,
                            seats_available=40,
                            baggage_allowance_kg=15,
                            cabin_baggage_kg=7
                        )
                        fare_prem = FlightFare(
                            id=str(uuid.uuid4()),
                            flight_id=flight.id,
                            travel_class=TravelClass.PREMIUM_ECONOMY,
                            base_fare=round(base_econ * 1.4, 2),
                            seats_available=12,
                            baggage_allowance_kg=20,
                            cabin_baggage_kg=7
                        )
                        fare_biz = FlightFare(
                            id=str(uuid.uuid4()),
                            flight_id=flight.id,
                            travel_class=TravelClass.BUSINESS,
                            base_fare=round(base_econ * 2.5, 2),
                            seats_available=8,
                            baggage_allowance_kg=30,
                            cabin_baggage_kg=10
                        )
                        db.add_all([fare_econ, fare_prem, fare_biz])

                        # Seat Map Generator
                        seats = []
                        for row in range(10, 16):
                            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                                s_num = f"{row}{col}"
                                extra = 300.0 if col in ['A', 'F'] else 0.0
                                seats.append(FlightSeat(
                                    id=str(uuid.uuid4()),
                                    flight_id=flight.id,
                                    seat_number=s_num,
                                    travel_class=TravelClass.ECONOMY,
                                    is_booked=False,
                                    price_extra=extra
                                ))
                        for row in range(1, 3):
                            for col in ['A', 'B', 'C', 'D']:
                                s_num = f"{row}{col}"
                                seats.append(FlightSeat(
                                    id=str(uuid.uuid4()),
                                    flight_id=flight.id,
                                    seat_number=s_num,
                                    travel_class=TravelClass.BUSINESS,
                                    is_booked=False,
                                    price_extra=0.0
                                ))
                        db.add_all(seats)
                        flight_count += 1

        db.commit()
        print(f"Successfully seeded {flight_count} flights (4 options per route/day) across 30 days!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
