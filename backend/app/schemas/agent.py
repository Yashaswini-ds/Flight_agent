from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.models.flight import TravelClass

class TravelIntent(BaseModel):
    intent_type: str = Field(..., description="SEARCH_FLIGHTS, BOOK_FLIGHT, SELECT_FLIGHT, SELECT_CLASS, SELECT_SEATS, PROVIDE_PASSENGERS, PROCEED_PAYMENT, CANCEL_BOOKING, CHECK_STATUS, MODIFY, CANCEL_DRAFT, GENERAL_QUERY")
    source: Optional[str] = Field(None, description="City name or airport code (e.g., BLR, Bangalore)")
    destination: Optional[str] = Field(None, description="City name or airport code (e.g., DEL, Delhi)")
    travel_date: Optional[str] = Field(None, description="Travel date in YYYY-MM-DD format")
    passenger_count: Optional[int] = Field(None, description="Number of passengers if explicitly stated")
    travel_class: Optional[TravelClass] = Field(None, description="ECONOMY, PREMIUM_ECONOMY, BUSINESS if explicitly stated")
    class_distribution: Optional[Dict[str, int]] = Field(default_factory=dict, description="Class breakdown e.g. {'BUSINESS': 2, 'ECONOMY': 1}")
    seat_preference: Optional[str] = Field(None, description="WINDOW, AISLE, EXTRA_LEGROOM preference")
    ambiguous_class_count: bool = Field(False, description="True if class distribution sum != passenger_count")
    booking_reference: Optional[str] = Field(None, description="Target booking reference if cancellation/status requested")
    flight_number: Optional[str] = Field(None, description="Flight number (e.g., DA-100)")
    selected_seats: Optional[List[str]] = Field(default_factory=list, description="List of chosen seat numbers")
    passengers_data: Optional[List[dict]] = Field(default_factory=list, description="List of passenger info dictionaries")
    cancel_target_passenger: Optional[str] = Field(None, description="Name or seat number of specific passenger to cancel")
    cancel_passenger_index: Optional[int] = Field(None, description="1-based index of passenger to cancel")
    cancel_all: bool = Field(False, description="True if cancelling entire booking with all passengers")
    is_complete: bool = Field(False, description="True if mandatory details for current step are captured")
    missing_fields: List[str] = Field(default_factory=list, description="Fields required to fulfill intent")


class AgentChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class AgentChatResponse(BaseModel):
    conversation_id: str
    reply: str
    intent: Optional[TravelIntent] = None
    action_suggested: Optional[str] = None
    booking_step: Optional[str] = None
    cancellation_step: Optional[str] = None
    flights_found: Optional[List[dict]] = None
    available_seats: Optional[List[dict]] = None
    fare_summary: Optional[dict] = None
    payment_intent: Optional[dict] = None
    draft_booking: Optional[dict] = None
    cancellation_preview: Optional[dict] = None
    cancellation_result: Optional[dict] = None


