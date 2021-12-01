#!/bin/zsh -f

export PYTHONPATH=`pwd`/src/
coverage run --branch --source src -m unittest discover
coverage html -d cov_html
