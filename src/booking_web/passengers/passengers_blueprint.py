"""
The passengers blueprint supplies view functions and templates for passenger management and seat allocation
"""

import datetime
from flask import Blueprint, render_template, redirect, request, session
from flight_model.logic import get_flight, add_passenger
from flight_model.logic import allocate_seat
from flight_model.logic import create_passenger, delete_passenger


passengers_bp = Blueprint("passengers", __name__, template_folder='templates')


def _render_passenger_addition_page(flight_id, error):
    """
    Helper to render the airline editing page

    :param flight_id: ID for the flight to which to add passengers
    :param error: Error message to display on the page or None
    :return: The rendered passenger addition template
    """
    return render_template("passengers/add.html",
                           flight=get_flight(flight_id),
                           error=error)


def _render_seat_allocation_page(flight_id, passenger_id, error):
    """
    Helper to render the page to allocate a seat to a passenger

    :param flight_id: ID of the flight the passenger is associated with
    :param passenger_id: Unique identifier for the passenger to allocate to a seat
    :param error: Error message to display on the page or None
    :return: The HTML for the seat allocation page
    """
    flight = get_flight(flight_id)
    passengers = [p for p in flight.passengers if p.id == passenger_id]
    return render_template("passengers/allocate.html",
                           flight=flight,
                           passengers=passengers,
                           error=error)


@passengers_bp.route("/list/<int:flight_id>")
def list_all(flight_id):
    """
    Serve the page showing passenger details and their seat allocations. From this page, seat allocations can
    be added and changed and passengers can be added to and removed from the flight.

    :return: The HTML for the passenger details page
    """
    flight = get_flight(flight_id)
    if flight.passenger_count > 0:
        return render_template("passengers/list.html",
                               flight=flight,
                               passengers=flight.passengers,
                               edit_enabled=True)
    else:
        return redirect(f"/passengers/add/{flight_id}")


@passengers_bp.route("/add/<int:flight_id>", methods=["GET", "POST"])
def add(flight_id):
    """
    Serve the page to add a passenger to a flight and handle the addition when the form is submitted

    :param flight_id: ID of the flight to add a passenger to
    :return: The HTML for the passenger entry page or a response object redirecting to /
    """
    if request.method == "POST":
        try:
            dob = datetime.datetime.strptime(request.form["dob"], "%d/%m/%Y").date()
            passenger = create_passenger(request.form["name"],
                                         request.form["gender"],
                                         dob,
                                         request.form["nationality"],
                                         request.form["residency"],
                                         request.form["passport_number"])
            add_passenger(flight_id, passenger)
            return redirect(f"/passengers/list/{flight_id}")
        except ValueError as e:
            return _render_passenger_addition_page(flight_id, e)
    else:
        return _render_passenger_addition_page(flight_id, None)


@passengers_bp.route("/delete/<int:flight_id>/<int:passenger_id>", methods=["GET", "POST"])
def delete(flight_id, passenger_id):
    """
    Serve the page to confirm deletion of a passenger from a flight and handle the deletion when the form is submitted

    :param flight_id: ID of the flight from which to delete a passenger
    :param passenger_id: ID for the passenger to delete
    :return: The rendered passenger deletion template or a redirect to the passenger list page
    """
    if request.method == "POST":
        delete_passenger(flight_id, passenger_id)
        return redirect(f"/passengers/list/{flight_id}")

    # Render the passenger list for the flight
    flight = get_flight(flight_id)
    passengers = [p for p in flight.passengers if p.id == passenger_id]
    return render_template("passengers/delete.html",
                           passengers=passengers,
                           flight=flight,
                           edit_enabled=False)


@passengers_bp.route("/allocate/<int:flight_id>/<int:passenger_id>", methods=["GET", "POST"])
def allocate(flight_id, passenger_id):
    """
    Serve the page prompting for a seat allocation for a single passenger

    :param flight_id: ID of the flight the passenger is associated with
    :param passenger_id: Unique identifier for the passenger to allocate to a seat
    :return: The HTML for the seat allocation page or a response object redirecting to the passenger details page
    """
    if request.method == "POST":
        try:
            allocate_seat(flight_id, passenger_id, request.form["seat_number"])
            return redirect(f"/passengers/list/{flight_id}")
        except ValueError as e:
            return _render_seat_allocation_page(flight_id, passenger_id, e)
    else:
        return _render_seat_allocation_page(flight_id, passenger_id, None)
