:: Copyright (C) 2022-2023 Thomas Hess <thomas.hess@udo.edu>
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

if "%1%"=="" (
  pushd build\exe*
) else (
  pushd "%1"
)

pushd lib

pushd PySide6

:: Don't need the executables, like Qt6 Designer, etc.
:: Delete all typing stubs
del *.exe *.pyi

:: Remove unused components. Each consists of a pair of QtComponent.pyd and Qt6Component.dll
del Q*tSerialPort* Qt*DBus* Qt*Designer* Qt*JsonRpc* Qt*Labs* Qt*LanguageServer* Qt*Network*
del Qt*Qml* Qt*Quick* Qt*RemoteObjects* Qt*Sensors* Qt*Sql* Qt*Test* Qt*WebChannel*
del Qt*Bluetooth* Qt*Charts* Qt*Concurrent* Qt*DataVisualization* Qt*Graphs* Qt*HttpServer*
del Qt*Nfc* Qt*Positioning* Qt*Scxml* Qt*SerialBus* Qt*SerialPort* Qt*ShaderTools*
del Qt*StateMachine* Qt*Test* Qt*TextToSpeech* Qt*Web* Qt*3D*
del Qt*Help* Qt*Multimedia* Qt*Xml*

:: Unused audio/video codec DLLs
del avformat-*.dll avutil-*.dll swresample-*.dll swscale-*.dll
:: Unused OpenGL bindings. The Qt6OpenGL DLLs are required and thus not removed
del QtOpenGL.pyd QtOpenGLWidgets.pyd opengl32sw.dll


pushd translations
:: Remove translations for unused/removed components
del assistant* designer* linguist* qtdeclarative*

:: leave translations
popd

pushd plugins
del /Q /S tls

:: leave plugins
popd

:: leave PySide6
popd


del shiboken6\shiboken6*.lib
del email\architecture.rst

:: leave lib
popd
::leave build directory
popd


