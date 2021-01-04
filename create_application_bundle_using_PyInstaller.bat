:: Generate an application bundle using PyInstaller.

:: --windowed suppresses the terminal window.
pyinstaller  --windowed --name MTGProxyPrinter --additional-hooks-dir pyinstaller_hooks mtg-proxy-printer-runner.py

