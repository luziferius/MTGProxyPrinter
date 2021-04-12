:: Generate an application bundle using PyInstaller.

:: --windowed suppresses the terminal window.
pyinstaller  --windowed --name MTGProxyPrinter --additional-hooks-dir pyinstaller_hooks mtg-proxy-printer-runner.py

rmdir /S /Q build
:: Some cleanup: Remove unused DLLs that were collected by PyInstaller.
:: Some of these are quite large, so this significantly reduces the bundle size.
cd dist\MTGProxyPrinter
del d3dcompiler_47.dll libGLESv2.dll opengl32sw.dll Qt5DBus.dll Qt5Network.dll Qt5Qml.dll Qt5QmlModels.dll Qt5Quick.dll Qt5WebSockets.dll
rmdir /S /Q pint\testsuite
cd PyQt5\Qt\plugins\imageformats\
:: Delete the four largest DLLs for unused image formats. Saves about 1.5 MiB
del qgif.dll qjpeg.dll qtiff.dll qwebp.dll
cd ..\..\..\..\..\..

