pyinstaller  --windowed --name MTGProxyPrinter --additional-hooks-dir pyinstaller_hooks mtg-proxy-printer-runner.py

:: Cleanup: Delete the automatically generated, compiled resources from the source tree after pyinstaller finished.
del mtg_proxy_printer\ui\compiled_resources.py
