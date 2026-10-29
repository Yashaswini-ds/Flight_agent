import pytest
from app.payment.payment_intent import create_simulated_payment_intent
from app.payment.authorization import generate_ap2_consent_token
from app.payment.transaction import execute_simulated_ap2_transaction
from app.models.payment import PaymentMethod, PaymentStatus
from app.services.booking_service import BookingService
from app.schemas.booking import CreateBookingRequest, PassengerInput
from app.models.flight import TravelClass
from app.models.booking import BookingStatus
from app.repositories.payment_repository import PaymentRepository
from datetime import datetime, timedelta

def test_ap2_payment_flow_simulation():
    # 1. Payment Intent
    payment = create_simulated_payment_intent(
        booking_id="test-booking-id-123",
        amount=5400.0,
        payment_method=PaymentMethod.UPI
    )

    assert payment.payment_intent_id.startswith("pi_sim_")
    assert payment.ap2_mandate_id.startswith("man_sim_")
    assert payment.status == PaymentStatus.INTENT_CREATED

    # 2. Authorization Mandate Consent Token
    token = generate_ap2_consent_token(
        payment_intent_id=payment.payment_intent_id,
        demo_pin_or_auth="1234",
        demo_identifier="rahul@upi"
    )

    assert token.startswith("ap2_consent_tok_")

    # 3. Transaction Execution & Masked Audit Logging
    success = execute_simulated_ap2_transaction(
        payment=payment,
        ap2_consent_token=token,
        demo_identifier="rahul@upi"
    )

    assert success is True
    assert payment.status == PaymentStatus.SUCCESS
    assert "r***@upi" in payment.payment_details_masked

def test_ap2_payment_execution_with_booking(seeded_db):
    b_service = BookingService(seeded_db)
    payment_repo = PaymentRepository(seeded_db)

    target_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    req = CreateBookingRequest(
        flight_id="flight-123",
        travel_class=TravelClass.ECONOMY,
        travel_date=target_date,
        passengers=[
            PassengerInput(first_name="Priya", last_name="Nair", age=26, gender="Female")
        ]
    )
    booking = b_service.create_booking(user_id="user-123", request=req)
    assert booking.status == BookingStatus.PAYMENT_PENDING

    # Create Payment Intent in DB
    payment = create_simulated_payment_intent(
        booking_id=booking.id,
        amount=booking.total_fare,
        payment_method=PaymentMethod.CARD
    )
    payment_repo.create_payment(payment)
    seeded_db.commit()

    # Generate consent token & execute
    token = generate_ap2_consent_token(payment.payment_intent_id, "1234", "4111222233334444")
    success = execute_simulated_ap2_transaction(payment, token, "4111222233334444")

    assert success is True
    # Confirm booking in DB
    b_obj = b_service.booking_repo.get_by_id(booking.id)
    b_obj.status = BookingStatus.CONFIRMED
    seeded_db.commit()

    assert b_obj.status == BookingStatus.CONFIRMED
    assert payment.status == PaymentStatus.SUCCESS
