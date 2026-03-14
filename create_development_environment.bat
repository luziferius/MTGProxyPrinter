echo "Creating virtual environment ..."
python -m venv venv
echo "Installing dependencies into the virtual environment ..."
call venv\Scripts\activate.bat

python -m pip install --upgrade pip setuptools
python -m pip install wheel "tox >= 4.41"
tox run -e generate_development_environment
