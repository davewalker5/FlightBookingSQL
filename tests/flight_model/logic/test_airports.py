import unittest
from src.flight_model.model import create_database, Session, Airport
from src.flight_model.logic import create_airport, list_airports


class TestAirports(unittest.TestCase):
    def setUp(self) -> None:
        create_database()

        # Use the production logic, here, as this is one of the methods under test
        create_airport("LGW", "London Gatwick", "Europe/London")

    def test_can_create_airport(self):
        with Session.begin() as session:
            airport = session.query(Airport).one()
            self.assertEqual("LGW", airport.code)
            self.assertEqual("London Gatwick", airport.name)
            self.assertEqual("Europe/London", airport.timezone)

    def test_can_list_airports(self):
        airports = list_airports()
        self.assertEqual(1, len(airports))
        self.assertEqual("LGW", airports[0].code)
        self.assertEqual("London Gatwick", airports[0].name)
        self.assertEqual("Europe/London", airports[0].timezone)
