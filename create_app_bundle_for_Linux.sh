#!/bin/bash

# Generate an application bundle using cx_Freeze for Linux.

if [ ! -e "venv" ]; then
  ./create_development_environment.sh
fi

source venv/bin/activate
tox -e py3-package

