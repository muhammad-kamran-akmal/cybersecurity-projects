#!/usr/bin/env bash
# ==============================================================================
# Cybersecurity Lab Environment - Phase 1 Verification Script
# Verifies container states, custom bridge network, and inter-container DNS/reachability.
# ==============================================================================

set -euo pipefail

BOLD="\033[1m"
GREEN="\033[32m"
RED="\033[31m"
YELLOW="\033[33m"
RESET="\033[0m"

echo -e "${BOLD}======================================================${RESET}"
echo -e "${BOLD}   Cybersecurity Lab: Environment Verification Test   ${RESET}"
echo -e "${BOLD}======================================================${RESET}"
echo ""

FAILURES=0

check_step() {
    local title="$1"
    local cmd="$2"
    echo -n " [*] Checking: ${title}... "
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}[PASS]${RESET}"
    else
        echo -e "${RED}[FAIL]${RESET}"
        FAILURES=$((FAILURES + 1))
    fi
}

# 1. Verify container existence and running state
check_step "Container 'attacker' is running" "docker compose ps --status running --format '{{.Name}}' | grep -qw attacker"
check_step "Container 'target' is running" "docker compose ps --status running --format '{{.Name}}' | grep -qw target"

# 2. Verify network existence
check_step "Custom network 'lab-network' exists" "docker network ls --format '{{.Name}}' | grep -qw lab-network"

# 3. Verify attachment to lab-network
check_step "'attacker' connected to 'lab-network'" "docker inspect attacker --format '{{json .NetworkSettings.Networks}}' | grep -q 'lab-network'"
check_step "'target' connected to 'lab-network'" "docker inspect target --format '{{json .NetworkSettings.Networks}}' | grep -q 'lab-network'"

# 4. Verify inter-container DNS resolution
check_step "'attacker' resolves 'target'" "docker compose exec -T attacker getent hosts target"
check_step "'target' resolves 'attacker'" "docker compose exec -T target getent hosts attacker"

echo ""
echo -e "${BOLD}--- Network Topology Details ---${RESET}"
ATTACKER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' attacker 2>/dev/null || echo "N/A")
TARGET_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' target 2>/dev/null || echo "N/A")

echo -e " Attacker Container : ${GREEN}attacker${RESET} (IP: ${YELLOW}${ATTACKER_IP}${RESET})"
echo -e " Target Container   : ${GREEN}target${RESET}   (IP: ${YELLOW}${TARGET_IP}${RESET})"
echo -e " Bridge Network     : ${GREEN}lab-network${RESET}"
echo ""

if [ "$FAILURES" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}[SUCCESS] All Phase 1 verification checks passed!${RESET}"
    exit 0
else
    echo -e "${RED}${BOLD}[ERROR] $FAILURES verification check(s) failed.${RESET}"
    exit 1
fi
