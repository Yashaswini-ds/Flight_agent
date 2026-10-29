import uuid
import secrets
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.booking import Booking, BookingStatus
from app.models.refund import Refund, RefundStatus
from app.models.payment import Payment, PaymentStatus
from app.repositories.booking_repository import BookingRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment import RefundResponse
from app.core.exceptions import NotFoundException, BadRequestException

class RefundService:
    def __init__(self, db: Session):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.payment_repo = PaymentRepository(db)

    def calculate_deterministic_refund(self, booking: Booking) -> dict:
        """
        100% Deterministic Financial Refund Calculator.
        Based on time remaining until flight departure.
        """
        now = datetime.now(timezone.utc)
        dep_time = booking.flight.departure_time if booking.flight else booking.travel_date
        if dep_time.tzinfo is None:
            dep_time = dep_time.replace(tzinfo=timezone.utc)

        hours_to_departure = (dep_time - now).total_seconds() / 3600.0

        if hours_to_departure >= 72:
            fee_percentage = 0.10  # 10% fee
        elif hours_to_departure >= 24:
            fee_percentage = 0.30  # 30% fee
        else:
            fee_percentage = 0.50  # 50% fee

        gross = booking.total_fare
        cancellation_fee = round(gross * fee_percentage, 2)
        net_refund = round(gross - cancellation_fee, 2)

        return {
            "gross_amount": gross,
            "cancellation_fee": cancellation_fee,
            "net_refund_amount": net_refund,
            "fee_percentage": int(fee_percentage * 100)
        }

    def calculate_passenger_refund(self, booking: Booking, passenger_ids: list[str]) -> dict:
        """
        Calculates deterministic pro-rata refund for specific passenger(s).
        """
        total_p_count = max(1, len(booking.passengers) if booking.passengers else booking.passenger_count)
        p_cancel_count = len(passenger_ids)
        
        now = datetime.now(timezone.utc)
        dep_time = booking.flight.departure_time if booking.flight else booking.travel_date
        if dep_time.tzinfo is None:
            dep_time = dep_time.replace(tzinfo=timezone.utc)

        hours_to_departure = (dep_time - now).total_seconds() / 3600.0

        if hours_to_departure >= 72:
            fee_percentage = 0.10
        elif hours_to_departure >= 24:
            fee_percentage = 0.30
        else:
            fee_percentage = 0.50

        # Pro-rata gross amount for target passengers
        gross_per_p = booking.total_fare / float(total_p_count)
        gross = round(gross_per_p * p_cancel_count, 2)
        cancellation_fee = round(gross * fee_percentage, 2)
        net_refund = round(gross - cancellation_fee, 2)

        return {
            "gross_amount": gross,
            "cancellation_fee": cancellation_fee,
            "net_refund_amount": net_refund,
            "fee_percentage": int(fee_percentage * 100),
            "cancelled_passenger_count": p_cancel_count,
            "total_passenger_count": total_p_count
        }

    def cancel_passenger_and_process_refund(
        self,
        booking_id: str,
        passenger_ids: list[str],
        user_id: Optional[str] = None,
        reason: str = "Customer requested passenger cancellation"
    ) -> RefundResponse:
        """
        Cancels specific passenger(s) in a booking while preserving remaining active passengers.
        """
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            booking = self.booking_repo.get_by_reference(booking_id)
        if not booking:
            booking = self.booking_repo.get_by_pnr(booking_id)
        if not booking:
            raise NotFoundException(f"Booking '{booking_id}' not found")

        if booking.status in [BookingStatus.CANCELLED, BookingStatus.REFUNDED]:
            raise BadRequestException("Booking is already completely cancelled")

        target_passengers = [p for p in booking.passengers if p.id in passenger_ids or (f"{p.first_name} {p.last_name}".lower() in [pid.lower() for pid in passenger_ids])]
        if not target_passengers:
            raise NotFoundException("Specified passengers not found in booking")

        # Check if already cancelled
        already_cancelled = [p for p in target_passengers if getattr(p, "is_cancelled", False)]
        if len(already_cancelled) == len(target_passengers):
            raise BadRequestException("Selected passenger(s) are already cancelled")

        active_targets = [p for p in target_passengers if not getattr(p, "is_cancelled", False)]
        refund_calc = self.calculate_passenger_refund(booking, [p.id for p in active_targets])
        refund_ref = f"RF-{secrets.token_hex(6).upper()}"

        try:
            # Mark targeted passengers as cancelled and release their seats
            for p in active_targets:
                p.is_cancelled = True
                if p.seat_number and booking.flight:
                    s_obj = next((s for s in booking.flight.seats if s.seat_number == p.seat_number), None)
                    if s_obj:
                        s_obj.is_booked = False

            # Restore fare seat counts for cancelled passengers
            if booking.flight:
                fare_obj = next((f for f in booking.flight.fares if f.travel_class == booking.travel_class), None)
                if fare_obj:
                    fare_obj.seats_available += len(active_targets)

            # Determine overall booking status
            remaining_active = [p for p in booking.passengers if not getattr(p, "is_cancelled", False)]
            if len(remaining_active) == 0:
                booking.status = BookingStatus.REFUNDED
            else:
                booking.status = BookingStatus.PARTIALLY_CANCELLED

            refund = Refund(
                id=str(uuid.uuid4()),
                booking_id=booking.id,
                refund_reference=refund_ref,
                gross_amount=refund_calc["gross_amount"],
                cancellation_fee=refund_calc["cancellation_fee"],
                net_refund_amount=refund_calc["net_refund_amount"],
                reason=reason,
                status=RefundStatus.PROCESSED,
                processed_at=datetime.now(timezone.utc)
            )
            self.db.add(refund)

            self.db.commit()
            self.db.refresh(refund)
            resp = RefundResponse.model_validate(refund)
            resp.booking_reference = booking.booking_reference
            resp.pnr = booking.pnr
            resp.fee_percentage = refund_calc["fee_percentage"]
            return resp

        except Exception as e:
            self.db.rollback()
            raise BadRequestException(f"Failed to cancel passenger: {str(e)}")

    def cancel_and_process_refund(self, booking_id: str, user_id: Optional[str] = None, reason: str = "Customer request") -> RefundResponse:
        """
        Cancels booking and executes deterministic refund inside an atomic transaction boundary.
        """
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            booking = self.booking_repo.get_by_reference(booking_id)
        if not booking:
            booking = self.booking_repo.get_by_pnr(booking_id)
        if not booking:
            raise NotFoundException(f"Booking '{booking_id}' not found")



        if booking.status in [BookingStatus.CANCELLED, BookingStatus.REFUNDED]:
            raise BadRequestException("Booking is already cancelled or refunded")

        refund_calc = self.calculate_deterministic_refund(booking)
        refund_ref = f"RF-{secrets.token_hex(6).upper()}"

        try:
            # Transaction Boundary Start
            refund = Refund(
                id=str(uuid.uuid4()),
                booking_id=booking.id,
                refund_reference=refund_ref,
                gross_amount=refund_calc["gross_amount"],
                cancellation_fee=refund_calc["cancellation_fee"],
                net_refund_amount=refund_calc["net_refund_amount"],
                reason=reason,
                status=RefundStatus.PROCESSED,
                processed_at=datetime.now(timezone.utc)
            )
            self.db.add(refund)

            booking.status = BookingStatus.REFUNDED
            
            # Update payment status if exists
            payment = self.payment_repo.get_by_booking_id(booking.id)
            if payment:
                payment.status = PaymentStatus.REFUNDED

            # Restore seat availability
            if booking.flight:
                fare_obj = next((f for f in booking.flight.fares if f.travel_class == booking.travel_class), None)
                if fare_obj:
                    fare_obj.seats_available += booking.passenger_count
                
                # Unlock individual seat map items
                for p in booking.passengers:
                    if p.seat_number:
                        s_obj = next((s for s in booking.flight.seats if s.seat_number == p.seat_number), None)
                        if s_obj:
                            s_obj.is_booked = False

            self.db.commit()
            self.db.refresh(refund)
            resp = RefundResponse.model_validate(refund)
            resp.booking_reference = booking.booking_reference
            resp.pnr = booking.pnr
            resp.fee_percentage = refund_calc["fee_percentage"]
            return resp


        except Exception as e:
            self.db.rollback()
            raise BadRequestException(f"Failed to cancel booking: {str(e)}")
