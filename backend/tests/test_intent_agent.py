import pytest
from app.agents.intent_agent import IntentAgent
from app.models.flight import TravelClass

def test_intent_agent_extraction():
    agent = IntentAgent()
    query = "Book 2 business class tickets from Bangalore to Delhi tomorrow"
    intent = agent.parse_intent(query)

    assert intent.intent_type in ["BOOK_FLIGHT", "SEARCH_FLIGHTS"]
    assert intent.source == "BLR"
    assert intent.destination == "DEL"
    assert intent.passenger_count == 2
    assert intent.travel_class == TravelClass.BUSINESS
    assert intent.is_complete is True

def test_intent_agent_city_ordering():
    agent = IntentAgent()
    query = "Flight from Delhi to Bangalore"
    intent = agent.parse_intent(query)

    assert intent.source == "DEL"
    assert intent.destination == "BLR"

def test_intent_agent_flight_number_booking():
    agent = IntentAgent()
    query = "Book DA-100"
    intent = agent.parse_intent(query)

    assert intent.intent_type == "BOOK_FLIGHT"
    assert intent.flight_number == "DA-100"
    assert intent.is_complete is True

def test_number_words_and_phrases():
    agent = IntentAgent()

    assert agent.parse_intent("book four tickets").passenger_count == 4
    assert agent.parse_intent("there are three of us").passenger_count == 3
    assert agent.parse_intent("both of us").passenger_count == 2
    assert agent.parse_intent("we are four").passenger_count == 4
    assert agent.parse_intent("just me").passenger_count == 1

def test_mixed_business_economy_intents():
    agent = IntentAgent()

    # "2 business and 1 economy"
    i1 = agent.parse_intent("Book 3 tickets, 2 business and 1 economy")
    assert i1.passenger_count == 3
    assert i1.class_distribution.get("BUSINESS") == 2
    assert i1.class_distribution.get("ECONOMY") == 1

    # "3 business, 2 economy"
    i2 = agent.parse_intent("3 business, 2 economy from BLR to HYD")
    assert i2.passenger_count == 5
    assert i2.class_distribution.get("BUSINESS") == 3
    assert i2.class_distribution.get("ECONOMY") == 2

def test_incomplete_class_distribution_intent():
    agent = IntentAgent()

    i = agent.parse_intent("Book 4 tickets, 2 business")
    assert i.passenger_count == 4
    assert i.class_distribution.get("BUSINESS") == 2
    assert i.ambiguous_class_count is True

def test_flight_selection_keywords():
    agent = IntentAgent()

    i1 = agent.parse_intent("take the cheapest one")
    assert i1.flight_number == "CHEAPEST"

    i2 = agent.parse_intent("I want the morning flight")
    assert i2.flight_number == "EARLIEST"

def test_natural_language_date_parsing_and_pnr_isolation():
    agent = IntentAgent()

    # Test 1: "29 august 2026"
    i1 = agent.parse_intent("29 august 2026", active_step="NEED_DATE")
    assert i1.travel_date == "2026-08-29"
    assert i1.booking_reference is None
    assert i1.intent_type != "CANCEL_BOOKING"

    # Test 2: "29-08-2026"
    i2 = agent.parse_intent("29-08-2026", active_step="NEED_DATE")
    assert i2.travel_date == "2026-08-29"
    assert i2.booking_reference is None
    assert i2.intent_type != "CANCEL_BOOKING"

    # Test 3: "29/08/2026"
    i3 = agent.parse_intent("29/08/2026", active_step="NEED_DATE")
    assert i3.travel_date == "2026-08-29"
    assert i3.booking_reference is None

    # Test 4: "29th August 2026"
    i4 = agent.parse_intent("29th August 2026", active_step="NEED_DATE")
    assert i4.travel_date == "2026-08-29"
    assert i4.booking_reference is None

    # Test 5: "August 29 2026"
    i5 = agent.parse_intent("August 29 2026", active_step="NEED_DATE")
    assert i5.travel_date == "2026-08-29"
    assert i5.booking_reference is None

    # Test 6: cancellation with explicit reference still works
    i6 = agent.parse_intent("cancel ticket BK-1234")
    assert i6.intent_type == "CANCEL_BOOKING"
    assert i6.booking_reference == "BK-1234"

    # Test 7: PNR lookup with PNR keyword still works
    i7 = agent.parse_intent("check status PNR ABC123")
    assert i7.intent_type == "CHECK_STATUS"
    assert i7.booking_reference == "ABC123"





