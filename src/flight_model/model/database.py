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
    Return the default path to the database file

    :return: The path to the database file
    """
    return os.path.join(get_data_path(), "airline.db")


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


Engine = _create_engine()
Session = sessionmaker(Engine, expire_on_commit=False)
