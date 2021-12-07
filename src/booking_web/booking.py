"""
This module implements a Flask-based web application based on the functionality provided by the "flight_model"
package.

The site is not responsive but the Bootstrap customizer has been used to generate a cut-down version of bootstrap
to provide button and form element styling.
"""

import datetime

import pytz
from flask import Flask, render_template, redirect, request, session
from flight_model.logic import list_flights, create_flight, get_flight, delete_flight, add_passenger
from flight_model.logic import list_airlines, create_airline
from flight_model.logic import list_airports, create_airport
from flight_model.logic import list_layouts, apply_aircraft_layout, allocate_seat
from flight_model.logic import create_passenger, delete_passenger
from flight_model.logic import generate_boarding_cards, InvalidOperationError, MissingBoardingCardPluginError

app = Flask("Flight Booking")
app.secret_key = b'some secret key'

options_map = [
    {
        "description": "Create Flight",
        "view": "create_new_flight"
    },
    {
        "description": "Airports",
        "view": "list_all_airports"
    },
    {
        "description": "Airlines",
        "view": "list_all_airlines"
    },
    {
        "description": "Home",
        "view": "home",
        "is_home_link": True
    }
]


@app.route("/")
def home():
    """
    Serve the home page for the flight booking site, listing the current flights

    :return: HTML for the home page
    """
    error = session.pop("error") if "error" in session else None
    message = session.pop("message") if "message" in session else None
    return render_template("home.html",
                           options_map=options_map,
                           flights=list_flights(),
                           edit_enabled=True,
                           error=error,
                           message=message)


@app.route("/create_new_flight", methods=["GET", "POST"])
def create_new_flight():
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
            return render_template("create_flight.html",
                                   airlines=list_airlines(),
                                   airports=list_airports(),
                                   error=e)
        else:
            return redirect("/")
    else:
        return render_template("create_flight.html",
                               options_map=options_map,
                               airlines=list_airlines(),
                               airports=list_airports(),
                               error=None)


@app.route("/select_layout/<int:flight_id>", methods=["GET", "POST"])
def select_layout(flight_id):
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

    return render_template("select_layout.html",
                           options_map=options_map,
                           flight_number=flight.number,
                           layouts=list_layouts(airline_id),
                           current_layout_id=aircraft_layout_id,
                           select_enabled=True,
                           error=error)


@app.route("/delete_flight_by_id/<int:flight_id>", methods=["GET", "POST"])
def delete_flight_by_id(flight_id):
    """
    Serve the page to confirm deletion of a flight and to handle the deletion once the form is submitted

    :param flight_id: ID for the flight to delete
    :return: The rendered flight deletion template or a redirect to /
    """
    if request.method == "POST":
        delete_flight(flight_id)
        return redirect("/")
    else:
        return render_template("delete_flight.html",
                               options_map=options_map,
                               flights=[get_flight(flight_id)],
                               edit_enabled=False)


@app.route("/list_passengers/<int:flight_id>")
def list_passengers(flight_id):
    """
    Serve the page showing passenger details and their seat allocations. From this page, seat allocations can
    be added and changed and passengers can be removed from the flight.

    :return: The HTML for the passenger details page
    """
    flight = get_flight(flight_id)
    if flight.passenger_count > 0:
        return render_template("list_passengers.html",
                               options_map=options_map,
                               flight=flight,
                               passengers=flight.passengers,
                               edit_enabled=True)
    else:
        session["message"] = "There are no passengers on the flight"
        return redirect("/")

@app.route("/add_passenger_to_flight/<int:flight_id>", methods=["GET", "POST"])
def add_passenger_to_flight(flight_id):
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
            return redirect(f"/list_passengers/{flight_id}")
        except ValueError as e:
            return render_template("add_passenger.html",
                                   options_map=options_map,
                                   flight=get_flight(flight_id),
                                   error=e)
    else:
        return render_template("add_passenger.html",
                               options_map=options_map,
                               flight=get_flight(flight_id),
                               error=None)


@app.route("/delete_passenger_from_flight/<int:flight_id>/<int:passenger_id>", methods=["GET", "POST"])
def delete_passenger_from_flight(flight_id, passenger_id):
    """
    Serve the page to confirm deletion of a passenger from a flight and handle the deletion when the form is submitted

    :param flight_id: ID of the flight from which to delete a passenger
    :param passenger_id: ID for the passenger to delete
    :return: The rendered passenger deletion template or a redirect to the passenger list page
    """
    if request.method == "POST":
        delete_passenger(flight_id, passenger_id)
        return redirect(f"/list_passengers/{flight_id}")

    # Render the passenger list for the flight
    flight = get_flight(flight_id)
    passengers = [p for p in flight.passengers if p.id == passenger_id]
    return render_template("delete_passenger.html",
                           options_map=options_map,
                           passengers=passengers,
                           flight=flight,
                           edit_enabled=False)


@app.route("/allocate_seat/<int:flight_id>/<int:passenger_id>", methods=["GET", "POST"])
def allocate_seat_to_passenger(flight_id, passenger_id):
    """
    Serve the page prompting for a seat allocation for a single passenger

    :param flight_id: ID of the flight the passenger is associated with
    :param passenger_id: Unique identifier for the passenger to allocate to a seat
    :return: The HTML for the seat allocation page or a response object redirecting to the passenger details page
    """
    if request.method == "POST":
        try:
            allocate_seat(flight_id, passenger_id, request.form["seat_number"])
            return redirect(f"/list_passengers/{flight_id}")
        except ValueError as e:
            return _render_seat_allocation_page(flight_id, passenger_id, e)
    else:
        return _render_seat_allocation_page(flight_id, passenger_id, None)


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
    return render_template("allocate_seat.html",
                           options_map=options_map,
                           flight=flight,
                           passengers=passengers,
                           error=error)


@app.route("/print_boarding_cards/<int:flight_id>", methods=["GET", "POST"])
def print_boarding_cards(flight_id):
    """
    Serve the page to prompt for a gate number and generate boarding cards when the form is submitted

    :return: The HTML for the boarding card generation page or a response object redirecting to /
    """
    if request.method == "POST":
        try:
            # TODO: This should be run on a background thread as it currently blocks the UI thread
            generate_boarding_cards(flight_id, "pdf", request.form["gate_number"])
            session["message"] = "Boarding cards have been generated"
        except (ValueError, InvalidOperationError, MissingBoardingCardPluginError) as e:
            return render_template("print_boarding_cards.html",
                                   flight=get_flight(flight_id),
                                   error=e)
        else:
            return redirect("/")
    else:
        return render_template("print_boarding_cards.html",
                               flight=get_flight(flight_id),
                               error=None)


@app.route("/list_airports")
def list_all_airports():
    """
    Show the page that lists all airports and is the entry point for adding new ones

    :return: The HTML for the airport listing page
    """
    return render_template("list_airports.html",
                           options_map=options_map,
                           airports=list_airports())


@app.route("/add_airport", methods=["GET", "POST"])
def add_airport():
    """
    Serve the page to add an airport and handle the addition when the form is submitted

    :return: The HTML for the airport entry page or a response object redirecting to the airport list page
    """
    if request.method == "POST":
        try:
            _ = create_airport(request.form["code"], request.form["name"], request.form["timezone"])
            return redirect("/list_airports")
        except ValueError as e:
            return render_template("add_airport.html",
                                   options_map=options_map,
                                   timezones=pytz.all_timezones,
                                   error=e)
    else:
        return render_template("add_airport.html",
                               options_map=options_map,
                               timezones=pytz.all_timezones,
                               error=None)


@app.route("/list_airlines")
def list_all_airlines():
    """
    Show the page that lists all airlines and is the entry point for adding new ones

    :return: The HTML for the airline listing page
    """
    return render_template("list_airlines.html",
                           options_map=options_map,
                           airlines=list_airlines())


@app.route("/v", methods=["GET", "POST"])
def add_airline():
    """
    Serve the page to add an airline and handle the addition when the form is submitted

    :return: The HTML for the airline entry page or a response object redirecting to the airline list page
    """
    if request.method == "POST":
        try:
            _ = create_airline(request.form["name"])
            return redirect("/list_airlines")
        except ValueError as e:
            return render_template("add_airline.html",
                                   options_map=options_map,
                                   error=e)
    else:
        return render_template("add_airline.html",
                               options_map=options_map,
                               error=None)
