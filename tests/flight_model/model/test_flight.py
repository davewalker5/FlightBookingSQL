import unittest
import datetime
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.flight_model.model import create_database, Session, Airline, Flight
from tests.flight_model.model.utils import create_test_airport, create_test_airline, create_test_flight

class TestFlight(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_test_airline("EasyJet")
        create_test_airport("LGW", "London Gatwick", "Europe/London")
        create_test_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_test_flight("EasyJet", "LGW", "RMU", "U28549", datetime.datetime(2021, 11, 20, 10, 45, 0),
                           datetime.timedelta(hours=2, minutes=25))

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
        create_test_flight("EasyJet", "LGW", "RMU", "U28549", datetime.datetime(2021, 11, 27, 10, 45, 0),
                           datetime.timedelta(hours=2, minutes=25))

        with Session.begin() as session:
            flights = session.query(Flight).all()
            self.assertEqual(2, len(flights))
            for flight in flights:
                self.assertEqual("U28549", flight.number)

    def test_cannot_add_flight_with_duplicate_number_and_departure_date(self):
        with self.assertRaises(IntegrityError):
            create_test_flight("EasyJet", "LGW", "RMU", "U28549", datetime.datetime(2021, 11, 20, 10, 45, 0),
                               datetime.timedelta(hours=2, minutes=25))

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
