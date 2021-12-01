#!/bin/zsh -f

source ../venv/bin/activate
SRCDIR=${0:a:h}/../src
export PYTHONPATH=$SRCDIR
make html
deactivate
