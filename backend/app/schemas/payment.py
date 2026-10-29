from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.payment import PaymentMethod, PaymentStatus

class PaymentIntentRequest(BaseModel):
    booking_id: str
    payment_method: PaymentMethod

class PaymentIntentResponse(BaseModel):
    payment_intent_id: str
    booking_id: str
    amount: float
    currency: str
    merchant_mandate_id: str
    status: PaymentStatus

class ExecutePaymentRequest(BaseModel):
    payment_intent_id: str
    payment_method: PaymentMethod
    demo_pin_or_auth: str  # e.g., "1234" for demo
    demo_identifier: str    # e.g., "user@upi" or "4111222233334444"

class PaymentResultResponse(BaseModel):
    transaction_reference: str
    payment_intent_id: str
    ap2_consent_token: str
    status: PaymentStatus
    amount: float
    pnr: str
    booking_reference: str
    message: str

class RefundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    booking_id: str
    refund_reference: str
    gross_amount: float
    cancellation_fee: float
    net_refund_amount: float
    reason: Optional[str]
    status: str
    processed_at: datetime
    booking_reference: Optional[str] = None
    pnr: Optional[str] = None
    fee_percentage: Optional[int] = 0


