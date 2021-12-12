import unittest
from src.flight_model.model import create_database, Session, Flight, AircraftLayout, Seat
from src.flight_model.logic import create_airport
from src.flight_model.logic import create_airline
from src.flight_model.logic import create_flight
from src.flight_model.logic import apply_aircraft_layout, allocate_seat, create_layout, add_row_to_layout
from tests.flight_model.utils import create_test_passengers_on_flight


class TestSeatAllocations(unittest.TestCase):
    def setUp(self) -> None:
        create_database()

        easyjet = create_airline("EasyJet")
        layout = create_layout(easyjet.id, "A321", "Neo")
        for row in range(1, 11):
            _ = add_row_to_layout(layout.id, row, "Economy", "ABC")

        layout = create_layout(easyjet.id, "A320", "1")
        _ = add_row_to_layout(layout.id, 1, "Economy", "ABCDEF")

        create_airport("LGW", "London Gatwick", "Europe/London")
        create_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_flight("EasyJet", "LGW", "RMU", "U28549", "20/11/2021", "10:45", "2:25")

    def test_can_allocate_seat(self):
        create_test_passengers_on_flight(1)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A321",
                        AircraftLayout.name == "Neo")\
                .one()

        apply_aircraft_layout(flight.id, aircraft_layout.id)
        allocate_seat(flight.id, flight.passengers[0].id, "1A")

        with Session.begin() as session:
            seat = session.query(Seat).filter(Seat.seat_number == "1A").one()
            self.assertEqual(flight.passengers[0].id, seat.passenger_id)

    def test_cannot_allocate_seat_to_passenger_not_on_flight(self):
        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A321",
                        AircraftLayout.name == "Neo")\
                .one()

        apply_aircraft_layout(flight.id, aircraft_layout.id)

        with self.assertRaises(ValueError):
            allocate_seat(flight.id, 1, "1A")

    def test_cannot_allocate_non_existent_seat(self):
        create_test_passengers_on_flight(1)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A321",
                        AircraftLayout.name == "Neo")\
                .one()

        apply_aircraft_layout(flight.id, aircraft_layout.id)

        with self.assertRaises(ValueError):
            allocate_seat(flight.id, flight.passengers[0].id, "1000A")

    def test_cannot_allocate_seat_with_no_layout(self):
        create_test_passengers_on_flight(1)

        with Session.begin() as session:
            flight = session.query(Flight).one()

        with self.assertRaises(ValueError):
            allocate_seat(flight.id, flight.passengers[0].id, "1000A")

    def test_cannot_allocate_seat_to_passenger_twice(self):
        create_test_passengers_on_flight(1)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A321",
                        AircraftLayout.name == "Neo")\
                .one()

        apply_aircraft_layout(flight.id, aircraft_layout.id)
        allocate_seat(flight.id, flight.passengers[0].id, "1A")

        with self.assertRaises(ValueError):
            allocate_seat(flight.id, flight.passengers[0].id, "1A")

    def test_cannot_allocate_previously_allocated_seat(self):
        create_test_passengers_on_flight(2)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A321",
                        AircraftLayout.name == "Neo")\
                .one()

        apply_aircraft_layout(flight.id, aircraft_layout.id)
        allocate_seat(flight.id, flight.passengers[0].id, "1A")

        with self.assertRaises(ValueError):
            allocate_seat(flight.id, flight.passengers[1].id, "1A")

    def test_applying_a_new_layout_copies_seat_allocations(self):
        create_test_passengers_on_flight(2)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A320",
                        AircraftLayout.name == "1")\
                .one()

        apply_aircraft_layout(flight.id, aircraft_layout.id)
        allocate_seat(flight.id, flight.passengers[0].id, "1A")

        with Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A321",
                        AircraftLayout.name == "Neo")\
                .one()

        apply_aircraft_layout(flight.id, aircraft_layout.id)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            self.assertEqual("1A", flight.passengers[0].seats[0].seat_number)

    def test_can_allocate_seat_if_not_in_new_layout(self):
        create_test_passengers_on_flight(2)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A320",
                        AircraftLayout.name == "1")\
                .one()

        apply_aircraft_layout(flight.id, aircraft_layout.id)
        allocate_seat(flight.id, flight.passengers[0].id, "1A")
        allocate_seat(flight.id, flight.passengers[1].id, "1D")

        with Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A321",
                        AircraftLayout.name == "Neo")\
                .one()

        apply_aircraft_layout(flight.id, aircraft_layout.id)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            self.assertEqual("1A", flight.passengers[0].seats[0].seat_number)
            self.assertEqual("1B", flight.passengers[1].seats[0].seat_number)

    def test_can_move_passenger(self):
        create_test_passengers_on_flight(1)

        with Session.begin() as session:
            flight = session.query(Flight).one()
            aircraft_layout = session.query(AircraftLayout) \
                .filter(AircraftLayout.airline_id == flight.airline.id,
                        AircraftLayout.aircraft == "A320",
                        AircraftLayout.name == "1")\
                .one()

        apply_aircraft_layout(flight.id, aircraft_layout.id)
        allocate_seat(flight.id, flight.passengers[0].id, "1A")
        allocate_seat(flight.id, flight.passengers[0].id, "1B")

        with Session.begin() as session:
            seat = session.query(Seat).filter(Seat.seat_number == "1A").one()
            self.assertIsNone(seat.passenger_id)

            seat = session.query(Seat).filter(Seat.seat_number == "1B").one()
            self.assertIsNotNone(seat.passenger_id)
