from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base


class Airline(Base):
    """
    Class representing an airline
    """
    __tablename__ = "AIRLINES"
    __table_args__ = (UniqueConstraint('name', name='AIRLINE_NAME_UX'),)

    #: Primary key
    id = Column(Integer, primary_key=True)
    #: Airline name
    name = Column(String, nullable=False, unique=True)

    #: Flights associated with this airline
    flights = relationship("Flight", back_populates="airline", cascade="all, delete, delete-orphan")
    #: Aircraft layouts associated with this airline
    aircraft_layouts = relationship("AircraftLayout", back_populates="airline", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id}, name={self.name!r})"
