"""
Row definition business logic
"""

from sqlalchemy.exc import IntegrityError, NoResultFound
from ..model import Session, AircraftLayout, RowDefinition


def add_row_to_layout(aircraft_layout_id, row_number, seating_class, seat_letters):
    """
    Add a row definition to an existing aircraft layout

    :param aircraft_layout_id: ID for the aircraft layout to add to
    :param row_number: Row number
    :param seating_class: Seating class for the row
    :param seat_letters: String of seat letters for the row e.g. ABCDEF
    """
    with Session.begin() as session:
        row_definition = RowDefinition(aircraft_layout_id=aircraft_layout_id,
                                       number=row_number,
                                       seating_class=seating_class,
                                       seats=seat_letters)
        session.add(row_definition)

    return row_definition


def delete_row_from_layout(layout_id, row_number):
    """
    Delete the row with the specified number from the specified layout

    :param layout_id: ID of the aircraft layout from which to delete a row
    :param row_number: Row number to delete
    :raises ValueError: If the layout or row don't exist
    """
    try:
        with Session.begin() as session:
            row_definition = session.query(RowDefinition)\
                .filter(RowDefinition.aircraft_layout_id == layout_id,
                        RowDefinition.number == row_number)\
                .one()
            session.delete(row_definition)
    except NoResultFound as e:
        raise ValueError("Aircraft layout or row number not found") from e


def update_row_definition(layout_id, row_number, seating_class, seat_letters):
    """
    Update the details for a row definition

    :param layout_id: ID of the aircraft layout containing the row to update
    :param row_number: Row number to update
    :param seating_class: New seating class
    :param seat_letters: New seat letters
    :raises ValueError: If the new details are invalid or the row definition doesn't exist
    """
    try:
        with Session.begin() as session:
            layout = session.query(AircraftLayout).get(layout_id)
            if layout is None:
                raise ValueError("Aircraft layout not found")

            row_definitions = [row for row in layout.row_definitions if row.number == row_number]
            if not row_definitions:
                raise ValueError("Row number not found")

            row_definitions[0].seating_class = seating_class
            row_definitions[0].seats = seat_letters
    except IntegrityError as e:
        raise ValueError("Seat letters and the seating class cannot be empty") from e
