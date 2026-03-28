:: Generate an application bundle using cx_Freeze

:: Create or activate the build environment
IF EXIST "venv" (
  call venv\Scripts\activate.bat
) ELSE (
  call create_development_environment.bat
)

:: Create a platform-dependent, portable build in the build directory
:: and an MSI-based installer in the dist directory.
:: Also creates a cross-platform Python sdist and wheel package in the dist directory.
tox run -e package_wheel,package_cx_freeze
