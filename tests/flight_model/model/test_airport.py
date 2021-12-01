import unittest
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.flight_model.model import create_database, Session, Airport
from tests.flight_model.model.utils import create_test_airport


class TestAirport(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_test_airport("LGW", "London Gatwick", "Europe/London")

    def test_can_add_airport(self):
        with Session.begin() as session:
            airport = session.query(Airport).filter(Airport.code == "LGW").one()
            self.assertEqual("LGW", airport.code)
            self.assertEqual("London Gatwick", airport.name)
            self.assertEqual("Europe/London", airport.timezone)

    def test_can_delete_airport(self):
        with Session.begin() as session:
            session.query(Airport).filter(Airport.code == "LGW").delete()

        with self.assertRaises(NoResultFound), Session.begin() as session:
            _ = session.query(Airport).filter(Airport.code == "LGW").one()

    def test_cannot_add_airport_with_duplicate_code(self):
        with self.assertRaises(IntegrityError):
            create_test_airport("LGW", "Name", "TZ")
