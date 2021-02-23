:: Generate an application bundle using PyInstaller.

:: --windowed suppresses the terminal window.
pyinstaller  --windowed --name MTGProxyPrinter --additional-hooks-dir pyinstaller_hooks mtg-proxy-printer-runner.py

:: Some cleanup: Remove unused DLLs that were collected by PyInstaller.
:: Some of these are quite large, so this significantly reduces the bundle size.
cd dist\MTGProxyPrinter
del d3dcompiler_47.dll libGLESv2.dll opengl32sw.dll Qt5DBus.dll Qt5Network.dll Qt5Qml.dll Qt5QmlModels.dll Qt5Quick.dll Qt5WebSockets.dll
