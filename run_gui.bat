@echo off
cd /d "%~dp0"
echo Starting Meta Table ETL GUI...

if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found at .venv
    pause
    exit /b
)

call .venv\Scripts\activate.bat
echo Running Streamlit...
.venv\Scripts\python.exe -m streamlit run app.py
pause
