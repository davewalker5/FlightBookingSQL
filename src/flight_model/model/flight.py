import pytz
from sqlalchemy import Column, Integer, String, DateTime, Interval, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base


class Flight(Base):
    """
    Class representing a numbered flight for a named airline on a given date and at a given time
    """
    __tablename__ = "FLIGHTS"
    __table_args__ = (UniqueConstraint('number', 'departure_date', name='NUMBER_DEPARTURE_UX'),)

    #: Primary key
    id = Column(Integer, primary_key=True)
    #: Parent airline id
    airline_id = Column(Integer, ForeignKey("AIRLINES.id"))
    #: Id for the record containing details of the airport of embarkation
    embarkation_airport_id = Column(Integer, ForeignKey("AIRPORTS.id"))
    #: Id for the record containing details of the destination airport
    destination_airport_id = Column(Integer, ForeignKey("AIRPORTS.id"))
    #: Id for the aircraft layout related to this flight
    aircraft_layout_id = Column(Integer, ForeignKey("AIRCRAFT_LAYOUTS.id"))
    #: Flight number
    number = Column(String, nullable=False)
    #: Departure date and time (UTC)
    departure_date = Column(DateTime, nullable=False)
    #: Flight duration
    duration = Column(Interval, nullable=False)

    #: Parent airline instance
    airline = relationship("Airline", back_populates="flights", lazy="joined")
    #: Airport instance for the airport of embarkation
    embarkation_airport = relationship("Airport", foreign_keys=[embarkation_airport_id], lazy="joined")
    #: Airport instance for the destination airport
    destination_airport = relationship("Airport", foreign_keys=[destination_airport_id], lazy="joined")
    #: Aircraft layout associated with this flight
    aircraft_layout = relationship("AircraftLayout")
    #: Collection of passengers on this flight
    passengers = relationship("Passenger", secondary="FLIGHT_PASSENGERS", back_populates="flights", lazy="joined")
    #: Collection of seats associated with this flight
    seats = relationship("Seat", back_populates="flight", cascade="all, delete, delete-orphan", lazy="joined")

    @property
    def departs_utc(self):
        """
        Return the departure date as a timezone-aware UTC date and time (the date and time that's
        read from the database is a UTC date and time but is not timezone-aware)

        :return: The departure date and time as a UTC timezone-aware date and time
        """
        return pytz.UTC.localize(self.departure_date)

    @property
    def departs_localtime(self):
        """
        Return the departure date and time converted to localtime for the point of embarkation

        :return: The departure time converted to localtime for the point of embarkation
        """
        embarkation_timezone = pytz.timezone(self.embarkation_airport.timezone)
        return self.departs_utc.astimezone(embarkation_timezone)

    @property
    def arrives_localtime(self):
        """
        The arrival date and time converted to localtime for the destination

        :return: The arrival date and time converted to localtime for the destination
        """
        arrives_utc = self.departs_utc + self.duration
        destination_timezone = pytz.timezone(self.destination_airport.timezone)
        return arrives_utc.astimezone(destination_timezone)

    @property
    def formatted_duration(self):
        """
        Return a formatted string representing the flight duration

        :return: A string representing the flight duration in the format HH:MM
        """
        hours, remainder = divmod(self.duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return "{:0d}:{:02d}".format(int(hours), int(minutes))

    @property
    def capacity(self):
        """
        Seating capacity for the flight

        :return: The total number of seats on the flight or 0 if no layout has been applied
        """
        return len(self.seats) if self.seats else 0

    @property
    def passenger_count(self):
        """
        Return the number of passengers on the flight

        :return: The number of passengers or 0 if there are none
        """
        return len(self.passengers) if self.passengers else 0

    @property
    def available_capacity(self):
        """
        The number of available seats

        :return: The number of seats available on the flight once all the current passengers have been seated
        """
        capacity = self.capacity
        passenger_count = self.passenger_count
        return capacity - passenger_count if capacity >= passenger_count else 0

    def __repr__(self):
        return f"{type(self).__name__}(" \
               f"id={self.id}, " \
               f"airline_id={self.airline_id!r}, " \
               f"embarkation_airport_id={self.embarkation_airport_id!r}, " \
               f"destination_airport_id={self.destination_airport_id!r}, " \
               f"aircraft_layout_id={self.aircraft_layout_id!r}, " \
               f"number={self.number!r}," \
               f"departure_date={self.departure_date!r}," \
               f"duration={self.duration!r})"
