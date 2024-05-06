python -m venv venv

call venv\Scripts\activate.bat

python -m pip install --upgrade pip setuptools
python -m pip install wheel
python -m pip install "pip-tools >= 7"
python scripts\rebuild_requirements.py
python -m pip install --upgrade -r requirements.txt -r requirements-dev.txt -r requirements-package.txt
python scripts/compile_ui_files.py --purge-existing
