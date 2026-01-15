@echo off
cd /d "%~dp0"
echo 🚀 Setting up Environment...

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo Virtual environment already exists.
)

echo Installing dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo ✅ Setup complete!
echo You can now run "run_app.bat" to start the application.
pause
