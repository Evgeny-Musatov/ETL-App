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

REM Create gcp-service-account directory if it doesn't exist
if not exist "src\gcp-service-account" (
    echo Creating gcp-service-account directory...
    mkdir "src\gcp-service-account"
    echo ✅ Created src\gcp-service-account directory
    echo    Please place your service_account.json file in this directory.
) else (
    echo gcp-service-account directory already exists.
)

REM Create config.json if it doesn't exist
if not exist "config.json" (
    echo Creating config.json...
    (
        echo {
        echo     "source_sheet_id": "",
        echo     "target_sheet_id": "",
        echo     "service_account_file": "src/gcp-service-account/service_account.json",
        echo     "start_date": "",
        echo     "end_date": ""
        echo }
    ) > config.json
    echo ✅ Created config.json
    echo    Please update config.json with your Google Sheet IDs.
) else (
    echo config.json already exists.
)

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo    1. Place your service_account.json file in src\gcp-service-account\
echo    2. Update config.json with your Google Sheet IDs
echo    3. Run "run_app.bat" to start the application.
pause
