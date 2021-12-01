import unittest
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.flight_model.model import create_database, Session, Airline
from tests.flight_model.model.utils import create_test_airline


class TestAirline(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_test_airline("EasyJet")

    def test_can_add_airline(self):
        with Session.begin() as session:
            airline = session.query(Airline).filter(Airline.name == "EasyJet").one()
            self.assertEqual("EasyJet", airline.name)

    def test_can_delete_airline(self):
        with Session.begin() as session:
            session.query(Airline).filter(Airline.name == "EasyJet").delete()

        with self.assertRaises(NoResultFound), Session.begin() as session:
            _ = session.query(Airline).filter(Airline.name == "EasyJet").one()

    def test_cannot_add_airline_with_duplicate_name(self):
        with self.assertRaises(IntegrityError):
            create_test_airline(name="EasyJet")
