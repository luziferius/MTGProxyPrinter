#!/bin/bash
ENVIRONMENT_NAME="venv"

if [ -e "${ENVIRONMENT_NAME}" ]; then
  echo "Removing already existing virtual environment."
  rm -r "${ENVIRONMENT_NAME}"
fi

virtualenv -p python3 "${ENVIRONMENT_NAME}"
source "${ENVIRONMENT_NAME}/bin/activate"

# Install including all dependencies
echo "Installing all dependencies, including development and test requirements."
pip3 install wheel
pip3 install -r requirements.txt

