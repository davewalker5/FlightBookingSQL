from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Seat(Base):
    """
    Class representing a physical seat on a flight, that can be allocated to a passenger
    """
    __tablename__ = "SEATS"

    # Applying new seating layouts to flights involves removing the existing seats and creating
    # new ones within the same session so that errors will rollback both operations. This constraint
    # prevents that process from working
    # __table_args__ = (UniqueConstraint('flight_id', 'seat_number', name='FLIGHT_SEAT_UX'),)

    #: Primary key
    id = Column(Integer, primary_key=True)
    #: Parent flight
    flight_id = Column(Integer, ForeignKey("FLIGHTS.id"))
    #: Id for the passenger allocated to this seat
    passenger_id = Column(Integer, ForeignKey("PASSENGERS.id"), nullable=True)
    #: Seat number e.g. 12A
    seat_number = Column(String, nullable=False)

    #: Parent flight instance
    flight = relationship("Flight", back_populates="seats")
    #: Associated passenger instance
    passenger = relationship("Passenger", back_populates="seats")

    def __repr__(self):
        return f"{type(self).__name__}(" \
               f"id={self.id}, " \
               f"flight_id={self.flight_id!r}, " \
               f"passenger_id={self.passenger_id!r}, " \
               f"seat_number={self.seat_number!r})"
