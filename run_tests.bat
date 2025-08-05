:: Runs the unit tests

:: Create or activate the build environment
IF EXIST "venv-PySide6" (
  call venv-PySide6\Scripts\activate.bat
) ELSE (
  call create_development_environment.bat
)

tox run
