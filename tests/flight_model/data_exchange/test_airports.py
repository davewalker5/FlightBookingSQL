import unittest
from src.flight_model.model import create_database, Session, Airport
from src.flight_model.data_exchange import import_airport_details


class TestAircraftLayouts(unittest.TestCase):
    def setUp(self) -> None:
        create_database()

    def test_import_airlines(self):
        import_airport_details()

        airports = {
            "ALC": {"name": "Alicante", "tz": "Europe/Madrid"},
            "LGW": {"name": "London Gatwick", "tz": "Europe/London"},
            "RMU": {"name": "Murcia International Airport", "tz": "Europe/Madrid"}
        }

        with Session.begin() as session:
            for airport_code in airports:
                airport = session.query(Airport).filter(Airport.code == airport_code).one()
                self.assertEqual(airport_code, airport.code)
                self.assertEqual(airports[airport_code]["name"], airport.name)
                self.assertEqual(airports[airport_code]["tz"], airport.timezone)

