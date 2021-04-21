python -m venv venv

call venv\Scripts\activate.bat

pip install ".[dev]"
pip uninstall -y MTGProxyPrinter