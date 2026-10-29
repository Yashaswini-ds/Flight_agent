import pytest
from app.services.booking_service import BookingService
from app.services.refund_service import RefundService
from app.schemas.booking import CreateBookingRequest, PassengerInput
from app.models.flight import TravelClass
from app.models.booking import BookingStatus
from app.core.exceptions import BadRequestException
from datetime import datetime, timedelta, timezone

def test_deterministic_refund_formulas(seeded_db):
    b_service = BookingService(seeded_db)
    refund_service = RefundService(seeded_db)

    # 1. > 72 hours departure: 90% refund (10% fee)
    target_date = (datetime.now(timezone.utc) + timedelta(days=5)).strftime("%Y-%m-%d")
    req = CreateBookingRequest(
        flight_id="flight-123",
        travel_class=TravelClass.ECONOMY,
        travel_date=target_date,
        passengers=[PassengerInput(first_name="Karan", last_name="Mehta", age=32, gender="Male")]
    )
    b_far = b_service.create_booking(user_id="user-123", request=req)
    b_obj_far = b_service.booking_repo.get_by_id(b_far.id)

    # Manually override departure_time for deterministic test rule
    b_obj_far.flight.departure_time = datetime.now(timezone.utc) + timedelta(hours=96)
    seeded_db.commit()

    calc_far = refund_service.calculate_deterministic_refund(b_obj_far)
    assert calc_far["fee_percentage"] == 10
    assert calc_far["cancellation_fee"] == round(b_obj_far.total_fare * 0.10, 2)
    assert calc_far["net_refund_amount"] == round(b_obj_far.total_fare * 0.90, 2)

    # 2. 24-72 hours departure: 70% refund (30% fee)
    b_mid = b_service.create_booking(user_id="user-123", request=req)
    b_obj_mid = b_service.booking_repo.get_by_id(b_mid.id)
    b_obj_mid.flight.departure_time = datetime.now(timezone.utc) + timedelta(hours=48)
    seeded_db.commit()

    calc_mid = refund_service.calculate_deterministic_refund(b_obj_mid)
    assert calc_mid["fee_percentage"] == 30

    # 3. < 24 hours departure: 50% refund (50% fee)
    b_close = b_service.create_booking(user_id="user-123", request=req)
    b_obj_close = b_service.booking_repo.get_by_id(b_close.id)
    b_obj_close.flight.departure_time = datetime.now(timezone.utc) + timedelta(hours=12)
    seeded_db.commit()

    calc_close = refund_service.calculate_deterministic_refund(b_obj_close)
    assert calc_close["fee_percentage"] == 50

def test_cancel_and_process_refund_execution(seeded_db):
    b_service = BookingService(seeded_db)
    refund_service = RefundService(seeded_db)

    target_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
    req = CreateBookingRequest(
        flight_id="flight-123",
        travel_class=TravelClass.ECONOMY,
        travel_date=target_date,
        passengers=[PassengerInput(first_name="Sanjay", last_name="Kumar", age=40, gender="Male", seat_number="12A")]
    )
    b_created = b_service.create_booking(user_id="user-123", request=req)
    
    # Confirm booking
    b_obj = b_service.booking_repo.get_by_id(b_created.id)
    b_obj.status = BookingStatus.CONFIRMED
    seeded_db.commit()

    # Cancel & refund
    res = refund_service.cancel_and_process_refund(booking_id=b_created.id, user_id="user-123", reason="Test cancel")

    assert res.refund_reference.startswith("RF-")
    assert res.status == "PROCESSED"

    b_updated = b_service.booking_repo.get_by_id(b_created.id)
    assert b_updated.status == BookingStatus.REFUNDED

def test_duplicate_cancellation_prevention(seeded_db):
    b_service = BookingService(seeded_db)
    refund_service = RefundService(seeded_db)

    target_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
    req = CreateBookingRequest(
        flight_id="flight-123",
        travel_class=TravelClass.ECONOMY,
        travel_date=target_date,
        passengers=[PassengerInput(first_name="Sunil", last_name="Verma", age=29, gender="Male")]
    )
    b_created = b_service.create_booking(user_id="user-123", request=req)
    refund_service.cancel_and_process_refund(booking_id=b_created.id, user_id="user-123")

    # Second attempt should raise BadRequestException
    with pytest.raises(BadRequestException):
        refund_service.cancel_and_process_refund(booking_id=b_created.id, user_id="user-123")
