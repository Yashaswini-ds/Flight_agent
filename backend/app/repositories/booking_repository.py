from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.booking import Booking, BookingPassenger, BookingStatus

class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, booking_id: str) -> Optional[Booking]:
        return self.db.query(Booking).filter(Booking.id == booking_id).first()

    def get_by_reference(self, booking_reference: str) -> Optional[Booking]:
        return self.db.query(Booking).filter(Booking.booking_reference == booking_reference).first()

    def get_by_pnr(self, pnr: str) -> Optional[Booking]:
        return self.db.query(Booking).filter(Booking.pnr == pnr).first()

    def get_user_bookings(self, user_id: str) -> List[Booking]:
        return (
            self.db.query(Booking)
            .filter(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
            .all()
        )

    def get_all_bookings(self) -> List[Booking]:
        return self.db.query(Booking).order_by(Booking.created_at.desc()).all()

    def create(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.flush()
        return booking

    def update_status(self, booking_id: str, status: BookingStatus) -> Optional[Booking]:
        booking = self.get_by_id(booking_id)
        if booking:
            booking.status = status
            self.db.flush()
        return booking
