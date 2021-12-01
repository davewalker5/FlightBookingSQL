"""
Utility methods to create records for core entities in the flight model, used to assist with setting up
test fixtures. Some of these methods simply chain to the production code equivalents, others are implemented
only here. Currently, the real SQLite database is used for testing but these methods provide a degree of
separation between the tests and the production code in case a mock database is implemented in future
"""

import datetime
from src.flight_model.model import Session, Airline, Flight, AircraftLayout, RowDefinition, Seat, Passenger
from src.flight_model.logic import create_airport, create_airline, create_flight, create_passenger


def create_test_airport(code, name, timezone):
    """
    Create an airport record for testing

    :param code: 3-letter IATA code
    :param name: Airport name
    :param timezone: Airport timezone
    """
    _ = create_airport(code, name, timezone)


def create_test_airline(name):
    """
    Create an airline record for testing

    :param name: Airline name
    """
    _ = create_airline(name)


def create_test_flight(airline_name, embarkation_code, destination_code, number, departure_date, duration):
    """
    Create a flight for testing

    :param airline_name: Airline name
    :param embarkation_code: 3-letter IATA code for the airport of embarkation
    :param destination_code: 3-letter IATA code for the destination airport
    :param number: Flight number
    :param departure_date: Departure date and time
    :param duration: Flight duration
    """
    # Construct string representations of the departure date and time in the required format
    departure_date_string = departure_date.strftime("%d/%m/%Y")
    departure_time_string = departure_date.strftime("%H:%M")

    # Construct a string representation of the flight duration in the required format
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    duration_string = "{:0d}:{:02d}".format(int(hours), int(minutes))

    _ = create_flight(airline_name,
                      embarkation_code,
                      destination_code,
                      number,
                      departure_date_string,
                      departure_time_string,
                      duration_string)


def create_test_passenger(name, gender, dob, nationality, residency, passport_number):
    """
    Create a passenger record for testing

    :param name: Passenger name
    :param gender: Passenger gender M/F
    :param dob: Date of birth
    :param nationality: Passenger nationality
    :param residency: Passenger's country of residency
    :param passport_number: Passport number
    """
    return create_passenger(name, gender, dob, nationality, residency, passport_number)


def create_test_layout(airline_name, aircraft, name, rows, letters):
    """
    Inset an aircraft layout and associated row definitions for testing

    :param airline_name: Name of the associated airline
    :param aircraft: Aircraft model e.g. A320
    :param name: Layout name e.g. Neo
    :param rows: Number of seating rows to add
    :param letters: String of seat letters in each row
    """
    with Session.begin() as session:
        airline = session.query(Airline).filter(Airline.name == airline_name).one()
        aircraft_layout = AircraftLayout(airline=airline, aircraft=aircraft, name=name)
        session.add(aircraft_layout)

        for row in range(1, rows + 1):
            row_definition = RowDefinition(number=row,
                                           seating_class="Economy",
                                           seats=letters,
                                           aircraft_layout=aircraft_layout)
            session.add(row_definition)


def create_test_seating_plan(flight_number, aircraft, name):
    """
    Insert a collection of seats for testing

    :param flight_number: Flight number associated with the plan
    :param aircraft: Aircraft model e.g. A320
    :param name: Layout name e.g. Neo
    """
    with Session.begin() as session:
        flight = session.query(Flight).filter(Flight.number == flight_number).one()

        flight.aircraft_layout = session.query(AircraftLayout)\
            .filter(AircraftLayout.airline_id == flight.airline_id,
                    AircraftLayout.aircraft == aircraft,
                    AircraftLayout.name == name)\
            .one()

        for row in flight.aircraft_layout.row_definitions:
            for letter in row.seats:
                seat = Seat(flight=flight, seat_number=f"{row.number}{letter}")
                session.add(seat)


def create_test_passengers_on_flight(number_of_passengers):
    """
    Create a number of passengers associated with a flight for testing purposes

    :param number_of_passengers: Number of passengers to create
    """
    with Session.begin() as session:
        flight = session.query(Flight).one()

        for i in range(number_of_passengers):
            passenger = Passenger(name=f"Passenger {i}",
                                  gender="M",
                                  dob=datetime.datetime(1970, 1, 1).date(),
                                  nationality="UK",
                                  residency="UK",
                                  passport_number=str(i))
            flight.passengers.append(passenger)
            session.add(passenger)
