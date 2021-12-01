import unittest
from src.flight_model.model import create_database, Session, Airline
from src.flight_model.logic import create_airline, list_airlines


class TestAirlines(unittest.TestCase):
    def setUp(self) -> None:
        create_database()

        # Use the production logic, here, as this is one of the methods under test
        create_airline("EasyJet")

    def test_can_create_airline(self):
        with Session.begin() as session:
            airline = session.query(Airline).one()
            self.assertEqual("EasyJet", airline.name)

    def test_can_list_airlines(self):
        airlines = list_airlines()
        self.assertEqual(1, len(airlines))
        self.assertEqual("EasyJet", airlines[0].name)
