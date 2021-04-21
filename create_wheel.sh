#!/bin/bash

ENVIRONMENT_NAME="venv"

if [ ! -e "${ENVIRONMENT_NAME}" ]; then
  echo "Creating required Python environment."
  ./create_development_environment.sh
fi

source "${ENVIRONMENT_NAME}/bin/activate"
python3 -m build --wheel
