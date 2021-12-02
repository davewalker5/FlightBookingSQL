import datetime
import os
import unittest
from unittest.mock import patch
from src.flight_model.model import create_database, Session, Flight
from src.flight_model.logic import InvalidOperationError, MissingBoardingCardPluginError, generate_boarding_cards, \
    allocate_seat, get_boarding_card_path
from tests.flight_model.utils import create_test_airline, create_test_airport, create_test_flight, \
    create_test_layout, create_test_seating_plan, create_test_passengers_on_flight, text_card_generator, \
    binary_card_generator


class TestAirlines(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_test_airline("EasyJet")
        create_test_layout("EasyJet", "A321", "Neo", 10, "ABC")
        create_test_airport("LGW", "London Gatwick", "Europe/London")
        create_test_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_test_flight("EasyJet", "LGW", "RMU", "U28549",
                           datetime.datetime(2021, 11, 20, 10, 45, 0),
                           datetime.timedelta(hours=2, minutes=25))

    @patch("src.flight_model.logic.boarding_cards.card_generator_map", {"txt": text_card_generator})
    def test_can_generate_boarding_cards(self):
        create_test_seating_plan("U28549", "A321", "Neo")
        create_test_passengers_on_flight(1)
        with Session.begin() as session:
            flight = session.query(Flight).one()
            allocate_seat(flight.id, flight.passengers[0].id, "1A")
            generate_boarding_cards(flight.id, "txt", "28A")

        # Boarding card text file should exist
        boarding_card_file = get_boarding_card_path(flight.number, "1A", flight.departure_date, "txt")
        self.assertTrue(os.path.exists(boarding_card_file))

        # Boarding card text file should contain each of the flight details
        with open(boarding_card_file, mode="rt", encoding="utf-8") as f:
            contents = f.read()
        os.unlink(boarding_card_file)

        self.assertIn("EasyJet", contents)
        self.assertIn("LGW", contents)
        self.assertIn("10:45 AM", contents)
        self.assertIn("RMU", contents)
        self.assertIn("02:10 PM", contents)
        self.assertIn("Passenger 0", contents)

    @patch("src.flight_model.logic.boarding_cards.card_generator_map", {"dat": binary_card_generator})
    def test_can_generate_binary_format_boarding_cards(self):
        create_test_seating_plan("U28549", "A321", "Neo")
        create_test_passengers_on_flight(1)
        with Session.begin() as session:
            flight = session.query(Flight).one()
            allocate_seat(flight.id, flight.passengers[0].id, "1A")
            generate_boarding_cards(flight.id, "dat", "28A")

        # Boarding card text file should exist
        boarding_card_file = get_boarding_card_path(flight.number, "1A", flight.departure_date, "dat")
        self.assertTrue(os.path.exists(boarding_card_file))

        # Boarding card text file should contain each of the flight details
        with open(boarding_card_file, mode="rt", encoding="utf-8") as f:
            contents = f.read()
        os.unlink(boarding_card_file)

        self.assertIn("EasyJet", contents)
        self.assertIn("LGW", contents)
        self.assertIn("10:45 AM", contents)
        self.assertIn("RMU", contents)
        self.assertIn("02:10 PM", contents)
        self.assertIn("Passenger 0", contents)

    @patch("src.flight_model.logic.boarding_cards.card_generator_map", {"txt": text_card_generator})
    def test_cannot_print_boarding_cards_with_no_gate(self):
        create_test_seating_plan("U28549", "A321", "Neo")
        create_test_passengers_on_flight(1)
        with self.assertRaises(ValueError), Session.begin() as session:
            flight = session.query(Flight).one()
            allocate_seat(flight.id, flight.passengers[0].id, "1A")
            generate_boarding_cards(flight.id, "txt", None)

    @patch("src.flight_model.logic.boarding_cards.card_generator_map", {"txt": text_card_generator})
    def test_cannot_print_boarding_cards_with_empty_gate(self):
        create_test_seating_plan("U28549", "A321", "Neo")
        create_test_passengers_on_flight(1)
        with self.assertRaises(ValueError), Session.begin() as session:
            flight = session.query(Flight).one()
            allocate_seat(flight.id, flight.passengers[0].id, "1A")
            generate_boarding_cards(flight.id, "txt", "")

    @patch("src.flight_model.logic.boarding_cards.card_generator_map", {"txt": text_card_generator})
    def test_cannot_print_boarding_cards_with_no_aircraft_layout(self):
        create_test_passengers_on_flight(1)
        with self.assertRaises(InvalidOperationError), Session.begin() as session:
            flight = session.query(Flight).one()
            generate_boarding_cards(flight.id, "txt", "28A")

    def test_cannot_print_boarding_cards_with_no_plugin(self):
        create_test_seating_plan("U28549", "A321", "Neo")
        create_test_passengers_on_flight(1)
        with self.assertRaises(MissingBoardingCardPluginError), Session.begin() as session:
            flight = session.query(Flight).one()
            allocate_seat(flight.id, flight.passengers[0].id, "1A")
            generate_boarding_cards(flight.id, "txt", "28A")

    @patch("src.flight_model.logic.boarding_cards.card_generator_map", {"txt": text_card_generator})
    def test_cannot_generate_boarding_cards_with_no_passengers(self):
        create_test_seating_plan("U28549", "A321", "Neo")
        with self.assertRaises(InvalidOperationError), Session.begin() as session:
            flight = session.query(Flight).one()
            generate_boarding_cards(flight.id, "txt", "28A")
