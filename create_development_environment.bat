python -m venv venv-PySide6

call venv-PySide6\Scripts\activate.bat

python -m pip install --upgrade pip setuptools
python -m pip install wheel
python -m pip install "pip-tools >= 7"

echo Creating requirements.txt from pyproject.toml. This takes a while.
python scripts\rebuild_requirements.py
python -m pip install --upgrade -r requirements.txt -r requirements-dev.txt
python scripts/compile_ui_files.py --purge-existing
