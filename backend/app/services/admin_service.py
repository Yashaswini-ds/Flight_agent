from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.booking_repository import BookingRepository
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole
from app.models.flight import Flight
from app.models.payment import Payment
from app.models.refund import Refund
from app.models.support import SupportTicket
from app.models.feedback import Feedback
from app.schemas.auth import UserResponse
from app.schemas.booking import BookingResponse

class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.booking_repo = BookingRepository(db)

    def get_dashboard_overview(self) -> Dict[str, Any]:
        total_users = self.db.query(User).filter(User.role == UserRole.USER).count()
        total_flights = self.db.query(Flight).count()
        total_bookings = self.db.query(BookingRepository(self.db).get_all_bookings()).count() if False else self.db.query(BookingRepository(self.db).db.query(BookingRepository(self.db).get_all_bookings()).statement if False else None) or self.db.query(Flight).count()
        
        # Exact stats
        users_cnt = self.db.query(User).count()
        flights_cnt = self.db.query(Flight).count()
        bookings_list = self.booking_repo.get_all_bookings()
        bookings_cnt = len(bookings_list)
        payments_cnt = self.db.query(Payment).count()
        refunds_cnt = self.db.query(Refund).count()
        tickets_cnt = self.db.query(SupportTicket).count()
        feedback_cnt = self.db.query(Feedback).count()

        return {
            "total_users": users_cnt,
            "total_flights": flights_cnt,
            "total_bookings": bookings_cnt,
            "total_payments": payments_cnt,
            "total_refunds": refunds_cnt,
            "open_tickets": tickets_cnt,
            "total_feedback": feedback_cnt
        }

    def list_all_users(self) -> List[UserResponse]:
        users = self.db.query(User).all()
        return [UserResponse.model_validate(u) for u in users]

    def list_all_bookings(self) -> List[BookingResponse]:
        from app.services.booking_service import BookingService
        b_service = BookingService(self.db)
        bookings = self.booking_repo.get_all_bookings()
        return [b_service._build_booking_response(b) for b in bookings]
