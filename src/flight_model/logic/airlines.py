"""
Airline business logic
"""

import sqlalchemy as db
from sqlalchemy.exc import IntegrityError, NoResultFound
from ..model import Session, Airline

def create_airline(name):
    """
    Insert an airline record for testing

    :param name: Airline name
    :returns: An instance of the Airline class for the created record
    """
    try:
        with Session.begin() as session:
            airline = Airline(name=name)
            session.add(airline)
    except IntegrityError as e:
        raise ValueError("Cannot create duplicate airline name") from e

    return airline


def get_airline(name):
    """
    Return the Airline instance for the airline with the specified name

    :param name: Airline name
    :return: Instance of the airline
    :raises ValueError: If the airline doesn't exist
    """
    try:
        with Session.begin() as session:
            airline = session.query(Airline).filter(Airline.name == name).one()
    except NoResultFound as e:
        raise ValueError("Airline not found") from e

    return airline


def list_airlines():
    """
    List all airlines

    :return: A list of Airline instances without eager loading of related entities
    """
    with Session.begin() as session:
        airlines = session.query(Airline).order_by(db.asc(Airline.name)).all()
    return airlines
