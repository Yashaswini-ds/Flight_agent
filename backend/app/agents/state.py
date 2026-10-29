from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class BookingStep:
    IDLE = "IDLE"
    NEED_DATE = "NEED_DATE"
    SEARCHING = "SEARCHING"
    FLIGHT_SELECTED = "FLIGHT_SELECTED"
    CLASS_SELECTED = "CLASS_SELECTED"
    SEATS_PENDING = "SEATS_PENDING"
    PASSENGERS_PENDING = "PASSENGERS_PENDING"
    REVIEW_PENDING = "REVIEW_PENDING"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"
    MODIFICATION_PENDING = "MODIFICATION_PENDING"

class CancellationStep:
    CANCELLATION_IDLE = "CANCELLATION_IDLE"
    CANCELLATION_NEED_REFERENCE = "CANCELLATION_NEED_REFERENCE"
    CANCELLATION_SELECT_PASSENGER = "CANCELLATION_SELECT_PASSENGER"
    CANCELLATION_LOOKUP = "CANCELLATION_LOOKUP"
    CANCELLATION_REVIEW = "CANCELLATION_REVIEW"
    CANCELLATION_CONFIRMATION_PENDING = "CANCELLATION_CONFIRMATION_PENDING"
    CANCELLATION_PROCESSING = "CANCELLATION_PROCESSING"
    CANCELLATION_COMPLETED = "CANCELLATION_COMPLETED"
    CANCELLATION_FAILED = "CANCELLATION_FAILED"

class AgentSessionState(BaseModel):
    user_id: str
    conversation_id: str
    booking_step: str = BookingStep.IDLE
    cancellation_step: str = CancellationStep.CANCELLATION_IDLE
    last_source: Optional[str] = None
    last_destination: Optional[str] = None
    last_travel_date: Optional[str] = None
    last_travel_class: Optional[str] = None
    class_distribution: Dict[str, int] = Field(default_factory=dict)
    passenger_class_map: Dict[str, str] = Field(default_factory=dict)
    seat_preference: Optional[str] = None
    passenger_count: int = 1
    passenger_count_explicit: bool = False
    available_flights: List[Dict[str, Any]] = Field(default_factory=list)
    selected_flight: Optional[Dict[str, Any]] = None
    original_flight: Optional[Dict[str, Any]] = None
    pending_flight: Optional[Dict[str, Any]] = None
    available_seats: List[Dict[str, Any]] = Field(default_factory=list)
    selected_seats: List[str] = Field(default_factory=list)
    passengers_data: List[Dict[str, Any]] = Field(default_factory=list)
    fare_summary: Optional[Dict[str, Any]] = None
    draft_booking_id: Optional[str] = None
    draft_booking_ref: Optional[str] = None
    payment_intent_id: Optional[str] = None
    last_booking_ref: Optional[str] = None
    cancellation_target_ref: Optional[str] = None
    cancellation_target_passenger_ids: List[str] = Field(default_factory=list)
    cancellation_target_passenger_names: List[str] = Field(default_factory=list)
    cancellation_cancel_all: bool = False
    cancellation_preview_data: Optional[Dict[str, Any]] = None

    def reset_booking_workflow(self):
        self.booking_step = BookingStep.IDLE
        self.available_flights = []
        self.selected_flight = None
        self.original_flight = None
        self.pending_flight = None
        self.available_seats = []
        self.selected_seats = []
        self.passengers_data = []
        self.class_distribution = {}
        self.passenger_class_map = {}
        self.seat_preference = None
        self.fare_summary = None
        self.draft_booking_id = None
        self.draft_booking_ref = None
        self.payment_intent_id = None
        self.passenger_count_explicit = False



    def reset_cancellation_workflow(self):
        self.cancellation_step = CancellationStep.CANCELLATION_IDLE
        self.cancellation_target_ref = None
        self.cancellation_preview_data = None

class SessionManager:
    _sessions: Dict[str, AgentSessionState] = {}

    @classmethod
    def get_or_create(cls, conversation_id: str, user_id: str) -> AgentSessionState:
        if conversation_id not in cls._sessions:
            cls._sessions[conversation_id] = AgentSessionState(
                conversation_id=conversation_id,
                user_id=user_id
            )
        return cls._sessions[conversation_id]

    @classmethod
    def update(cls, session: AgentSessionState):
        cls._sessions[session.conversation_id] = session

    @classmethod
    def clear(cls):
        cls._sessions.clear()



