"""
The layouts blueprint supplies view functions and templates for aircraft layout management
"""

from flask import Blueprint, render_template, redirect, request
from flight_model.logic import get_flight
from flight_model.logic import list_airlines
from flight_model.logic import list_layouts, apply_aircraft_layout, get_layout, delete_layout, update_layout
from flight_model.logic import delete_row_from_layout, update_row_definition
from flight_model.data_exchange import import_aircraft_layout_from_stream


layouts_bp = Blueprint("layouts", __name__, template_folder='templates')


def _render_layout_selection_page(flight_id, error):
    """
    Helper to render the aircraft layout selection page

    :param flight_id: The ID of the flight record
    :param error: Error message to display on the page or None
    :return: The rendered layout selection template
    """
    # Get the flight, airline and, if there's a seating plan on the flight, the aircraft layout
    flight = get_flight(flight_id)
    airline_id = flight.airline_id
    aircraft_layout_id = flight.aircraft_layout_id if flight.aircraft_layout_id else 0

    return render_template("layouts/select.html",
                           flight_number=flight.number,
                           layouts=list_layouts(airline_id),
                           current_layout_id=aircraft_layout_id,
                           select_enabled=True,
                           error=error)


def _render_layout_addition_page(error):
    """
    Helper to render the aircraft layout addition page

    :param error: Error message to display on the page or None
    :return: The rendered aircraft layout addition template
    """
    return render_template("layouts/add.html",
                           airlines=list_airlines(),
                           error=error)


def _render_layout_editing_page(layout_id, error):
    """
    Helper to render the aircraft layout editing page

    :param layout_id: ID for the aircraft layout to edit
    :param error: Error message to display on the page or None
    :return: The rendered aircraft layout editing template
    """
    return render_template("layouts/edit.html",
                           layout=get_layout(layout_id),
                           error=error)


def _render_layout_deletion_page(layout_id, error):
    """
    Helper to render the aircraft layout deletion page

    :param layout_id: ID for the aircraft layout to delete
    :param error: Error message to display on the page or None
    :return: The rendered airport deletion template
    """
    return render_template("layouts/delete.html",
                           layouts=[get_layout(layout_id)],
                           error=error,
                           edit_enabled=error)


def _render_row_editing_page(layout_id, row_number, error):
    """
    Helper to render the aircraft layout row definition editing page

    :param layout_id: ID for the aircraft layout
    :param row_number: Row number to edit
    :param error: Error message to display on the page or None
    :return: The rendered row editing template
    """
    layout = get_layout(layout_id)
    row = [row for row in layout.row_definitions if row.number == row_number][0]
    return render_template("layouts/edit_row.html",
                           layout=get_layout(layout_id),
                           row=row,
                           error=error)


def _render_row_deletion_page(layout_id, row_number, error):
    """
    Helper to render the aircraft layout row definition deletion page

    :param layout_id: ID for the aircraft layout from which to delete a row
    :param row_number: Row number to delete
    :param error: Error message to display on the page or None
    :return: The rendered row deletion template
    """
    layout = get_layout(layout_id)
    row = [row for row in layout.row_definitions if row.number == row_number][0]
    return render_template("layouts/delete_row.html",
                           layout=get_layout(layout_id),
                           rows=[row],
                           error=error,
                           edit_enabled=False)


@layouts_bp.route("/select/<int:flight_id>", methods=["GET", "POST"])
def select(flight_id):
    """
    Serve the page to select an aircraft layout for a given flight and apply that layout when the form is submitted

    :param flight_id: The ID of the flight record
    :return: The HTML for the aircraft layout selection page or a response object redirecting to /
    """
    if request.method == "POST":
        try:
            apply_aircraft_layout(flight_id, int(request.form["layout_id"]))
            return redirect("/")
        except ValueError as e:
            return _render_layout_selection_page(flight_id, e)
    else:
        return _render_layout_selection_page(flight_id, None)


@layouts_bp.route("/list")
def list_all():
    """
    Show the page that lists all airlines and is the entry point for adding new ones

    :return: The HTML for the airline listing page
    """
    return render_template("layouts/list.html",
                           layouts=list_layouts(None),
                           edit_enabled=True)


@layouts_bp.route("/list_rows/<int:layout_id>")
def list_rows(layout_id):
    """
    Show the page that lists the row definitions for a specified layout and is the entry point for editing them

    :param layout_id: ID for the layout for which to show the row definitions
    :return: The HTML for the row definition listing page
    """
    layout = get_layout(layout_id)
    return render_template("layouts/row_list.html",
                           layout=layout,
                           rows=layout.row_definitions,
                           edit_enabled=True)


@layouts_bp.route("/add", methods=["GET", "POST"])
def add():
    """
    Serve the page to add an aircraft layout and handle the addition when the form is submitted

    :return: The HTML for the aircraft layout upload page or a response object redirecting to the layout list page
    """
    if request.method == "POST":
        try:
            import_aircraft_layout_from_stream(request.form["airline"],
                                               request.form["aircraft"],
                                               request.form["layout_name"],
                                               request.files["csv_file_name"])
            return redirect("/layouts/list")
        except ValueError as e:
            return _render_layout_addition_page(e)
    else:
        return _render_layout_addition_page(None)


@layouts_bp.route("/edit/<int:layout_id>", methods=["GET", "POST"])
def edit(layout_id):
    """
    Serve the page to edit an existing aircraft layout and handle the action when the form is submitted

    :param layout_id: ID for the layout to edit
    :return: The HTML for the aircraft layout upload page or a response object redirecting to the layout list page
    """
    if request.method == "POST":
        try:
            update_layout(layout_id, request.form["aircraft"], request.form["layout_name"])
            return redirect("/layouts/list")
        except ValueError as e:
            return _render_layout_editing_page(layout_id, e)
    else:
        return _render_layout_editing_page(layout_id, None)


@layouts_bp.route("/edit_row/<int:layout_id>/<int:row_number>", methods=["GET", "POST"])
def edit_row(layout_id, row_number):
    """
    Serve the page to edit an aircraft layout row definition and handle the edit when the form is submitted

    :param layout_id: ID for the layout from which to delete a row
    :param row_number: Row number to edit
    :return: The rendered row editing template or a redirect to the row list page
    """
    if request.method == "POST":
        try:
            update_row_definition(layout_id, row_number, request.form["seating_class"], request.form["letters"])
            return redirect(f"/layouts/list_rows/{layout_id}")
        except ValueError as e:
            return _render_row_editing_page(layout_id, row_number, e)
    else:
        return _render_row_editing_page(layout_id, row_number, None)


@layouts_bp.route("/delete/<int:layout_id>", methods=["GET", "POST"])
def delete(layout_id):
    """
    Serve the page to confirm deletion of an aircraft layout and handle the deletion when the form is submitted

    :param layout_id: ID for the airport to delete
    :return: The rendered airport deletion template or a redirect to the airport list page
    """
    if request.method == "POST":
        try:
            delete_layout(layout_id)
            return redirect("/layouts/list")
        except ValueError as e:
            return _render_layout_deletion_page(layout_id, e)
    else:
        return _render_layout_deletion_page(layout_id, None)


@layouts_bp.route("/delete_row/<int:layout_id>/<int:row_number>", methods=["GET", "POST"])
def delete_row(layout_id, row_number):
    """
    Serve the page to confirm deletion of an aircraft layout row definition and handle the deletion when the
    form is submitted

    :param layout_id: ID for the layout from which to delete a row
    :param row_number: Row number to delete
    :return: The rendered row deletion template or a redirect to the row list page
    """
    if request.method == "POST":
        try:
            delete_row_from_layout(layout_id, row_number)
            return redirect(f"/layouts/list_rows/{row_number}")
        except ValueError as e:
            return _render_row_deletion_page(layout_id, row_number, e)
    else:
        return _render_row_deletion_page(layout_id, row_number, None)
