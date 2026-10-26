#!/usr/bin/env bash
# ==============================================================================
# Starts the cybersecurity lab environment
# ==============================================================================

set -euo pipefail

echo "[*] Initializing Cybersecurity Lab Environment..."
docker compose up -d --build

echo "[+] Lab environment active. Verifying configuration..."
"$(dirname "$0")/verify_network.sh"
