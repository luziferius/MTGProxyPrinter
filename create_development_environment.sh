#!/bin/bash
ENVIRONMENT_NAME="venv"

if [ -e "${ENVIRONMENT_NAME}" ]; then
  echo "A virtual environment already exists. Doing nothing."
  exit
fi

virtualenv -p python3 "${ENVIRONMENT_NAME}"
source "${ENVIRONMENT_NAME}/bin/activate"

# Install including all dependencies
echo "Installing all dependencies, including development and test requirements."
pip3 install -e ".[dev]"
echo ""
echo "Uninstall the main package again, leaving the dependencies in place."
pip3 uninstall --yes MTGProxyPrinter
