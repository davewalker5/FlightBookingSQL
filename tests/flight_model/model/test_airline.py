import unittest
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.flight_model.model import create_database, Session, Airline
from src.flight_model.logic import create_airport
from src.flight_model.logic import create_airline
from src.flight_model.logic import create_flight


class TestAirline(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_airline("EasyJet")

    def test_can_add_airline(self):
        with Session.begin() as session:
            airline = session.query(Airline).filter(Airline.name == "EasyJet").one()
            self.assertEqual("EasyJet", airline.name)

    def test_can_delete_airline(self):
        with Session.begin() as session:
            session.query(Airline).filter(Airline.name == "EasyJet").delete()

        with self.assertRaises(NoResultFound), Session.begin() as session:
            _ = session.query(Airline).filter(Airline.name == "EasyJet").one()

    def test_cannot_delete_airline_in_use(self):
        create_airport("LGW", "London Gatwick", "Europe/Madrid")
        create_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_flight("EasyJet", "LGW", "RMU", "U28549", "20/11/2021", "10:45", "2:25")
        with self.assertRaises(IntegrityError), Session.begin() as session:
            session.query(Airline).filter(Airline.name == "EasyJet").delete()

    def test_cannot_add_airline_with_duplicate_name(self):
        with self.assertRaises(ValueError):
            create_airline(name="EasyJet")
