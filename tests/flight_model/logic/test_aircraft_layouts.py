import unittest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from src.flight_model.model import create_database, Session, Flight, AircraftLayout, Airline
from src.flight_model.logic import create_airport
from src.flight_model.logic import create_airline, get_airline
from src.flight_model.logic import create_flight, list_flights
from src.flight_model.logic import apply_aircraft_layout, list_layouts, create_layout, add_row_to_layout, get_layout, \
    delete_layout, update_layout
from tests.flight_model.utils import create_test_layout, create_test_passengers_on_flight


class TestAircraftLayouts(unittest.TestCase):
    def setUp(self) -> None:
        create_database()

        easyjet = create_airline("EasyJet")
        layout = create_layout(easyjet.id, "A321", "Neo")
        for row in range(1, 11):
            _ = add_row_to_layout(layout.id, row, "Economy", "ABC")

        layout = create_layout(easyjet.id, "A320", "1")
        _ = add_row_to_layout(layout.id, 1, "Economy", "ABCDEF")

        ba = create_airline("British Airways")
        layout = create_layout(ba.id, "A320", "")
        _ = add_row_to_layout(layout.id, 1, "Economy", "ABCDEF")

        create_airport("LGW", "London Gatwick", "Europe/London")
        create_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_flight("EasyJet", "LGW", "RMU", "U28549", "20/11/2021", "10:45", "2:25")

    def test_can_list_layouts_for_airline(self):
        with Session.begin() as session:
            airline_id = session.query(Airline).filter(Airline.name == "EasyJet").one().id

        layouts = list_layouts(airline_id)
        unique_airline_ids = set([layout.airline_id for layout in layouts])
        self.assertEqual(2, len(layouts))
        self.assertEqual(1, len(unique_airline_ids))

    def test_can_list_layouts_for_all_airlines(self):
        layouts = list_layouts(None)
        unique_airline_ids = set([layout.airline_id for layout in layouts])
        self.assertEqual(3, len(layouts))
        self.assertEqual(2, len(unique_airline_ids))

    def test_can_apply_aircraft_layout(self):
        # Get the flight that the seating plan will be associated with and find the aircraft layout
        with Session.begin() as session:
            flight = session.query(Flight).one()

            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A321",
                        AircraftLayout.name == "Neo")\
                .one()
            aircraft_layout_id = aircraft_layout.id

        # Apply the new aircraft layout to the flight
        apply_aircraft_layout(flight.id, aircraft_layout_id)

        with Session.begin() as session:
            # Retrieve the flight and verify the seating properties
            flight = session.query(Flight)\
                .options(joinedload(Flight.aircraft_layout))\
                .one()

            self.assertEqual("A321", flight.aircraft_layout.aircraft)
            self.assertEqual("Neo", flight.aircraft_layout.name)
            self.assertEqual(30, len(flight.seats))

            seat_numbers = [seat.seat_number for seat in flight.seats]
            for row in range(1, 11):
                for letter in "ABC":
                    self.assertTrue(f"{row}{letter}" in seat_numbers)

    def test_cannot_reapply_same_aircraft_layout(self):
        # Get the flight that the seating plan will be associated with and find the aircraft layout
        with Session.begin() as session:
            flight = session.query(Flight).one()

            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A321",
                        AircraftLayout.name == "Neo")\
                .one()
            aircraft_layout_id = aircraft_layout.id

        # Apply the new aircraft layout to the flight
        apply_aircraft_layout(flight.id, aircraft_layout_id)
        with self.assertRaises(ValueError):
            apply_aircraft_layout(flight.id, aircraft_layout_id)

    def test_cannot_apply_a_layout_for_another_airline(self):
        # Get the flight that the seating plan will be associated with and find the aircraft layout
        with Session.begin() as session:
            flight = session.query(Flight).one()
            airline = session.query(Airline).filter(Airline.name == "British Airways").one()

            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == airline.id) \
                .one()
            aircraft_layout_id = aircraft_layout.id

        # Apply the new aircraft layout to the flight
        with self.assertRaises(ValueError):
            apply_aircraft_layout(flight.id, aircraft_layout_id)

    def test_cannot_apply_aircraft_layout_with_insufficient_capacity(self):
        create_test_passengers_on_flight(20)

        with Session.begin() as session:
            flight = session.query(Flight).one()

            # Get a layout that doesn't have enough capacity
            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A320",
                        AircraftLayout.name == "1")\
                .one()
            aircraft_layout_id = aircraft_layout.id

        # Attempt to apply the new aircraft layout to the flight
        with self.assertRaises(ValueError):
            apply_aircraft_layout(flight.id, aircraft_layout_id)

    def test_cannot_add_duplicate_layout(self):
        with self.assertRaises(IntegrityError):
            create_test_layout("EasyJet", "A321", "Neo", 10, "ABCDEF")

    def test_can_get_layout(self):
        airline = get_airline("British Airways")
        layouts = list_layouts(airline.id)
        layout = get_layout(layouts[0].id)
        self.assertEqual("British Airways", layout.airline.name)
        self.assertEqual("A320", layout.aircraft)
        self.assertEqual("", layout.name)
        self.assertEqual(1, len(layout.row_definitions))
        self.assertEqual("ABCDEF", layout.row_definitions[0].seats)

    def test_cannot_get_missing_layout(self):
        with self.assertRaises(ValueError):
            _ = get_layout(-1)

    def test_can_delete_layout(self):
        airline = get_airline("British Airways")
        layouts = list_layouts(airline.id)
        delete_layout(layouts[0].id)
        layouts = list_layouts(airline.id)
        self.assertEqual(0, len(layouts))

    def test_cannot_delete_layout_in_use(self):
        airline = get_airline("EasyJet")
        flights = list_flights(airline.id)
        layouts = list_layouts(airline.id)
        apply_aircraft_layout(flights[0].id, layouts[0].id)
        with self.assertRaises(ValueError):
            delete_layout(layouts[0].id)

    def test_can_update_layout(self):
        airline = get_airline("EasyJet")
        layout = [layout
                  for layout in list_layouts(airline.id)
                  if layout.aircraft == "A321"][0]
        update_layout(layout.id, "A319", "")
        updated = get_layout(layout.id)
        self.assertEqual("EasyJet", updated.airline.name)
        self.assertEqual("A319", updated.aircraft)
        self.assertEqual("", updated.name)

    def test_cannot_update_missing_layout(self):
        with self.assertRaises(ValueError):
            update_layout(-1, "A319", "1")

    def test_cannot_update_layout_to_create_duplicate(self):
        airline = get_airline("EasyJet")
        layout = [layout
                  for layout in list_layouts(airline.id)
                  if layout.aircraft == "A320"][0]
        with self.assertRaises(ValueError):
            update_layout(layout.id, "A321", "Neo")
