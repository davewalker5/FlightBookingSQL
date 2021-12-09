"""
Aircraft layout and seat allocation business logic
"""

import sqlalchemy as db
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from ..model import Session, AircraftLayout, Flight, Seat, RowDefinition


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


def _retrieve_and_validate_new_layout(flight_id, aircraft_layout_id):
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


def _remove_current_seats(flight_id):
    """
    Remove the current seats from the specified flight and return the pre-removal seat allocations

    :param flight_id: ID of the flight to remove seats from
    :return: A list of (seat number, passenger ID) tuples for current passenger seat allocations
    """
    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)

        if flight.seats:
            current_allocations = [(seat.seat_number, seat.passenger_id)
                                   for seat in flight.seats
                                   if seat.passenger_id is not None]

            for seat in flight.seats:
                session.delete(seat)
        else:
            current_allocations = []

    return current_allocations


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


def _copy_seat_allocations(flight_id, allocations):
    """
    Re-apply a set of seat allocations

    :param flight_id: ID for the flight to apply the allocations  to
    :param allocations: A list of (seat number, passenger ID) tuples for the seat allocations to apply
    :return: A list of passenger IDs for passengers whose seat allocations couldn't be preserved
    """
    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)

        # Generate a dictionary of the new seats to make it easier to find and allocate a seat by
        # seat number. A seat number from an original layout isn't guaranteed to be available in the
        # new layout so capture passengers that can't be put in the same seat number
        not_allocated = []
        new_seats = {seat.seat_number: seat for seat in flight.seats}
        for seat_number, passenger_id in allocations:
            if seat_number in new_seats:
                new_seats[seat_number].passenger_id = passenger_id
            else:
                not_allocated.append(passenger_id)

    return not_allocated


def _allocate_available_seats(flight_id, passenger_ids):
    # Local map transformation function to allocate a seat to a passenger
    def _allocate_seat(unallocated_passenger_id, seat):
        seat.passenger_id = unallocated_passenger_id

    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)
        available_seats = [seat for seat in sorted(flight.seats, key=lambda s: s.id) if seat.passenger_id is None]
        for _ in map(_allocate_seat, passenger_ids, available_seats):
            pass


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
    current_allocations = _remove_current_seats(flight_id)

    # Create the new seats
    _create_seats_from_layout(flight_id, aircraft_layout)

    # Copy seating allocations across
    not_allocated = _copy_seat_allocations(flight_id, current_allocations)

    # It's possible some seats don't exist in the new layout compared to the old. If there are any passengers
    # who were in those seats, move them to the next available seats
    if not_allocated:
        _allocate_available_seats(flight_id, not_allocated)


def allocate_seat(flight_id, passenger_id, seat_number):
    """
    Allocate a seat to a passenger

    :param flight_id: ID of the flight
    :param passenger_id: ID of the passenger
    :param seat_number: Seat number to allocate e.g. 28A
    """
    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)

        if not flight.seats:
            raise ValueError("The flight does not have an aircraft layout")

        passenger_ids = [passenger.id for passenger in flight.passengers]
        if passenger_id not in passenger_ids:
            raise ValueError("The passenger doesn't belong to the specified flight")

        required_seat = [seat for seat in flight.seats if seat.seat_number == seat_number]
        if not required_seat:
            raise ValueError("The specified seat does not exist on the flight")

        if required_seat[0].passenger_id == passenger_id:
            raise ValueError("The seat is already allocated to the passenger")

        if required_seat[0].passenger_id is not None:
            raise ValueError("The seat is already allocated to another passenger")

        current_seat = [seat for seat in flight.seats if seat.passenger_id == passenger_id]
        if current_seat:
            current_seat[0].passenger_id = None

        required_seat[0].passenger_id = passenger_id


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


def add_row_to_layout(aircraft_layout_id, row_number, seating_class, seat_letters):
    """
    Add a row definition to an existing aircraft layout

    :param aircraft_layout_id: ID for the aircraft layout to add to
    :param row_number: Row number
    :param seating_class: Seating class for the row
    :param seat_letters: String of seat letters for the row e.g. ABCDEF
    """
    with Session.begin() as session:
        row_definition = RowDefinition(aircraft_layout_id=aircraft_layout_id,
                                       number=row_number,
                                       seating_class=seating_class,
                                       seats=seat_letters)
        session.add(row_definition)

    return row_definition


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
