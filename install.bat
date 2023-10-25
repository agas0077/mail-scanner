python -m venv .venv
"./.venv/Scripts/python.exe" -m pip install -U pip
"./.venv/Scripts/pip.exe" install wheel
"./.venv/Scripts/pip.exe" install -r requirements.txt
echo off
echo "Installation successful!"
pause
echo on