import unittest
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.flight_model.model import create_database, Session, Airport
from src.flight_model.logic import create_airport
from src.flight_model.logic import create_airline
from src.flight_model.logic import create_flight


class TestAirport(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_airport("LGW", "London Gatwick", "Europe/London")

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

    def test_cannot_delete_airport_in_use(self):
        create_airline("EasyJet")
        create_airport("RMU", "Murcia International Airport", "Europe/Madrid")
        create_flight("EasyJet", "LGW", "RMU", "U28549", "20/11/2021", "10:45", "2:25")
        with self.assertRaises(IntegrityError), Session.begin() as session:
            session.query(Airport).filter(Airport.code == "LGW").delete()

    def test_cannot_add_airport_with_duplicate_code(self):
        with self.assertRaises(ValueError):
            create_airport("LGW", "Name", "TZ")
