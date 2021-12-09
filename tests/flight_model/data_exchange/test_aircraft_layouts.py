import unittest
from src.flight_model.model import create_database
from src.flight_model.logic import create_airline
from src.flight_model.logic import list_layouts
from src.flight_model.data_exchange import import_aircraft_layout_from_file, import_aircraft_layout_from_stream, \
    get_layout_file_path


class TestAircraftLayouts(unittest.TestCase):
    def confirm_layout_properties(self, aircraft_layout):
        self.assertEqual("EasyJet", aircraft_layout.airline.name)
        self.assertEqual("A320", aircraft_layout.aircraft)
        self.assertEqual("", aircraft_layout.name)
        self.assertEqual(31, len(aircraft_layout.row_definitions))

        row_numbers = [definition.number for definition in aircraft_layout.row_definitions]
        for row in range(1, 11):
            self.assertTrue(row in row_numbers)
            self.assertEqual("ABCDEF", aircraft_layout.row_definitions[row - 1].seats)

    def setUp(self) -> None:
        create_database()
        create_airline("EasyJet")

    def test_can_import_layout_from_file(self):
        import_aircraft_layout_from_file("EasyJet", "A320", None)
        aircraft_layout = list_layouts(None)[0]
        self.confirm_layout_properties(aircraft_layout)

    def test_can_import_layout_from_text_stream(self):
        layout_file = get_layout_file_path("EasyJet", "A320", None)
        with open(layout_file, mode="rt", encoding="UTF-8") as f:
            import_aircraft_layout_from_stream("EasyJet", "A320", None, f)

        aircraft_layout = list_layouts(None)[0]
        self.confirm_layout_properties(aircraft_layout)

    def test_can_import_layout_from_binary_stream(self):
        layout_file = get_layout_file_path("EasyJet", "A320", None)
        with open(layout_file, mode="rb") as f:
            import_aircraft_layout_from_stream("EasyJet", "A320", None, f)

        aircraft_layout = list_layouts(None)[0]
        self.confirm_layout_properties(aircraft_layout)

    def test_cannot_import_duplicate_layout(self):
        import_aircraft_layout_from_file("EasyJet", "A320", None)
        with self.assertRaises(ValueError):
            import_aircraft_layout_from_file("EasyJet", "A320", None)
