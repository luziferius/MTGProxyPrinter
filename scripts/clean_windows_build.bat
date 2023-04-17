:: Cleanup various items that bloat the application bundle. Mostly related to unused PySide6 and Qt6 components

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
del QtOpenGL.* QtOpenGLWidgets.*
del Qt*DBus*
del Qt*JsonRpc*
del Qt*Sql*

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


