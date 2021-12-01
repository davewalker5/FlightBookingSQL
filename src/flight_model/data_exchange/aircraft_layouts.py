"""
Utilities for data exchange of aircraft layout data between the database and data files. The data files are in CSV
format in the data folder of the application

Available seating plans are read from CSV-formatted data files with a single row of column headers followed by one
row per aircraft row, each with the following columns:

+-------+------------------------------------------------------+
| Row   | The row number                                       |
+-------+------------------------------------------------------+
| Class | The seating class for the row e.g. Economy, Business |
+-------+------------------------------------------------------+
| Seats | A string of seat letters for each seat in the row    |
+-------+------------------------------------------------------+

For example, if row number 28 of a seating plan contains 6 economy class seats with the letters A-F, the corresponding
CSV row would be:

28,Economy,ABCDEF
"""

import csv
import os
import re
from ..model import get_data_path, Session, Airline, AircraftLayout, RowDefinition

ROW_NUMBER_COLUMN = 0
CLASS_COLUMN = 1
SEAT_LETTERS_COLUMN = 2


def get_layout_file_path(airline, aircraft, layout=None):
    """
    Construct the path to an aircraft layout file

    :param airline: Name of the airline
    :param aircraft: Name of the aircraft
    :param layout: Optional layout name
    """
    # Seating plan file names are airline_aircraft_layout.csv, where the layout is optional. Non-alphanumeric
    # characters are replaced with underscores
    file_name = "_".join([airline, aircraft, layout]) if layout is not None else "_".join([airline, aircraft])
    file_name = re.sub("\\W", "_", file_name).lower() + ".csv"
    return os.path.join(get_data_path(), "sample_data", "layouts", file_name)


def import_aircraft_layout(airline_name, aircraft, layout_name):
    """
    Read and return an empty seating plan

    :param airline_name: Name of the airline
    :param aircraft: Aircraft model e.g. A320
    :param layout_name: Optional airline-specific layout name
    """
    with Session.begin() as session:
        airline = session.query(Airline).filter(Airline.name == airline_name).one()
        aircraft_layout = AircraftLayout(airline=airline, aircraft=aircraft, name=layout_name)
        session.add(aircraft_layout)

        # Read the rows, throwing away the (mandatory) headers
        file_path = get_layout_file_path(airline_name, aircraft, layout_name)
        with open(file_path, mode="rt", encoding="utf-8") as f:
            # Initialise the CSV reader and skip the headers
            reader = csv.reader(f)
            next(reader, None)

            for row in reader:
                # Create a row definition and add it to the model
                row_definition = RowDefinition(number=row[ROW_NUMBER_COLUMN],
                                               seating_class=row[CLASS_COLUMN],
                                               seats=row[SEAT_LETTERS_COLUMN])
                aircraft_layout.row_definitions.append(row_definition)
                session.add(row_definition)
