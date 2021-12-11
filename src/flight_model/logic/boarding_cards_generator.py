"""
This module defines a class that wraps the logic for generating boarding card files in a form that can either be
run in the foreground or on a background thread.

Plugins are used to generate boarding cards in different formats. Plugins capable of generating boarding cards should
extend the following entry point:

::

    flight_booking.card_generator_plugins

They should expose the following symbols:

+----------------+---------------------------------------------------------------------------------------------------+
| card_format    | String containing the format in which boarding card data is generated e.g. html, pdf, txt         |
+----------------+---------------------------------------------------------------------------------------------------+
| card_generator | Function that generates and returns boarding card data in the format indicated by the card_format |
+----------------+---------------------------------------------------------------------------------------------------+

The card_generator function receives a dictionary of properties, as follows:

+------------------+----------------------------------------------------------------------------------+
| gate             | The departure gate number                                                        |
+------------------+----------------------------------------------------------------------------------+
| airline          | The name of the airline                                                          |
+------------------+----------------------------------------------------------------------------------+
| embarkation_name | The name of the embarkation airport                                              |
+------------------+----------------------------------------------------------------------------------+
| embarkation      | 3-letter IATA code for the destination airport                                   |
+------------------+----------------------------------------------------------------------------------+
| departs          | Departure time (local) formatted using the 12-hour clock with an am or pm suffix |
+------------------+----------------------------------------------------------------------------------+
| destination_name | The name of the destination airport                                              |
+------------------+----------------------------------------------------------------------------------+
| destination      | 3-letter IATA code for the destination airport                                   |
+------------------+----------------------------------------------------------------------------------+
| arrives          | Arrival time (local) formatted using the 12-hour clock with an am or pm suffix   |
+------------------+----------------------------------------------------------------------------------+
| name             | The passenger name                                                               |
+------------------+----------------------------------------------------------------------------------+
| seat_number      | The seat number                                                                  |
+------------------+----------------------------------------------------------------------------------+
"""

import os
import re
import pkg_resources
import threading
from ..model import Session, Flight, get_data_path
from .exceptions import InvalidOperationError, MissingBoardingCardPluginError


# Set comprehension that uses pkg_resources to identify entry point objects
# for the boarding card printer. The load() method on these returns the module
card_printer_plugins = {
    entry_point.load()
    for entry_point
    in pkg_resources.iter_entry_points("flight_booking.card_generator_plugins")
}

# Build a dictionary of plugins that maps their format string to their callable
# card printer
card_generator_map = {
    module.card_format: module.card_generator
    for module in card_printer_plugins
}


class BoardingCardsGenerator(threading.Thread):
    def __init__(self, flight_id, card_format, gate):
        threading.Thread.__init__(self)

        if not gate:
            raise ValueError("Gate must be specified to print boarding cards")

        with Session.begin() as session:
            self._flight = session.query(Flight).get(flight_id)

        if not self._flight.seats:
            # An empty sequence or None will be falsy
            raise InvalidOperationError("Cannot print boarding cards if the flight has no aircraft layout")

        if not self._flight.passengers:
            raise InvalidOperationError("Cannot print boarding cards if the flight has no passengers")

        try:
            self._generator = card_generator_map[card_format]
        except KeyError as e:
            raise MissingBoardingCardPluginError(
                f"Boarding card plugin not registered for format {card_format}",
                card_format=card_format
            ) from e

        self._card_format = card_format
        self._gate = gate

    def generate_cards(self):
        """
        Generate boarding cards on the current thread
        """
        allocations = [(seat.seat_number, seat.passenger_id)
                       for seat in self._flight.seats
                       if seat.passenger_id is not None]

        for seat_number, passenger_id in allocations:
            # Construct the card details for this passenger and generate the card
            passengers = [passenger for passenger in self._flight.passengers if passenger.id == passenger_id]
            card_data = self._generator({
                "gate": self._gate,
                "airline": self._flight.airline.name,
                "embarkation_name": self._flight.embarkation_airport.name,
                "embarkation": self._flight.embarkation_airport.code,
                "departs": self._flight.departs_localtime.strftime("%I:%M %p"),
                "destination_name": self._flight.destination_airport.name,
                "destination": self._flight.destination_airport.code,
                "arrives": self._flight.arrives_localtime.strftime("%I:%M %p"),
                "name": passengers[0].name,
                "seat_number": seat_number
            })

            # Write the card to a file
            card_file_path = BoardingCardsGenerator.get_boarding_card_path(self._flight.number,
                                                                           seat_number,
                                                                           self._flight.departure_date,
                                                                           self._card_format)
            if isinstance(card_data, str):
                with open(card_file_path, mode="wt", encoding="utf-8") as f:
                    f.write(card_data)
            else:
                with open(card_file_path, mode="wb") as f:
                    f.write(card_data)

    def run(self, *args, **kwargs):
        """
        Generate boarding cards on a background thread

        :param args: Variable positional arguments
        :param kwargs: Variable keyword arguments
        """
        self.generate_cards()

    @staticmethod
    def get_boarding_card_path(flight_number, seat_number, departure_date, card_format):
        """
        Construct the path to a boarding card file

        :param flight_number: Flight number
        :param seat_number: Seat number
        :param departure_date: Departure date and time
        :param card_format: Boarding card format, used as the file extension
        :return:
        """
        # Boarding card file names are flight-number_seat-number_date.csv, with non-alphanumeric characters
        # replaced with underscores
        file_name = "_".join([flight_number, seat_number, departure_date.strftime("%Y%m%d")])
        file_name = re.sub("\\W", "_", file_name).lower()
        return os.path.join(BoardingCardsGenerator._get_boarding_card_folder(),
                            file_name.lower() + "." + card_format)

    @staticmethod
    def _get_boarding_card_folder():
        """
        Get the path to the folder where boarding card files are created and create it if it doesn't exist

        :returns: The boarding card folder path
        """
        card_folder = os.path.join(get_data_path(), "boarding_cards")
        if not os.path.exists(card_folder):
            os.makedirs(card_folder)

        return card_folder
