#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 Setting up Environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

# Install dependencies
echo "Installing dependencies..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo "You can now run 'run_app.command' to start the application."
echo ""
read -p "Press Enter to exit..."
