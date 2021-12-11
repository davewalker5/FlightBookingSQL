"""
The flights blueprint supplies view functions and templates for flight management
"""

from flask import Blueprint, render_template, redirect, request, session
from flight_model.logic import list_flights, create_flight, get_flight, delete_flight
from flight_model.logic import list_airlines
from flight_model.logic import list_airports

flights_bp = Blueprint("flights", __name__, template_folder='templates')


def _render_flight_addition_page(error):
    """
    Helper to render the flight addition page

    :param error: Error message to display on the page or None
    :return: The rendered flight addition template
    """
    return render_template("flights/add.html",
                           airlines=list_airlines(),
                           airports=list_airports(),
                           error=error)


@flights_bp.route("/list")
def list_all():
    """
    Serve the home page for the flight booking site, listing the current flights

    :return: HTML for the home page
    """
    error = session.pop("error") if "error" in session else None
    message = session.pop("message") if "message" in session else None
    return render_template("flights/list.html",
                           flights=list_flights(),
                           edit_enabled=True,
                           error=error,
                           message=message)


@flights_bp.route("/add", methods=["GET", "POST"])
def add():
    """
    Serve the page to prompt for the details for a new flight and create the flight when the form is submitted

    :return: The HTML for the create flight page or a response object redirecting to /
    """
    if request.method == "POST":
        try:
            create_flight(request.form["airline"],
                          request.form["embarkation"],
                          request.form["destination"],
                          request.form["number"],
                          request.form["departure_date"],
                          request.form["departure_time"],
                          request.form["duration"])
        except ValueError as e:
            return _render_flight_addition_page(e)
        else:
            return redirect("/flights/list")
    else:
        return _render_flight_addition_page(None)


@flights_bp.route("/delete/<int:flight_id>", methods=["GET", "POST"])
def delete(flight_id):
    """
    Serve the page to confirm deletion of a flight and to handle the deletion once the form is submitted

    :param flight_id: ID for the flight to delete
    :return: The rendered flight deletion template or a redirect to /
    """
    if request.method == "POST":
        delete_flight(flight_id)
        return redirect("/flights/list")
    else:
        return render_template("flights/delete.html",
                               flights=[get_flight(flight_id)],
                               edit_enabled=False)
