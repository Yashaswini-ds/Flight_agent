import uuid
import secrets
from typing import Dict, Any
from app.models.payment import Payment, PaymentMethod, PaymentStatus

def create_simulated_payment_intent(
    booking_id: str,
    amount: float,
    payment_method: PaymentMethod,
    currency: str = "INR"
) -> Payment:
    """
    Creates a simulated AP2 Payment Intent.
    Generates unique payment_intent_id and merchant mandate reference.
    """
    payment_intent_id = f"pi_sim_{secrets.token_hex(12)}"
    merchant_mandate_id = f"man_sim_{secrets.token_hex(8)}"
    transaction_ref = f"tx_sim_{secrets.token_hex(12)}"

    payment = Payment(
        id=str(uuid.uuid4()),
        booking_id=booking_id,
        payment_intent_id=payment_intent_id,
        transaction_reference=transaction_ref,
        ap2_mandate_id=merchant_mandate_id,
        payment_method=payment_method,
        amount=amount,
        currency=currency,
        status=PaymentStatus.INTENT_CREATED,
        payment_details_masked=f"Simulated {payment_method.value}"
    )
    return payment
