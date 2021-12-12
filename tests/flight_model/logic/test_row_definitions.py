import unittest
from sqlalchemy.exc import IntegrityError
from src.flight_model.model import create_database, Session, AircraftLayout
from src.flight_model.logic import create_airline
from src.flight_model.logic import list_layouts, create_layout, add_row_to_layout, get_layout, delete_row_from_layout, \
    update_row_definition


class TestRowDefinitions(unittest.TestCase):
    def setUp(self) -> None:
        create_database()

        easyjet = create_airline("EasyJet")
        layout = create_layout(easyjet.id, "A321", "Neo")
        for row in range(1, 11):
            _ = add_row_to_layout(layout.id, row, "Economy", "ABC")

    def test_can_update_row_definition(self):
        layout = list_layouts()[0]
        update_row_definition(layout.id, 1, "Business", "XYZ")
        layout = get_layout(layout.id)
        updated = [row for row in layout.row_definitions if row.number == 1][0]
        self.assertEqual("Business", updated.seating_class)
        self.assertEqual("XYZ", updated.seats)

    def test_cannot_add_duplicate_row(self):
        with self.assertRaises(IntegrityError), Session.begin() as session:
            layout = session.query(AircraftLayout).first()
            _ = add_row_to_layout(layout.id, 1, "Economy", "ABCDEF")

    def test_can_delete_row(self):
        layout = list_layouts()[0]
        delete_row_from_layout(layout.id, 5)
        updated = get_layout(layout.id)
        row_numbers = [r.number for r in updated.row_definitions]
        self.assertFalse(5 in row_numbers)
        self.assertEqual(9, len(updated.row_definitions))

    def test_cannot_delete_missing_row(self):
        layout = list_layouts()[0]
        with self.assertRaises(ValueError):
            delete_row_from_layout(layout.id, 1000)

    def test_cannot_delete_row_from_missing_layout(self):
        with self.assertRaises(ValueError):
            delete_row_from_layout(-1, 1)

    def test_cannot_add_row_with_blank_seats(self):
        layout = list_layouts()[0]
        with self.assertRaises(IntegrityError):
            add_row_to_layout(layout.id, 100, "Economy", "")

    def test_cannot_add_row_with_whitespace_seats(self):
        layout = list_layouts()[0]
        with self.assertRaises(IntegrityError):
            add_row_to_layout(layout.id, 100, "Economy", "         ")

    def test_cannot_add_row_with_blank_class(self):
        layout = list_layouts()[0]
        with self.assertRaises(IntegrityError):
            add_row_to_layout(layout.id, 100, "", "ABCDEF")

    def test_cannot_add_row_with_whitespace_class(self):
        layout = list_layouts()[0]
        with self.assertRaises(IntegrityError):
            add_row_to_layout(layout.id, 100, "        ", "ABCDEF")

    def test_cannot_update_row_definition_for_missing_layout(self):
        with self.assertRaises(ValueError):
            update_row_definition(-1, 1, "Business", "XYZ")

    def test_cannot_update_missing_row_definition(self):
        layout = list_layouts()[0]
        with self.assertRaises(ValueError):
            update_row_definition(layout.id, -1, "Business", "XYZ")

    def test_cannot_update_seats_to_empty(self):
        layout = list_layouts()[0]
        with self.assertRaises(ValueError):
            update_row_definition(layout.id, 1, "Business", "")

    def test_cannot_update_seats_to_whitespace(self):
        layout = list_layouts()[0]
        with self.assertRaises(ValueError):
            update_row_definition(layout.id, 1, "Business", "        ")

    def test_cannot_update_class_to_empty(self):
        layout = list_layouts()[0]
        with self.assertRaises(ValueError):
            update_row_definition(layout.id, 1, "Business", "")

    def test_cannot_update_class_to_whitespace(self):
        layout = list_layouts()[0]
        with self.assertRaises(ValueError):
            update_row_definition(layout.id, 1, "Business", "       ")
