#!/bin/zsh -f

export PROJECT_ROOT=$( cd "$(dirname "$0")" ; pwd -P )
source "$PROJECT_ROOT/venv/bin/activate"
export PYTHONPATH="$PROJECT_ROOT/src"
export FLIGHT_BOOKING_DB="$PROJECT_ROOT/data/flight_booking.db"
export FLASK_ENV=development
export FLASK_APP=booking.py
cd src/booking_web && flask run
