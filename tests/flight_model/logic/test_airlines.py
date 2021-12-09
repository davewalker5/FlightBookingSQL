import unittest
from src.flight_model.model import create_database, Session, Airline
from src.flight_model.logic import create_airline, list_airlines, get_airline


class TestAirlines(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_airline("EasyJet")

    def test_can_create_airline(self):
        with Session.begin() as session:
            airline = session.query(Airline).one()
            self.assertEqual("EasyJet", airline.name)

    def test_cannot_create_duplicate_airline(self):
        with self.assertRaises(ValueError), Session.begin() as session:
            _ = create_airline("EasyJet")

    def test_can_list_airlines(self):
        airlines = list_airlines()
        self.assertEqual(1, len(airlines))
        self.assertEqual("EasyJet", airlines[0].name)

    def test_can_get_airline(self):
        airline = get_airline("EasyJet")
        self.assertEqual("EasyJet", airline.name)

    def test_cannot_get_missing_airline(self):
        with self.assertRaises(ValueError):
            _ = get_airline("British Airways")
