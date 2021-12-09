"""
Airline business logic
"""

import sqlalchemy as db
from functools import singledispatch
from sqlalchemy.exc import IntegrityError, NoResultFound
from ..model import Session, Airline


def create_airline(name):
    """
    Insert an airline record for testing

    :param name: Airline name
    :returns: An instance of the Airline class for the created record
    :raises ValueError: If the airline is a duplicate
    """
    try:
        with Session.begin() as session:
            airline = Airline(name=name)
            session.add(airline)
    except IntegrityError as e:
        raise ValueError("Cannot create duplicate airline name") from e

    return airline


@singledispatch
def get_airline(_):
    """
    Return the Airline instance for the airline with the specified identifier

    :param name: Airline name
    :param airline_id: Airline ID
    :return: Instance of the airline
    :raises ValueError: If the airline doesn't exist
    """
    raise TypeError("Invalid parameter type for get_airline")


@get_airline.register(str)
def _(name):
    try:
        with Session.begin() as session:
            airline = session.query(Airline).filter(Airline.name == name).one()
    except NoResultFound as e:
        raise ValueError("Airline not found") from e

    return airline


@get_airline.register(int)
def _(airline_id):
    with Session.begin() as session:
        airline = session.query(Airline).get(airline_id)

    if airline is None:
        raise ValueError("Airline not found")

    return airline


def list_airlines():
    """
    List all airlines

    :return: A list of Airline instances without eager loading of related entities
    """
    with Session.begin() as session:
        airlines = session.query(Airline).order_by(db.asc(Airline.name)).all()
    return airlines


def delete_airline(airline_id):
    """
    Delete the airline with the specified ID

    :param airline_id: ID of the airline to delete
    """
    with Session.begin() as session:
        airline = session.query(Airline).get(airline_id)
        session.delete(airline)
