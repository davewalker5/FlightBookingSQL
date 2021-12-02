from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base


class Passenger(Base):
    """
    Class representing a passenger
    """
    __tablename__ = "PASSENGERS"

    #: Primary key
    id = Column(Integer, primary_key=True)
    #: Passenger name
    name = Column(String, nullable=False)
    #: Gender
    gender = Column(String, nullable=False)
    #: Date of birth
    dob = Column(Date, nullable=False)
    #: Nationality
    nationality = Column(String, nullable=False)
    #: Country of residence
    residency = Column(String, nullable=False)
    #: Passport number
    passport_number = Column(String, nullable=False, unique=True)

    #: Collection of flights for this passenger
    flights = relationship("Flight", secondary="FLIGHT_PASSENGERS", back_populates="passengers")
    #: Collection of seat allocations for this passenger
    seats = relationship("Seat", back_populates="passenger", lazy="joined")

    __tableargs__ = (
        CheckConstraint(gender.in_(["M", "F"])),
        UniqueConstraint('passport_number', name='PASSPORT_NUMBER_UX')
    )

    def __repr__(self):
        return f"{type(self).__name__}(" \
               f"id={self.id}, " \
               f"name={self.name!r}, " \
               f"dob={self.dob!r}, " \
               f"nationality={self.nationality!r}, " \
               f"residency={self.residency!r}," \
               f"passport_number={self.passport_number!r})"


class FlightPassenger(Base):
    """
    Many-to-many mapping between flights and passengers
    """
    __tablename__ = "FLIGHT_PASSENGERS"

    #: ID for the related flight
    flight_id = Column(Integer, ForeignKey("FLIGHTS.id"), primary_key=True)
    #: ID for the related passenger
    passenger_id = Column(Integer, ForeignKey("PASSENGERS.id"), primary_key=True)

    def __repr__(self):
        return f"{type(self).__name__}(" \
               f"flight_id={self.flight_id!r}, " \
               f"passenger_id={self.passenger_id!r})"
