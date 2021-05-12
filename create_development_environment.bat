python -m venv venv

call venv\Scripts\activate.bat

pip install wheel
pip install ".[dev]"
pip uninstall -y MTGProxyPrinter

:: Cleanup various items that bloat the application bundle. Mostly related to unused PyQt5 and Qt5 components

pushd venv\Lib\site-packages

pushd PyQt5

:: Unused Qsci
rmdir /S /Q Qt

:: Unused Qml bindings
rmdir /S /Q Qt5\qml


::  Unused DLLs
pushd Qt5\bin
del d3dcompiler_47.dll libEGL.dll libGLESv2.dll opengl32sw.dll Qt5Bluetooth.dll Qt5DBus.dll Qt5Designer.dll Qt5Help.dll
del Qt5Location.dll Qt5Multimedia.dll Qt5MultimediaWidgets.dll Qt5Network.dll Qt5Nfc.dll Qt5OpenGL.dll Qt5Positioning.dll
del Qt5PositioningQuick.dll Qt5Qml.dll Qt5QmlModels.dll Qt5QmlWorkerScript.dll Qt5Quick.dll Qt5Quick3D.dll
del Qt5Quick3DAssetImport.dll Qt5Quick3DRender.dll Qt5Quick3DRuntimeRender.dll Qt5Quick3DUtils.dll Qt5QuickControls2.dll
del Qt5QuickParticles.dll Qt5QuickShapes.dll Qt5QuickTemplates2.dll Qt5QuickTest.dll Qt5QuickWidgets.dll Qt5RemoteObjects.dll
del Qt5Sensors.dll Qt5SerialPort.dll Qt5Sql.dll Qt5Test.dll Qt5WebChannel.dll Qt5WebSockets.dll Qt5WebView.dll
popd

:: Unused extension modules
del QAxContainer.pyd  QAxContainer.pyi QtBluetooth.pyd QtBluetooth.pyi QtDBus.pyd QtDBus.pyi QtDesigner.pyd QtDesigner.pyi
del QtHelp.pyd QtHelp.pyi QtLocation.pyd QtLocation.pyi QtMultimedia.pyd QtMultimedia.pyi QtMultimediaWidgets.pyd QtMultimediaWidgets.pyi
del QtNetwork.pyd QtNetwork.pyi QtNfc.pyd QtNfc.pyi QtOpenGL.pyd QtOpenGL.pyi QtPositioning.pyd QtPositioning.pyi
del QtQml.pyd QtQml.pyi QtQuick.pyd QtQuick.pyi QtQuick3D.pyd QtQuick3D.pyi QtQuickWidgets.pyd QtQuickWidgets.pyi
del QtRemoteObjects.pyd QtRemoteObjects.pyi QtSensors.pyd QtSensors.pyi QtSerialPort.pyd QtSerialPort.pyi
del QtSql.pyd QtSql.pyi QtTest.pyd QtTest.pyi QtTextToSpeech.pyd QtTextToSpeech.pyi QtWebChannel.pyd QtWebChannel.pyi
del QtWebSockets.pyd QtWebSockets.pyi _QOpenGLFunctions_2_0.pyd _QOpenGLFunctions_2_1.pyd _QOpenGLFunctions_4_1_Core.pyd

:: Unused bindings
pushd bindings
FOR %%G IN (
  QAxContainer QtBluetooth QtDBus QtDesigner
  QtHelp QtLocation QtMultimedia QtMultimediaWidgets
  QtNetwork QtNfc QtOpenGL QtPositioning
  QtQml QtQuick QtQuick3D QtQuickWidgets
  QtRemoteObjects QtSensors QtSerialPort QtSql
  QtTest QtTextToSpeech QtWebChannel QtWebSockets
) DO rmdir /S /Q %%G
popd

:: leave PyQt5
popd

:: leave site-packages
popd
