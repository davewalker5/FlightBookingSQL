import unittest
from src.flight_model.model import create_database, Session, AircraftLayout
from src.flight_model.data_exchange import import_aircraft_layout_from_file
from tests.flight_model.utils import create_test_airline


class TestAircraftLayouts(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_test_airline("EasyJet")

    def test_import_layout(self):
        import_aircraft_layout_from_file("EasyJet", "A320", None)
        with Session.begin() as session:
            aircraft_layout = session.query(AircraftLayout).one()

            self.assertEqual("EasyJet", aircraft_layout.airline.name)
            self.assertEqual("A320", aircraft_layout.aircraft)
            self.assertIsNone(aircraft_layout.name)
            self.assertEqual(31, len(aircraft_layout.row_definitions))

            row_numbers = [definition.number for definition in aircraft_layout.row_definitions]
            for row in range(1, 11):
                self.assertTrue(row in row_numbers)
                self.assertEqual("ABCDEF", aircraft_layout.row_definitions[row - 1].seats)
