export type UserRole = 'USER' | 'ADMIN';
export type TravelClass = 'ECONOMY' | 'PREMIUM_ECONOMY' | 'BUSINESS';
export type BookingStatus = 'BOOKED' | 'PAYMENT_PENDING' | 'CONFIRMED' | 'CANCELLED' | 'REFUND_PENDING' | 'REFUNDED' | 'COMPLETED';
export type PaymentMethod = 'UPI' | 'QR' | 'CARD';
export type PaymentStatus = 'INTENT_CREATED' | 'AUTHORIZED' | 'SUCCESS' | 'FAILED' | 'REFUNDED';

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: UserRole;
  created_at: string;
}

export interface City {
  id: string;
  code: string;
  name: string;
  state: string;
}

export interface FlightFare {
  travel_class: TravelClass;
  base_fare: number;
  seats_available: number;
  baggage_allowance_kg: number;
  cabin_baggage_kg: number;
}

export interface Seat {
  id: string;
  seat_number: string;
  travel_class: TravelClass;
  is_booked: boolean;
  price_extra: number;
}

export interface Flight {
  id: string;
  flight_number: string;
  airline_code: string;
  airline_name: string;
  origin_code: string;
  origin_city: string;
  destination_code: string;
  destination_city: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  stops: number;
  status: string;
  fares: FlightFare[];
}

export interface Passenger {
  id?: string;
  first_name: string;
  last_name: string;
  age: number;
  gender: string;
  seat_number?: string;
}

export interface Booking {
  id: string;
  booking_reference: string;
  pnr: string;
  user_id: string;
  flight_id: string;
  airline_name: string;
  flight_number: string;
  origin_code: string;
  origin_city: string;
  destination_code: string;
  destination_city: string;
  departure_time: string;
  arrival_time: string;
  travel_class: TravelClass;
  travel_date: string;
  passenger_count: number;
  base_fare: number;
  seat_addons_fee: number;
  baggage_addons_fee: number;
  taxes: number;
  total_fare: number;
  status: BookingStatus;
  created_at: string;
  passengers: Passenger[];
}

export interface PaymentIntent {
  payment_intent_id: string;
  booking_id: string;
  amount: number;
  currency: string;
  merchant_mandate_id: string;
  status: PaymentStatus;
}

export interface PaymentResult {
  transaction_reference: string;
  payment_intent_id: string;
  ap2_consent_token: string;
  status: PaymentStatus;
  amount: number;
  pnr: string;
  booking_reference: string;
  message: string;
}

export interface RefundResult {
  id: string;
  booking_id: string;
  refund_reference: string;
  gross_amount: number;
  cancellation_fee: number;
  net_refund_amount: number;
  reason?: string;
  status: string;
  processed_at: string;
}

export interface SupportTicket {
  id: string;
  user_id: string;
  booking_reference?: string;
  category: 'BOOKING' | 'PAYMENT' | 'CANCELLATION' | 'GENERAL';
  subject: string;
  message: string;
  status: string;
  admin_response?: string;
  created_at: string;
}

export interface Feedback {
  id: string;
  user_id: string;
  user_name?: string;
  booking_reference?: string;
  rating: number;
  category: string;
  comments: string;
  created_at: string;
}

export interface TravelIntent {
  intent_type: string;
  source?: string;
  destination?: string;
  travel_date?: string;
  passenger_count?: number;
  travel_class?: TravelClass;
  booking_reference?: string;
  is_complete: boolean;
  missing_fields: string[];
}

export interface AgentResponse {
  conversation_id: string;
  reply: string;
  intent?: TravelIntent;
  action_suggested?: string;
  booking_step?: string;
  cancellation_step?: string;
  flights_found?: Flight[];
  available_seats?: Seat[];
  fare_summary?: any;
  payment_intent?: PaymentIntent;
  draft_booking?: any;
  cancellation_preview?: any;
  cancellation_result?: any;
}


