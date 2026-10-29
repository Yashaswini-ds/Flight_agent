# Architecture & System Design

## Overview
FlightAgent is a production-grade, two-agent GenAI flight booking application designed for high security, modularity, and deterministic business logic.

```
React (TypeScript + Vite)
        ↓
FastAPI Backend
        ↓
JWT Auth & RBAC (USER / ADMIN)
        ↓
Agent Layer (Intent Agent → Booking Agent)
        ↓
Controlled Backend Tools
        ↓
Service Layer (Deterministic Fares & Refunds)
        ↓
Repository Layer
        ↓
SQLAlchemy ORM
        ↓
PostgreSQL Engine (Alembic Migrations)
```

## Key Architectural Principles
1. **PostgreSQL Relational DB**: PostgreSQL is the single authoritative relational store with Alembic schema versioning.
2. **Dual AI Agents**:
   - `Intent Agent`: Translates natural language into structured Pydantic `TravelIntent`.
   - `Booking Agent`: Coordinates flight search and booking via controlled tool wrappers.
3. **Controlled Tool Boundaries**: AI agents cannot execute arbitrary SQL or modify DB records directly. They invoke deterministic Python service wrappers.
4. **Deterministic Fares & Financial Math**: Fares, configurable demo taxes (`DEMO_TAX_PERCENTAGE`), seat selection fees, and cancellation refund percentages are strictly computed by Python algorithms.
5. **Database Transaction Boundaries**: Multi-step booking and cancellation workflows execute inside SQLAlchemy transactions with explicit commit/rollback handling.
