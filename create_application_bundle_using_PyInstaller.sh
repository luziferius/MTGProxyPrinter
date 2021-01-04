#!/bin/bash

# Generate an application bundle using PyInstaller.

source venv/bin/activate

# Allow passing in additional parameters, such as --onefile
pyinstaller "$@" --name MTGProxyPrinter --additional-hooks-dir pyinstaller_hooks mtg-proxy-printer-runner.py

# pyinstaller sets the executable bit for all bundled libraries. So remove it, both for security (shared objects should
#not be executable) and for ease of use, as the shell won’t auto-complete non-executables when using ./<tab>
find . -type f \( -name "*.so" -or -name "*.so.*" \) -print0 | xargs -0 chmod a-x
