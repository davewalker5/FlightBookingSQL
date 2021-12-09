"""
Utility methods used to assist with setting up test fixtures
"""

import datetime
from src.flight_model.model import Session, Airline, Flight, AircraftLayout
from src.flight_model.logic import create_layout, add_row_to_layout, apply_aircraft_layout
from src.flight_model.logic import add_passenger, create_passenger


def create_test_layout(airline_name, aircraft, name, rows, letters):
    """
    Insert an aircraft layout and associated row definitions for testing

    :param airline_name: Name of the associated airline
    :param aircraft: Aircraft model e.g. A320
    :param name: Layout name e.g. Neo
    :param rows: Number of seating rows to add
    :param letters: String of seat letters in each row
    """
    with Session.begin() as session:
        airline = session.query(Airline).filter(Airline.name == airline_name).one()

    aircraft_layout = create_layout(airline.id, aircraft, name)
    for row in range(1, rows + 1):
        add_row_to_layout(aircraft_layout.id, row, "Economy", letters)


def create_test_seating_plan(flight_number, aircraft, name):
    """
    Insert a collection of seats for testing

    :param flight_number: Flight number associated with the plan
    :param aircraft: Aircraft model e.g. A320
    :param name: Layout name e.g. Neo
    """
    with Session.begin() as session:
        flight = session.query(Flight).filter(Flight.number == flight_number).one()
        aircraft_layout = session.query(AircraftLayout)\
            .filter(AircraftLayout.airline_id == flight.airline_id,
                    AircraftLayout.aircraft == aircraft,
                    AircraftLayout.name == name)\
            .one()

    apply_aircraft_layout(flight.id, aircraft_layout.id)


def create_test_passengers_on_flight(number_of_passengers):
    """
    Create a number of passengers associated with a flight for testing purposes

    :param number_of_passengers: Number of passengers to create
    """
    with Session.begin() as session:
        flight = session.query(Flight).one()

    for i in range(number_of_passengers):
        passenger = create_passenger(f"Passenger {i}", "M", datetime.datetime(1970, 1, 1).date(), "UK", "UK", str(i))
        add_passenger(flight.id, passenger)


def text_card_generator(card_details):
    """
    Stub card generator monkeypatched in for testing boarding card printing

    :param card_details: Boarding card details
    """
    return "\n".join(card_details.values())


def binary_card_generator(card_details):
    """
    Stub card generator monkeypatched in for testing boarding card printing

    :param card_details: Boarding card details
    """
    return "\n".join(card_details.values()).encode("utf-8")
