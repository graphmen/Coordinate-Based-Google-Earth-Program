@echo off
echo.
echo ===========================================
echo   GIS Coordinate Verification Launcher
echo ===========================================
echo.

set PYTHON_PATH="venv\Scripts\python.exe"

echo [1/2] Checking and installing dependencies...
%PYTHON_PATH% -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to install dependencies. Please ensure Python is installed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Launching Web Application...
echo.
%PYTHON_PATH% -m streamlit run app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to launch Streamlit.
    pause
)

pause
