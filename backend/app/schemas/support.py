from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.support import TicketStatus, TicketCategory

class SupportTicketCreate(BaseModel):
    category: TicketCategory
    booking_reference: Optional[str] = None
    subject: str
    message: str

class SupportTicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    booking_reference: Optional[str]
    category: TicketCategory
    subject: str
    message: str
    status: TicketStatus
    admin_response: Optional[str]
    created_at: datetime

class FeedbackCreate(BaseModel):
    booking_reference: Optional[str] = None
    rating: int
    category: str
    comments: str

class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    user_name: Optional[str] = None
    booking_reference: Optional[str]
    rating: int
    category: str
    comments: str
    created_at: datetime
