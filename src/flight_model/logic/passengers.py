"""
Passenger management business logic
"""

from sqlalchemy.exc import IntegrityError
from ..model import Session, Passenger, Flight, Seat


def create_passenger(name, gender, dob, nationality, residency, passport_number):
    """
    Insert a passenger record for testing

    :param name: Passenger name
    :param gender: Passenger gender M/F
    :param dob: Date of birth
    :param nationality: Passenger nationality
    :param residency: Passenger's country of residency
    :param passport_number: Passport number
    """
    try:
        with Session.begin() as session:
            passenger = Passenger(name=name,
                                  gender=gender,
                                  dob=dob,
                                  nationality=nationality,
                                  residency=residency,
                                  passport_number=passport_number)
            session.add(passenger)
    except IntegrityError as e:
        raise ValueError("A passenger with the specified passport number already exists") from e

    return passenger


def delete_passenger(flight_id, passenger_id):
    """
    The model supports a common set of passengers across multiple flights and multiple seat allocations but for the
    purpose of this demonstration project the UI only permits creation of a passenger against one flight, rather
    than mapping them to multiple flights, so the deletion logic just removes the passenger completely

    :param flight_id: ID for the flight from which to remove the passenger
    :param passenger_id: ID of the passenger to delete
    """
    print(f"Deleting passenger {passenger_id}")
    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)
        passenger = session.query(Passenger).get(passenger_id)
        flight.passengers.remove(passenger)

        # Find any seats allocated to the passenger and remove the allocation
        seats = session.query(Seat).filter(Seat.passenger_id == passenger_id).all()
        for seat in seats:
            seat.passenger_id = None

        session.delete(passenger)
