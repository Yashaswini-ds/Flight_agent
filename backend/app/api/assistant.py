import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.agent import AgentChatRequest, AgentChatResponse
from app.agents.intent_agent import IntentAgent
from app.agents.booking_agent import BookingAgent
from app.api.deps import get_current_user_or_demo
from app.models.user import User

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])

@router.post("/chat", response_model=AgentChatResponse)
def assistant_chat(
    request: AgentChatRequest,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    from app.agents.state import SessionManager
    conv_id = request.conversation_id or str(uuid.uuid4())
    session = SessionManager.get_or_create(conv_id, current_user.id)
    
    # 1. Intent Agent extracts structured intent with active session context
    intent_agent = IntentAgent()
    intent = intent_agent.parse_intent(
        request.message,
        active_step=session.booking_step,
        active_cancellation_step=session.cancellation_step
    )

    # 2. Booking Agent consumes intent and operates strictly via tool wrappers
    booking_agent = BookingAgent(db)
    response = booking_agent.process_intent(
        intent=intent,
        conversation_id=conv_id,
        user_id=current_user.id,
        user_message=request.message
    )

    return response
