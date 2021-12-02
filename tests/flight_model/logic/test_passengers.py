import datetime
import unittest
from sqlalchemy.exc import NoResultFound
from src.flight_model.model import create_database, Session, Passenger, Flight, Seat
from tests.flight_model.utils import create_test_airline, create_test_flight, create_test_layout, \
    create_test_airport, create_test_seating_plan
from src.flight_model.logic import create_passenger, delete_passenger


class TestPassengers(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_test_airline("EasyJet")
        create_test_layout("EasyJet", "A321", "Neo", 10, "ABCDEF")
        create_test_airport("LGW", "London Gatwick", "Europe/London")
        create_test_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_test_flight("EasyJet", "LGW", "RMU", "U28549", datetime.datetime(2021, 11, 20, 10, 45, 0),
                           datetime.timedelta(hours=2, minutes=25))
        create_test_seating_plan("U28549", "A321", "Neo")

        # Use the production logic, here, as this is one of the methods under test
        create_passenger("Some One", "F", datetime.datetime(1970, 2, 1).date(), "UK", "UK", "1234567890")

    def test_can_create_passenger(self):
        with Session.begin() as session:
            passenger = session.query(Passenger).one()
            self.assertEqual("Some One", passenger.name)
            self.assertEqual("F", passenger.gender)
            self.assertEqual("01/02/1970", passenger.dob.strftime("%d/%m/%Y"))
            self.assertEqual("UK", passenger.nationality)
            self.assertEqual("UK", passenger.residency)
            self.assertEqual("1234567890", passenger.passport_number)

    def test_can_delete_passenger(self):
        with Session.begin() as session:
            flight = session.query(Flight).one()
            passenger = session.query(Passenger).one()
            flight.passengers.append(passenger)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            self.assertEqual(1, len(flight.passengers))

        delete_passenger(flight.id, passenger.id)

        with self.assertRaises(NoResultFound), Session.begin() as session:
            _ = session.query(Passenger).one()

    def test_delete_passenger_removes_seat_allocation(self):
        with Session.begin() as session:
            flight = session.query(Flight).one()
            passenger = session.query(Passenger).one()
            flight.passengers.append(passenger)
            seat = session.query(Seat).filter(Seat.seat_number == "5C").one()
            seat.passenger_id = passenger.id

        with Session.begin() as session:
            seat = session.query(Seat).filter(Seat.seat_number == "5C").one()
            self.assertIsNotNone(seat.passenger_id)

        delete_passenger(flight.id, passenger.id)

        with Session.begin() as session:
            seat = session.query(Seat).filter(Seat.seat_number == "5C").one()
            self.assertIsNone(seat.passenger_id)
