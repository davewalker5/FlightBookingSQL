"""
Boarding card printing business logic.

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


def _get_boarding_card_path(flight_number, seat_number, departure_date, card_format):
    """
    Construct the path to a boarding card file

    :param flight_number: Flight number
    :param seat_number: Seat number
    :param departure_date: Departure date and time
    :param card_format: Boarding card format, used as the file extension
    :return:
    """
    # Boarding card file names are flight-number_seat-number_date.csv
    card_folder = os.path.join(get_data_path(), "boarding_cards")
    file_name = "_".join([flight_number, seat_number, departure_date.strftime("%Y%m%d")])

    # Replace non-alphanumeric characters with underscores
    file_name = re.sub("\\W", "_", file_name).lower()
    return os.path.join(card_folder, file_name.lower() + "." + card_format)


def generate_boarding_cards(flight_id, card_format, gate):
    """
    Generate boarding cards in the specified format

    :param flight_id: ID for the flight for which to generate boarding cards
    :param card_format: The format for the generated card data file
    :param gate: The gate number the flight will depart from
    :raises ValueError: If the gate is None or blank
    :raises InvalidOperationError: If there is no aircraft layout
    :raises MissingBoardingCardPluginError: If there is no plugin available for the requested format
    """
    if not gate:
        raise ValueError("Gate must be specified to print boarding cards")

    with Session.begin() as session:
        flight = session.query(Flight).get(flight_id)

    if not flight.seats:
        # An empty sequence or None will be falsy
        raise InvalidOperationError("Cannot print boarding cards if the flight has no seat allocations")

    try:
        generator = card_generator_map[card_format]
    except KeyError as e:
        raise MissingBoardingCardPluginError(
            f"Boarding card plugin not registered for format {card_format}",
            card_format=card_format
        ) from e

    allocations = [(seat.seat_number, seat.passenger_id)
                   for seat in flight.seats
                   if seat.passenger_id is not None]

    for seat_number, passenger_id in allocations:
        # Construct the card details for this passenger and generate the card
        passengers = [passenger for passenger in flight.passengers if passenger.id == passenger_id]
        card_data = generator({
            "gate": gate,
            "airline": flight.airline.name,
            "embarkation_name": flight.embarkation_airport.name,
            "embarkation": flight.embarkation_airport.code,
            "departs": flight.departs_localtime.strftime("%I:%M %p"),
            "destination_name": flight.destination_airport.name,
            "destination": flight.destination_airport.code,
            "arrives": flight.arrives_localtime.strftime("%I:%M %p"),
            "name": passengers[0].name,
            "seat_number": seat_number
        })

        # Write the card to a file
        card_file_path = _get_boarding_card_path(flight.number, seat_number, flight.departure_date, card_format)
        if isinstance(card_data, str):
            with open(card_file_path, mode="wt", encoding="utf-8") as f:
                f.write(card_data)
        else:
            with open(card_file_path, mode="wb") as f:
                f.write(card_data)
