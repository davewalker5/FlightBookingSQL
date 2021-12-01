#!/bin/zsh -f

export PYTHONPATH=`pwd`/..
export FLASK_APP=booking.py
export FLASK_ENV=development
flask run
