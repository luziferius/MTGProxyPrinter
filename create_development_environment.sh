#!/usr/bin/env bash
ENVIRONMENT_NAME="venv"

if [ -e "${ENVIRONMENT_NAME}" ]; then
  echo "Removing already existing virtual environment."
  rm -r "${ENVIRONMENT_NAME}"
fi

python -m venv "${ENVIRONMENT_NAME}"
source "${ENVIRONMENT_NAME}/bin/activate"

echo "Installing all dependencies, including development and test requirements."

python -m pip install --upgrade pip setuptools
python -m pip install wheel "tox >= 4.41"
tox run -e generate_development_environment
