import unittest
import datetime
from src.flight_model.model import create_database, Session, Flight, Passenger
from src.flight_model.logic import create_airport
from src.flight_model.logic import create_airline
from src.flight_model.logic import create_flight
from src.flight_model.logic import create_passenger


class TestFlight(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_airline("EasyJet")
        create_airport("LGW", "London Gatwick", "Europe/London")
        create_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_flight("EasyJet", "LGW", "RMU", "U28549", "20/11/2021", "10:45", "2:25")
        create_passenger("Some Passenger", "M", datetime.date(1970, 2, 1), "United Kingdom", "England", "1234567890")

        # Add the test passenger to the test flight
        with Session.begin() as session:
            flight = session.query(Flight).one()
            passenger = session.query(Passenger).one()
            flight.passengers.append(passenger)

    def test_can_add_passenger_to_flight(self):
        with Session.begin() as session:
            flight = session.query(Flight).one()
            self.assertEqual(1, flight.passenger_count)
            self.assertEqual("1234567890", flight.passengers[0].passport_number)

            passenger = session.query(Passenger).one()
            self.assertEqual(1, flight.passenger_count)
            self.assertEqual("U28549", passenger.flights[0].number)

    def test_can_delete_passenger_from_flight(self):
        with Session.begin() as session:
            flight = session.query(Flight).one()
            flight.passengers.remove(flight.passengers[0])

        with Session.begin() as session:
            flight = session.query(Flight).one()
            self.assertEqual(0, flight.passenger_count)

            # Make sure the passenger is still there!
            _ = session.query(Passenger).one()

    def test_can_delete_flight_from_passenger(self):
        with Session.begin() as session:
            passenger = session.query(Passenger).one()
            passenger.flights.remove(passenger.flights[0])

        with Session.begin() as session:
            passenger = session.query(Passenger).one()
            self.assertEqual(0, len(passenger.flights))

            # Make sure the passenger is still there!
            _ = session.query(Flight).one()
