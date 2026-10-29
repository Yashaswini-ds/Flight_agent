from typing import Optional
from sqlalchemy.orm import Session
from app.models.payment import Payment, PaymentStatus
from app.models.refund import Refund

class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_intent_id(self, payment_intent_id: str) -> Optional[Payment]:
        return self.db.query(Payment).filter(Payment.payment_intent_id == payment_intent_id).first()

    def get_by_transaction_ref(self, transaction_ref: str) -> Optional[Payment]:
        return self.db.query(Payment).filter(Payment.transaction_reference == transaction_ref).first()

    def get_by_booking_id(self, booking_id: str) -> Optional[Payment]:
        return self.db.query(Payment).filter(Payment.booking_id == booking_id).first()

    def create_payment(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.flush()
        return payment

    def create_refund(self, refund: Refund) -> Refund:
        self.db.add(refund)
        self.db.flush()
        return refund
