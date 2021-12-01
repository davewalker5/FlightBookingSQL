import unittest
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.flight_model.model import create_database, Session, Airline, AircraftLayout, RowDefinition
from tests.flight_model.model.utils import create_test_airline, create_test_layout


class TestAircraftLayout(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_test_airline("EasyJet")
        create_test_layout("EasyJet", "A321", "Neo", 10, "ABCDEF")

    def test_can_add_layout(self):
        with Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout)\
                .filter(AircraftLayout.aircraft == "A321",
                        AircraftLayout.name == "Neo")\
                .one()

            self.assertEqual("EasyJet", aircraft_layout.airline.name)
            self.assertEqual("A321", aircraft_layout.aircraft)
            self.assertEqual("Neo", aircraft_layout.name)
            self.assertEqual(10, len(aircraft_layout.row_definitions))

            row_numbers = [definition.number for definition in aircraft_layout.row_definitions]
            for row in range(1, 11):
                self.assertTrue(row in row_numbers)
                self.assertEqual("ABCDEF", aircraft_layout.row_definitions[row - 1].seats)

    def test_can_delete_layout(self):
        with Session.begin() as session:
            # Note that delete won't cascade if we use delete() on the query object. Get the
            # layout object and delete it to cause the cascade that will delete row definitions
            aircraft_layout = session.query(AircraftLayout)\
                .filter(AircraftLayout.aircraft == "A321",
                        AircraftLayout.name == "Neo")\
                .one()
            session.delete(aircraft_layout)

        with self.assertRaises(NoResultFound), Session.begin() as session:
            session.query(AircraftLayout).one()

        with self.assertRaises(NoResultFound), Session.begin() as session:
            session.query(RowDefinition).one()

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
        create_test_airline("British Airways")
        create_test_layout("British Airways", "A321", "Neo", 10, "ABCDEF")

        with Session.begin() as session:
            aircraft_layouts = session.query(AircraftLayout).all()
            self.assertEqual(2, len(aircraft_layouts))

    def test_cannot_add_duplicate_layout(self):
        with self.assertRaises(IntegrityError):
            create_test_layout("EasyJet", "A321", "Neo", 10, "ABCDEF")
