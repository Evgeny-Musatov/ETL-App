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

# Create gcp-service-account directory if it doesn't exist
if [ ! -d "src/gcp-service-account" ]; then
    echo "Creating gcp-service-account directory..."
    mkdir -p "src/gcp-service-account"
    echo "✅ Created src/gcp-service-account directory"
    echo "   Please place your service_account.json file in this directory."
else
    echo "gcp-service-account directory already exists."
fi

# Create config.json if it doesn't exist
if [ ! -f "config.json" ]; then
    echo "Creating config.json..."
    cat > config.json << 'EOF'
{
    "source_sheet_id": "",
    "target_sheet_id": "",
    "service_account_file": "src/gcp-service-account/service_account.json",
    "start_date": "",
    "end_date": ""
}
EOF
    echo "✅ Created config.json"
    echo "   Please update config.json with your Google Sheet IDs."
else
    echo "config.json already exists."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Place your service_account.json file in src/gcp-service-account/"
echo "   2. Update config.json with your Google Sheet IDs"
echo "   3. Run 'run_app.command' to start the application."
echo ""
read -p "Press Enter to exit..."
