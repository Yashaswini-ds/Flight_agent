from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_admin
from app.models.user import User
from app.services.admin_service import AdminService
from app.schemas.auth import UserResponse
from app.schemas.booking import BookingResponse
from app.schemas.support import SupportTicketResponse, FeedbackResponse
from app.models.support import SupportTicket
from app.models.feedback import Feedback

router = APIRouter(prefix="/api/admin", tags=["Admin Operations"])

@router.get("/overview")
def get_admin_overview(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    return service.get_dashboard_overview()

@router.get("/users", response_model=List[UserResponse])
def list_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    return service.list_all_users()

@router.get("/bookings", response_model=List[BookingResponse])
def list_bookings(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    return service.list_all_bookings()

@router.get("/tickets", response_model=List[SupportTicketResponse])
def list_support_tickets(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tickets = db.query(SupportTicket).order_by(SupportTicket.created_at.desc()).all()
    return [SupportTicketResponse.model_validate(t) for t in tickets]

@router.get("/feedback", response_model=List[FeedbackResponse])
def list_feedback(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    fbs = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    results = []
    for f in fbs:
        u = db.query(User).filter(User.id == f.user_id).first()
        results.append(
            FeedbackResponse(
                id=f.id,
                user_id=f.user_id,
                user_name=u.full_name if u else "User",
                booking_reference=f.booking_reference,
                rating=f.rating,
                category=f.category,
                comments=f.comments,
                created_at=f.created_at
            )
        )
    return results
