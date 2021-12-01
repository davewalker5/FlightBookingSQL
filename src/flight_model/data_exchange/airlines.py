"""
Utilities for data exchange of airline data between the database and data files
"""

import json
import os
from ..model import get_data_path, Session, Airline


def import_airline_details():
    """
    Read the airport definition data file and create one airport record in the database for each airport. The
    data file is in JSON format in the data folder of the application
    """
    code_file = os.path.join(get_data_path(), "sample_data", "airlines", "airlines.json")
    with open(code_file, mode="rt", encoding="utf-8") as f:
        json_data = json.load(f)

    with Session.begin() as session:
        for airline_name in json_data:
            airline = Airline(name=airline_name)
            session.add(airline)
