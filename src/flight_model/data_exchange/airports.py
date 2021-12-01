"""
Utilities for data exchange of airport data between the database and data files
"""

import json
import os
from ..model import get_data_path, Session, Airport


def import_airport_details():
    """
    Read the airport definition data file and create one airport record in the database for each airport. The
    data file is in JSON format in the data folder of the application
    """
    code_file = os.path.join(get_data_path(), "sample_data", "airports", "airports.json")
    with open(code_file, mode="rt", encoding="utf-8") as f:
        json_data = json.load(f)

    with Session.begin() as session:
        for airport_dict in json_data["airports"].values():
            airport = Airport(code=airport_dict["code"], name=airport_dict["name"], timezone=airport_dict["tz"])
            session.add(airport)
