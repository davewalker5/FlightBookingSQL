"""
Airport business logic
"""

import sqlalchemy as db
from sqlalchemy.exc import IntegrityError, NoResultFound
from ..model import Session, Airport


def create_airport(code, name, timezone):
    """
    Create an airport record

    :param code: 3-letter IATA code
    :param name: Airport name
    :param timezone: Airport timezone
    :returns: An instance of the Airport class for the created record
    :raises ValueError: If the airport code is duplicated
    """
    try:
        with Session.begin() as session:
            airport = Airport(code=code, name=name, timezone=timezone)
            session.add(airport)
    except IntegrityError as e:
        raise ValueError("Cannot create duplicate airport code") from e

    return airport


def list_airports():
    """
    List all airports

    :return: A list of Airport instances without eager loading of related entities
    """
    with Session.begin() as session:
        airports = session.query(Airport).order_by(db.asc(Airport.code)).all()
    return airports


def get_airport(airport_id):
    """
    Get the airport with the specified ID

    :param airport_id: ID of the airport to return
    :return: Airport instance for the specified airport record
    :raises ValueError: If the airport doesn't exist
    """
    with Session.begin() as session:
        airport = session.query(Airport).get(airport_id)

    if airport is None:
        raise ValueError("Airport not found")

    return airport


def delete_airport(airport_id):
    """
    Delete the airport with the specified ID

    :param airport_id: ID of the airport to delete
    :raises ValueError: If the airport is still referenced
    """
    try:
        with Session.begin() as session:
            airport = session.query(Airport).get(airport_id)
            session.delete(airport)
    except IntegrityError as e:
        raise ValueError("Cannot delete an airport that is referenced by a flight") from e


def update_airport(airport_id, code, name, timezone):
    """
    Update an airport record with a new set of properties

    :param airport_id: ID of the airline to update
    :param code: 3-letter IATA airport code
    :param name: New airline name
    :param timezone: Timezone the airport is in
    :raises ValueError: If the airport becomes a duplicate as part of the update
    """
    try:
        with Session.begin() as session:
            airport = session.query(Airport).filter(Airport.id == airport_id).one()
            airport.code = code
            airport.name = name
            airport.timezone = timezone
    except NoResultFound as e:
        raise ValueError("Airport not found") from e
    except IntegrityError as e:
        raise ValueError("Cannot update airport as this would create a duplicate airport code") from e
