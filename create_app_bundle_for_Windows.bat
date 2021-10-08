:: Generate an application bundle using cx_Freeze

:: Create or activate the build environment
IF EXIST "venv" (
  call venv\Scripts\activate.bat
) ELSE (
  call create_development_environment.bat
)

:: Create a platform-dependent, portable build in the build directory
:: and an MSI-based installer in the dist directory
python setup_cx_freeze.py build_exe
pushd build\exe*
del lib\PyQt5\*.dll
del lib\ijson\backends\python*.dll
rmdir /S /Q PyQt5.uic.widget-plugins
popd
python setup_cx_freeze.py bdist_msi
