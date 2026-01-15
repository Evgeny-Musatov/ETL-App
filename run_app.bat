@echo off
cd /d "%~dp0"
echo Starting ETL App...

if not exist .venv (
    echo Virtual environment .venv not found.
    echo Please run setup_env.bat first to install dependencies.
    pause
    exit /b
)

echo Launching application...
.venv\Scripts\python.exe -m streamlit run app.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ App exited with error code: %errorlevel%
)

echo.
echo Application closed.
pause
