#!/bin/bash
ENVIRONMENT_NAME="venv"

if [ -e "${ENVIRONMENT_NAME}" ]; then
  echo "Removing already existing virtual environment."
  rm -r "${ENVIRONMENT_NAME}"
fi

python -m venv "${ENVIRONMENT_NAME}"
source "${ENVIRONMENT_NAME}/bin/activate"

# Install including all dependencies
echo "Installing all dependencies, including development and test requirements."

python -m pip install --upgrade pip setuptools
python -m pip install wheel
python -m pip install "pip-tools >= 7"
echo "Creating requirements.txt from pyproject.toml. This takes a while."
python scripts/rebuild_requirements.py
python -m pip install --upgrade -r requirements.txt -r requirements-dev.txt
python scripts/compile_ui_files.py --purge-existing
