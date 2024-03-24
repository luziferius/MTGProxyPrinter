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

:: Some versions of cx_Freeze copy the python DLL here
:: So remove duplicates, if present
del ijson\backends\python*.dll


pushd PySide6

:: Don't need the executables, like Qt Designer, etc
del *.exe

:: Remove unused QML-related DLLs and bindings
del Qt*Qml* Qt*Quick* Qt*Labs*
del Qt6Designer.dll QtDesigner.pyi QtDesigner.pyd
del Qt*Test*
:: Unused OpenGL bindings. The Qt6OpenGL DLLs are required and thus not removed
del QtOpenGL.pyd QtOpenGLWidgets.pyd opengl32sw.dll
del Qt*DBus*
del Qt*JsonRpc*
del Qt*Sql*
del Qt*Network*
del Qt*LanguageServer*
:: Delete all typing stubs
del *.pyi

pushd translations
:: Remove translations for unused/removed components
del assistant* designer* linguist* qtdeclarative*
:: leave translations
popd

pushd plugins\imageformats
:: Unused image format libraries, around 1.3 MiB
del qwebp.dll qtiff.dll qjpeg.dll
::leave plugins\imageformats
popd

:: leave PySide6
popd


del shiboken6\shiboken6*.lib
del email\architecture.rst

:: leave lib
popd
::leave build directory
popd


