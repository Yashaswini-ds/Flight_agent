import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.support import SupportTicket, TicketStatus
from app.schemas.support import SupportTicketCreate, SupportTicketResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/support", tags=["Support Tickets"])

@router.post("", response_model=SupportTicketResponse)
def create_support_ticket(
    request: SupportTicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = SupportTicket(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        booking_reference=request.booking_reference,
        category=request.category,
        subject=request.subject,
        message=request.message,
        status=TicketStatus.OPEN
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return SupportTicketResponse.model_validate(ticket)

@router.get("", response_model=List[SupportTicketResponse])
def get_user_support_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tickets = db.query(SupportTicket).filter(SupportTicket.user_id == current_user.id).order_by(SupportTicket.created_at.desc()).all()
    return [SupportTicketResponse.model_validate(t) for t in tickets]
