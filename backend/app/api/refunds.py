from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.payment import RefundResponse
from app.services.refund_service import RefundService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/bookings", tags=["Cancellation & Refunds"])

@router.post("/{booking_id}/cancel", response_model=RefundResponse)
def cancel_booking_and_refund(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = RefundService(db)
    return service.cancel_and_process_refund(booking_id=booking_id, user_id=current_user.id)
