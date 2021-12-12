"""
Seat allocation business logic
"""

from ..model import Session, Flight


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


def get_current_seat_allocations(flight_id):
    """
    Return the current seat allocations for a flight

    :param flight_id: ID of the flight for which to get allocations
    :return: A list of (seat number, passenger ID) tuples for current passenger seat allocations
    """
    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)

        if flight.seats:
            current_allocations = [(seat.seat_number, seat.passenger_id)
                                   for seat in flight.seats
                                   if seat.passenger_id is not None]
        else:
            current_allocations = []

    return current_allocations


def remove_seats(flight_id):
    """
    Remove the current seats from the specified flight

    :param flight_id: ID of the flight for which to remove seats
    """
    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)

        if flight.seats:
            for seat in flight.seats:
                session.delete(seat)


def copy_seat_allocations(flight_id, allocations):
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


def allocate_available_seats(flight_id, passenger_ids):
    """
    Allocate available seats to a set of passengers

    :param flight_id: ID for the flight
    :param passenger_ids: IDs for the passengers requiring seat allocations
    """

    # Local map transformation function to allocate a seat to a passenger
    def _allocate_seat(unallocated_passenger_id, seat):
        seat.passenger_id = unallocated_passenger_id

    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)
        available_seats = [seat for seat in sorted(flight.seats, key=lambda s: s.id) if seat.passenger_id is None]
        for _ in map(_allocate_seat, passenger_ids, available_seats):
            pass
