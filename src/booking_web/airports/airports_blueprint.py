"""
The airports blueprint supplies view functions and templates for airport management
"""

import pytz
from flask import Blueprint, render_template, redirect, request
from flight_model.logic import list_airports, create_airport, get_airport, delete_airport, update_airport

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


@airports_bp.route("/edit", defaults={"airport_id": None}, methods=["GET", "POST"])
@airports_bp.route("/add/<int:airport_id>", methods=["GET", "POST"])
def edit(airport_id):
    """
    Serve the page to add  new airport or edit an existing one and handle the appropriate action
    when the form is submitted

    :param airport_id: ID for an airport to edit or None to create a new airport
    :return: The HTML for the airport entry page or a response object redirecting to the airport list page
    """
    if request.method == "POST":
        try:
            if airport_id:
                update_airport(airport_id, request.form["code"], request.form["name"], request.form["timezone"])
            else:
                _ = create_airport(request.form["code"], request.form["name"], request.form["timezone"])
            return redirect("/airports/list")
        except ValueError as e:
            airport = get_airport(airport_id) if airport_id else None
            return render_template("airports/edit.html",
                                   timezones=pytz.all_timezones,
                                   airport=airport,
                                   error=e)
    else:
        airport = get_airport(airport_id) if airport_id else None
        return render_template("airports/edit.html",
                               timezones=pytz.all_timezones,
                               airport=airport,
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
