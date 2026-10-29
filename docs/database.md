# Database Schema & Relational Design

FlightAgent uses PostgreSQL as its primary database.

## Entity Relationship Diagram

```
User (1) ---- (N) Booking (1) ---- (N) BookingPassenger
                   |
                   |--- (1) Payment
                   |--- (1) Refund
                   |--- (1) Flight (N) ---- (1) Airline
                                 |
                                 |---- (N) FlightFare
                                 |---- (N) FlightSeat
```

## Relational Tables
- `users`: User credentials (bcrypt hashed), profile, role (`USER` / `ADMIN`).
- `cities`: Predefined 5 Indian cities (BLR, MAA, HYD, BOM, DEL).
- `airports`: Airport codes and names.
- `airlines`: Demo airlines (Demo Air, SkyExpress, IndiaFly).
- `flights`: Schedule, origin/destination city codes, departure/arrival timestamps.
- `flight_fares`: Fare breakdown per `TravelClass` (Economy, Premium Economy, Business).
- `seats`: Interactive seat layout map per flight with extra baggage/seat pricing.
- `bookings`: Booking records, unique `booking_reference`, PNR code, status.
- `booking_passengers`: Passenger details and assigned seat numbers.
- `payments`: AP2 Payment intent, consent token, masked audit trail, idempotency keys.
- `refunds`: Deterministic refund calculation, cancellation fees, net refund amount.
- `support_tickets`: Support requests and admin responses.
- `feedback`: User platform ratings (1-5 stars) and comments.
