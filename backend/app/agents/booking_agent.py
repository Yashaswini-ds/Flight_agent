from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.agents.tools import BookingAgentTools
from app.schemas.agent import TravelIntent, AgentChatResponse
from app.agents.state import SessionManager, AgentSessionState, BookingStep
from app.models.flight import TravelClass
import uuid

class BookingAgent:
    """
    Dedicated Booking Agent.
    Receives structured TravelIntent from IntentAgent.
    Operates strictly via controlled BookingAgentTools wrappers to execute backend services.
    Never executes SQL or accesses database directly.
    Enforces strict multi-step booking state machine.
    """
    def __init__(self, db: Session):
        self.tools = BookingAgentTools(db)

    def process_intent(
        self,
        intent: TravelIntent,
        conversation_id: str,
        user_id: str,
        user_message: str
    ) -> AgentChatResponse:
        session = SessionManager.get_or_create(conversation_id, user_id)

        # 0. Check reset / cancel draft action
        if intent.intent_type == "CANCEL_DRAFT":
            session.reset_booking_workflow()
            SessionManager.update(session)
            return AgentChatResponse(
                conversation_id=conversation_id,
                reply="I have cancelled your current booking draft. How else can I help you today?",
                intent=intent,
                action_suggested="DRAFT_CANCELLED",
                booking_step=session.booking_step
            )

        # -------------------------------------------------------------
        # MODIFICATION WORKFLOW ENGINE (Pre-Payment Draft Adjustments)
        # -------------------------------------------------------------
        upper_msg = user_message.upper().strip()
        mod_target = intent.flight_number

        if intent.intent_type == "MODIFY" or session.booking_step == BookingStep.MODIFICATION_PENDING or upper_msg in ["MODIFY", "MODIFY BOOKING", "MODIFY MY BOOKING", "WHAT CAN I CHANGE?"]:
            if "1" in upper_msg and "FLIGHT" in upper_msg or upper_msg in ["1", "FLIGHT", "OPTION 1", "CHANGE FLIGHT"] or mod_target == "CHANGE_FLIGHT":
                session.original_flight = session.selected_flight
                session.pending_flight = None
                session.selected_flight = None
                session.booking_step = BookingStep.SEARCHING
                SessionManager.update(session)
            elif "2" in upper_msg and "CLASS" in upper_msg or upper_msg in ["2", "TRAVEL CLASS", "CLASS", "OPTION 2", "CHANGE CLASS"] or mod_target == "CHANGE_CLASS":
                session.last_travel_class = None
                session.class_distribution = {}
                session.booking_step = BookingStep.CLASS_SELECTED
                SessionManager.update(session)
            elif "3" in upper_msg and "SEAT" in upper_msg or upper_msg in ["3", "SEAT", "SEATS", "OPTION 3", "CHANGE SEAT"] or mod_target == "CHANGE_SEAT":
                session.selected_seats = []
                session.booking_step = BookingStep.SEATS_PENDING
                SessionManager.update(session)
            elif "4" in upper_msg and "PASSENGER" in upper_msg or upper_msg in ["4", "PASSENGER DETAILS", "PASSENGERS", "OPTION 4", "CHANGE PASSENGERS"] or mod_target == "CHANGE_PASSENGERS":
                session.passengers_data = []
                session.booking_step = BookingStep.PASSENGERS_PENDING
                SessionManager.update(session)
                reply_msg = (
                    f"Seats {', '.join(session.selected_seats[:session.passenger_count])} selected.\n\n"
                    f"Please provide updated passenger details for all {session.passenger_count} traveler(s).\n"
                    f"Required per passenger: First Name, Last Name, Age, Gender."
                )
                return AgentChatResponse(
                    conversation_id=conversation_id,
                    reply=reply_msg,
                    intent=intent,
                    action_suggested="COLLECT_PASSENGERS",
                    booking_step=session.booking_step
                )

            elif "5" in upper_msg or "CANCEL MODIFICATION" in upper_msg or mod_target == "CANCEL_MODIFICATION":
                session.booking_step = BookingStep.REVIEW_PENDING
                SessionManager.update(session)
            else:
                session.booking_step = BookingStep.MODIFICATION_PENDING
                SessionManager.update(session)
                reply_msg = (
                    "What would you like to change?\n\n"
                    "1. Flight\n"
                    "2. Travel class\n"
                    "3. Seat\n"
                    "4. Passenger details\n"
                    "5. Cancel modification"
                )
                return AgentChatResponse(
                    conversation_id=conversation_id,
                    reply=reply_msg,
                    intent=intent,
                    action_suggested="MODIFICATION_MENU",
                    booking_step=session.booking_step
                )

        # Update Session Memory from current intent
        if intent.source: session.last_source = intent.source
        if intent.destination: session.last_destination = intent.destination
        if intent.travel_date: session.last_travel_date = intent.travel_date

        if intent.class_distribution:
            for k, v in intent.class_distribution.items():
                if k == "_REMAINING_CLASS_":
                    known_sum = sum(cnt for ck, cnt in session.class_distribution.items() if ck != "_REMAINING_CLASS_")
                    rem_cnt = max(1, session.passenger_count - known_sum)
                    session.class_distribution[v] = rem_cnt
                else:
                    session.class_distribution[k] = v

        if len(session.class_distribution) > 1:
            session.last_travel_class = None
        elif intent.travel_class and not session.class_distribution:
            session.last_travel_class = intent.travel_class.value if hasattr(intent.travel_class, 'value') else intent.travel_class

        # Preserve explicit passenger count when user provides class count only
        if intent.passenger_count:
            if not session.passenger_count_explicit or intent.ambiguous_class_count or any(w in user_message.upper() for w in ["TICKET", "PASSENGER", "PEOPLE", "MAKE IT", "PERSON"]):
                session.passenger_count = intent.passenger_count
                session.passenger_count_explicit = True


        if intent.seat_preference:
            session.seat_preference = intent.seat_preference

        if intent.selected_seats:
            for s in intent.selected_seats:
                if s not in session.selected_seats:
                    session.selected_seats.append(s)

        # Hard Passenger Validation Helper & Merging
        INVALID_PASSENGER_TOKENS = {"FULL NAME", "PASSENGER 1", "PASSENGER 2", "PASSENGER 3", "PASSENGER 4", "PASSENGER", "MALE", "FEMALE", "UNKNOWN", "TEST", "JOHN DOE", "FIRST LAST", "AGE", "GENDER", "NAME"}

        def is_valid_name(val: Any) -> bool:
            if not val or not isinstance(val, str):
                return False
            c = val.strip().upper()
            if c in INVALID_PASSENGER_TOKENS or any(b in c for b in ["PASSENGER", "FULL NAME", "UNKNOWN", "TEST"]):
                return False
            return len(c) >= 2

        if intent.passengers_data:
            for p in intent.passengers_data:
                f_n = p.get('first_name')
                if not is_valid_name(f_n):
                    continue
                matched = False
                for existing in session.passengers_data:
                    if existing.get('first_name', '').upper() == f_n.upper():
                        if is_valid_name(p.get('last_name')):
                            existing['last_name'] = p['last_name']
                        if p.get('age') and isinstance(p['age'], int):
                            existing['age'] = p['age']
                        if p.get('gender') in ["MALE", "FEMALE"]:
                            existing['gender'] = p['gender']
                        matched = True
                        break
                if not matched:
                    session.passengers_data.append({
                        "first_name": f_n,
                        "last_name": p.get('last_name') if is_valid_name(p.get('last_name')) else "",
                        "age": p.get('age') if isinstance(p.get('age'), int) else None,
                        "gender": p.get('gender') if p.get('gender') in ["MALE", "FEMALE"] else None
                    })

        # Cancellation workflow dispatch (MUST override active booking state!)
        if intent.intent_type in ["CANCEL_BOOKING", "CONFIRM_CANCELLATION", "CANCEL_INFO"] or session.cancellation_step != "CANCELLATION_IDLE":
            return self.handle_cancellation_workflow(session, intent, conversation_id, user_id, user_message)

        if intent.intent_type == "CHECK_STATUS":
            if intent.booking_reference:
                try:
                    booking = self.tools.get_booking(intent.booking_reference, user_id=user_id)
                    reply_msg = (
                        f"Booking Status for {booking['booking_reference']}\n\n"
                        f"Flight: {booking['airline_name']} ({booking['flight_number']})\n"
                        f"Route: {booking['origin_city']} → {booking['destination_city']}\n"
                        f"Date: {booking['travel_date']}\n"
                        f"PNR: {booking['pnr']}\n"
                        f"Status: {booking['status']}"
                    )
                except Exception:
                    reply_msg = f"Could not find booking {intent.booking_reference} under your account."
            else:
                user_bookings = self.tools.get_user_bookings(user_id)
                if user_bookings:
                    lines = [
                        f"• {b['booking_reference']} ({b['origin_code']} → {b['destination_code']}, PNR: {b['pnr']}, Status: {b['status']})"
                        for b in user_bookings[:4]
                    ]
                    b_str = "\n".join(lines)
                    reply_msg = f"Here are your active booking(s):\n\n{b_str}\n\nProvide a specific booking reference (e.g. BK-...) for full details."
                else:
                    reply_msg = "You have no active bookings under your account. Provide a Booking Reference (e.g. BK-1234) if you want to check a specific ticket."

            return AgentChatResponse(
                conversation_id=conversation_id,
                reply=reply_msg,
                intent=intent,
                action_suggested="STATUS_CHECKED"
            )

        # -------------------------------------------------------------
        # MULTI-STEP CONVERSATIONAL BOOKING WORKFLOW ENGINE
        # -------------------------------------------------------------

        # STEP 1: Route & Date Validation
        if not session.last_source or not session.last_destination:
            return AgentChatResponse(
                conversation_id=conversation_id,
                reply="I can help you search and book flights. Please specify your origin and destination cities (e.g. from Bangalore to Hyderabad).",
                intent=intent,
                action_suggested="NEED_INFO",
                booking_step=session.booking_step
            )

        if not session.last_travel_date:
            session.booking_step = BookingStep.NEED_DATE
            SessionManager.update(session)
            return AgentChatResponse(
                conversation_id=conversation_id,
                reply=f"Sure, I can help you book a flight from {session.last_source} to {session.last_destination}.\n\nWhat date would you like to travel?",
                intent=intent,
                action_suggested="NEED_DATE",
                booking_step=session.booking_step
            )

        # STEP 2: Flight Search & Selection
        t_class_enum = TravelClass[session.last_travel_class] if session.last_travel_class and session.last_travel_class in TravelClass.__members__ else TravelClass.ECONOMY

        if not session.available_flights:
            flights = self.tools.search_flights(
                origin=session.last_source,
                destination=session.last_destination,
                travel_date=session.last_travel_date,
                passenger_count=session.passenger_count,
                travel_class=t_class_enum
            )
            session.available_flights = flights

        if not session.available_flights:
            return AgentChatResponse(
                conversation_id=conversation_id,
                reply=f"No available flights found from {session.last_source} to {session.last_destination} on {session.last_travel_date} for {session.passenger_count} passenger(s).",
                intent=intent,
                action_suggested="NO_FLIGHTS",
                booking_step=session.booking_step
            )

        # Check if user selects a flight in current turn
        upper_msg = user_message.upper()
        if intent.intent_type == "SELECT_FLIGHT" or intent.flight_number or any(w in upper_msg for w in ["CHEAPEST", "LOWEST", "EARLIEST", "MORNING", "FIRST", "SECOND", "THIRD", "OPTION"]):
            matched_flt = None
            if intent.flight_number == "CHEAPEST" or "CHEAPEST" in upper_msg or "LOWEST" in upper_msg:
                matched_flt = min(session.available_flights, key=lambda f: f['fares'][0]['base_fare'] if f.get('fares') else 99999)
            elif intent.flight_number == "EARLIEST" or "EARLIEST" in upper_msg or "MORNING" in upper_msg:
                matched_flt = min(session.available_flights, key=lambda f: str(f['departure_time']))
            elif intent.flight_number:
                for f in session.available_flights:
                    if f['flight_number'].upper() == intent.flight_number.upper():
                        matched_flt = f
                        break
            if not matched_flt:
                if "SECOND" in upper_msg or "OPTION 2" in upper_msg or "FLIGHT 2" in upper_msg:
                    matched_flt = session.available_flights[1] if len(session.available_flights) > 1 else session.available_flights[0]
                elif "THIRD" in upper_msg or "OPTION 3" in upper_msg or "FLIGHT 3" in upper_msg:
                    matched_flt = session.available_flights[2] if len(session.available_flights) > 2 else session.available_flights[0]
                else:
                    matched_flt = session.available_flights[0]

            if matched_flt:
                session.pending_flight = matched_flt
                session.selected_flight = session.pending_flight
                session.pending_flight = None
                session.original_flight = None
                session.booking_step = BookingStep.FLIGHT_SELECTED

        # If flight is NOT selected yet, present flight options and wait for user selection
        if not session.selected_flight:
            session.booking_step = BookingStep.SEARCHING
            SessionManager.update(session)

            lines = []
            for idx, f in enumerate(session.available_flights[:4], 1):
                fare_val = f['fares'][0]['base_fare'] if f.get('fares') else 0.0
                d_time = f['departure_time'].strftime("%H:%M") if hasattr(f['departure_time'], 'strftime') else str(f['departure_time'])[11:16]
                a_time = f['arrival_time'].strftime("%H:%M") if hasattr(f['arrival_time'], 'strftime') else str(f['arrival_time'])[11:16]
                lines.append(
                    f"{idx}. {f['airline_name']} ({f['flight_number']}) - Departs {f['origin_code']} at {d_time}, Arrives {f['destination_code']} at {a_time} | Economy from ₹{fare_val:,.0f}"
                )

            summary_text = "\n".join(lines)
            reply_msg = (
                f"Available flight options for {session.last_source} → {session.last_destination} on {session.last_travel_date} ({session.passenger_count} passenger(s)):\n\n"
                f"{summary_text}\n\n"
                f"Please choose a flight to proceed (e.g. 'Flight 1', 'take the second one', or 'cheapest one')."
            )

            return AgentChatResponse(
                conversation_id=conversation_id,
                reply=reply_msg,
                intent=intent,
                action_suggested="SELECT_FLIGHT",
                booking_step=session.booking_step,
                flights_found=session.available_flights
            )

        # STEP 3: Mixed Class Distribution & Class Ambiguity Resolution
        if session.class_distribution:
            dist_sum = sum(v for k, v in session.class_distribution.items() if k != "_REMAINING_CLASS_")
            if dist_sum < session.passenger_count:
                session.last_travel_class = None
                session.booking_step = BookingStep.CLASS_SELECTED
                SessionManager.update(session)
                unassigned = session.passenger_count - dist_sum
                specified_str = ", ".join(f"{cnt} {cls}" for cls, cnt in session.class_distribution.items() if cls != "_REMAINING_CLASS_")
                reply_msg = (
                    f"You requested {session.passenger_count} passengers and specified {specified_str}.\n\n"
                    f"What travel class should the remaining {unassigned} passenger(s) use?"
                )
                return AgentChatResponse(
                    conversation_id=conversation_id,
                    reply=reply_msg,
                    intent=intent,
                    action_suggested="SELECT_CLASS",
                    booking_step=session.booking_step
                )

        if not session.last_travel_class and not session.class_distribution:
            if intent.travel_class:
                session.last_travel_class = intent.travel_class.value if hasattr(intent.travel_class, 'value') else intent.travel_class
                session.booking_step = BookingStep.CLASS_SELECTED
            else:
                session.booking_step = BookingStep.CLASS_SELECTED
                SessionManager.update(session)

                sel_flt = session.selected_flight
                base_fare = sel_flt['fares'][0]['base_fare'] if sel_flt.get('fares') else 3500.0

                reply_msg = (
                    f"Selected flight: {sel_flt['airline_name']} ({sel_flt['flight_number']}) from {sel_flt['origin_code']} to {sel_flt['destination_code']}.\n\n"
                    f"Which travel class would you like for your {session.passenger_count} passenger(s)?\n"
                    f"• Economy (₹{base_fare:,.0f} per passenger)\n"
                    f"• Premium Economy (₹{round(base_fare * 1.4):,.0f} per passenger)\n"
                    f"• Business (₹{round(base_fare * 2.5):,.0f} per passenger)"
                )

                return AgentChatResponse(
                    conversation_id=conversation_id,
                    reply=reply_msg,
                    intent=intent,
                    action_suggested="SELECT_CLASS",
                    booking_step=session.booking_step
                )

        # STEP 4: Seat Selection
        if session.class_distribution:
            all_seats = []
            for c_name in session.class_distribution.keys():
                if c_name == "_REMAINING_CLASS_": continue
                c_enum = TravelClass[c_name] if c_name in TravelClass.__members__ else TravelClass.ECONOMY
                st_list = self.tools.get_available_seats(session.selected_flight['id'], c_enum)
                for st in st_list:
                    if not any(ex['seat_number'] == st['seat_number'] for ex in all_seats):
                        all_seats.append(st)
            session.available_seats = all_seats
            t_class_enum = TravelClass.ECONOMY
        else:
            t_class_enum = TravelClass[session.last_travel_class] if session.last_travel_class in TravelClass.__members__ else TravelClass.ECONOMY
            if not session.available_seats:
                seats = self.tools.get_available_seats(session.selected_flight['id'], t_class_enum)
                session.available_seats = seats

        # Validate selected seats count against passenger_count
        if len(session.selected_seats) < session.passenger_count:
            session.booking_step = BookingStep.SEATS_PENDING
            SessionManager.update(session)

            if session.class_distribution:
                c_lines = [f"- {c.replace('_', ' ').capitalize()}: {cnt} passenger(s)" for c, cnt in session.class_distribution.items() if c != "_REMAINING_CLASS_"]
                class_prompt = "Travel Classes:\n" + "\n".join(c_lines)
            else:
                class_prompt = f"Travel class: {session.last_travel_class} ({session.passenger_count} passenger(s))"

            unbooked_seats = [s['seat_number'] for s in session.available_seats if not s.get('is_booked')][:12]
            seat_str = ", ".join(unbooked_seats) if unbooked_seats else "12A, 12B"

            reply_msg = (
                f"{class_prompt}\n\n"
                f"Available Seats: {seat_str}\n\n"
                f"Please choose exactly {session.passenger_count} seat(s)."
            )

            return AgentChatResponse(
                conversation_id=conversation_id,
                reply=reply_msg,
                intent=intent,
                action_suggested="SELECT_SEATS",
                booking_step=session.booking_step,
                available_seats=session.available_seats
            )


        # STEP 5: Passenger Details Collection (Hard Validation: N complete records required)
        complete_passengers = []
        for p in session.passengers_data:
            fn = p.get('first_name')
            ln = p.get('last_name')
            age = p.get('age')
            gender = p.get('gender')
            if is_valid_name(fn) and is_valid_name(ln) and age is not None and isinstance(age, int) and gender in ["MALE", "FEMALE"]:
                complete_passengers.append(p)

        if len(complete_passengers) < session.passenger_count:
            session.booking_step = BookingStep.PASSENGERS_PENDING
            SessionManager.update(session)

            needed = session.passenger_count - len(complete_passengers)
            seats_str = ", ".join(session.selected_seats[:session.passenger_count])

            if len(complete_passengers) > 0:
                provided_names = ", ".join(f"{p['first_name']} {p['last_name']}" for p in complete_passengers)
                reply_msg = (
                    f"Details received for {len(complete_passengers)} of {session.passenger_count} passenger(s) ({provided_names}).\n\n"
                    f"Please provide complete details (first name, last name, age, gender) for the remaining {needed} passenger(s)."
                )
            else:
                reply_msg = (
                    f"Seats {seats_str} selected.\n\n"
                    f"Please provide passenger details for all {session.passenger_count} traveler(s).\n"
                    f"Required per passenger: First Name, Last Name, Age, Gender.\n\n"
                    f"*(Example: 'Priya Sharma, 26, female. Amit Sharma, 29, male')*"
                )

            return AgentChatResponse(
                conversation_id=conversation_id,
                reply=reply_msg,
                intent=intent,
                action_suggested="COLLECT_PASSENGERS",
                booking_step=session.booking_step
            )

        # Update session with complete valid passengers
        session.passengers_data = complete_passengers[:session.passenger_count]

        # STEP 6: Fare Review Summary
        fares_list = session.selected_flight.get('fares', [])
        econ_fare_obj = next((f for f in fares_list if f.get('travel_class') in ['ECONOMY', TravelClass.ECONOMY]), fares_list[0] if fares_list else {})
        econ_base_fare = float(econ_fare_obj.get('base_fare', 3500.0))

        fare_breakdown_lines = []
        if session.class_distribution:
            total_class_base = 0.0
            for cls_name, cnt in session.class_distribution.items():
                if cls_name == "_REMAINING_CLASS_": continue
                mult = 2.5 if cls_name == "BUSINESS" else (1.4 if cls_name == "PREMIUM_ECONOMY" else 1.0)
                sub_total = cnt * (econ_base_fare * mult)
                total_class_base += sub_total
                fare_breakdown_lines.append(f"• {cls_name.replace('_', ' ').capitalize()} × {cnt}: ₹{sub_total:,.2f}")
            avg_base_fare = total_class_base / max(1, session.passenger_count)
            fare_breakdown_str = "\n".join(fare_breakdown_lines)
        else:
            c_mult = 2.5 if session.last_travel_class == "BUSINESS" else (1.4 if session.last_travel_class == "PREMIUM_ECONOMY" else 1.0)
            avg_base_fare = econ_base_fare * c_mult
            cls_lbl = session.last_travel_class.replace('_', ' ').capitalize() if session.last_travel_class else "Economy"
            fare_breakdown_str = f"• {cls_lbl} × {session.passenger_count}: ₹{avg_base_fare * session.passenger_count:,.2f}"

        seat_fee_total = 0.0
        for sn in session.selected_seats:
            s_match = next((s for s in session.available_seats if s['seat_number'] == sn), None)
            if s_match:
                seat_fee_total += s_match.get('price_extra', 0.0)

        fare_calc = self.tools.calculate_fare(
            base_fare=avg_base_fare,
            passenger_count=session.passenger_count,
            seat_addons_fee=seat_fee_total
        )
        session.fare_summary = fare_calc

        if intent.intent_type == "PROCEED_PAYMENT":
            draft_booking = self.tools.create_booking_draft(
                user_id=user_id,
                flight_id=session.selected_flight['id'],
                travel_class=t_class_enum,
                travel_date=session.last_travel_date,
                passengers=session.passengers_data[:session.passenger_count]
            )

            payment_intent = self.tools.create_payment_intent(
                booking_id=draft_booking['id'],
                user_id=user_id
            )

            session.draft_booking_id = draft_booking['id']
            session.draft_booking_ref = draft_booking['booking_reference']
            session.payment_intent_id = payment_intent['payment_intent_id']
            session.booking_step = BookingStep.PAYMENT_PENDING
            SessionManager.update(session)

            reply_msg = (
                f"Demo Payment Authorization Required\n\n"
                f"Booking Reference: {draft_booking['booking_reference']}\n"
                f"Status: PAYMENT_PENDING\n"
                f"Total Amount: ₹{draft_booking['total_fare']:,.2f}\n\n"
                f"Please choose your demo payment method below to authorize and confirm your booking:"
            )

            return AgentChatResponse(
                conversation_id=conversation_id,
                reply=reply_msg,
                intent=intent,
                action_suggested="LAUNCH_PAYMENT",
                booking_step=session.booking_step,
                payment_intent=payment_intent,
                draft_booking=draft_booking,
                fare_summary=fare_calc
            )

        session.booking_step = BookingStep.REVIEW_PENDING
        SessionManager.update(session)

        seats_display = ", ".join(session.selected_seats[:session.passenger_count]) if session.selected_seats else "Standard"

        if session.class_distribution:
            class_display_lines = [f"• {cls.replace('_', ' ').capitalize()} × {cnt}" for cls, cnt in session.class_distribution.items() if cls != "_REMAINING_CLASS_"]
            class_display_str = "Travel Class\n" + "\n".join(class_display_lines)
        else:
            cls_lbl = session.last_travel_class.replace('_', ' ').capitalize() if session.last_travel_class else "Economy"
            class_display_str = f"Travel Class\n• {cls_lbl} × {session.passenger_count}"

        pass_summary_lines = []
        for idx, p in enumerate(session.passengers_data[:session.passenger_count], 1):
            st = session.selected_seats[idx - 1] if idx - 1 < len(session.selected_seats) else "Standard"
            p_cls = p.get('travel_class', session.last_travel_class or 'ECONOMY')
            pass_summary_lines.append(f"  {idx}. {p['first_name']} {p['last_name']} ({p.get('gender', 'MALE')}, {p.get('age', 25)}) - Seat {st} ({p_cls.replace('_', ' ').capitalize()})")
        pass_summary_str = "\n".join(pass_summary_lines)

        reply_msg = (
            f"Booking Review\n\n"
            f"Flight: {session.selected_flight['airline_name']} ({session.selected_flight['flight_number']})\n"
            f"Route: {session.selected_flight['origin_city']} → {session.selected_flight['destination_city']}\n"
            f"Date: {session.last_travel_date}\n\n"
            f"{class_display_str}\n\n"
            f"Passengers: {session.passenger_count}\n"
            f"Seats: {seats_display}\n\n"
            f"Passenger Details:\n{pass_summary_str}\n\n"
            f"Fare Summary\n"
            f"{fare_breakdown_str}\n"
            f"• Tax: ₹{fare_calc['taxes']:,.2f}\n"
            f"• Total: ₹{fare_calc['total_fare']:,.2f}\n\n"
            f"Would you like to proceed to payment?"
        )


        return AgentChatResponse(
            conversation_id=conversation_id,
            reply=reply_msg,
            intent=intent,
            action_suggested="REVIEW_SUMMARY",
            booking_step=session.booking_step,
            fare_summary=fare_calc
        )


    def handle_cancellation_workflow(
        self,
        session: AgentSessionState,
        intent: TravelIntent,
        conversation_id: str,
        user_id: str,
        user_message: str
    ) -> AgentChatResponse:
        from app.agents.state import CancellationStep

        upper_msg = user_message.upper().strip()
        is_explicit_confirmation = intent.intent_type == "CONFIRM_CANCELLATION" or (
            session.cancellation_step in [CancellationStep.CANCELLATION_REVIEW, CancellationStep.CANCELLATION_CONFIRMATION_PENDING] and
            any(w in upper_msg for w in ["CONFIRM", "YES", "CANCEL IT", "PROCEED WITH CANCELLATION", "PROCEED", "CONFIRM CANCEL"]) and
            not any(w in upper_msg for w in ["DON'T", "NOT", "NO", "KEEP", "STOP"])
        )

        target_ref = intent.booking_reference or session.cancellation_target_ref

        if is_explicit_confirmation:
            if not target_ref:
                session.cancellation_step = CancellationStep.CANCELLATION_NEED_REFERENCE
                SessionManager.update(session)
                return AgentChatResponse(
                    conversation_id=conversation_id,
                    reply="Sure. Please provide your Booking Reference (e.g. BK-1234) or PNR code.",
                    intent=intent,
                    action_suggested="CANCELLATION_NEED_REF",
                    cancellation_step=session.cancellation_step
                )

            try:
                if session.cancellation_target_passenger_ids and not session.cancellation_cancel_all:
                    # Partial passenger cancellation
                    preview = self.tools.get_passenger_cancellation_preview(target_ref, session.cancellation_target_passenger_ids, user_id)
                    res = self.tools.cancel_passenger_booking(
                        booking_id=preview['booking_id'],
                        passenger_ids=session.cancellation_target_passenger_ids,
                        user_id=user_id,
                        reason="Confirmed passenger cancellation via assistant"
                    )
                    session.cancellation_step = CancellationStep.CANCELLATION_COMPLETED
                    session.reset_cancellation_workflow()
                    SessionManager.update(session)

                    target_p_str = ", ".join([f"{p['first_name']} {p['last_name']} (Seat {p['seat_number'] or 'N/A'})" for p in preview['target_passengers']])
                    rem_p_str = ", ".join([f"{p['first_name']} {p['last_name']} (Seat {p['seat_number'] or 'N/A'})" for p in preview['remaining_passengers']]) or "None"
                    seats_released = ", ".join([p['seat_number'] for p in preview['target_passengers'] if p['seat_number']]) or "N/A"

                    orig_amt = float(preview['original_amount'])
                    fee_amt = float(preview['cancellation_fee'])
                    ref_amt = float(preview['refund_amount'])

                    reply_msg = (
                        f"Passenger Ticket Cancelled Successfully\n\n"
                        f"Booking Reference: {preview['booking_reference']}\n"
                        f"PNR: {preview['pnr']}\n\n"
                        f"Cancelled Passenger(s): {target_p_str}\n"
                        f"Remaining Booked Passenger(s): {rem_p_str}\n\n"
                        f"Original Fare Portion: Rs.{orig_amt:,.2f}\n"
                        f"Cancellation Fee: Rs.{fee_amt:,.2f}\n"
                        f"Refund Amount: Rs.{ref_amt:,.2f}\n"
                        f"Refund Status: PROCESSED\n\n"
                        f"Released Seat(s): {seats_released}\n\n"
                        f"The passenger cancellation and refund have been successfully processed."
                    )
                    return AgentChatResponse(
                        conversation_id=conversation_id,
                        reply=reply_msg,
                        intent=intent,
                        action_suggested="CANCELLATION_COMPLETED",
                        cancellation_step=CancellationStep.CANCELLATION_COMPLETED,
                        cancellation_result=res
                    )
                else:
                    # Full booking cancellation
                    preview = self.tools.get_cancellation_preview(target_ref, user_id)
                    res = self.tools.cancel_booking(booking_id=preview['booking_id'], user_id=user_id, reason="Confirmed cancellation via assistant")

                    session.cancellation_step = CancellationStep.CANCELLATION_COMPLETED
                    session.reset_cancellation_workflow()
                    SessionManager.update(session)

                    seat_str = ", ".join(preview['seats']) if preview['seats'] else "N/A"
                    orig_amt = float(preview['original_amount'])
                    fee_amt = float(preview['cancellation_fee'])
                    ref_amt = float(preview['refund_amount'])

                    reply_msg = (
                        f"Ticket Cancelled Successfully\n\n"
                        f"Booking Reference: {preview['booking_reference']}\n"
                        f"PNR: {preview['pnr']}\n\n"
                        f"Original Amount: Rs.{orig_amt:,.2f}\n"
                        f"Cancellation Fee: Rs.{fee_amt:,.2f}\n"
                        f"Refund Amount: Rs.{ref_amt:,.2f}\n"
                        f"Refund Status: REFUNDED\n\n"
                        f"Released Seats: {seat_str}\n\n"
                        f"The cancellation and refund have been successfully processed."
                    )

                    return AgentChatResponse(
                        conversation_id=conversation_id,
                        reply=reply_msg,
                        intent=intent,
                        action_suggested="CANCELLATION_COMPLETED",
                        cancellation_step=CancellationStep.CANCELLATION_COMPLETED,
                        cancellation_result=res
                    )
            except Exception as e:
                err_text = str(e).replace("ValueError:", "").strip()
                session.cancellation_step = CancellationStep.CANCELLATION_FAILED
                SessionManager.update(session)
                return AgentChatResponse(
                    conversation_id=conversation_id,
                    reply=f"Cancellation could not be completed. {err_text}",
                    intent=intent,
                    action_suggested="CANCELLATION_FAILED",
                    cancellation_step=session.cancellation_step
                )

        if intent.intent_type == "CANCEL_INFO":
            return AgentChatResponse(
                conversation_id=conversation_id,
                reply="Our refund policy depends on departure time:\n• >72 hours before departure: 10% fee (90% refund)\n• 24-72 hours before departure: 30% fee (70% refund)\n• <24 hours before departure: 50% fee (50% refund)\n\nPlease provide your Booking Reference or PNR if you would like to view your cancellation preview.",
                intent=intent,
                action_suggested="CANCELLATION_INFO",
                cancellation_step=session.cancellation_step
            )

        if not target_ref:
            session.cancellation_step = CancellationStep.CANCELLATION_NEED_REFERENCE
            SessionManager.update(session)
            return AgentChatResponse(
                conversation_id=conversation_id,
                reply="Sure. Please provide your Booking Reference (e.g. BK-1234) or PNR code.",
                intent=intent,
                action_suggested="CANCELLATION_NEED_REF",
                cancellation_step=session.cancellation_step
            )

        # Retrieve booking details preview
        try:
            preview = self.tools.get_cancellation_preview(target_ref, user_id)
            session.cancellation_target_ref = target_ref
            passengers = preview['passengers']

            if len(passengers) > 1:
                # Check for explicit cancellation target
                cancel_all = intent.cancel_all or any(w in upper_msg for w in ["ENTIRE BOOKING", "ALL PASSENGERS", "BOTH PASSENGERS", "EVERYONE", "CANCEL ALL", "ALL TICKETS"])
                resolved_p_ids = []

                if cancel_all:
                    session.cancellation_cancel_all = True
                    session.cancellation_target_passenger_ids = []
                else:
                    target_str = intent.cancel_target_passenger
                    target_idx = intent.cancel_passenger_index

                    # Match by index
                    if target_idx and 1 <= target_idx <= len(passengers):
                        resolved_p_ids = [passengers[target_idx - 1]['first_name']]
                    elif target_str:
                        # Match by name or seat number
                        target_str_clean = target_str.strip().lower()
                        matched = [p for p in passengers if target_str_clean in f"{p['first_name']} {p['last_name']}".lower() or p['first_name'].lower() == target_str_clean or (p['seat_number'] and p['seat_number'].lower() == target_str_clean)]
                        if len(matched) == 1:
                            resolved_p_ids = [matched[0]['first_name']]
                        elif len(matched) > 1:
                            session.cancellation_step = CancellationStep.CANCELLATION_SELECT_PASSENGER
                            SessionManager.update(session)
                            p_lines = [f"{idx}. {p['first_name']} {p['last_name']} (Seat {p['seat_number'] or 'N/A'})" for idx, p in enumerate(passengers, 1)]
                            p_str = "\n".join(p_lines)
                            return AgentChatResponse(
                                conversation_id=conversation_id,
                                reply=f"Multiple passengers match '{target_str}'. Please specify the exact seat number or passenger number:\n\n{p_str}",
                                intent=intent,
                                action_suggested="CANCELLATION_SELECT_PASSENGER",
                                cancellation_step=session.cancellation_step
                            )

                    if not resolved_p_ids and not session.cancellation_target_passenger_ids:
                        session.cancellation_step = CancellationStep.CANCELLATION_SELECT_PASSENGER
                        SessionManager.update(session)
                        p_lines = [f"{idx}. {p['first_name']} {p['last_name']} (Seat {p['seat_number'] or 'N/A'})" for idx, p in enumerate(passengers, 1)]
                        p_str = "\n".join(p_lines)
                        return AgentChatResponse(
                            conversation_id=conversation_id,
                            reply=(
                                f"Cancellation Request\n\n"
                                f"Booking: {preview['booking_reference']} (PNR: {preview['pnr']})\n\n"
                                f"Passengers:\n{p_str}\n\n"
                                f"Which passenger would you like to cancel, or do you want to cancel the entire booking?"
                            ),
                            intent=intent,
                            action_suggested="CANCELLATION_SELECT_PASSENGER",
                            cancellation_step=session.cancellation_step
                        )

                if resolved_p_ids:
                    session.cancellation_target_passenger_ids = resolved_p_ids

                if session.cancellation_target_passenger_ids and not session.cancellation_cancel_all:
                    # Render passenger-specific cancellation preview
                    p_preview = self.tools.get_passenger_cancellation_preview(target_ref, session.cancellation_target_passenger_ids, user_id)
                    session.cancellation_target_passenger_ids = p_preview['target_passenger_ids']
                    session.cancellation_preview_data = p_preview
                    session.cancellation_step = CancellationStep.CANCELLATION_REVIEW
                    SessionManager.update(session)

                    target_p_str = ", ".join([f"{p['first_name']} {p['last_name']} (Seat {p['seat_number'] or 'N/A'})" for p in p_preview['target_passengers']])
                    rem_p_str = ", ".join([f"{p['first_name']} {p['last_name']} (Seat {p['seat_number'] or 'N/A'})" for p in p_preview['remaining_passengers']]) or "None"

                    orig_amt = float(p_preview['original_amount'])
                    fee_amt = float(p_preview['cancellation_fee'])
                    ref_amt = float(p_preview['refund_amount'])

                    reply_msg = (
                        f"Cancellation Request Preview\n\n"
                        f"Booking: {preview['booking_reference']} (PNR: {preview['pnr']})\n\n"
                        f"Passenger to Cancel:\n• {target_p_str}\n\n"
                        f"Remaining Booked Passenger(s):\n• {rem_p_str}\n\n"
                        f"Original Fare Portion: Rs.{orig_amt:,.2f}\n"
                        f"Cancellation Fee: Rs.{fee_amt:,.2f}\n"
                        f"Refund Amount: Rs.{ref_amt:,.2f}\n"
                        f"Fee Percentage: {p_preview['fee_percentage']}%\n\n"
                        f"Would you like to confirm cancellation?"
                    )

                    return AgentChatResponse(
                        conversation_id=conversation_id,
                        reply=reply_msg,
                        intent=intent,
                        action_suggested="CANCELLATION_REVIEW_SUMMARY",
                        cancellation_step=session.cancellation_step,
                        cancellation_preview=p_preview
                    )

            # Single passenger or full booking cancellation preview
            session.cancellation_target_ref = target_ref
            session.cancellation_preview_data = preview
            session.cancellation_step = CancellationStep.CANCELLATION_REVIEW
            SessionManager.update(session)

            p_lines = [f"{idx}. {p['first_name']} {p['last_name']} — Seat {p['seat_number'] or 'N/A'}" for idx, p in enumerate(preview['passengers'], 1)]
            p_str = "\n".join(p_lines) if p_lines else "1 Passenger"
            orig_amt = float(preview['original_amount'])
            fee_amt = float(preview['cancellation_fee'])
            ref_amt = float(preview['refund_amount'])

            reply_msg = (
                f"Cancellation Summary\n\n"
                f"Flight: {preview['airline_name']} ({preview['flight_number']})\n"
                f"Route: {preview['origin_city']} ({preview['origin_code']}) -> {preview['destination_city']} ({preview['destination_code']})\n"
                f"Departure: {preview['departure_date']}\n"
                f"Booking Reference: {preview['booking_reference']}\n"
                f"PNR: {preview['pnr']}\n\n"
                f"Passenger(s):\n{p_str}\n\n"
                f"Original Amount Paid: Rs.{orig_amt:,.2f}\n"
                f"Cancellation Fee: Rs.{fee_amt:,.2f}\n"
                f"Refund Amount: Rs.{ref_amt:,.2f}\n"
                f"Refund Percentage: {preview['refund_percentage']}%\n\n"
                f"Would you like to confirm cancellation?"
            )

            return AgentChatResponse(
                conversation_id=conversation_id,
                reply=reply_msg,
                intent=intent,
                action_suggested="CANCELLATION_REVIEW_SUMMARY",
                cancellation_step=session.cancellation_step,
                cancellation_preview=preview
            )
        except Exception as e:
            err_text = str(e).replace("ValueError:", "").strip()
            session.cancellation_step = CancellationStep.CANCELLATION_FAILED
            SessionManager.update(session)
            return AgentChatResponse(
                conversation_id=conversation_id,
                reply=f"{err_text}",
                intent=intent,
                action_suggested="CANCELLATION_FAILED",
                cancellation_step=session.cancellation_step
            )



