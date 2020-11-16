#!/bin/bash

source venv/bin/activate
# See https://docs.python.org/3/library/devmode.html#devmode
# for PYTHONDEVMODE=1
PYTHONDEVMODE=1 pytest --numprocesses=auto --cov=mtg_proxy_printer "$@" tests/
deactivate
