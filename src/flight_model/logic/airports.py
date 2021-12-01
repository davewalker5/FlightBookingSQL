"""
Airport business logic
"""

import sqlalchemy as db
from ..model import Session, Airport


def create_airport(code, name, timezone):
    """
    Create an airport record

    :param code: 3-letter IATA code
    :param name: Airport name
    :param timezone: Airport timezone
    :returns: An instance of the Airport class for the created record
    """
    with Session.begin() as session:
        airport = Airport(code=code, name=name, timezone=timezone)
        session.add(airport)

    return airport


def list_airports():
    """
    List all airports

    :return: A list of Airport instances without eager loading of related entities
    """
    with Session.begin() as session:
        airports = session.query(Airport).order_by(db.asc(Airport.code)).all()
    return airports
