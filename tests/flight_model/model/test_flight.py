import unittest
import datetime
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.flight_model.model import create_database, Session, Airline, Flight
from src.flight_model.logic import create_airport
from src.flight_model.logic import create_airline
from src.flight_model.logic import create_flight
from tests.flight_model.utils import create_test_layout, \
    create_test_seating_plan, create_test_passengers_on_flight

class TestFlight(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_airline("EasyJet")
        create_airport("LGW", "London Gatwick", "Europe/London")
        create_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_flight("EasyJet", "LGW", "RMU", "U28549", "20/11/2021", "10:45", "2:25")

    def test_can_add_flight(self):
        with Session.begin() as session:
            flight = session.query(Flight).filter(Flight.number == "U28549").one()
            self.assertEqual("EasyJet", flight.airline.name)
            self.assertEqual("LGW", flight.embarkation_airport.code)
            self.assertEqual("RMU", flight.destination_airport.code)
            self.assertEqual("U28549", flight.number)
            self.assertEqual(datetime.datetime(2021, 11, 20, 10, 45, 0), flight.departure_date)
            self.assertEqual(datetime.timedelta(seconds=8700), flight.duration)

    def test_can_add_flight_with_duplicate_number(self):
        create_flight("EasyJet", "LGW", "RMU", "U28549", "27/11/2021", "10:45", "2:25")
        with Session.begin() as session:
            flights = session.query(Flight).all()
            self.assertEqual(2, len(flights))
            for flight in flights:
                self.assertEqual("U28549", flight.number)

    def test_cannot_add_flight_with_duplicate_number_and_departure_date(self):
        with self.assertRaises(IntegrityError):
            create_flight("EasyJet", "LGW", "RMU", "U28549", "20/11/2021", "10:45", "2:25")

    def test_can_delete_flight(self):
        with Session.begin() as session:
            session.query(Flight).filter(Flight.number == "U28549").delete()

        with self.assertRaises(NoResultFound), Session.begin() as session:
            _ = session.query(Flight).filter(Flight.number == "U28549").one()

    def test_related_flights_returned_with_airline(self):
        with Session.begin() as session:
            airline = session.query(Airline).filter(Airline.name == "EasyJet").one()
            self.assertEqual(1, len(airline.flights))
            self.assertEqual("U28549", airline.flights[0].number)

    def test_related_flights_deleted_with_airline(self):
        with Session.begin() as session:
            # Note that delete won't cascade if we use delete() on the query object. Get the
            # airline object and delete it to cause the cascade that will delete flights
            airline = session.query(Airline).filter(Airline.name == "EasyJet").one()
            session.delete(airline)

        with self.assertRaises(NoResultFound), Session.begin() as session:
            _ = session.query(Flight).filter(Flight.number == "U28549").one()

    def test_flight_with_no_seats_has_no_capacity(self):
        with Session.begin() as session:
            flight = session.query(Flight).filter(Flight.number == "U28549").one()
            self.assertEqual(0, flight.capacity)

    def test_flight_with_seats_has_capacity(self):
        create_test_layout("EasyJet", "A321", "Neo", 10, "ABCDEF")
        create_test_seating_plan("U28549", "A321", "Neo")
        with Session.begin() as session:
            flight = session.query(Flight).filter(Flight.number == "U28549").one()
            self.assertEqual(60, flight.capacity)
            self.assertEqual(60, flight.available_capacity)

    def test_flight_with_passengers_reduces_available_capacity(self):
        create_test_layout("EasyJet", "A321", "Neo", 10, "ABCDEF")
        create_test_seating_plan("U28549", "A321", "Neo")
        create_test_passengers_on_flight(10)

        with Session.begin() as session:
            flight = session.query(Flight).filter(Flight.number == "U28549").one()
            self.assertEqual(60, flight.capacity)
            self.assertEqual(50, flight.available_capacity)
