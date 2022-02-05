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
call clean_windows_build.bat
python setup_cx_freeze.py bdist_msi --skip-build
