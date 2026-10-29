# API Specification Summary

## Auth APIs
- `POST /api/auth/register`: Register user account.
- `POST /api/auth/login`: Authenticate and receive JWT access token.
- `GET /api/auth/me`: Get current user profile.

## Flight APIs
- `GET /api/flights/cities`: List 5 predefined cities (BLR, MAA, HYD, BOM, DEL).
- `GET /api/flights/search`: Search available database flights.
- `GET /api/flights/{id}`: Get single flight details and fares.
- `GET /api/flights/{id}/seats`: Get seat grid layout for flight and travel class.

## Booking APIs
- `POST /api/bookings`: Create new booking draft.
- `GET /api/bookings`: List user bookings.
- `GET /api/bookings/{id_or_ref}`: Get full booking details with passenger info and status.
- `PATCH /api/bookings/{id}`: Modify eligible booking (travel date / travel class).
- `POST /api/bookings/{id}/cancel`: Process deterministic cancellation and refund.

## AP2 Payment APIs
- `POST /api/payments/intent`: Generate AP2 payment intent.
- `POST /api/payments/execute`: Execute AP2 simulated payment with consent token authorization.

## Support & Feedback APIs
- `POST /api/support`: Submit support ticket.
- `GET /api/support`: List user support tickets.
- `POST /api/feedback`: Submit platform rating and feedback.
- `GET /api/feedback`: List user feedback.

## AI Assistant & Admin APIs
- `POST /api/assistant/chat`: Dual-agent conversational AI assistant endpoint.
- `GET /api/admin/overview`: Get system-wide platform statistics (Admin only).
- `GET /api/admin/users`: List all platform users (Admin only).
- `GET /api/admin/bookings`: List all system bookings (Admin only).
