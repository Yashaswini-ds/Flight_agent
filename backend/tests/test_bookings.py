import pytest
from app.services.booking_service import BookingService
from app.schemas.booking import CreateBookingRequest, PassengerInput, ModifyBookingRequest
from app.models.flight import TravelClass
from app.models.booking import BookingStatus
from app.core.exceptions import BadRequestException, NotFoundException
from datetime import datetime, timedelta

def test_create_booking_draft_and_fare_calc(seeded_db):
    service = BookingService(seeded_db)
    target_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

    req = CreateBookingRequest(
        flight_id="flight-123",
        travel_class=TravelClass.ECONOMY,
        travel_date=target_date,
        passengers=[
            PassengerInput(first_name="Rahul", last_name="Sharma", age=30, gender="Male", seat_number="12A")
        ],
        extra_baggage_kg=5
    )

    res = service.create_booking(user_id="user-123", request=req)

    assert res.id is not None
    assert res.pnr is not None
    assert len(res.pnr) == 6
    assert res.booking_reference.startswith("BK-")
    assert res.status == BookingStatus.PAYMENT_PENDING
    assert res.passenger_count == 1
    assert res.seat_addons_fee == 300.0  # 12A seat fee
    assert res.baggage_addons_fee == 1500.0  # 5kg * ₹300

    # Base: ₹4000, Seat: ₹300, Baggage: ₹1500 -> Subtotal: ₹5800. Tax 18%: ₹1044 -> Total: ₹6844
    assert res.base_fare == 4000.0
    assert res.taxes == 1044.0
    assert res.total_fare == 6844.0

def test_get_booking_by_reference(seeded_db):
    service = BookingService(seeded_db)
    target_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

    req = CreateBookingRequest(
        flight_id="flight-123",
        travel_class=TravelClass.ECONOMY,
        travel_date=target_date,
        passengers=[
            PassengerInput(first_name="Anita", last_name="Roy", age=28, gender="Female")
        ]
    )
    b_created = service.create_booking(user_id="user-123", request=req)

    b_fetched = service.get_booking(b_created.booking_reference, user_id="user-123")
    assert b_fetched.id == b_created.id
    assert b_fetched.pnr == b_created.pnr

def test_modify_booking(seeded_db):
    service = BookingService(seeded_db)
    target_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    new_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

    req = CreateBookingRequest(
        flight_id="flight-123",
        travel_class=TravelClass.ECONOMY,
        travel_date=target_date,
        passengers=[
            PassengerInput(first_name="Vikram", last_name="Singh", age=35, gender="Male")
        ]
    )
    b_created = service.create_booking(user_id="user-123", request=req)

    mod_req = ModifyBookingRequest(new_travel_date=new_date, new_travel_class=TravelClass.BUSINESS)
    b_modified = service.modify_booking(b_created.id, user_id="user-123", request=mod_req)

    assert b_modified.travel_class == TravelClass.BUSINESS
