#!/usr/bin/env bash
# ==============================================================================
# Stops and removes the cybersecurity lab environment
# ==============================================================================

set -euo pipefail

echo "[*] Tearing down Cybersecurity Lab Environment..."
docker compose down

echo "[+] Lab environment stopped and network resources cleaned up."
