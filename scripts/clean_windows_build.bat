:: Copyright (C) 2020-2026 Thomas Hess <thomas.hess@udo.edu>
::
:: This program is free software: you can redistribute it and/or modify
:: it under the terms of the GNU General Public License as published by
:: the Free Software Foundation, either version 3 of the License, or
:: (at your option) any later version.
::
:: This program is distributed in the hope that it will be useful,
:: but WITHOUT ANY WARRANTY; without even the implied warranty of
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
:: GNU General Public License for more details.
::
:: You should have received a copy of the GNU General Public License
:: along with this program. If not, see <http://www.gnu.org/licenses/>.


:: Cleanup various items that bloat the application bundle. Mostly related to unused PyQt5 and Qt5 components
if "%1%"=="" (
  pushd build\exe*
) else (
  pushd "%1"
)

rmdir /S /Q PyQt5.uic.widget-plugins

pushd lib
del ijson\backends\python*.dll


pushd PyQt5
:: All DLLs here are also in Qt5\bin\
del *.dll
del QtRemoteObjects.pyd QtSerialPort.pyd QtSensors.pyd QtNetwork.pyd QtXml.pyd QtXmlPatterns.pyd pyrcc.pyd

:: The sip bindings aren't used at runtime
rmdir /S /Q bindings

pushd Qt5

:: Unused Qsci
rmdir /S /Q qsci

:: Unused Qml bindings
rmdir /S /Q qml


::  Unused DLLs
pushd bin
del d3dcompiler_47.dll libEGL.dll libGLESv2.dll opengl32sw.dll Qt5Bluetooth.dll Qt5DBus.dll Qt5Designer.dll Qt5Help.dll
del Qt5Location.dll Qt5Multimedia.dll Qt5MultimediaWidgets.dll Qt5Network.dll Qt5Nfc.dll Qt5OpenGL.dll Qt5Positioning.dll
del Qt5PositioningQuick.dll Qt5Qml.dll Qt5QmlModels.dll Qt5QmlWorkerScript.dll Qt5Quick.dll Qt5Quick3D.dll
del Qt5Quick3DAssetImport.dll Qt5Quick3DRender.dll Qt5Quick3DRuntimeRender.dll Qt5Quick3DUtils.dll Qt5QuickControls2.dll
del Qt5QuickParticles.dll Qt5QuickShapes.dll Qt5QuickTemplates2.dll Qt5QuickTest.dll Qt5QuickWidgets.dll Qt5RemoteObjects.dll
del Qt5Sensors.dll Qt5SerialPort.dll Qt5Sql.dll Qt5Test.dll Qt5WebChannel.dll
del Qt5WebSockets.dll Qt5WebView.dll Qt5XmlPatterns.dll
del libcrypto-1_1-x64.dll libssl-1_1-x64.dll
popd


:: Unused plugins
pushd plugins

:: Remove duplicated Qt5 base DLLs
FOR %%G IN ( printsupport platforms imageformats styles
) DO del %%G\Qt5*.dll


FOR %%G IN (
  assetimporters audio geometryloaders geoservices mediaservice playlistformats
  position renderers sceneparsers sensorgestures sensors sqldrivers texttospeech webview
) DO rmdir /S /Q %%G
popd


:: Unused translations (of unused modules)
pushd translations
del qtxmlpatterns_*.qm
del qtconnectivity_*.qm
del qtdeclarative_*.qm
del qtlocation_*.qm
del qtmultimedia_*.qm
del qtquickcontrols_*.qm
del qtquickcontrols2_*.qm
del qtserialport_*.qm
del qtwebsockets_*.qm
popd

:: leave Qt5
popd

:: Unused extension modules
del *.pyi
del QAxContainer.pyd QtBluetooth.pyd QtDBus.pyd QtDesigner.pyd QtHelp.pyd QtLocation.pyd QtMultimedia.pyd QtMultimediaWidgets.pyd
del QtOpenGL.pyd QtNfc.pyd QtPositioning.pyd QtQml.pyd QtQuick.pyd QtQuick3D.pyd QtQuickWidgets.pyd
del QtRemoteObjects.pydQtSensors.pydQtSerialPort.pyd QtSql.pyd QtTest.pyd QtTextToSpeech.pyd QtWebChannel.pyd
del QtWebSockets.pyd _QOpenGLFunctions_2_0.pyd _QOpenGLFunctions_2_1.pyd _QOpenGLFunctions_4_1_Core.pyd

:: leave PyQt5
popd
:: leave lib
popd
::leave build directory
popd


