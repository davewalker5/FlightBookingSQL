import datetime
import unittest
from src.flight_model.model import create_database, Session, Flight
from src.flight_model.logic import create_flight, get_flight, list_flights, delete_flight
from src.flight_model.logic import create_airport
from src.flight_model.logic import create_airline, list_airlines
from src.flight_model.logic import create_passenger, add_passenger


class TestFlights(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_airline("EasyJet")
        create_airport("LGW", "London Gatwick", "Europe/London")
        create_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_flight("EasyJet", "LGW", "RMU", "U28549", "20/11/2021", "10:45", "2:25")

    def test_can_create_flight(self):
        with Session.begin() as session:
            flight = session.query(Flight).one()
            self.assertEqual("EasyJet", flight.airline.name)
            self.assertEqual("LGW", flight.embarkation_airport.code)
            self.assertEqual("RMU", flight.destination_airport.code)
            self.assertEqual("U28549", flight.number)
            self.assertEqual("20/11/2021", flight.departs_localtime.strftime("%d/%m/%Y"))
            self.assertEqual("2:25", flight.formatted_duration)

    def test_can_get_flight(self):
        with Session.begin() as session:
            flight_id = session.query(Flight).one().id

        flight = get_flight(flight_id)
        self.assertEqual("EasyJet", flight.airline.name)
        self.assertEqual("LGW", flight.embarkation_airport.code)
        self.assertEqual("RMU", flight.destination_airport.code)
        self.assertEqual("U28549", flight.number)
        self.assertEqual("20/11/2021", flight.departs_localtime.strftime("%d/%m/%Y"))
        self.assertEqual("2:25", flight.formatted_duration)

    def test_can_list_all_flights(self):
        flights = list_flights()
        self.assertEqual(1, len(flights))

    def test_can_list_flights_by_airline(self):
        airline = list_airlines()[0]
        flights = list_flights(airline.id)
        self.assertEqual(1, len(flights))

    def test_cannot_list_flights_for_missing_airline(self):
        flights = list_flights(-1)
        self.assertEqual(0, len(flights))

    def test_can_delete_flight(self):
        with Session.begin() as session:
            flight_id = session.query(Flight).one().id

        delete_flight(flight_id)

        flight = get_flight(flight_id)
        self.assertIsNone(flight)

    def test_can_add_passenger_to_flight(self):
        with Session.begin() as session:
            flight_id = session.query(Flight).one().id

        passenger = create_passenger("Some One", "F", datetime.datetime(1970, 2, 1).date(), "UK", "UK", "123456789")
        add_passenger(flight_id, passenger)

        flight = get_flight(flight_id)
        self.assertEqual(1, len(flight.passengers))

    def test_cannot_add_flight_with_same_departure_and_destination(self):
        with self.assertRaises(ValueError):
            create_flight("EasyJet", "LGW", "LGW", "U28549", "20/11/2021", "10:45", "2:25")
