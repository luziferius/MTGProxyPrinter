#!/bin/bash

# Generate an application bundle using PyInstaller.

PARAMETERS="--name MTGProxyPrinter --additional-hooks-dir pyinstaller_hooks mtg-proxy-printer-runner.py"
# Allow passing in additional parameters, such as --onefile
pyinstaller "$1" $PARAMETERS

# Cleanup: Delete the automatically generated, compiled resources from the source tree after pyinstaller finished.
rm "mtg_proxy_printer/ui/compiled_resources.py"
