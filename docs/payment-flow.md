# Payment Simulation & Refund Workflow

## 1. AP2 Payment Workflow

```
Select Flight & Seat
        ↓
Create Draft Booking (Status: PAYMENT_PENDING)
        ↓
POST /api/payments/intent
        ↓
Generates AP2 Payment Intent ID (pi_sim_...) & Mandate ID
        ↓
User Selects UPI / QR / Card & Enters Demo Authorization PIN (1234)
        ↓
POST /api/payments/execute
        ↓
Generates AP2 User Consent Token (ap2_consent_tok_...)
        ↓
Atomic DB Commit: Updates Payment to SUCCESS, Booking to CONFIRMED, & Generates PNR
        ↓
Booking Confirmation & Interactive E-Ticket
```

## 2. Deterministic Cancellation & Refund Calculation

```
My Trips → Booking Details → Cancel Booking
        ↓
Deterministic Calculation based on time remaining to departure:
  - > 72 hours: 90% refund (10% fee)
  - 24 - 72 hours: 70% refund (30% fee)
  - < 24 hours: 50% refund (50% fee)
        ↓
POST /api/bookings/{id}/cancel
        ↓
Atomic DB Transaction: Updates Booking to REFUNDED, Payment to REFUNDED, Records Refund Audit & Unlocks Seats
```
