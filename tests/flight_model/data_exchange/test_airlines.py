import unittest
from src.flight_model.model import create_database, Session, Airline
from src.flight_model.data_exchange import import_airline_details


class TestAircraftLayouts(unittest.TestCase):
    def setUp(self) -> None:
        create_database()

    def test_import_airlines(self):
        import_airline_details()
        with Session.begin() as session:
            airlines = session.query(Airline).all()
            airline_names = [airline.name for airline in airlines]
            self.assertTrue("British Airways" in airline_names)
            self.assertTrue("EasyJet" in airline_names)
            self.assertTrue("Ryanair" in airline_names)
