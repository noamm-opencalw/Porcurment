#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Porcurment Setup ==="

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating venv..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -e .

echo "Copying .env template..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env — please fill in your API keys."
else
    echo ".env already exists, skipping."
fi

echo ""
echo "=== Setup complete! ==="
echo "Activate with: source .venv/bin/activate"
echo "Run UI with:   streamlit run app.py"
