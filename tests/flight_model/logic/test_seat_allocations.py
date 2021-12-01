import datetime
import unittest
from sqlalchemy.orm import joinedload
from src.flight_model.model import create_database, Session, Flight, AircraftLayout, Seat
from src.flight_model.logic import apply_aircraft_layout, allocate_seat
from tests.flight_model.utils import create_test_airline, create_test_flight, create_test_layout, \
    create_test_airport, create_test_passengers_on_flight


class TestSeatAllocations(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_test_airline("EasyJet")
        create_test_layout("EasyJet", "A321", "Neo", 10, "ABCDEF")
        create_test_layout("EasyJet", "A320", "1", 1, "ABCDEF")
        create_test_airport("LGW", "London Gatwick", "Europe/London")
        create_test_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_test_flight("EasyJet", "LGW", "RMU", "U28549", datetime.datetime(2021, 11, 20, 10, 45, 0),
                           datetime.timedelta(hours=2, minutes=25))

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
            self.assertEqual(60, len(flight.seats))

            seat_numbers = [seat.seat_number for seat in flight.seats]
            for row in range(1, 11):
                for letter in "ABCDEF":
                    self.assertTrue(f"{row}{letter}" in seat_numbers)

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

    def test_can_allocate_seat(self):
        create_test_passengers_on_flight(1)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layouts = session.query(AircraftLayout).all()

        apply_aircraft_layout(flight.id, aircraft_layouts[0].id)
        allocate_seat(flight.id, flight.passengers[0].id, "1A")

        with Session.begin() as session:
            seat = session.query(Seat).filter(Seat.seat_number == "1A").one()
            self.assertEqual(flight.passengers[0].id, seat.passenger_id)

    def test_cannot_allocate_seat_to_passenger_not_on_flight(self):
        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layouts = session.query(AircraftLayout).all()

        apply_aircraft_layout(flight.id, aircraft_layouts[0].id)

        with self.assertRaises(ValueError):
            allocate_seat(flight.id, 1, "1A")

    def test_cannot_allocate_non_existent_seat(self):
        create_test_passengers_on_flight(1)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layouts = session.query(AircraftLayout).all()

        apply_aircraft_layout(flight.id, aircraft_layouts[0].id)

        with self.assertRaises(ValueError):
            allocate_seat(flight.id, flight.passengers[0].id, "1000A")

    def test_cannot_allocate_seat_to_passenger_twice(self):
        create_test_passengers_on_flight(1)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layouts = session.query(AircraftLayout).all()

        apply_aircraft_layout(flight.id, aircraft_layouts[0].id)
        allocate_seat(flight.id, flight.passengers[0].id, "1A")

        with self.assertRaises(ValueError):
            allocate_seat(flight.id, flight.passengers[0].id, "1A")

    def test_cannot_allocate_previously_allocated_seat(self):
        create_test_passengers_on_flight(2)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layouts = session.query(AircraftLayout).all()

        apply_aircraft_layout(flight.id, aircraft_layouts[0].id)
        allocate_seat(flight.id, flight.passengers[0].id, "1A")

        with self.assertRaises(ValueError):
            allocate_seat(flight.id, flight.passengers[1].id, "1A")
