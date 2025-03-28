python -m venv venv

call venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install wheel
python -m pip install "pip-tools >= 7"

echo Creating requirements.txt from pyproject.toml. This takes a while.
python -m piptools compile -o requirements.txt pyproject.toml
python -m piptools compile --extra dev -o requirements-dev.txt pyproject.toml
python -m piptools compile --extra package -o requirements-package.txt pyproject.toml
python -m pip install --upgrade -r requirements.txt -r requirements-dev.txt -r requirements-package.txt
python scripts\compile_ui_files.py --purge-existing
