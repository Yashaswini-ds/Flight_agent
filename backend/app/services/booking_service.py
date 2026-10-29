import uuid
import secrets
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.booking import Booking, BookingPassenger, BookingStatus
from app.models.flight import Flight, FlightFare, FlightSeat, TravelClass
from app.repositories.booking_repository import BookingRepository
from app.repositories.flight_repository import FlightRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.booking import CreateBookingRequest, BookingResponse, PassengerResponse, ModifyBookingRequest
from app.payment.payment_intent import create_simulated_payment_intent
from app.payment.authorization import generate_ap2_consent_token
from app.payment.transaction import execute_simulated_ap2_transaction
from app.models.payment import PaymentMethod, PaymentStatus
from app.core.config import settings
from app.core.exceptions import NotFoundException, BadRequestException, ConflictException

class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.flight_repo = FlightRepository(db)
        self.payment_repo = PaymentRepository(db)

    def calculate_deterministic_fare(
        self,
        base_fare_per_passenger: float,
        passenger_count: int,
        seat_addons_fee: float = 0.0,
        extra_baggage_kg: int = 0
    ) -> dict:
        """
        100% Deterministic Financial Calculation Engine.
        Taxes calculated using configurable settings.DEMO_TAX_PERCENTAGE.
        """
        total_base = base_fare_per_passenger * passenger_count
        baggage_fee = extra_baggage_kg * 300.0  # ₹300 per extra kg
        taxable_subtotal = total_base + seat_addons_fee + baggage_fee
        taxes = round((taxable_subtotal * (settings.DEMO_TAX_PERCENTAGE / 100.0)), 2)
        total_fare = round(taxable_subtotal + taxes, 2)

        return {
            "total_base": total_base,
            "seat_addons_fee": seat_addons_fee,
            "baggage_addons_fee": baggage_fee,
            "taxes": taxes,
            "total_fare": total_fare
        }

    def create_booking(self, user_id: str, request: CreateBookingRequest) -> BookingResponse:
        """
        Creates a flight booking inside a clean SQLAlchemy transaction boundary.
        Updates seat inventory and calculates deterministic fare breakdown.
        """
        flight = self.flight_repo.get_flight_by_id(request.flight_id)
        if not flight:
            raise NotFoundException("Target flight not found")

        fare_obj = next((f for f in flight.fares if f.travel_class == request.travel_class), None)
        if not fare_obj or fare_obj.seats_available < len(request.passengers):
            raise BadRequestException("Insufficient seats available for requested travel class")

        try:
            travel_dt = datetime.strptime(request.travel_date, "%Y-%m-%d")
        except ValueError:
            raise BadRequestException("Invalid travel date format. Expected YYYY-MM-DD")

        # Seat addons calculation
        seat_fee_total = 0.0
        selected_seat_numbers = [p.seat_number for p in request.passengers if p.seat_number]
        if selected_seat_numbers:
            flight_seats = self.flight_repo.get_seats_for_flight(flight.id, request.travel_class)
            for sn in selected_seat_numbers:
                s_match = next((s for s in flight_seats if s.seat_number == sn), None)
                if s_match:
                    if s_match.is_booked:
                        raise ConflictException(f"Seat {sn} is already booked")
                    seat_fee_total += s_match.price_extra

        fare_calc = self.calculate_deterministic_fare(
            base_fare_per_passenger=fare_obj.base_fare,
            passenger_count=len(request.passengers),
            seat_addons_fee=seat_fee_total,
            extra_baggage_kg=request.extra_baggage_kg
        )

        booking_ref = f"BK-{secrets.token_hex(4).upper()}"
        pnr_code = f"{secrets.token_hex(3).upper()}"

        try:
            # Transaction Boundary Start
            booking = Booking(
                id=str(uuid.uuid4()),
                booking_reference=booking_ref,
                pnr=pnr_code,
                user_id=user_id,
                flight_id=flight.id,
                travel_class=request.travel_class,
                travel_date=travel_dt,
                passenger_count=len(request.passengers),
                base_fare=fare_calc["total_base"],
                seat_addons_fee=fare_calc["seat_addons_fee"],
                baggage_addons_fee=fare_calc["baggage_addons_fee"],
                taxes=fare_calc["taxes"],
                total_fare=fare_calc["total_fare"],
                status=BookingStatus.PAYMENT_PENDING
            )
            self.db.add(booking)
            self.db.flush()

            for p_in in request.passengers:
                pass_obj = BookingPassenger(
                    id=str(uuid.uuid4()),
                    booking_id=booking.id,
                    first_name=p_in.first_name,
                    last_name=p_in.last_name,
                    age=p_in.age,
                    gender=p_in.gender,
                    seat_number=p_in.seat_number
                )
                self.db.add(pass_obj)
                if p_in.seat_number:
                    # Lock seat
                    s_to_lock = next((s for s in flight.seats if s.seat_number == p_in.seat_number), None)
                    if s_to_lock:
                        s_to_lock.is_booked = True

            # Deduct available seats
            fare_obj.seats_available -= len(request.passengers)
            
            self.db.commit()
            self.db.refresh(booking)
            return self._build_booking_response(booking)
        except Exception as e:
            self.db.rollback()
            raise BadRequestException(f"Failed to create booking: {str(e)}")

    def get_booking(self, booking_id_or_ref: str, user_id: Optional[str] = None) -> BookingResponse:
        booking = self.booking_repo.get_by_id(booking_id_or_ref)
        if not booking:
            booking = self.booking_repo.get_by_reference(booking_id_or_ref)
        if not booking:
            booking = self.booking_repo.get_by_pnr(booking_id_or_ref)
        if not booking:
            raise NotFoundException("Booking not found")

        return self._build_booking_response(booking)


    def get_user_bookings(self, user_id: str) -> List[BookingResponse]:
        bookings = self.booking_repo.get_user_bookings(user_id)
        return [self._build_booking_response(b) for b in bookings]

    def modify_booking(self, booking_id: str, user_id: str, request: ModifyBookingRequest) -> BookingResponse:
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking or booking.user_id != user_id:
            raise NotFoundException("Booking not found")
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.REFUNDED]:
            raise BadRequestException("Cancelled or refunded bookings cannot be modified")

        try:
            if request.new_travel_date:
                booking.travel_date = datetime.strptime(request.new_travel_date, "%Y-%m-%d")
            if request.new_travel_class:
                booking.travel_class = request.new_travel_class
            
            self.db.commit()
            self.db.refresh(booking)
            return self._build_booking_response(booking)
        except Exception as e:
            self.db.rollback()
            raise BadRequestException(f"Failed to modify booking: {str(e)}")

    def _build_booking_response(self, booking: Booking) -> BookingResponse:
        flight = booking.flight
        passengers_resp = [PassengerResponse.model_validate(p) for p in booking.passengers]
        return BookingResponse(
            id=booking.id,
            booking_reference=booking.booking_reference,
            pnr=booking.pnr,
            user_id=booking.user_id,
            flight_id=booking.flight_id,
            airline_name=flight.airline.name if flight and flight.airline else "Demo Air",
            flight_number=flight.flight_number if flight else "",
            origin_code=flight.origin.code if flight and flight.origin else "",
            origin_city=flight.origin.name if flight and flight.origin else "",
            destination_code=flight.destination.code if flight and flight.destination else "",
            destination_city=flight.destination.name if flight and flight.destination else "",
            departure_time=flight.departure_time if flight else datetime.now(),
            arrival_time=flight.arrival_time if flight else datetime.now(),
            travel_class=booking.travel_class,
            travel_date=booking.travel_date,
            passenger_count=booking.passenger_count,
            base_fare=booking.base_fare,
            seat_addons_fee=booking.seat_addons_fee,
            baggage_addons_fee=booking.baggage_addons_fee,
            taxes=booking.taxes,
            total_fare=booking.total_fare,
            status=booking.status,
            created_at=booking.created_at,
            passengers=passengers_resp
        )
