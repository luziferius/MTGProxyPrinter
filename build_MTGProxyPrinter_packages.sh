#!/bin/bash
ENVIRONMENT_NAME="venv"
# Generate an application bundle using cx_Freeze for Linux.

if [ ! -e "${ENVIRONMENT_NAME}" ]; then
  ./create_development_environment.sh
fi

source "${ENVIRONMENT_NAME}/bin/activate"
tox run -e package_wheel,package_cx_freeze

