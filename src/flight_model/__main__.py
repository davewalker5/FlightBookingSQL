import datetime
from random import randint

import pytz

from .model import create_database, Session, Airline, Airport, Flight, AircraftLayout, Passenger
from .logic import apply_aircraft_layout
from .data_exchange.airports import import_airport_details
from .data_exchange.airlines import import_airline_details
from .data_exchange.aircraft_layouts import import_aircraft_layout


def import_reference_data():
    """
    Import airport definitions, airline definitions and sample aircraft layouts from sample data files
    """
    import_airport_details()
    import_airline_details()
    import_aircraft_layout("EasyJet", "A320", None)
    import_aircraft_layout("EasyJet", "A320", "1")
    import_aircraft_layout("EasyJet", "A321", "neo")


def create_sample_flight(airline_name, embarkation_code, destination_code, number, departure_date, duration):
    """
    Create a sample flight. The airline and airport records must be created first by importing the sample
    data files

    :param airline_name: Airline name
    :param embarkation_code: 3-letter IATA code for the airport of embarkation
    :param destination_code: 3-letter IATA code for the destination airport
    :param number: Flight number
    :param departure_date: Departure date and time in the embarkation timezone
    :param duration: Flight duration
    """
    with Session.begin() as session:
        airline = session.query(Airline).filter(Airline.name == airline_name).one()
        embarkation = session.query(Airport).filter(Airport.code == embarkation_code).one()
        destination = session.query(Airport).filter(Airport.code == destination_code).one()
        utc_departure_date = pytz.timezone(embarkation.timezone).localize(departure_date).astimezone(pytz.UTC)
        flight = Flight(airline=airline,
                        embarkation_airport=embarkation,
                        destination_airport=destination,
                        number=number,
                        departure_date=utc_departure_date,
                        duration=duration)
        session.add(flight)


def create_sample_seating_plan(flight_number, aircraft, layout_name):
    """
    Expand one of the sample aircraft layouts to generate a seating plan for a sample flight. The aircraft layouts
    must've been imported from the sample data files and the flight must exist

    :param flight_number: Flight number to apply the layout to
    :param aircraft: Aircraft model
    :param layout_name: Layout name
    """
    with Session.begin() as session:
        # There's only one sample flight, so we can just get that one
        flight = session.query(Flight).filter(Flight.number == flight_number).one()
        flight_id = flight.id

        # Get an aircraft layout to expand
        aircraft_layout = session.query(AircraftLayout) \
            .filter(AircraftLayout.airline_id == flight.airline_id,
                    AircraftLayout.aircraft == aircraft,
                    AircraftLayout.name == layout_name)\
            .one()

        apply_aircraft_layout(flight_id, aircraft_layout.id)


def create_sample_passengers(flight_number, number_of_passengers):
    """
    Create a set of sample passengers and associate them with the specified flight

    ":param number_of_passengers: The number of passengers to add
    """
    passport_number = randint(1, 1000000)
    with Session.begin() as session:
        flight = session.query(Flight)\
            .filter(Flight.number == flight_number)\
            .one()

        for i in range(number_of_passengers):
            year = randint(1970, 1990)
            month = randint(1, 12)
            day = randint(1, 28)
            gender = "M" if randint(1, 10) > 5 else "F"

            passenger = Passenger(name=f"Passenger {i}",
                                  gender=gender,
                                  dob=datetime.datetime(year, month, day),
                                  nationality="United Kingdom",
                                  residency="United Kingdom",
                                  passport_number=str(passport_number).zfill(6))
            session.add(passenger)

            flight.passengers.append(passenger)
            passport_number += 1


def allocate_available_seats(flight_number):
    """
    Allocate each seat on a sample flight to each passenger, in turn

    :param flight_number: Flight number to perform seat allocations for
    """
    with Session.begin() as session:
        # Get the flight with
        flight = session.query(Flight)\
            .filter(Flight.number == flight_number)\
            .one()

        # Iterable of available seats on the flight ordered by seat number (relying on the seats having
        # been created in row then letter order)
        seats = [seat
                 for seat in sorted(flight.seats, key=lambda seat: seat.id)
                 if seat.passenger_id is None]

        # Map transformation function to allocate a seat to a passenger
        def _allocate_sample_seat(passenger, seat):
            seat.passenger_id = passenger.id

        # Lazily-evaluated map
        for _ in map(_allocate_sample_seat, flight.passengers, seats):
            pass


def create_database_with_sample_data():
    """
    (Re)create the SQLite database with the table scheme and create the sample data
    """
    # Create the flight database file and import the reference data
    create_database()
    import_reference_data()

    # Create a sample flight
    create_sample_flight("EasyJet",
                         "LGW",
                         "RMU",
                         "U28549",
                         datetime.datetime(2021, 8, 20, 10, 45, 0),
                         datetime.timedelta(hours=2, minutes=25))

    # Load an aircraft layout for the flight -> generates a set of seats
    create_sample_seating_plan("U28549", "A320", "1")

    # Create a set of sample passengers
    create_sample_passengers("U28549", 10)

    # Perform seat allocations
    allocate_available_seats("U28549")


create_database_with_sample_data()
