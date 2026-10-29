HEAD
# FlightAgent - Production-Grade GenAI Flight Ticket Booking Platform

FlightAgent is a full-stack, two-agent GenAI flight booking application designed for high security, modularity, and deterministic business logic.

---

## Technical Stack & Architecture

- **Frontend**: React + TypeScript + Vite + Tailwind CSS (Primary Teal `#0F766E`, `#0D9488`, Secondary `#F0FDFA`)
- **Backend**: FastAPI + Pydantic v2
- **Database**: PostgreSQL + SQLAlchemy ORM + Alembic Migrations
- **Security**: JWT Authentication + Bcrypt Password Hashing + Role-Based Access Control (`USER` / `ADMIN`)
- **AI Agents**: Decoupled `Intent Agent` and `Booking Agent` operating via controlled service tools
- **Payment Protocol**: AP2 (Agent Payments Protocol) simulated authorization and payment intent flow
- **Testing**: Pytest automated test suite

---

## 5 Predefined Cities Supported
1. **Bangalore / Bengaluru** (`BLR`)
2. **Chennai** (`MAA`)
3. **Hyderabad** (`HYD`)
4. **Mumbai** (`BOM`)
5. **Delhi** (`DEL`)

---

## Pre-seeded Demo Credentials (Testing Only)

> [!NOTE]
> These credentials are provided for development and manager inspection purposes only. Passwords are securely hashed using bcrypt in PostgreSQL.

- **User Account**:
  - **Email**: `user@flightagent.com`
  - **Password**: `user123`
  - **Role**: `USER`

- **Admin Account**:
  - **Email**: `admin@flightagent.com`
  - **Password**: `admin123`
  - **Role**: `ADMIN`

---

## Setup & Local Installation

### 1. Backend Setup (Python 3.11+)

```bash
cd backend

# Create virtual environment
python -m venv venv
# Activate on Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run Alembic Database Migrations
alembic upgrade head

# Seed Database (Cities, Flights, Seats, Fares, Demo Accounts)
python app/db/seed.py

# Start Backend Server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup (Node v20+)

```bash
cd frontend

# Install dependencies
npm install

# Start Vite Development Server
npm run dev
```

### 3. Running Backend Tests

```bash
cd backend
pytest
```

---

## Project Documentation Links
- [System Architecture](file:///docs/architecture.md)
- [Database Schema & ERD](file:///docs/database.md)
- [Dual AI Agents Specification](file:///docs/agents.md)
- [AP2 Payment Protocol Mapping](file:///docs/ap2.md)
- [Payment & Refund Workflow](file:///docs/payment-flow.md)
- [REST API Reference](file:///docs/api.md)
=======
# Flight_agent
AI-powered flight booking platform with secure auth, smart booking agents, and a modern full-stack architecture.
 692efc7a7ea94d1d38ab3c2855f1b59bc0897a4e
