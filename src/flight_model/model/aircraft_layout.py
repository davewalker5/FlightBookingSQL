"""
Declare the model classes relating to aircraft layouts. Aircraft layouts define the physical layout of an aircraft
in terms of the number of rows of seats and the seat letters in each row. They act as templates for creation of a set
of seats on a flight
"""

from sqlalchemy import Column, ForeignKey, UniqueConstraint, Integer, String, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base


class AircraftLayout(Base):
    """
    Aircraft layout, based on the airline, aircraft model and layout name
    """
    __tablename__ = "AIRCRAFT_LAYOUTS"
    __table_args__ = (UniqueConstraint('airline_id', 'aircraft', 'name', name='AIRLINE_AIRCRAFT_LAYOUT_UX'),)

    #: Primary key
    id = Column(Integer, primary_key=True)
    #: Id for the related airline
    airline_id = Column(Integer, ForeignKey("AIRLINES.id"))
    #: Aircraft model e.g. A321
    aircraft = Column(String, nullable=False)
    #: Layout name e.g. Neo
    name = Column(String, nullable=False)
    #: Related airline instance
    airline = relationship("Airline", back_populates="aircraft_layouts")
    #: Row definitions associated with this layout
    row_definitions = relationship("RowDefinition",
                                   back_populates="aircraft_layout",
                                   cascade="all, delete, delete-orphan",
                                   lazy="joined")

    @property
    def capacity(self):
        return sum([len(row.seats) for row in self.row_definitions])

    def __repr__(self):
        return f"{type(self).__name__}(" \
               f"id={self.id}, " \
               f"airline_id={self.airline_id}, " \
               f"aircraft={self.aircraft!r}, " \
               f"name={self.name!r})"


class RowDefinition(Base):
    """
    Row definition for an aircraft layout, giving the row number and the seat letters in that row
    """
    __tablename__ = "ROW_DEFINITIONS"

    #: Primary key
    id = Column(Integer, primary_key=True)
    #: Id for the parent aircraft layout
    aircraft_layout_id = Column(Integer, ForeignKey("AIRCRAFT_LAYOUTS.id"))
    #: Row number
    number = Column(Integer, nullable=False)
    #: LClass of seating e.g. Business, Economy
    seating_class = Column(String, nullable=False)
    #: A string of letters, one for each seat in the row e.g. ABCDEF
    seats = Column(String, nullable=False)
    #: Parent aircraft layout instance
    aircraft_layout = relationship("AircraftLayout", back_populates="row_definitions")

    __table_args__ = (
        UniqueConstraint('aircraft_layout_id', 'number', name='AIRLINE_AIRCRAFT_LAYOUT_UX'),
        CheckConstraint("LENGTH(TRIM(seating_class)) > 0"),
        CheckConstraint("LENGTH(TRIM(seats)) > 0")
    )

    def __repr__(self):
        return f"{type(self).__name__}(" \
               f"id={self.id}, " \
               f"aircraft_layout_id={self.aircraft_layout_id}" \
               f"number={self.number!r}, " \
               f"seating_class={self.seating_class!r}, " \
               f"seats={self.seats!r})"
