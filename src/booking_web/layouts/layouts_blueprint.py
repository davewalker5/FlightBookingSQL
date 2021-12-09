"""
The layouts blueprint supplies view functions and templates for aircraft layout management
"""

from flask import Blueprint, render_template, redirect, request
from flight_model.logic import get_flight
from flight_model.logic import list_airlines
from flight_model.logic import list_layouts, apply_aircraft_layout, get_layout, delete_layout
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
            return render_template("layouts/add.html",
                                   airlines=list_airlines(),
                                   error=e)
    else:
        return render_template("layouts/add.html",
                               airlines=list_airlines(),
                               error=None)


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
            return redirect(f"/layouts/list")
        except ValueError as e:
            return render_template("layouts/delete.html",
                                   layouts=[get_layout(layout_id)],
                                   error=e,
                                   edit_enabled=False)
    else:
        return render_template("layouts/delete.html",
                               layouts=[get_layout(layout_id)],
                               error=None,
                               edit_enabled=False)
