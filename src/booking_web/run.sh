#!/bin/zsh -f

#export PYTHONPATH=`pwd`/..
export PYTHONPATH=/Users/dave/PycharmProjects/FlightBookingSQL/src
export FLASK_APP=booking.py
export FLASK_ENV=development
echo "PYTHONPATH = " $PYTHONPATH
flask run
