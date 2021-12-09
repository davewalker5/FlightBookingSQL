import datetime
import unittest
from sqlalchemy.exc import NoResultFound
from src.flight_model.model import create_database, Session, Passenger
from src.flight_model.logic import create_passenger


class TestPassenger(unittest.TestCase):
    def setUp(self) -> None:
        create_database()
        create_passenger("Some Passenger", "F", datetime.date(1970, 2, 1), "United Kingdom", "England", "1234567890")

    def test_can_add_passenger(self):
        with Session.begin() as session:
            passenger = session.query(Passenger).filter(Passenger.passport_number == "1234567890").one()
            self.assertEqual("Some Passenger", passenger.name)
            self.assertEqual(datetime.date(1970, 2, 1), passenger.dob)
            self.assertEqual("United Kingdom", passenger.nationality)
            self.assertEqual("England", passenger.residency)

    def test_can_delete_passenger(self):
        with Session.begin() as session:
            session.query(Passenger).filter(Passenger.passport_number == "1234567890").delete()

        with self.assertRaises(NoResultFound), Session.begin() as session:
            _ = session.query(Passenger).filter(Passenger.passport_number == "1234567890").one()

    def test_can_add_passenger_with_different_passport_number(self):
        create_passenger("Some Other Passenger",
                         "F",
                         datetime.date(1980, 1, 2),
                         "España",
                         "España",
                         "0987654321")

        with Session.begin() as session:
            passengers = session.query(Passenger).all()
            self.assertEqual(2, len(passengers))

    def test_cannot_add_passenger_with_duplicate_passport_number(self):
        with self.assertRaises(ValueError):
            create_passenger("Some Other Passenger",
                             "F",
                             datetime.date(1980, 1, 2),
                             "España",
                             "España",
                             "1234567890")

    def test_can_add_male_passenger(self):
        create_passenger("Some Other Passenger",
                         "M",
                         datetime.date(1980, 1, 2),
                         "España",
                         "España",
                         "5432167890")

        with Session.begin() as session:
            _ = session.query(Passenger).filter(Passenger.passport_number == "5432167890").one()

    def test_can_add_female_passenger(self):
        create_passenger("Some Other Passenger",
                         "F",
                         datetime.date(1980, 1, 2),
                         "España",
                         "España",
                         "5432167890")

        with Session.begin() as session:
            _ = session.query(Passenger).filter(Passenger.passport_number == "5432167890").one()

    def test_cannot_add_passenger_with_invalid_gender(self):
        with self.assertRaises(ValueError):
            create_passenger("Some Other Passenger",
                             "Not a valid gender",
                             datetime.date(1980, 1, 2),
                             "España",
                             "España",
                             "5432167890")
