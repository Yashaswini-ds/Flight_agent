# AI Agents Architecture & Tool Safety

## Two-Agent Design

FlightAgent implements two strictly decoupled AI agents:

### 1. Intent Agent (`backend/app/agents/intent_agent.py`)
- **Role**: Natural language processing and parameter extraction.
- **Input**: Raw text from user prompt.
- **Output**: Structured `TravelIntent` Pydantic model (`intent_type`, `source`, `destination`, `travel_date`, `passenger_count`, `travel_class`, `missing_fields`).
- **Safety**: Pure extraction engine. Does not possess database access or service tools.

### 2. Booking Agent (`backend/app/agents/booking_agent.py`)
- **Role**: Workflow coordination & tool invocation.
- **Input**: Structured `TravelIntent` output from Intent Agent.
- **Tools Used**: Strictly limited to wrapper functions in `backend/app/agents/tools.py`.
- **Safety**: Cannot write SQL queries, modify DB records, or compute fares directly. All execution flows through the Service Layer.
