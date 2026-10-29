from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.booking_service import BookingService
from app.schemas.booking import CreateBookingRequest, BookingResponse, ModifyBookingRequest
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

@router.post("", response_model=BookingResponse)
def create_booking(
    request: CreateBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = BookingService(db)
    return service.create_booking(user_id=current_user.id, request=request)

@router.get("", response_model=List[BookingResponse])
def get_user_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = BookingService(db)
    return service.get_user_bookings(user_id=current_user.id)

@router.get("/{booking_id_or_ref}", response_model=BookingResponse)
def get_booking_by_id(
    booking_id_or_ref: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = BookingService(db)
    return service.get_booking(booking_id_or_ref=booking_id_or_ref, user_id=current_user.id)

@router.patch("/{booking_id}", response_model=BookingResponse)
def modify_booking(
    booking_id: str,
    request: ModifyBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = BookingService(db)
    return service.modify_booking(booking_id=booking_id, user_id=current_user.id, request=request)
