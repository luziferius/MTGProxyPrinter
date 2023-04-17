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
:: Remove C++ code and headers
rmdir /S /Q glue include
:: Remove unused QML modules
rmdir /S /Q qml
:: Remove other unused stuff
rmdir /S /Q scripts support metatypes typesystems
:: Remove Javascript/Typescript runtime used for QML
rmdir /S /Q resources

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

pushd plugins
:: The app uses Python's sqlite3 module, thus Qt's sqldrivers aren't used
rmdir /S /Q sqldrivers qmltooling designer assetimporters
pushd imageformats
:: Unused image format libraries, around 1.3 MiB
del qwebp.dll qtiff.dll qjpeg.dll
popd
::leave plugins
popd

:: leave PySide6
popd


del shiboken6\shiboken6*.lib


:: leave lib
popd
::leave build directory
popd


