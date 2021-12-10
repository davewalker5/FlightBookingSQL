"""
The airlines blueprint supplies view functions and templates for airline management
"""

from flask import Blueprint, render_template, redirect, request
from flight_model.logic import list_airlines, create_airline, delete_airline, get_airline, update_airline


airlines_bp = Blueprint("airlines", __name__, template_folder='templates')


@airlines_bp.route("/list")
def list_all():
    """
    Show the page that lists all airlines and is the entry point for adding new ones

    :return: The HTML for the airline listing page
    """
    return render_template("airlines/list.html",
                           airlines=list_airlines(),
                           edit_enabled=True)

@airlines_bp.route("/edit", defaults={"airline_id": None}, methods=["GET", "POST"])
@airlines_bp.route("/edit/<int:airline_id>", methods=["GET", "POST"])
def edit(airline_id):
    """
    Serve the page to add/edit an airline and handle the appropriate action when the form is submitted

    :param airline_id: ID for an airline to edit or None to create a new airline
    :return: The HTML for the airline entry page or a response object redirecting to the airline list page
    """
    if request.method == "POST":
        try:
            if airline_id:
                update_airline(airline_id, request.form["name"])
            else:
                _ = create_airline(request.form["name"])
            return redirect("/airlines/list")
        except ValueError as e:
            airline = get_airline(airline_id) if airline_id else None
            return render_template("airlines/edit.html",
                                   airline=airline,
                                   error=e)
    else:
        airline = get_airline(airline_id) if airline_id else None
        return render_template("airlines/edit.html",
                               airline=airline,
                               error=None)


@airlines_bp.route("/delete/<int:airline_id>", methods=["GET", "POST"])
def delete(airline_id):
    """
    Serve the page to confirm deletion of an airline and handle the deletion when the form is submitted

    :param airline_id: ID for the airline to delete
    :return: The rendered airport deletion template or a redirect to the airline list page
    """
    if request.method == "POST":
        delete_airline(airline_id)
        return redirect(f"/airlines/list")
    else:
        return render_template("airlines/delete.html",
                               airlines=[get_airline(airline_id)],
                               error=None,
                               edit_enabled=False)
