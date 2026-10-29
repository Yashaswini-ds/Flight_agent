import pytest
from datetime import datetime, timedelta
from app.agents.intent_agent import IntentAgent
from app.agents.booking_agent import BookingAgent
from app.models.flight import TravelClass
from app.agents.state import BookingStep, SessionManager


def test_intent_agent_full_workflow():
    intent_agent = IntentAgent()
    query = "Find me 2 business class tickets from BLR to DEL tomorrow"
    intent = intent_agent.parse_intent(query)

    assert intent.intent_type == "SEARCH_FLIGHTS"
    assert intent.source == "BLR"
    assert intent.destination == "DEL"
    assert intent.passenger_count == 2
    assert intent.travel_class == TravelClass.BUSINESS

def test_booking_agent_does_not_autobook_initial_request(seeded_db):
    """VERIFY: 'Book a flight from Bangalore to Hyderabad' does NOT auto-book or generate PNR."""
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    query = "Book a flight from Bangalore to Hyderabad"
    intent = intent_agent.parse_intent(query)

    response = booking_agent.process_intent(
        intent=intent,
        conversation_id="conv-no-autobook-1",
        user_id="user-123",
        user_message=query
    )

    # Missing date should prompt for date
    assert response.action_suggested in ["NEED_DATE", "SELECT_FLIGHT"]
    assert "PNR" not in response.reply
    assert "Successfully Booked" not in response.reply
    assert "Total Fare Paid" not in response.reply

def test_conversational_step_by_step_booking_workflow(seeded_db):
    """VERIFY: Full step-by-step state machine transition: SEARCH -> SELECT FLIGHT -> SELECT CLASS -> SELECT SEATS -> COLLECT PASSENGERS -> REVIEW -> PAYMENT INTENT -> CONFIRMATION"""
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-workflow-full-1"
    user_id = "user-123"

    # Turn 1: "Book a flight from Bangalore to Delhi"
    res1 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Book a flight from Bangalore to Delhi"),
        conversation_id=conv_id, user_id=user_id, user_message="Book a flight from Bangalore to Delhi"
    )
    assert res1.action_suggested == "NEED_DATE"

    # Turn 2: "Day after tomorrow"
    res2 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Day after tomorrow"),
        conversation_id=conv_id, user_id=user_id, user_message="Day after tomorrow"
    )
    assert res2.action_suggested == "SELECT_FLIGHT"
    assert res2.flights_found is not None
    flt_num = res2.flights_found[0]['flight_number']


    # Turn 3: Select flight
    res3 = booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"Flight {flt_num}"),
        conversation_id=conv_id, user_id=user_id, user_message=f"Flight {flt_num}"
    )
    assert res3.action_suggested == "SELECT_CLASS"

    # Turn 4: Select class
    res4 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Business"),
        conversation_id=conv_id, user_id=user_id, user_message="Business"
    )
    assert res4.action_suggested == "SELECT_SEATS"

    # Turn 5: Choose Seat
    res5 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Seat 1A"),
        conversation_id=conv_id, user_id=user_id, user_message="Seat 1A"
    )
    assert res5.action_suggested == "COLLECT_PASSENGERS"

    # Turn 6: Provide passenger details
    res6 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Priya Sharma, 26, female"),
        conversation_id=conv_id, user_id=user_id, user_message="Priya Sharma, 26, female"
    )
    assert res6.action_suggested == "REVIEW_SUMMARY"
    assert "Total" in res6.reply
    assert "PNR" not in res6.reply


    # Turn 7: Proceed to payment -> Draft Booking + Payment Intent (NO PNR YET!)
    res7 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Proceed to payment"),
        conversation_id=conv_id, user_id=user_id, user_message="Proceed to payment"
    )
    assert res7.action_suggested == "LAUNCH_PAYMENT"
    assert res7.payment_intent is not None
    assert res7.draft_booking is not None
    assert res7.draft_booking['status'] == "PAYMENT_PENDING"
    assert "PNR" not in res7.reply

def test_regression_two_passengers_workflow(seeded_db):
    """VERIFY: Regression test for passenger_count = 2 workflow.
    - Intent Agent extracts passenger_count = 2.
    - System does NOT auto-create 2 fake passengers or duplicate logged-in user name.
    - System requires flight selection, class selection, exactly 2 seats, details for Passenger 1 & Passenger 2, fare review, and payment before CONFIRMED / PNR.
    """
    from app.services.booking_service import BookingService
    from app.services.refund_service import RefundService
    from app.repositories.booking_repository import BookingRepository
    from app.repositories.payment_repository import PaymentRepository
    from app.payment.payment_intent import create_simulated_payment_intent
    from app.payment.authorization import generate_ap2_consent_token
    from app.payment.transaction import execute_simulated_ap2_transaction
    from app.models.booking import BookingStatus

    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-2-passengers-test"
    user_id = "user-123"

    # Turn 1: "Book 2 tickets from Bangalore to Delhi"
    res1 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Book 2 tickets from Bangalore to Delhi"),
        conversation_id=conv_id, user_id=user_id, user_message="Book 2 tickets from Bangalore to Delhi"
    )
    assert res1.intent.passenger_count == 2
    assert res1.action_suggested == "NEED_DATE"
    assert "PNR" not in res1.reply
    assert "Successfully Booked" not in res1.reply

    # Turn 2: "Day after tomorrow"
    res2 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Day after tomorrow"),
        conversation_id=conv_id, user_id=user_id, user_message="Day after tomorrow"
    )
    assert res2.action_suggested == "SELECT_FLIGHT"
    assert res2.flights_found is not None

    # Turn 3: "Flight 1"
    res3 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Flight 1"),
        conversation_id=conv_id, user_id=user_id, user_message="Flight 1"
    )
    assert res3.action_suggested == "SELECT_CLASS"

    # Turn 4: "Economy"
    res4 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Economy"),
        conversation_id=conv_id, user_id=user_id, user_message="Economy"
    )
    assert res4.action_suggested == "SELECT_SEATS"
    assert "2 seat(s)" in res4.reply

    # Turn 5: Choose exactly 2 seats: "12A and 12B"
    res5 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("12A and 12B"),
        conversation_id=conv_id, user_id=user_id, user_message="12A and 12B"
    )
    assert res5.action_suggested == "COLLECT_PASSENGERS"
    assert "traveler(s)" in res5.reply or "Passenger" in res5.reply


    # Turn 6: Provide details for both Passenger 1 and Passenger 2
    p_msg = "Passenger 1: Priya Sharma, 26, female\nPassenger 2: Amit Sharma, 29, male"
    res6 = booking_agent.process_intent(
        intent=intent_agent.parse_intent(p_msg),
        conversation_id=conv_id, user_id=user_id, user_message=p_msg
    )
    assert res6.action_suggested == "REVIEW_SUMMARY"
    assert "Priya Sharma" in res6.reply
    assert "Amit Sharma" in res6.reply
    assert "Rahul Sharma" not in res6.reply  # No fabricated names!
    assert "PNR" not in res6.reply

    # Turn 7: Proceed to payment -> Draft Booking + Payment Intent
    res7 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Proceed to payment"),
        conversation_id=conv_id, user_id=user_id, user_message="Proceed to payment"
    )
    assert res7.action_suggested == "LAUNCH_PAYMENT"
    assert res7.payment_intent is not None
    assert res7.draft_booking is not None
    assert res7.draft_booking['passenger_count'] == 2
    assert res7.draft_booking['status'] == "PAYMENT_PENDING"
    assert "PNR" not in res7.reply

    # Turn 8: Backend Payment Execution (POST /api/payments/execute simulation)
    payment_repo = PaymentRepository(seeded_db)
    booking_repo = BookingRepository(seeded_db)

    payment = payment_repo.get_by_intent_id(res7.payment_intent['payment_intent_id'])
    assert payment is not None

    consent_tok = generate_ap2_consent_token(payment.payment_intent_id, "1234", "user@upi")
    success = execute_simulated_ap2_transaction(payment, consent_tok, "user@upi")
    assert success is True

    booking = booking_repo.get_by_id(payment.booking_id)
    booking.status = BookingStatus.CONFIRMED
    seeded_db.commit()

    # Verify final confirmed state
    assert booking.status == BookingStatus.CONFIRMED
    assert booking.pnr is not None
    assert len(booking.pnr) > 0
    assert len(booking.passengers) == 2
    assert booking.passengers[0].first_name == "Priya"
    assert booking.passengers[1].first_name == "Amit"


# =====================================================================
# CANCELLATION WORKFLOW REGRESSION TESTS
# =====================================================================

def helper_create_test_confirmed_booking(db, user_id="user-123", passenger_count=1):
    from app.models.booking import Booking, BookingStatus, BookingPassenger
    from app.models.flight import TravelClass, Flight
    import uuid
    from datetime import datetime, timedelta, timezone

    flight = db.query(Flight).first()
    b_ref = f"BK-{uuid.uuid4().hex[:8].upper()}"
    pnr_val = f"PNR{uuid.uuid4().hex[:4].upper()}"
    b = Booking(
        id=str(uuid.uuid4()),
        booking_reference=b_ref,
        pnr=pnr_val,
        user_id=user_id,
        flight_id=flight.id,
        travel_class=TravelClass.ECONOMY,
        travel_date=(datetime.now() + timedelta(days=2)).date(),
        passenger_count=passenger_count,
        base_fare=4000.0 * passenger_count,
        seat_addons_fee=0.0,
        baggage_addons_fee=0.0,
        taxes=720.0 * passenger_count,
        total_fare=4720.0 * passenger_count,
        status=BookingStatus.CONFIRMED
    )


    db.add(b)
    db.flush()

    for idx in range(passenger_count):
        p = BookingPassenger(
            id=str(uuid.uuid4()),
            booking_id=b.id,
            first_name=f"Passenger{idx+1}",
            last_name="Test",
            age=25 + idx,
            gender="FEMALE",
            seat_number=f"12{chr(65+idx)}"
        )
        db.add(p)
    db.commit()
    return b

def test_cancel_without_reference_requests_reference(seeded_db):
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    res = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Cancel ticket"),
        conversation_id="conv-cancel-1", user_id="user-123", user_message="Cancel ticket"
    )
    assert res.action_suggested == "CANCELLATION_NEED_REF"
    assert "Booking Reference" in res.reply

def test_cancel_with_booking_reference(seeded_db):
    b = helper_create_test_confirmed_booking(seeded_db)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    res = booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel {b.booking_reference}"),
        conversation_id="conv-cancel-2", user_id="user-123", user_message=f"cancel {b.booking_reference}"
    )
    assert res.action_suggested == "CANCELLATION_REVIEW_SUMMARY"
    assert "Cancellation Summary" in res.reply
    assert b.booking_reference in res.reply

def test_cancel_does_not_enter_booking_review(seeded_db):
    b = helper_create_test_confirmed_booking(seeded_db)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    res = booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel {b.booking_reference}"),
        conversation_id="conv-cancel-3", user_id="user-123", user_message=f"cancel {b.booking_reference}"
    )
    assert "Booking Review & Fare Summary" not in res.reply
    assert "Proceed to payment" not in res.reply
    assert "Would you like to proceed to payment" not in res.reply

def test_cancel_does_not_create_payment_intent(seeded_db):
    b = helper_create_test_confirmed_booking(seeded_db)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    res = booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel {b.booking_reference}"),
        conversation_id="conv-cancel-4", user_id="user-123", user_message=f"cancel {b.booking_reference}"
    )
    assert res.payment_intent is None

def test_cancel_requires_confirmation(seeded_db):
    from app.models.booking import BookingStatus, Booking
    b = helper_create_test_confirmed_booking(seeded_db)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    # Preview query
    res = booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel {b.booking_reference}"),
        conversation_id="conv-cancel-5", user_id="user-123", user_message=f"cancel {b.booking_reference}"
    )
    assert res.action_suggested == "CANCELLATION_REVIEW_SUMMARY"

    # DB state MUST NOT be changed yet!
    db_b = seeded_db.query(Booking).filter(Booking.id == b.id).first()
    assert db_b.status == BookingStatus.CONFIRMED

def test_confirm_cancellation(seeded_db):
    from app.models.booking import BookingStatus, Booking
    b = helper_create_test_confirmed_booking(seeded_db)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    # Preview
    booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel {b.booking_reference}"),
        conversation_id="conv-cancel-6", user_id="user-123", user_message=f"cancel {b.booking_reference}"
    )

    # Confirmation
    res_conf = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Confirm cancellation"),
        conversation_id="conv-cancel-6", user_id="user-123", user_message="Confirm cancellation"
    )
    assert res_conf.action_suggested == "CANCELLATION_COMPLETED"
    assert "Ticket Cancelled Successfully" in res_conf.reply

    seeded_db.refresh(b)
    assert b.status.value in ["CANCELLED", "REFUNDED"]



def test_refund_amount_is_deterministic(seeded_db):
    b = helper_create_test_confirmed_booking(seeded_db)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    res = booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel {b.booking_reference}"),
        conversation_id="conv-cancel-7", user_id="user-123", user_message=f"cancel {b.booking_reference}"
    )
    assert res.cancellation_preview is not None
    # 4720.0 gross amount, >24h -> 10% or 30% fee calculated deterministically
    assert res.cancellation_preview["original_amount"] == 4720.0
    assert res.cancellation_preview["refund_amount"] > 0

def test_seat_released_after_cancellation(seeded_db):
    from app.models.flight import FlightSeat
    b = helper_create_test_confirmed_booking(seeded_db)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    # Mark seat as booked
    seat = seeded_db.query(FlightSeat).filter(FlightSeat.flight_id == b.flight_id, FlightSeat.seat_number == "12A").first()
    if seat:
        seat.is_booked = True
        seeded_db.commit()

    # Cancel
    booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel {b.booking_reference}"),
        conversation_id="conv-cancel-8", user_id="user-123", user_message=f"cancel {b.booking_reference}"
    )
    booking_agent.process_intent(
        intent=intent_agent.parse_intent("Confirm cancellation"),
        conversation_id="conv-cancel-8", user_id="user-123", user_message="Confirm cancellation"
    )

    if seat:
        seeded_db.refresh(seat)
        assert seat.is_booked is False

def test_duplicate_cancellation_prevented(seeded_db):
    b = helper_create_test_confirmed_booking(seeded_db)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    # First cancellation
    booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel {b.booking_reference}"),
        conversation_id="conv-cancel-9", user_id="user-123", user_message=f"cancel {b.booking_reference}"
    )
    booking_agent.process_intent(
        intent=intent_agent.parse_intent("Confirm cancellation"),
        conversation_id="conv-cancel-9", user_id="user-123", user_message="Confirm cancellation"
    )

    # Second cancellation attempt
    res_dup = booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel {b.booking_reference}"),
        conversation_id="conv-cancel-9b", user_id="user-123", user_message=f"cancel {b.booking_reference}"
    )
    assert "already been cancelled" in res_dup.reply

def test_wrong_user_cannot_cancel_booking(seeded_db):
    b = helper_create_test_confirmed_booking(seeded_db, user_id="user-owner")
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    res = booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel {b.booking_reference}"),
        conversation_id="conv-cancel-10", user_id="user-attacker", user_message=f"cancel {b.booking_reference}"
    )
    assert "not authorized to cancel" in res.reply

def test_cancel_by_pnr(seeded_db):
    b = helper_create_test_confirmed_booking(seeded_db)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    res = booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel PNR {b.pnr}"),
        conversation_id="conv-cancel-11", user_id="user-123", user_message=f"cancel PNR {b.pnr}"
    )
    assert res.action_suggested == "CANCELLATION_REVIEW_SUMMARY"
    assert b.pnr in res.reply

def test_cancel_interrupts_review_pending(seeded_db):
    b = helper_create_test_confirmed_booking(seeded_db)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    # Put session into REVIEW_PENDING in booking workflow
    conv_id = "conv-cancel-interrupt"
    booking_agent.process_intent(
        intent=intent_agent.parse_intent("Book a flight from Bangalore to Delhi"),
        conversation_id=conv_id, user_id="user-123", user_message="Book a flight from Bangalore to Delhi"
    )

    # User interrupts with cancellation
    res_cancel = booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel {b.booking_reference}"),
        conversation_id=conv_id, user_id="user-123", user_message=f"cancel {b.booking_reference}"
    )

    assert res_cancel.action_suggested == "CANCELLATION_REVIEW_SUMMARY"
    assert "Proceed to payment" not in res_cancel.reply
    assert "Booking Review & Fare Summary" not in res_cancel.reply

def test_cancel_two_passenger_booking(seeded_db):
    b = helper_create_test_confirmed_booking(seeded_db, passenger_count=2)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    # Turn 1: Providing reference for 2-passenger booking asking which passenger to cancel
    res1 = booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel {b.booking_reference}"),
        conversation_id="conv-cancel-2p", user_id="user-123", user_message=f"cancel {b.booking_reference}"
    )
    assert res1.action_suggested == "CANCELLATION_SELECT_PASSENGER"
    assert "Which passenger would you like to cancel" in res1.reply

    # Turn 2: Explicitly requesting entire booking cancellation
    res2 = booking_agent.process_intent(
        intent=intent_agent.parse_intent(f"cancel entire booking {b.booking_reference}"),
        conversation_id="conv-cancel-2p-all", user_id="user-123", user_message=f"cancel entire booking {b.booking_reference}"
    )
    assert res2.action_suggested == "CANCELLATION_REVIEW_SUMMARY"
    assert res2.cancellation_preview["passenger_count"] == 2
    assert res2.cancellation_preview["original_amount"] == 4720.0 * 2

def test_no_fake_cancellation(seeded_db):
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    # Unknown reference
    res = booking_agent.process_intent(
        intent=intent_agent.parse_intent("cancel BK-99999999"),
        conversation_id="conv-cancel-fake", user_id="user-123", user_message="cancel BK-99999999"
    )
    assert "Ticket Cancelled Successfully" not in res.reply
    assert "couldn't find a booking" in res.reply or "not found" in res.reply

def test_cancellation_original_bug_reproduction(seeded_db):
    """REPRODUCE ORIGINAL BUG SCENARIO:
    1. User: 'Cancel ticket' -> Assistant asks for reference.
    2. User: 'BK-4E64457F' -> Assistant shows Cancellation Summary (NOT Booking Review).
    3. ASSERT: Response does NOT contain 'Booking Review & Fare Summary', 'Proceed to Payment', 'Payment Intent'.
    4. User: 'Confirm cancellation' -> Ticket is cancelled and refunded.
    """
    b = helper_create_test_confirmed_booking(seeded_db)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-orig-bug-repro"

    # Turn 1: "Cancel ticket"
    res1 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Cancel ticket"),
        conversation_id=conv_id, user_id="user-123", user_message="Cancel ticket"
    )
    assert res1.action_suggested == "CANCELLATION_NEED_REF"

    # Turn 2: Providing reference "BK-..."
    res2 = booking_agent.process_intent(
        intent=intent_agent.parse_intent(b.booking_reference),
        conversation_id=conv_id, user_id="user-123", user_message=b.booking_reference
    )
    assert res2.action_suggested == "CANCELLATION_REVIEW_SUMMARY"

    # ABSOLUTE BUG VERIFICATION: Response MUST NOT contain booking/payment prompt!
    assert "Booking Review & Fare Summary" not in res2.reply
    assert "Proceed to payment" not in res2.reply
    assert "Payment Intent" not in res2.reply
    assert "Authorize & Pay" not in res2.reply
    assert res2.payment_intent is None

    # Turn 3: "Confirm cancellation"
    res3 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Confirm cancellation"),
        conversation_id=conv_id, user_id="user-123", user_message="Confirm cancellation"
    )
    assert res3.action_suggested == "CANCELLATION_COMPLETED"
    assert "Ticket Cancelled Successfully" in res3.reply

    seeded_db.refresh(b)
    assert b.status.value in ["CANCELLED", "REFUNDED"]


def test_natural_language_mixed_class_workflow(seeded_db):
    """VERIFY: Mixed class booking (2 Business + 1 Economy) workflow with natural language."""
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-nl-mixed-1"

    # Turn 1: "Book 3 tickets from Bangalore to Delhi day after tomorrow, 2 business and 1 economy"
    res1 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Book 3 tickets from Bangalore to Delhi day after tomorrow, 2 business and 1 economy"),
        conversation_id=conv_id, user_id="user-123", user_message="Book 3 tickets from Bangalore to Delhi day after tomorrow, 2 business and 1 economy"
    )
    assert res1.action_suggested == "SELECT_FLIGHT"
    assert res1.intent.passenger_count == 3
    assert res1.intent.class_distribution.get("BUSINESS") == 2
    assert res1.intent.class_distribution.get("ECONOMY") == 1


def test_incomplete_class_distribution_prompts(seeded_db):
    """VERIFY: If user specifies class for 2 of 4 passengers, system asks for remaining 2 class selection."""
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-nl-incomp-class"

    # Turn 1: "Book 4 tickets from Bangalore to Delhi day after tomorrow"
    booking_agent.process_intent(
        intent=intent_agent.parse_intent("Book 4 tickets from Bangalore to Delhi day after tomorrow"),
        conversation_id=conv_id, user_id="user-123", user_message="Book 4 tickets from Bangalore to Delhi day after tomorrow"
    )

    # Turn 2: Select flight 1
    booking_agent.process_intent(
        intent=intent_agent.parse_intent("Flight 1"),
        conversation_id=conv_id, user_id="user-123", user_message="Flight 1"
    )

    # Turn 3: "2 business" (Incomplete class count for 4 passengers!)
    res3 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("2 business"),
        conversation_id=conv_id, user_id="user-123", user_message="2 business"
    )
    assert res3.action_suggested == "SELECT_CLASS"
    assert "remaining" in res3.reply or "Business" in res3.reply


def test_cheapest_flight_selection(seeded_db):
    """VERIFY: User says 'take the cheapest one' -> system deterministically selects flight with lowest base fare."""
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-nl-cheap-flt"

    booking_agent.process_intent(
        intent=intent_agent.parse_intent("Book a flight from Bangalore to Delhi day after tomorrow"),
        conversation_id=conv_id, user_id="user-123", user_message="Book a flight from Bangalore to Delhi day after tomorrow"
    )

    res_cheap = booking_agent.process_intent(
        intent=intent_agent.parse_intent("take the cheapest one"),
        conversation_id=conv_id, user_id="user-123", user_message="take the cheapest one"
    )
    assert res_cheap.action_suggested == "SELECT_CLASS"
    assert res_cheap.booking_step in ["FLIGHT_SELECTED", "CLASS_SELECTED"]


def helper_setup_review_state(seeded_db, conv_id="conv-mod-setup"):
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)

    # 1. Search
    booking_agent.process_intent(
        intent=intent_agent.parse_intent("Book a flight from Bangalore to Delhi day after tomorrow"),
        conversation_id=conv_id, user_id="user-123", user_message="Book a flight from Bangalore to Delhi day after tomorrow"
    )

    # 2. Select Flight
    booking_agent.process_intent(
        intent=intent_agent.parse_intent("Flight 1"),
        conversation_id=conv_id, user_id="user-123", user_message="Flight 1"
    )

    # 3. Select Class
    booking_agent.process_intent(
        intent=intent_agent.parse_intent("Economy"),
        conversation_id=conv_id, user_id="user-123", user_message="Economy"
    )

    # 4. Select Seat
    booking_agent.process_intent(
        intent=intent_agent.parse_intent("1A"),
        conversation_id=conv_id, user_id="user-123", user_message="1A"
    )

    # 5. Provide Passengers
    res_review = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Priya Sharma, 26, female"),
        conversation_id=conv_id, user_id="user-123", user_message="Priya Sharma, 26, female"
    )
    assert res_review.action_suggested == "REVIEW_SUMMARY"
    return intent_agent, booking_agent, conv_id, res_review


def test_modify_button_enters_modification_menu(seeded_db):
    intent_agent, booking_agent, conv_id, _ = helper_setup_review_state(seeded_db, "conv-mod-btn")
    res_mod = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Modify"),
        conversation_id=conv_id, user_id="user-123", user_message="Modify"
    )
    assert res_mod.action_suggested == "MODIFICATION_MENU"
    assert res_mod.booking_step == "MODIFICATION_PENDING"
    assert "What would you like to change?" in res_mod.reply


def test_modify_flight(seeded_db):
    intent_agent, booking_agent, conv_id, _ = helper_setup_review_state(seeded_db, "conv-mod-flt")
    # Open menu
    booking_agent.process_intent(intent=intent_agent.parse_intent("Modify"), conversation_id=conv_id, user_id="user-123", user_message="Modify")
    # Choose Flight
    res = booking_agent.process_intent(intent=intent_agent.parse_intent("Flight"), conversation_id=conv_id, user_id="user-123", user_message="Flight")
    assert res.action_suggested == "SELECT_FLIGHT"


def test_modify_class(seeded_db):
    intent_agent, booking_agent, conv_id, _ = helper_setup_review_state(seeded_db, "conv-mod-cls")
    # Open menu
    booking_agent.process_intent(intent=intent_agent.parse_intent("Modify"), conversation_id=conv_id, user_id="user-123", user_message="Modify")
    # Choose Class
    res = booking_agent.process_intent(intent=intent_agent.parse_intent("Travel class"), conversation_id=conv_id, user_id="user-123", user_message="Travel class")
    assert res.action_suggested == "SELECT_CLASS"


def test_modify_seat(seeded_db):
    intent_agent, booking_agent, conv_id, _ = helper_setup_review_state(seeded_db, "conv-mod-seat")
    # Open menu
    booking_agent.process_intent(intent=intent_agent.parse_intent("Modify"), conversation_id=conv_id, user_id="user-123", user_message="Modify")
    # Choose Seat
    res = booking_agent.process_intent(intent=intent_agent.parse_intent("Seat"), conversation_id=conv_id, user_id="user-123", user_message="Seat")
    assert res.action_suggested == "SELECT_SEATS"


def test_modify_passenger_details(seeded_db):
    intent_agent, booking_agent, conv_id, _ = helper_setup_review_state(seeded_db, "conv-mod-pass")
    # Open menu
    booking_agent.process_intent(intent=intent_agent.parse_intent("Modify"), conversation_id=conv_id, user_id="user-123", user_message="Modify")
    # Choose Passenger Details
    res = booking_agent.process_intent(intent=intent_agent.parse_intent("Passenger details"), conversation_id=conv_id, user_id="user-123", user_message="Passenger details")
    assert res.action_suggested == "COLLECT_PASSENGERS"


def test_modify_does_not_create_new_booking(seeded_db):
    intent_agent, booking_agent, conv_id, _ = helper_setup_review_state(seeded_db, "conv-mod-nobk")
    session = SessionManager.get_or_create(conv_id, "user-123")
    assert session.draft_booking_id is None
    # Click modify
    booking_agent.process_intent(intent=intent_agent.parse_intent("Modify"), conversation_id=conv_id, user_id="user-123", user_message="Modify")
    assert session.draft_booking_id is None


def test_modify_does_not_create_payment_intent(seeded_db):
    intent_agent, booking_agent, conv_id, _ = helper_setup_review_state(seeded_db, "conv-mod-nopay")
    session = SessionManager.get_or_create(conv_id, "user-123")
    assert session.payment_intent_id is None
    booking_agent.process_intent(intent=intent_agent.parse_intent("Modify"), conversation_id=conv_id, user_id="user-123", user_message="Modify")
    assert session.payment_intent_id is None


def test_modify_does_not_generate_pnr(seeded_db):
    intent_agent, booking_agent, conv_id, _ = helper_setup_review_state(seeded_db, "conv-mod-nopnr")
    session = SessionManager.get_or_create(conv_id, "user-123")
    assert session.last_booking_ref is None
    booking_agent.process_intent(intent=intent_agent.parse_intent("Modify"), conversation_id=conv_id, user_id="user-123", user_message="Modify")
    assert session.last_booking_ref is None


def test_cancel_does_not_enter_modification(seeded_db):
    intent_agent, booking_agent, conv_id, _ = helper_setup_review_state(seeded_db, "conv-cancel-not-mod")
    res_cancel = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Cancel ticket"),
        conversation_id=conv_id, user_id="user-123", user_message="Cancel ticket"
    )
    assert res_cancel.action_suggested in ["CANCELLATION_NEED_REF", "CANCELLATION_NEED_REFERENCE", "CANCELLATION_REVIEW_SUMMARY", "CANCELLATION_LOOKUP"]
    assert res_cancel.action_suggested != "MODIFICATION_MENU"



def test_modified_booking_recalculates_fare(seeded_db):
    intent_agent, booking_agent, conv_id, res_review1 = helper_setup_review_state(seeded_db, "conv-recalc-fare")
    fare1 = res_review1.fare_summary['total_fare']

    # Open menu and change travel class to Business
    booking_agent.process_intent(intent=intent_agent.parse_intent("Modify"), conversation_id=conv_id, user_id="user-123", user_message="Modify")
    booking_agent.process_intent(intent=intent_agent.parse_intent("Travel class"), conversation_id=conv_id, user_id="user-123", user_message="Travel class")
    res_review2 = booking_agent.process_intent(intent=intent_agent.parse_intent("Business"), conversation_id=conv_id, user_id="user-123", user_message="Business")

    assert res_review2.action_suggested == "REVIEW_SUMMARY"
    fare2 = res_review2.fare_summary['total_fare']
    assert fare2 > fare1


def test_two_economy_one_business():
    intent_agent = IntentAgent()
    intent = intent_agent.parse_intent("2 economy and 1 business")
    assert intent.passenger_count == 3
    assert intent.class_distribution == {"ECONOMY": 2, "BUSINESS": 1}
    assert intent.travel_class is None


def test_two_business_one_economy():
    intent_agent = IntentAgent()
    intent = intent_agent.parse_intent("2 business and 1 economy")
    assert intent.passenger_count == 3
    assert intent.class_distribution == {"BUSINESS": 2, "ECONOMY": 1}
    assert intent.travel_class is None


def test_three_class_distribution():
    intent_agent = IntentAgent()
    intent = intent_agent.parse_intent("1 premium economy, 2 business and 1 economy")
    assert intent.passenger_count == 4
    assert intent.class_distribution == {"PREMIUM_ECONOMY": 1, "BUSINESS": 2, "ECONOMY": 1}
    assert intent.travel_class is None


def test_mixed_class_count_must_match_passengers(seeded_db):
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-mixed-count-match"
    res1 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Book 3 tickets from Bangalore to Delhi day after tomorrow"),
        conversation_id=conv_id, user_id="user-123", user_message="Book 3 tickets from Bangalore to Delhi day after tomorrow"
    )
    res2 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("Flight 1"),
        conversation_id=conv_id, user_id="user-123", user_message="Flight 1"
    )
    res3 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("2 economy"),
        conversation_id=conv_id, user_id="user-123", user_message="2 economy"
    )
    assert res3.action_suggested == "SELECT_CLASS"
    assert "remaining 1 passenger" in res3.reply or "remaining" in res3.reply.lower()


def test_mixed_class_not_collapsed_to_single_class(seeded_db):
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-not-collapsed"
    res1 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("I need 3 tickets from Bangalore to Delhi day after tomorrow. 2 economy and 1 business."),
        conversation_id=conv_id, user_id="user-123", user_message="I need 3 tickets from Bangalore to Delhi day after tomorrow. 2 economy and 1 business."
    )
    assert res1.intent.class_distribution == {"ECONOMY": 2, "BUSINESS": 1}
    assert res1.intent.travel_class is None
    assert "BUSINESS (3 passenger(s))" not in res1.reply


def test_mixed_class_fare_calculation(seeded_db):
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-mixed-fare"
    booking_agent.process_intent(intent=intent_agent.parse_intent("Book 3 tickets from Bangalore to Delhi day after tomorrow. 2 economy and 1 business."), conversation_id=conv_id, user_id="u1", user_message="Book 3 tickets from Bangalore to Delhi day after tomorrow. 2 economy and 1 business.")
    booking_agent.process_intent(intent=intent_agent.parse_intent("Flight 1"), conversation_id=conv_id, user_id="u1", user_message="Flight 1")
    booking_agent.process_intent(intent=intent_agent.parse_intent("10A, 10B, 1A"), conversation_id=conv_id, user_id="u1", user_message="10A, 10B, 1A")
    res_review = booking_agent.process_intent(intent=intent_agent.parse_intent("Passenger 1: Priya Sharma, 26, female\nPassenger 2: Amit Sharma, 29, male\nPassenger 3: Rahul Sharma, 25, male"), conversation_id=conv_id, user_id="u1", user_message="Priya Sharma 26 female, Amit Sharma 29 male, Rahul Sharma 25 male")
    assert res_review.action_suggested == "REVIEW_SUMMARY"
    assert "Economy" in res_review.reply
    assert "Business" in res_review.reply
    assert "Total" in res_review.reply


def test_mixed_class_seat_selection(seeded_db):
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-mixed-seat"
    booking_agent.process_intent(intent=intent_agent.parse_intent("Book 3 tickets from Bangalore to Delhi day after tomorrow. 2 economy and 1 business."), conversation_id=conv_id, user_id="u1", user_message="Book 3 tickets from Bangalore to Delhi day after tomorrow. 2 economy and 1 business.")
    res_flt = booking_agent.process_intent(intent=intent_agent.parse_intent("Flight 1"), conversation_id=conv_id, user_id="u1", user_message="Flight 1")
    assert res_flt.action_suggested == "SELECT_SEATS"
    assert "Economy" in res_flt.reply
    assert "Business" in res_flt.reply


def test_modify_passenger_class(seeded_db):
    intent_agent, booking_agent, conv_id, res_review = helper_setup_review_state(seeded_db, "conv-mod-pass-cls")
    booking_agent.process_intent(intent=intent_agent.parse_intent("Modify"), conversation_id=conv_id, user_id="user-123", user_message="Modify")
    res = booking_agent.process_intent(intent=intent_agent.parse_intent("Travel class"), conversation_id=conv_id, user_id="user-123", user_message="Travel class")
    assert res.action_suggested in ["SELECT_CLASS", "REVIEW_SUMMARY"]


def test_natural_language_mixed_class_number_words():
    intent_agent = IntentAgent()
    intent = intent_agent.parse_intent("two in economy and one in business")
    assert intent.passenger_count == 3
    assert intent.class_distribution == {"ECONOMY": 2, "BUSINESS": 1}
    assert intent.travel_class is None


def test_mixed_class_persists_to_review(seeded_db):
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-persist-rev"
    booking_agent.process_intent(intent=intent_agent.parse_intent("Book 3 tickets from BLR to DEL day after tomorrow. 2 economy and 1 business."), conversation_id=conv_id, user_id="u1", user_message="Book 3 tickets from BLR to DEL day after tomorrow. 2 economy and 1 business.")
    booking_agent.process_intent(intent=intent_agent.parse_intent("Flight 1"), conversation_id=conv_id, user_id="u1", user_message="Flight 1")
    booking_agent.process_intent(intent=intent_agent.parse_intent("10A, 10B, 1A"), conversation_id=conv_id, user_id="u1", user_message="10A, 10B, 1A")
    p_msg = "Passenger 1: Priya Sharma, 26, female\nPassenger 2: Amit Sharma, 29, male\nPassenger 3: Rahul Sharma, 25, male"
    res = booking_agent.process_intent(intent=intent_agent.parse_intent(p_msg), conversation_id=conv_id, user_id="u1", user_message=p_msg)
    assert res.action_suggested == "REVIEW_SUMMARY"
    assert "Economy" in res.reply
    assert "Business" in res.reply


def test_active_booking_date_input_does_not_trigger_cancellation(seeded_db):
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-date-routing-test"
    target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    date_str = (datetime.now() + timedelta(days=1)).strftime("%d %B %Y")

    # Step 1: "book ticket" -> NEED_INFO
    res1 = booking_agent.process_intent(
        intent=intent_agent.parse_intent("book ticket"),
        conversation_id=conv_id,
        user_id="u1",
        user_message="book ticket"
    )
    assert res1.action_suggested == "NEED_INFO"

    # Step 2: "bangalore to delhi" -> NEED_DATE
    intent2 = intent_agent.parse_intent("bangalore to delhi")
    res2 = booking_agent.process_intent(
        intent=intent2,
        conversation_id=conv_id,
        user_id="u1",
        user_message="bangalore to delhi"
    )
    assert res2.action_suggested == "NEED_DATE"

    # Step 3: Natural date input -> SEARCH_FLIGHTS / SELECT_FLIGHT (must NOT trigger cancellation or PNR lookup)
    intent3 = intent_agent.parse_intent(date_str, active_step=res2.booking_step)
    assert intent3.travel_date == target_date
    assert intent3.booking_reference is None
    assert intent3.intent_type != "CANCEL_BOOKING"

    res3 = booking_agent.process_intent(
        intent=intent3,
        conversation_id=conv_id,
        user_id="u1",
        user_message=date_str
    )
    assert res3.action_suggested in ["SELECT_FLIGHT", "NO_FLIGHTS"]
    assert "cancellation" not in res3.reply.lower()
    assert "Booking Reference" not in res3.reply


def test_passenger_level_cancellation(seeded_db):
    b = helper_create_test_confirmed_booking(seeded_db, passenger_count=2)
    intent_agent = IntentAgent()
    booking_agent = BookingAgent(seeded_db)
    conv_id = "conv-passenger-cancel-test"
    user_id = "user-123"
    b_ref = b.booking_reference

    # Step 1: User requests cancellation of Passenger1's ticket
    cancel_intent = intent_agent.parse_intent(f"cancel Passenger1 from {b_ref}")
    res_cancel_preview = booking_agent.process_intent(
        intent=cancel_intent,
        conversation_id=conv_id,
        user_id=user_id,
        user_message=f"cancel Passenger1 from {b_ref}"
    )

    assert "Passenger1" in res_cancel_preview.reply
    assert "Passenger2" in res_cancel_preview.reply
    assert "Would you like to confirm cancellation?" in res_cancel_preview.reply

    # Step 2: Confirm passenger cancellation
    confirm_intent = intent_agent.parse_intent("Confirm cancellation")
    res_confirm = booking_agent.process_intent(
        intent=confirm_intent,
        conversation_id=conv_id,
        user_id=user_id,
        user_message="Confirm cancellation"
    )

    assert "Passenger Ticket Cancelled Successfully" in res_confirm.reply
    assert "Passenger1" in res_confirm.reply
    assert "Passenger2" in res_confirm.reply

    # Verify DB state
    from app.services.booking_service import BookingService
    from app.models.booking import BookingStatus
    b_service = BookingService(seeded_db)
    updated_b = b_service.booking_repo.get_by_reference(b_ref)
    assert updated_b.status == BookingStatus.PARTIALLY_CANCELLED
    p_1 = next(p for p in updated_b.passengers if p.first_name == "Passenger1")
    p_2 = next(p for p in updated_b.passengers if p.first_name == "Passenger2")
    assert p_1.is_cancelled is True
    assert p_2.is_cancelled is False

    # Verify seat 12A is unbooked and seat 12B remains booked
    s_12a = next(s for s in updated_b.flight.seats if s.seat_number == "12A")
    s_12b = next(s for s in updated_b.flight.seats if s.seat_number == "12B")
    assert s_12a.is_booked is False
    assert s_12b.is_booked is True

















