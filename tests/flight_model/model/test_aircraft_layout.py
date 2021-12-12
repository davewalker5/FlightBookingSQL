import unittest
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.flight_model.model import create_database, Session, Airline, AircraftLayout, RowDefinition
from src.flight_model.logic import create_airline
from src.flight_model.logic import create_airport
from src.flight_model.logic import create_flight
from tests.flight_model.utils import create_test_layout, create_test_seating_plan


class TestAircraftLayout(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_airline("EasyJet")
        create_test_layout("EasyJet", "A321", "Neo", 10, "ABCDEF")

    def test_can_add_layout(self):
        with Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout).one()

            self.assertEqual("EasyJet", aircraft_layout.airline.name)
            self.assertEqual("A321", aircraft_layout.aircraft)
            self.assertEqual("Neo", aircraft_layout.name)
            self.assertEqual(10, len(aircraft_layout.row_definitions))

            row_numbers = [definition.number for definition in aircraft_layout.row_definitions]
            for row in range(1, 11):
                self.assertTrue(row in row_numbers)
                self.assertEqual("ABCDEF", aircraft_layout.row_definitions[row - 1].seats)

    def test_cannot_update_layout_to_create_duplicate(self):
        create_test_layout("EasyJet", "A320", "1", 10, "ABCDEF")
        with self.assertRaises(IntegrityError), Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout).filter(AircraftLayout.aircraft == "A320").one()
            aircraft_layout.aircraft = "A321"
            aircraft_layout.name = "Neo"

    def test_can_delete_layout(self):
        with Session.begin() as session:
            # Note that delete won't cascade if we use delete() on the query object. Get the
            # layout object and delete it to cause the cascade that will delete row definitions
            aircraft_layout = session.query(AircraftLayout).one()
            session.delete(aircraft_layout)

        with self.assertRaises(NoResultFound), Session.begin() as session:
            session.query(AircraftLayout).one()

        with self.assertRaises(NoResultFound), Session.begin() as session:
            session.query(RowDefinition).one()

    def test_cannot_delete_layout_in_use(self):
        create_airport("LGW", "London Gatwick", "Europe/London")
        create_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_flight("EasyJet", "LGW", "RMU", "U28549", "20/11/2021", "10:45", "2:25")
        create_test_seating_plan("U28549", "A321", "Neo")
        with self.assertRaises(IntegrityError), Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout).one()
            session.delete(aircraft_layout)

    def test_related_layouts_returned_with_airline(self):
        with Session.begin() as session:
            airline = session.query(Airline).filter(Airline.name == "EasyJet").one()
            self.assertEqual(1, len(airline.aircraft_layouts))

    def test_related_layouts_deleted_with_airline(self):
        with Session.begin() as session:
            # Note that delete won't cascade if we use delete() on the query object. Get the
            # airline object and delete it to cause the cascade that will delete related records
            airline = session.query(Airline).filter(Airline.name == "EasyJet").one()
            session.delete(airline)

        with self.assertRaises(NoResultFound), Session.begin() as session:
            session.query(AircraftLayout).one()

        with self.assertRaises(NoResultFound), Session.begin() as session:
            session.query(RowDefinition).one()

    def test_can_add_same_layout_for_different_airline(self):
        create_airline("British Airways")
        create_test_layout("British Airways", "A321", "Neo", 10, "ABCDEF")

        with Session.begin() as session:
            aircraft_layouts = session.query(AircraftLayout).all()
            self.assertEqual(2, len(aircraft_layouts))

    def test_cannot_add_duplicate_layout(self):
        with self.assertRaises(IntegrityError):
            create_test_layout("EasyJet", "A321", "Neo", 10, "ABCDEF")

    def test_cannot_add_duplicate_row(self):
        with self.assertRaises(IntegrityError), Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout).one()
            row_definition = RowDefinition(aircraft_layout_id=aircraft_layout.id,
                                           number=1,
                                           seating_class="Economy",
                                           seats="ABCDEF")
            session.add(row_definition)

    def test_can_delete_row(self):
        with Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout).one()
            row_to_delete = aircraft_layout.row_definitions[4]
            del aircraft_layout.row_definitions[4]
            session.delete(row_to_delete)

        with Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout).one()
            row_numbers = [r.number for r in aircraft_layout.row_definitions]
            self.assertFalse(5 in row_numbers)
            self.assertEqual(9, len(aircraft_layout.row_definitions))

    def test_cannot_add_row_with_blank_seats(self):
        with self.assertRaises(IntegrityError), Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout).one()
            row_definition = RowDefinition(aircraft_layout_id=aircraft_layout.id,
                                           number=100,
                                           seating_class="Economy",
                                           seats="")
            session.add(row_definition)

    def test_cannot_add_row_with_whitespace_seats(self):
        with self.assertRaises(IntegrityError), Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout).one()
            row_definition = RowDefinition(aircraft_layout_id=aircraft_layout.id,
                                           number=100,
                                           seating_class="Economy",
                                           seats="         ")
            session.add(row_definition)

    def test_cannot_add_row_with_blank_class(self):
        with self.assertRaises(IntegrityError), Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout).one()
            row_definition = RowDefinition(aircraft_layout_id=aircraft_layout.id,
                                           number=100,
                                           seating_class="",
                                           seats="ABCDEF")
            session.add(row_definition)

    def test_cannot_add_row_with_whitespace_class(self):
        with self.assertRaises(IntegrityError), Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout).one()
            row_definition = RowDefinition(aircraft_layout_id=aircraft_layout.id,
                                           number=100,
                                           seating_class="       ",
                                           seats="ABCDEF")
            session.add(row_definition)

    def test_cannot_update_seats_to_empty(self):
        with self.assertRaises(IntegrityError), Session.begin() as session:
            row_definition = session.query(RowDefinition).all()[0]
            row_definition.seats = ""

    def test_cannot_update_seats_to_whitespace(self):
        with self.assertRaises(IntegrityError), Session.begin() as session:
            row_definition = session.query(RowDefinition).all()[0]
            row_definition.seats = "       "

    def test_cannot_update_class_to_empty(self):
        with self.assertRaises(IntegrityError), Session.begin() as session:
            row_definition = session.query(RowDefinition).all()[0]
            row_definition.seating_class = ""

    def test_cannot_update_class_to_whitespace(self):
        with self.assertRaises(IntegrityError), Session.begin() as session:
            row_definition = session.query(RowDefinition).all()[0]
            row_definition.seating_class = "       "
