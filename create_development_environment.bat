echo Creating temporary bootstrap environment

python -m venv venv-tmp
call venv-tmp\Scripts\activate.bat
pip install "tox>=4.41"


echo Creating virtual environment ...
tox run -e generate_development_environment
call venv-tmp\Scripts\deactivate.bat
echo Deleting bootstrap environment ...
rmdir/Q /S venv-tmp
echo Bootstrap environment deleted

call venv\Scripts\activate.bat
echo Done!
