"""
This module implements a Flask-based web application based on the functionality provided by the "flight_model"
package.

The site is not responsive but the Bootstrap customizer has been used to generate a cut-down version of bootstrap
to provide button and form element styling.
"""

import os
from flask import Flask, redirect
from booking_web.airports import airports_bp
from booking_web.airlines import airlines_bp
from booking_web.layouts import layouts_bp
from booking_web.passengers import passengers_bp
from booking_web.flights import flights_bp
from booking_web.boarding_cards import boarding_cards_bp


app = Flask("Flight Booking",
            static_folder=os.path.join(os.path.dirname(__file__), "static"),
            template_folder=os.path.join(os.path.dirname(__file__), "templates"))

app.secret_key = b'some secret key'
app.register_blueprint(airports_bp, url_prefix='/airports')
app.register_blueprint(airlines_bp, url_prefix='/airlines')
app.register_blueprint(layouts_bp, url_prefix='/layouts')
app.register_blueprint(passengers_bp, url_prefix='/passengers')
app.register_blueprint(flights_bp, url_prefix='/flights')
app.register_blueprint(boarding_cards_bp, url_prefix='/boarding_cards')


@app.route("/")
def home():
    """
    Serve the home page for the site. This just redirects to the flights list

    :return: Redirect to the flights list page
    """
    return redirect("/flights/list")
