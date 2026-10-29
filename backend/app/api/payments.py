from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.payment import PaymentIntentRequest, PaymentIntentResponse, ExecutePaymentRequest, PaymentResultResponse
from app.payment.payment_intent import create_simulated_payment_intent
from app.payment.authorization import generate_ap2_consent_token
from app.payment.transaction import execute_simulated_ap2_transaction
from app.repositories.booking_repository import BookingRepository
from app.repositories.payment_repository import PaymentRepository
from app.models.booking import BookingStatus
from app.models.payment import PaymentStatus
from app.api.deps import get_current_user
from app.models.user import User
from app.core.exceptions import NotFoundException, BadRequestException, ConflictException

router = APIRouter(prefix="/api/payments", tags=["Payments AP2"])

@router.post("/intent", response_model=PaymentIntentResponse)
def create_payment_intent(
    request: PaymentIntentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking_repo = BookingRepository(db)
    payment_repo = PaymentRepository(db)

    booking = booking_repo.get_by_id(request.booking_id)
    if not booking or booking.user_id != current_user.id:
        raise NotFoundException("Booking not found")

    if booking.status in [BookingStatus.CONFIRMED, BookingStatus.COMPLETED]:
        raise ConflictException("Booking is already confirmed and paid")

    existing_payment = payment_repo.get_by_booking_id(booking.id)
    if existing_payment and existing_payment.status == PaymentStatus.SUCCESS:
        raise ConflictException("Payment for this booking was already successfully completed")

    payment = create_simulated_payment_intent(
        booking_id=booking.id,
        amount=booking.total_fare,
        payment_method=request.payment_method
    )

    try:
        if existing_payment:
            existing_payment.payment_intent_id = payment.payment_intent_id
            existing_payment.transaction_reference = payment.transaction_reference
            existing_payment.payment_method = payment.payment_method
            existing_payment.status = PaymentStatus.INTENT_CREATED
            db.commit()
            payment = existing_payment
        else:
            payment_repo.create_payment(payment)
            db.commit()

        return PaymentIntentResponse(
            payment_intent_id=payment.payment_intent_id,
            booking_id=booking.id,
            amount=payment.amount,
            currency=payment.currency,
            merchant_mandate_id=payment.ap2_mandate_id or "",
            status=payment.status
        )
    except Exception as e:
        db.rollback()
        raise BadRequestException(f"Failed to create payment intent: {str(e)}")

@router.post("/execute", response_model=PaymentResultResponse)
def execute_payment(
    request: ExecutePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    payment_repo = PaymentRepository(db)
    booking_repo = BookingRepository(db)

    payment = payment_repo.get_by_intent_id(request.payment_intent_id)
    if not payment:
        raise NotFoundException("Payment intent not found")

    if payment.status == PaymentStatus.SUCCESS:
        booking = booking_repo.get_by_id(payment.booking_id)
        return PaymentResultResponse(
            transaction_reference=payment.transaction_reference,
            payment_intent_id=payment.payment_intent_id,
            ap2_consent_token=payment.ap2_consent_token or "",
            status=payment.status,
            amount=payment.amount,
            pnr=booking.pnr if booking else "",
            booking_reference=booking.booking_reference if booking else "",
            message="Payment was previously completed successfully (Idempotent call)"
        )

    try:
        # Generate AP2 consent token
        consent_tok = generate_ap2_consent_token(
            payment_intent_id=payment.payment_intent_id,
            demo_pin_or_auth=request.demo_pin_or_auth,
            demo_identifier=request.demo_identifier
        )

        success = execute_simulated_ap2_transaction(
            payment=payment,
            ap2_consent_token=consent_tok,
            demo_identifier=request.demo_identifier
        )

        if not success:
            db.rollback()
            raise BadRequestException("Payment execution failed")

        booking = booking_repo.get_by_id(payment.booking_id)
        if booking:
            booking.status = BookingStatus.CONFIRMED

        db.commit()

        return PaymentResultResponse(
            transaction_reference=payment.transaction_reference,
            payment_intent_id=payment.payment_intent_id,
            ap2_consent_token=consent_tok,
            status=payment.status,
            amount=payment.amount,
            pnr=booking.pnr if booking else "",
            booking_reference=booking.booking_reference if booking else "",
            message="Simulated AP2 payment authorized and confirmed successfully"
        )
    except Exception as e:
        db.rollback()
        raise BadRequestException(f"Payment execution error: {str(e)}")
