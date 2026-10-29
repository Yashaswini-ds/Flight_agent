import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.feedback import Feedback
from app.schemas.support import FeedbackCreate, FeedbackResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

@router.post("", response_model=FeedbackResponse)
def create_feedback(
    request: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fb = Feedback(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        booking_reference=request.booking_reference,
        rating=request.rating,
        category=request.category,
        comments=request.comments
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return FeedbackResponse(
        id=fb.id,
        user_id=fb.user_id,
        user_name=current_user.full_name,
        booking_reference=fb.booking_reference,
        rating=fb.rating,
        category=fb.category,
        comments=fb.comments,
        created_at=fb.created_at
    )

@router.get("", response_model=List[FeedbackResponse])
def get_user_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fbs = db.query(Feedback).filter(Feedback.user_id == current_user.id).order_by(Feedback.created_at.desc()).all()
    return [
        FeedbackResponse(
            id=f.id,
            user_id=f.user_id,
            user_name=current_user.full_name,
            booking_reference=f.booking_reference,
            rating=f.rating,
            category=f.category,
            comments=f.comments,
            created_at=f.created_at
        ) for f in fbs
    ]
