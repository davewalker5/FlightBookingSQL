from sqlalchemy import Column, Integer, String, UniqueConstraint
from .base import Base


class Airport(Base):
    """
    Class representing an airport
    """
    __tablename__ = "AIRPORTS"
    __table_args__ = (UniqueConstraint('code', name='AIRPORT_CODE_UX'),)

    #: Primary key
    id = Column(Integer, primary_key=True)
    #: 3-letter IATA airport code for the airport e.g. LGW
    code = Column(String, nullable=False, unique=True)
    #: Airport name e.g. London Gatwick
    name = Column(String, nullable=False)
    #: Timezone name e.g. Europe/London
    timezone = Column(String, nullable=False)

    def __repr__(self):
        return f"{type(self).__name__}(" \
               f"id={self.id}, " \
               f"code={self.code!r}, " \
               f"name={self.name!r}, " \
               f"timezone={self.timezone!r})"
