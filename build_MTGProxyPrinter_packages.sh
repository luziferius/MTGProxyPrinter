#!/bin/bash
ENVIRONMENT_NAME="venv-PySide6"
# Generate an application bundle using cx_Freeze for Linux.

if [ ! -e "${ENVIRONMENT_NAME}" ]; then
  ./create_development_environment.sh
fi

source "${ENVIRONMENT_NAME}/bin/activate"
tox run -f py3 package

