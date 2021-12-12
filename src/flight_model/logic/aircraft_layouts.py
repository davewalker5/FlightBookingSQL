"""
Aircraft layout business logic
"""

import sqlalchemy as db
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound
from .seat_allocations import allocate_available_seats, copy_seat_allocations, get_current_seat_allocations, \
    remove_seats
from ..model import Session, AircraftLayout, Flight, Seat


def _retrieve_and_validate_new_layout(flight_id, aircraft_layout_id):
    """
    Retrieve an aircraft layout and confirm that it's suitable to be applied to a given flight

    :param flight_id: ID for the flight to validate the layout for
    :param aircraft_layout_id: ID for the aircraft layout
    :return: Instance of the AircraftLayout with the specified ID
    """
    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)

        aircraft_layout = session.query(AircraftLayout).get(aircraft_layout_id)
        if flight.airline_id != aircraft_layout.airline_id:
            raise ValueError("Aircraft layout is not associated with the airline for the flight")

        if flight.aircraft_layout_id == aircraft_layout_id:
            raise ValueError("New aircraft layout is the same as the current aircraft layout")

        if aircraft_layout.capacity < flight.passenger_count:
            raise ValueError("Aircraft layout doesn't have enough seats to accommodate all passengers")

    return aircraft_layout


def _create_seats_from_layout(flight_id, aircraft_layout):
    """
    Apply an aircraft layout to the specified flight

    :param flight_id: ID for the flight to apply the layout to
    :param aircraft_layout: AircraftLayout instance to apply
    """
    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)

        # Iterate over the row definitions and the seat letters in each, adding a seat in association with the flight
        for row_definition in aircraft_layout.row_definitions:
            # Iterate over the seats in the row, adding each to the flight
            for seat_letter in row_definition.seats:
                seat = Seat(flight=flight, seat_number=f"{row_definition.number}{seat_letter}")
                session.add(seat)

        # Make the association between flight and layout
        flight.aircraft_layout = aircraft_layout


def apply_aircraft_layout(flight_id, aircraft_layout_id):
    """
    Apply an aircraft layout to a flight, copying across seat allocations

    :param flight_id: ID of the flight to apply the layout to
    :param aircraft_layout_id: ID of the aircraft layout to apply
    """

    # TODO : This needs refactoring but works well enough as a demo for now

    # Get the aircraft layout and make sure it's valid for the specified flight
    aircraft_layout = _retrieve_and_validate_new_layout(flight_id, aircraft_layout_id)

    # Get the current seating allocations and remove the existing seats
    current_allocations = get_current_seat_allocations(flight_id)
    remove_seats(flight_id)

    # Create the new seats
    _create_seats_from_layout(flight_id, aircraft_layout)

    # Copy seating allocations across
    not_allocated = copy_seat_allocations(flight_id, current_allocations)

    # It's possible some seats don't exist in the new layout compared to the old. If there are any passengers
    # who were in those seats, move them to the next available seats
    if not_allocated:
        allocate_available_seats(flight_id, not_allocated)


def list_layouts(airline_id=None):
    """
    List of aircraft layouts for an airline

    :param airline_id: ID of the airline for which to load aircraft layouts (or None to list all layouts)
    :return: A list of Aircraft layout instances with eager loading of related entities
    """
    with Session.begin() as session:
        if airline_id:
            layouts = session.query(AircraftLayout) \
                .options(joinedload(AircraftLayout.airline)) \
                .filter(AircraftLayout.airline_id == airline_id) \
                .order_by(db.asc(AircraftLayout.aircraft),
                          db.asc(AircraftLayout.name)) \
                .all()
        else:
            layouts = session.query(AircraftLayout) \
                .options(joinedload(AircraftLayout.airline)) \
                .order_by(db.asc(AircraftLayout.aircraft),
                          db.asc(AircraftLayout.name)) \
                .all()

    return layouts


def get_layout(layout_id):
    """
    Get the aircraft layout with the specified ID

    :param layout_id: ID of the aircraft layout to return
    :return: AircraftLayout instance for the specified layout record
    :raises ValueError: If the layout doesn't exist
    """
    with Session.begin() as session:
        layout = session.query(AircraftLayout) \
            .options(joinedload(AircraftLayout.airline)) \
            .get(layout_id)

    if layout is None:
        raise ValueError("Aircraft layout not found")

    return layout


def create_layout(airline_id, aircraft_model, layout_name):
    """
    Create a new aircraft layout with the specified properties

    :param airline_id: ID for the airline associated with the layout
    :param aircraft_model: Aircraft model e.g. A321
    :param layout_name: Layout name e.g. Neo
    """
    with Session.begin() as session:
        aircraft_layout = AircraftLayout(airline_id=airline_id,
                                         aircraft=aircraft_model,
                                         name="" if layout_name is None else layout_name)
        session.add(aircraft_layout)

    return aircraft_layout


def update_layout(layout_id, aircraft_model, layout_name):
    """
    Update the core details for an aircraft layout

    :param layout_id: ID for the aircraft layout to update
    :param aircraft_model: Aircraft model e.g. A321
    :param layout_name: Layout name e.g. Neo
    :raises ValueError: If the edit would result in a duplicate layout or the layout doesn't exist
    """
    try:
        with Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout)\
                .filter(AircraftLayout.id == layout_id)\
                .one()
            aircraft_layout.aircraft = aircraft_model
            aircraft_layout.name = layout_name
    except NoResultFound as e:
        raise ValueError("Aircraft layout not found") from e
    except IntegrityError as e:
        raise ValueError("Cannot update aircraft layout as this would create a duplicate") from e


def delete_layout(layout_id):
    """
    Delete the airport with the specified ID

    :param layout_id: ID of the aircraft layout to delete
    :raises ValueError: If the layout is still referenced
    """
    try:
        with Session.begin() as session:
            layout = session.query(AircraftLayout).get(layout_id)
            session.delete(layout)
    except IntegrityError as e:
        raise ValueError("Cannot delete an aircraft layout that is referenced by a flight") from e
