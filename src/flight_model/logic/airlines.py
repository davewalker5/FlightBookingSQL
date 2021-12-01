"""
Airline business logic
"""

import sqlalchemy as db
from ..model import Session, Airline

def create_airline(name):
    """
    Insert an airline record for testing

    :param name: Airline name
    :returns: An instance of the Airline class for the created record
    """
    with Session.begin() as session:
        airline = Airline(name=name)
        session.add(airline)

    return airline


def list_airlines():
    """
    List all airlines

    :return: A list of Airline instances without eager loading of related entities
    """
    with Session.begin() as session:
        airlines = session.query(Airline).order_by(db.asc(Airline.name)).all()
    return airlines
