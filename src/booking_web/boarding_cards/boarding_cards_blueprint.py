"""
The boarding cards blueprint supplies view functions and templates for printing boarding cards
"""

from flask import Blueprint, render_template, redirect, request, session
from flight_model.logic import get_flight
from flight_model.logic import BoardingCardsGenerator, InvalidOperationError, MissingBoardingCardPluginError

boarding_cards_bp = Blueprint("boarding_cards", __name__, template_folder='templates')


@boarding_cards_bp.route("/print/<int:flight_id>", methods=["GET", "POST"])
def print_cards(flight_id):
    """
    Serve the page to prompt for a gate number and generate boarding cards when the form is submitted

    :return: The HTML for the boarding card generation page or a response object redirecting to /
    """
    if request.method == "POST":
        try:
            generator = BoardingCardsGenerator(flight_id, "pdf", request.form["gate_number"])
            generator.start()
            session["message"] = "Boarding cards are being generated in the background"
        except (ValueError, InvalidOperationError, MissingBoardingCardPluginError) as e:
            return render_template("boarding_cards/print.html",
                                   flight=get_flight(flight_id),
                                   error=e)
        else:
            return redirect("/flights/list")
    else:
        return render_template("boarding_cards/print.html",
                               flight=get_flight(flight_id),
                               error=None)
