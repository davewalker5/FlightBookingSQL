import datetime
import unittest
from sqlalchemy.orm import joinedload
from src.flight_model.model import create_database, Session, Flight, AircraftLayout, Passenger
from src.flight_model.logic import apply_aircraft_layout
from tests.flight_model.model.utils import create_test_airline, create_test_flight, create_test_layout, \
    create_test_airport


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
            print(flight)

            self.assertEqual("A321", flight.aircraft_layout.aircraft)
            self.assertEqual("Neo", flight.aircraft_layout.name)
            self.assertEqual(60, len(flight.seats))

            seat_numbers = [seat.seat_number for seat in flight.seats]
            for row in range(1, 11):
                for letter in "ABCDEF":
                    self.assertTrue(f"{row}{letter}" in seat_numbers)

    def test_cannot_apply_aircraft_layout_with_insufficient_capacity(self):
        with Session.begin() as session:
            # Add some passengers to the flight
            flight = session.query(Flight).one()
            for i in range(20):
                passenger = Passenger(name=f"Passenger {i}",
                                      gender="M",
                                      dob=datetime.datetime(1970, 1, 1).date(),
                                      nationality="UK",
                                      residency="UK",
                                      passport_number=str(i))
                flight.passengers.append(passenger)
                session.add(passenger)

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
