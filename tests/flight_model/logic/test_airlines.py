import unittest
from src.flight_model.model import create_database, Session, Airline
from src.flight_model.logic import create_airport
from src.flight_model.logic import create_flight, list_flights
from src.flight_model.logic import create_airline, list_airlines, get_airline, delete_airline, update_airline
from src.flight_model.logic import create_layout, list_layouts


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

    def test_can_get_airline_by_name(self):
        airline = get_airline("EasyJet")
        self.assertEqual("EasyJet", airline.name)

    def test_can_get_airline_by_id(self):
        airline_id = get_airline("EasyJet").id
        airline = get_airline(airline_id)
        self.assertEqual("EasyJet", airline.name)

    def test_cannot_get_missing_airline_by_name(self):
        with self.assertRaises(ValueError):
            _ = get_airline("British Airways")

    def test_cannot_get_missing_airline_by_id(self):
        with self.assertRaises(ValueError):
            _ = get_airline(-1)

    def test_cannot_get_missing_airline_by_unrecognised_type(self):
        with self.assertRaises(TypeError):
            _ = get_airline(1.0)

    def test_can_delete_airline(self):
        airline = get_airline("EasyJet")
        delete_airline(airline.id)
        airlines = list_airlines()
        self.assertEqual(0, len(airlines))

    def test_delete_airline_in_use_deletes_related_flights(self):
        create_airport("LGW", "London Gatwick", "Europe/London")
        create_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_flight("EasyJet", "LGW", "RMU", "U28549", "20/11/2021", "10:45", "2:25")
        airline = get_airline("EasyJet")
        delete_airline(airline.id)
        flights = list_flights()
        self.assertEqual(0, len(flights))

    def test_delete_airline_in_use_deletes_related_layouts(self):
        airline = get_airline("EasyJet")
        create_layout(airline.id, "A321", "neo")
        delete_airline(airline.id)
        layouts = list_layouts()
        self.assertEqual(0, len(layouts))

    def test_can_update_airline(self):
        airline = get_airline("EasyJet")
        update_airline(airline.id, "British Airways")

        with self.assertRaises(ValueError):
            _ = get_airline("EasyJet")

        updated = get_airline(airline.id)
        self.assertEqual("British Airways", updated.name)

    def test_cannot_update_missing_airline(self):
        with self.assertRaises(ValueError):
            update_airline(-1, "SAS")

    def test_cannot_update_airline_to_create_duplicate(self):
        airline = create_airline("British Airways")
        with self.assertRaises(ValueError):
            update_airline(airline.id, "EasyJet")
