import datetime
import unittest
from sqlalchemy.exc import NoResultFound
from src.flight_model.model import create_database, Session, Flight, Seat, Passenger
from src.flight_model.logic import create_airport
from src.flight_model.logic import create_airline
from src.flight_model.logic import create_flight
from src.flight_model.logic import create_passenger
from tests.flight_model.utils import create_test_layout, create_test_seating_plan


class TestSeats(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_airline("EasyJet")
        create_airport("LGW", "London Gatwick", "Europe/London")
        create_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_flight("EasyJet", "LGW", "RMU", "U28549", "20/11/2021", "10:45", "2:25")
        create_test_layout("EasyJet", "A321", "Neo", 10, "ABCDEF")
        create_test_seating_plan("U28549", "A321", "Neo")
        create_passenger("Some Passenger", "M", datetime.date(1970, 2, 1), "United Kingdom", "England", "1234567890")

    def test_can_add_seats(self):
        with Session.begin() as session:
            flight = session.query(Flight).one()

            self.assertEqual("A321", flight.aircraft_layout.aircraft)
            self.assertEqual("Neo", flight.aircraft_layout.name)
            self.assertEqual(60, len(flight.seats))

            seat_numbers = [seat.seat_number for seat in flight.seats]
            for row in range(1, 11):
                for letter in "ABCDEF":
                    self.assertTrue(f"{row}{letter}" in seat_numbers)

    def test_related_seats_returned_with_flight(self):
        with Session.begin() as session:
            flight = session.query(Flight).one()
            self.assertEqual(60, len(flight.seats))

    def test_related_seats_deleted_with_flight(self):
        with Session.begin() as session:
            # Note that delete won't cascade if we use delete() on the query object. Get the
            # layout object and delete it to cause the cascade that will delete row definitions
            flight = session.query(Flight).one()
            session.delete(flight)

        with self.assertRaises(NoResultFound), Session.begin() as session:
            _ = session.query(Seat).one()

    def test_can_allocate_seat_to_passenger(self):
        with Session.begin() as session:
            passenger = session.query(Passenger).one()
            seat = session.query(Seat).filter(Seat.seat_number == "3A").one()
            seat.passenger = passenger

        with Session.begin() as session:
            seat = session.query(Seat).filter(Seat.seat_number == "3A").one()
            self.assertEqual(passenger.id, seat.passenger.id)

    def test_can_unallocate_seat(self):
        with Session.begin() as session:
            seat = session.query(Seat).filter(Seat.seat_number == "3A").one()
            seat.passenger = None

        with Session.begin() as session:
            seat = session.query(Seat).filter(Seat.seat_number == "3A").one()
            self.assertIsNone(seat.passenger)
