:: Runs the unit tests

:: Create or activate the build environment
IF EXIST "venv" (
  call venv\Scripts\activate.bat
) ELSE (
  call create_development_environment.bat
)

tox
