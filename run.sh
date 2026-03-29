#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

PRODUCT="${*:-wireless keyboard}"

echo "=== Porcurment Deal Finder ==="
echo "Searching for: $PRODUCT"
echo ""

python3 -m src.flows.main_flow "$PRODUCT"
