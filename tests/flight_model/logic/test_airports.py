import unittest
from src.flight_model.model import create_database, Session, Airport
from src.flight_model.logic import create_airport, list_airports, get_airport, delete_airport, update_airport
from src.flight_model.logic import create_airline
from src.flight_model.logic import create_flight


class TestAirports(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_airport("LGW", "London Gatwick", "Europe/London")

    def test_can_create_airport(self):
        with Session.begin() as session:
            airport = session.query(Airport).one()
            self.assertEqual("LGW", airport.code)
            self.assertEqual("London Gatwick", airport.name)
            self.assertEqual("Europe/London", airport.timezone)

    def test_cannot_create_duplicate_code(self):
        with self.assertRaises(ValueError), Session.begin() as session:
            _ = create_airport("LGW", "Some Airport", "Europe/Madrid")

    def test_can_list_airports(self):
        airports = list_airports()
        self.assertEqual(1, len(airports))
        self.assertEqual("LGW", airports[0].code)
        self.assertEqual("London Gatwick", airports[0].name)
        self.assertEqual("Europe/London", airports[0].timezone)

    def test_can_get_airport(self):
        airports = list_airports()
        airport = get_airport(airports[0].id)
        self.assertEqual("LGW", airport.code)
        self.assertEqual("London Gatwick", airport.name)
        self.assertEqual("Europe/London", airport.timezone)

    def test_cannot_get_missing_airport(self):
        with self.assertRaises(ValueError):
            _ = get_airport(-1)

    def test_can_delete_airport(self):
        airport = list_airports()[0]
        delete_airport(airport.id)
        airports = list_airports()
        self.assertEqual(0, len(airports))

    def test_cannot_delete_airport_in_use(self):
        create_airline("EasyJet")
        create_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_flight("EasyJet", "LGW", "RMU", "U28549", "20/11/2021", "10:45", "2:25")
        airport = list_airports()[0]
        with self.assertRaises(ValueError):
            delete_airport(airport.id)

    def test_can_edit_airport(self):
        airport = list_airports()[0]
        update_airport(airport.id, "ALC", "Alicante", "Europe/Madrid")
        updated = get_airport(airport.id)
        self.assertEqual("ALC", updated.code)
        self.assertEqual("Alicante", updated.name)
        self.assertEqual("Europe/Madrid", updated.timezone)

    def test_cannot_edit_airport_to_create_duplicate_code(self):
        airport = list_airports()[0]
        create_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        with self.assertRaises(ValueError):
            update_airport(airport.id, "RMU", "Murcia", "Europe/Madrid")

    def test_cannot_edit_missing_airport(self):
        with self.assertRaises(ValueError):
            update_airport(-1, "RMU", "Murcia", "Europe/Madrid")
