"""
Flight business logic
"""

import datetime
import sqlalchemy as db
from ..model import Session, Airline, Airport, Flight


def _construct_date_and_time(date_string, time_string):
    """
    Given strings representing the date and time parts of the departure date, combine them to generate a full date
    and time object

    :param date_string: Date part in the format DD/MM/YYYY
    :param time_string: Time part in the format HH:MM
    :return: A datetime object representing the date and time
    """
    departs_date = datetime.datetime.strptime(date_string, "%d/%m/%Y").date()
    departs_time = datetime.datetime.strptime(time_string, "%H:%M").time()
    return datetime.datetime.combine(departs_date, departs_time)


def _construct_duration(duration_string):
    """
    Given a string representing the flight duration, parse it to generate a timedelta object

    :param duration_string: Duration in the format HH:MM
    :return: A timedelta object representing the flight duration
    """
    words = duration_string.split(sep=":")
    hours = int(words[0])
    minutes = int(words[1])
    return datetime.timedelta(hours=hours, minutes=minutes)


def create_flight(airline_name, embarkation_code, destination_code, number, departure_date, departure_time, duration):
    """
    Insert a flight for testing

    :param airline_name: Airline name
    :param embarkation_code: 3-letter IATA code for the airport of embarkation
    :param destination_code: 3-letter IATA code for the destination airport
    :param number: Flight number
    :param departure_date: String representing the departure date DD/MM/YYYY
    :param departure_time: String representing the departure time HH:MM
    :param duration: Flight duration
    :returns: An instance of the Flight class for the created record
    :raises: ValueError if the embarkation and destination airports are the same
    """
    if embarkation_code == destination_code:
        raise ValueError("Embarkation and destination airports cannot be the same")

    departure_date_and_time = _construct_date_and_time(departure_date, departure_time)
    flight_duration = _construct_duration(duration)

    with Session.begin() as session:
        airline = session.query(Airline).filter(Airline.name == airline_name).one()
        embarkation = session.query(Airport).filter(Airport.code == embarkation_code).one()
        destination = session.query(Airport).filter(Airport.code == destination_code).one()
        flight = Flight(airline=airline,
                        embarkation_airport=embarkation,
                        destination_airport=destination,
                        number=number,
                        departure_date=departure_date_and_time,
                        duration=flight_duration)
        session.add(flight)

    return flight


def list_flights():
    """
    List all flights

    :return: A list of instances of the Flight object with relevant associated attributes eager-loaded
    """
    with Session.begin() as session:
        flights = session.query(Flight) \
            .order_by(db.asc(Flight.departure_date)) \
            .all()

    return flights


def get_flight(flight_id):
    """
    Return a single flight given its ID

    :param flight_id: ID of the flight to return
    :return: Flight object for the record with the specified ID
    """
    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)

    return flight


def delete_flight(flight_id):
    """
    Delete a flight record, and related data

    :param flight_id: The ID of the flight record to delete
    """
    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)
        session.delete(flight)


def add_passenger(flight_id, passenger):
    """
    Add a passenger to the flight with the specified ID

    :param flight_id: ID for the flight to add to
    :param passenger: Passenger instance to add
    """
    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)
        flight.passengers.append(passenger)
