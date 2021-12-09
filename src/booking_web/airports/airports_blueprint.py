"""
The airports blueprint supplies view functions and templates for airport management
"""

import pytz
from flask import Blueprint, render_template, redirect, request
from flight_model.logic import list_airports, create_airport, get_airport, delete_airport

airports_bp = Blueprint("airports", __name__, template_folder='templates')


@airports_bp.route("/list")
def list_all():
    """
    Show the page that lists all airports and is the entry point for adding new ones

    :return: The HTML for the airport listing page
    """
    return render_template("airports/list.html",
                           airports=list_airports(),
                           edit_enabled=True)


@airports_bp.route("/add", methods=["GET", "POST"])
def add():
    """
    Serve the page to add an airport and handle the addition when the form is submitted

    :return: The HTML for the airport entry page or a response object redirecting to the airport list page
    """
    if request.method == "POST":
        try:
            _ = create_airport(request.form["code"], request.form["name"], request.form["timezone"])
            return redirect("/airports/list")
        except ValueError as e:
            return render_template("airports/add.html",
                                   timezones=pytz.all_timezones,
                                   error=e)
    else:
        return render_template("airports/add.html",
                               timezones=pytz.all_timezones,
                               error=None)


@airports_bp.route("/delete/<int:airport_id>", methods=["GET", "POST"])
def delete(airport_id):
    """
    Serve the page to confirm deletion of an airport and handle the deletion when the form is submitted

    :param airport_id: ID for the airport to delete
    :return: The rendered airport deletion template or a redirect to the airport list page
    """
    if request.method == "POST":
        try:
            delete_airport(airport_id)
            return redirect(f"/airports/list")
        except ValueError as e:
            return render_template("airports/delete.html",
                                   airports=[get_airport(airport_id)],
                                   error=e,
                                   edit_enabled=False)
    else:
        return render_template("airports/delete.html",
                               airports=[get_airport(airport_id)],
                               error=None,
                               edit_enabled=False)
