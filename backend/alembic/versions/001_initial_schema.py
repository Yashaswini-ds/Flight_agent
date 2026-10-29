"""Initial schema creation for PostgreSQL database

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-25 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), unique=True, index=True, nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('role', sa.Enum('USER', 'ADMIN', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # Cities
    op.create_table(
        'cities',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('code', sa.String(length=10), unique=True, index=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False)
    )

    # Airports
    op.create_table(
        'airports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('code', sa.String(length=10), unique=True, index=True, nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('city_code', sa.String(length=10), sa.ForeignKey('cities.code'), nullable=False)
    )

    # Airlines
    op.create_table(
        'airlines',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('code', sa.String(length=10), unique=True, index=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('logo_url', sa.String(length=255), nullable=True)
    )

    # Flights
    op.create_table(
        'flights',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('flight_number', sa.String(length=20), index=True, nullable=False),
        sa.Column('airline_code', sa.String(length=10), sa.ForeignKey('airlines.code'), nullable=False),
        sa.Column('origin_code', sa.String(length=10), sa.ForeignKey('cities.code'), nullable=False),
        sa.Column('destination_code', sa.String(length=10), sa.ForeignKey('cities.code'), nullable=False),
        sa.Column('departure_time', sa.DateTime(), nullable=False),
        sa.Column('arrival_time', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('stops', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='SCHEDULED')
    )

    # Flight Fares
    op.create_table(
        'flight_fares',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('flight_id', sa.String(length=36), sa.ForeignKey('flights.id'), nullable=False),
        sa.Column('travel_class', sa.Enum('ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', name='travelclass'), nullable=False),
        sa.Column('base_fare', sa.Float(), nullable=False),
        sa.Column('seats_available', sa.Integer(), nullable=False),
        sa.Column('baggage_allowance_kg', sa.Integer(), nullable=False),
        sa.Column('cabin_baggage_kg', sa.Integer(), nullable=False)
    )

    # Seats
    op.create_table(
        'seats',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('flight_id', sa.String(length=36), sa.ForeignKey('flights.id'), nullable=False),
        sa.Column('seat_number', sa.String(length=10), nullable=False),
        sa.Column('travel_class', sa.Enum('ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', name='travelclass'), nullable=False),
        sa.Column('is_booked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('price_extra', sa.Float(), nullable=False, server_default='0.0')
    )

    # Bookings
    op.create_table(
        'bookings',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('booking_reference', sa.String(length=20), unique=True, index=True, nullable=False),
        sa.Column('pnr', sa.String(length=10), unique=True, index=True, nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('flight_id', sa.String(length=36), sa.ForeignKey('flights.id'), nullable=False),
        sa.Column('travel_class', sa.Enum('ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', name='travelclass'), nullable=False),
        sa.Column('travel_date', sa.DateTime(), nullable=False),
        sa.Column('passenger_count', sa.Integer(), nullable=False),
        sa.Column('base_fare', sa.Float(), nullable=False),
        sa.Column('seat_addons_fee', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('baggage_addons_fee', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('taxes', sa.Float(), nullable=False),
        sa.Column('total_fare', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('BOOKED', 'PAYMENT_PENDING', 'CONFIRMED', 'CANCELLED', 'REFUND_PENDING', 'REFUNDED', 'COMPLETED', name='bookingstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # Booking Passengers
    op.create_table(
        'booking_passengers',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('booking_id', sa.String(length=36), sa.ForeignKey('bookings.id'), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('gender', sa.String(length=20), nullable=False),
        sa.Column('seat_number', sa.String(length=10), nullable=True)
    )

    # Payments
    op.create_table(
        'payments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('booking_id', sa.String(length=36), sa.ForeignKey('bookings.id'), nullable=False),
        sa.Column('payment_intent_id', sa.String(length=64), unique=True, index=True, nullable=False),
        sa.Column('transaction_reference', sa.String(length=64), unique=True, index=True, nullable=False),
        sa.Column('ap2_consent_token', sa.String(length=128), nullable=True),
        sa.Column('ap2_mandate_id', sa.String(length=64), nullable=True),
        sa.Column('payment_method', sa.Enum('UPI', 'QR', 'CARD', name='paymentmethod'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('status', sa.Enum('INTENT_CREATED', 'AUTHORIZED', 'SUCCESS', 'FAILED', 'REFUNDED', name='paymentstatus'), nullable=False),
        sa.Column('payment_details_masked', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # Refunds
    op.create_table(
        'refunds',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('booking_id', sa.String(length=36), sa.ForeignKey('bookings.id'), nullable=False),
        sa.Column('refund_reference', sa.String(length=64), unique=True, index=True, nullable=False),
        sa.Column('gross_amount', sa.Float(), nullable=False),
        sa.Column('cancellation_fee', sa.Float(), nullable=False),
        sa.Column('net_refund_amount', sa.Float(), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSED', 'FAILED', name='refundstatus'), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=False)
    )

    # Support Tickets
    op.create_table(
        'support_tickets',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('booking_reference', sa.String(length=20), nullable=True),
        sa.Column('category', sa.Enum('BOOKING', 'PAYMENT', 'CANCELLATION', 'GENERAL', name='ticketcategory'), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED', name='ticketstatus'), nullable=False),
        sa.Column('admin_response', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # Feedback
    op.create_table(
        'feedback',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('booking_reference', sa.String(length=20), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('comments', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('feedback')
    op.drop_table('support_tickets')
    op.drop_table('refunds')
    op.drop_table('payments')
    op.drop_table('booking_passengers')
    op.drop_table('bookings')
    op.drop_table('seats')
    op.drop_table('flight_fares')
    op.drop_table('flights')
    op.drop_table('airlines')
    op.drop_table('airports')
    op.drop_table('cities')
    op.drop_table('users')
