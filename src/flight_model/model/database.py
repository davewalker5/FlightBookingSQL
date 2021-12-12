"""
Declare methods and module-level variables for creating a SQLite database and establishing a session. The following
module-level variables are defined:

+----------+-----------------------------------------------------------------------------+
| **Name** | **Comments**                                                                |
+----------+-----------------------------------------------------------------------------+
| Engine   | Instance of the SQLAlchemy Engine class used for connection management      |
+----------+-----------------------------------------------------------------------------+
| Session  | Definition of the Session class returned by the sessionmaker for the Engine |
+----------+-----------------------------------------------------------------------------+
"""

import os
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from .utils import get_data_path
from .base import Base


def _get_db_path():
    """
    Return the path to the database file. If the environment variable FLIGHT_BOOKING_DB is set, this will be used
    as the path to the SQLite database file. If not, then the default "development" database file, in the
    applications data folder, is  used.

    :return: The path to the database file
    """
    db_path = os.environ["FLIGHT_BOOKING_DB"] if "FLIGHT_BOOKING_DB" in os.environ else None
    if not db_path:
        db_path = os.path.join(get_data_path(), "flight_booking_dev.db")
    return db_path


def _delete_db():
    """
    Remove the database file at the default path
    """
    db_path = _get_db_path()
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass


def _create_engine():
    """
    Create a SQLAlchemy engine for the Flight Booking SQLite database

    :return: Instance of the SQLAlchemy Engine class
    """
    return db.create_engine(f"sqlite:///{_get_db_path()}", echo=False)


def create_database():
    """
    Delete and re-create the Flight Booking SQLite database
    """
    _delete_db()
    engine = _create_engine()
    Base.metadata.create_all(engine)


#: Instance of the SQLAlchemy database engine
Engine = _create_engine()

#: Session class for the engine, used  to create session instances
Session = sessionmaker(Engine, expire_on_commit=False)


@db.event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _):
    """
    Intercept connection events for the database engine and ensure foreign keys are enabled. From the SQLAlchemy
    SQLite documentation:

    "SQLite supports FOREIGN KEY syntax when emitting CREATE statements for tables, however by default these
    constraints have no effect on the operation of the table" and, aside from pre-requisites concerning the SQLite
    version and how it's been compiled, "The PRAGMA foreign_keys = ON statement must be emitted on all connections
    before use – including the initial call to MetaData.create_all()"

    :param dbapi_connection:
    :param _:
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
