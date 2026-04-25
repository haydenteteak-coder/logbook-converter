@echo off
cd /d "%~dp0"

echo Starting Airline Logbook Converter...
echo.

set "PYTHON_CMD="

py --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py"
)

if not defined PYTHON_CMD (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo Python was not found.
    echo Install Python 3 and then run:
    echo py -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

%PYTHON_CMD% -m streamlit --version >nul 2>&1
if errorlevel 1 (
    echo Streamlit is not installed for this Python interpreter.
    echo Run:
    echo %PYTHON_CMD% -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

%PYTHON_CMD% -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo The app did not start.
    echo Make sure dependencies are installed and run:
    echo %PYTHON_CMD% -m pip install -r requirements.txt
    echo.
    pause
)
