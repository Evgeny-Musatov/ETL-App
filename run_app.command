#!/bin/bash
cd "$(dirname "$0")"
echo "Starting ETL App..."

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "Virtual environment (.venv) not found."
    echo "Please set up the environment first."
    read -p "Press Enter to exit..."
    exit 1
fi

# Run directly using the venv python executable
echo "Launching application..."
.venv/bin/python -m streamlit run app.py

# Keep window open on exit (like 'pause' in Windows)
echo ""
echo "Application closed."
read -p "Press Enter to exit..."
