from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.flight_service import FlightService
from app.services.booking_service import BookingService
from app.services.refund_service import RefundService
from app.models.flight import TravelClass
from app.schemas.booking import CreateBookingRequest, PassengerInput, ModifyBookingRequest
from app.schemas.payment import PaymentMethod

class BookingAgentTools:
    """
    Controlled Tool Interfaces wrapper for the Booking Agent.
    Strictly delegates all DB, state, and financial math to deterministic Backend Services.
    """
    def __init__(self, db: Session):
        self.db = db
        self.flight_service = FlightService(db)
        self.booking_service = BookingService(db)
        self.refund_service = RefundService(db)

    def search_flights(
        self,
        origin: str,
        destination: str,
        travel_date: str,
        passenger_count: int = 1,
        travel_class: TravelClass = TravelClass.ECONOMY
    ) -> List[Dict[str, Any]]:
        results = self.flight_service.search_flights(
            origin=origin,
            destination=destination,
            travel_date_str=travel_date,
            passenger_count=passenger_count,
            travel_class=travel_class
        )
        return [r.model_dump() for r in results]

    def get_flight_details(self, flight_id: str) -> Dict[str, Any]:
        flight = self.flight_service.get_flight_details(flight_id)
        return flight.model_dump()

    def calculate_fare(
        self,
        base_fare: float,
        passenger_count: int,
        seat_addons_fee: float = 0.0,
        extra_baggage_kg: int = 0
    ) -> Dict[str, Any]:
        return self.booking_service.calculate_deterministic_fare(
            base_fare_per_passenger=base_fare,
            passenger_count=passenger_count,
            seat_addons_fee=seat_addons_fee,
            extra_baggage_kg=extra_baggage_kg
        )

    def create_booking(
        self,
        user_id: str,
        flight_id: str,
        travel_class: TravelClass,
        travel_date: str,
        passengers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        pass_inputs = [PassengerInput(**p) for p in passengers]
        req = CreateBookingRequest(
            flight_id=flight_id,
            travel_class=travel_class,
            travel_date=travel_date,
            passengers=pass_inputs
        )
        resp = self.booking_service.create_booking(user_id=user_id, request=req)
        return resp.model_dump()

    def get_available_seats(self, flight_id: str, travel_class: TravelClass) -> List[Dict[str, Any]]:
        seats = self.flight_service.get_flight_seats(flight_id, travel_class)
        return [s.model_dump() for s in seats]

    def create_booking_draft(
        self,
        user_id: str,
        flight_id: str,
        travel_class: TravelClass,
        travel_date: str,
        passengers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        pass_inputs = [PassengerInput(**p) for p in passengers]
        req = CreateBookingRequest(
            flight_id=flight_id,
            travel_class=travel_class,
            travel_date=travel_date,
            passengers=pass_inputs
        )
        resp = self.booking_service.create_booking(user_id=user_id, request=req)
        return resp.model_dump()

    def create_payment_intent(
        self,
        booking_id: str,
        user_id: str,
        payment_method: PaymentMethod = PaymentMethod.UPI
    ) -> Dict[str, Any]:
        from app.repositories.booking_repository import BookingRepository
        from app.repositories.payment_repository import PaymentRepository
        from app.payment.payment_intent import create_simulated_payment_intent

        booking_repo = BookingRepository(self.db)
        payment_repo = PaymentRepository(self.db)

        booking = booking_repo.get_by_id(booking_id)
        if not booking:
            booking = booking_repo.get_by_reference(booking_id)
        if not booking:
            raise ValueError("Draft booking not found")

        existing_payment = payment_repo.get_by_booking_id(booking.id)
        if existing_payment:
            return {
                "payment_intent_id": existing_payment.payment_intent_id,
                "booking_id": booking.id,
                "amount": existing_payment.amount,
                "currency": existing_payment.currency,
                "merchant_mandate_id": existing_payment.ap2_mandate_id or "",
                "status": existing_payment.status
            }

        payment = create_simulated_payment_intent(
            booking_id=booking.id,
            amount=booking.total_fare,
            payment_method=payment_method
        )
        payment_repo.create_payment(payment)
        self.db.commit()

        return {
            "payment_intent_id": payment.payment_intent_id,
            "booking_id": booking.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "merchant_mandate_id": payment.ap2_mandate_id or "",
            "status": payment.status
        }

    def get_booking(self, booking_reference: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        resp = self.booking_service.get_booking(booking_id_or_ref=booking_reference, user_id=user_id)
        return resp.model_dump()

    def get_cancellation_preview(self, booking_ref_or_pnr: str, user_id: str) -> Dict[str, Any]:
        from app.repositories.booking_repository import BookingRepository
        from app.models.booking import BookingStatus
        from app.models.user import User, UserRole

        booking_repo = BookingRepository(self.db)
        booking = booking_repo.get_by_id(booking_ref_or_pnr)
        if not booking:
            booking = booking_repo.get_by_reference(booking_ref_or_pnr)
        if not booking:
            booking = booking_repo.get_by_pnr(booking_ref_or_pnr)

        if not booking:
            raise ValueError(f"I couldn't find a booking with reference or PNR {booking_ref_or_pnr}.")

        if user_id and booking.user_id != user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or user.role != UserRole.ADMIN:
                raise ValueError("You are not authorized to cancel this booking.")

        if booking.status in [BookingStatus.CANCELLED, BookingStatus.REFUNDED]:
            raise ValueError("This booking has already been cancelled.")

        if booking.status != BookingStatus.CONFIRMED:
            raise ValueError("This booking cannot be cancelled because it has not been confirmed.")

        calc = self.refund_service.calculate_deterministic_refund(booking)
        passengers = [{"first_name": p.first_name, "last_name": p.last_name, "seat_number": p.seat_number} for p in booking.passengers]
        seats = [p.seat_number for p in booking.passengers if p.seat_number]

        airline_name = booking.flight.airline.name if hasattr(booking.flight, 'airline') and booking.flight.airline else "Demo Air"
        origin_city = booking.flight.origin.name if hasattr(booking.flight, 'origin') and booking.flight.origin else booking.flight.origin_code
        destination_city = booking.flight.destination.name if hasattr(booking.flight, 'destination') and booking.flight.destination else booking.flight.destination_code

        dep_dt = booking.flight.departure_time if hasattr(booking.flight, 'departure_time') else booking.travel_date
        dep_str = dep_dt.strftime("%Y-%m-%d") if hasattr(dep_dt, 'strftime') else str(dep_dt)[:10]


        return {
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "pnr": booking.pnr,
            "airline_name": airline_name,
            "flight_number": booking.flight.flight_number,
            "origin_city": origin_city,
            "origin_code": booking.flight.origin_code,
            "destination_city": destination_city,
            "destination_code": booking.flight.destination_code,
            "departure_date": dep_str,
            "passenger_count": booking.passenger_count,
            "passengers": passengers,
            "seats": seats,
            "original_amount": calc["gross_amount"],
            "cancellation_fee": calc["cancellation_fee"],
            "refund_amount": calc["net_refund_amount"],
            "fee_percentage": calc["fee_percentage"],
            "refund_percentage": 100 - calc["fee_percentage"],
            "can_cancel": True
        }

    def cancel_booking(self, booking_id: str, user_id: str, reason: str = "Agent requested cancellation") -> Dict[str, Any]:
        resp = self.refund_service.cancel_and_process_refund(booking_id=booking_id, user_id=user_id, reason=reason)
        return resp.model_dump()

    def get_passenger_cancellation_preview(self, booking_ref_or_pnr: str, passenger_ids: List[str], user_id: str) -> Dict[str, Any]:
        from app.repositories.booking_repository import BookingRepository
        from app.models.booking import BookingStatus
        from app.models.user import User, UserRole

        booking_repo = BookingRepository(self.db)
        booking = booking_repo.get_by_id(booking_ref_or_pnr)
        if not booking:
            booking = booking_repo.get_by_reference(booking_ref_or_pnr)
        if not booking:
            booking = booking_repo.get_by_pnr(booking_ref_or_pnr)

        if not booking:
            raise ValueError(f"I couldn't find a booking with reference or PNR {booking_ref_or_pnr}.")

        if user_id and booking.user_id != user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or user.role != UserRole.ADMIN:
                raise ValueError("You are not authorized to cancel this booking.")

        if booking.status in [BookingStatus.CANCELLED, BookingStatus.REFUNDED]:
            raise ValueError("This booking has already been completely cancelled.")

        target_passengers = [p for p in booking.passengers if p.id in passenger_ids or (f"{p.first_name} {p.last_name}".lower() in [pid.lower() for pid in passenger_ids]) or (p.seat_number and p.seat_number.upper() in [pid.upper() for pid in passenger_ids])]
        if not target_passengers:
            raise ValueError("Specified passenger(s) not found in booking.")

        calc = self.refund_service.calculate_passenger_refund(booking, [p.id for p in target_passengers])
        cancelled_p_list = [{"id": p.id, "first_name": p.first_name, "last_name": p.last_name, "seat_number": p.seat_number} for p in target_passengers]
        remaining_p_list = [{"id": p.id, "first_name": p.first_name, "last_name": p.last_name, "seat_number": p.seat_number} for p in booking.passengers if p not in target_passengers and not getattr(p, 'is_cancelled', False)]

        return {
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "pnr": booking.pnr,
            "target_passenger_ids": [p.id for p in target_passengers],
            "target_passengers": cancelled_p_list,
            "remaining_passengers": remaining_p_list,
            "original_amount": calc["gross_amount"],
            "cancellation_fee": calc["cancellation_fee"],
            "refund_amount": calc["net_refund_amount"],
            "fee_percentage": calc["fee_percentage"],
            "can_cancel": True
        }

    def cancel_passenger_booking(self, booking_id: str, passenger_ids: List[str], user_id: str, reason: str = "Passenger cancellation") -> Dict[str, Any]:
        resp = self.refund_service.cancel_passenger_and_process_refund(booking_id=booking_id, passenger_ids=passenger_ids, user_id=user_id, reason=reason)
        return resp.model_dump()


    def get_flight_by_number(self, flight_number: str) -> Optional[Dict[str, Any]]:
        flight = self.flight_service.get_flight_by_number(flight_number)
        return flight.model_dump() if flight else None

    def get_user_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        bookings = self.booking_service.get_user_bookings(user_id)
        return [b.model_dump() for b in bookings]

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        from app.models.user import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            return {"id": user.id, "full_name": user.full_name, "email": user.email}
        return None

    def calculate_refund(self, booking_id: str, user_id: str) -> Dict[str, Any]:
        booking = self.booking_service.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")
        return self.refund_service.calculate_deterministic_refund(booking)


