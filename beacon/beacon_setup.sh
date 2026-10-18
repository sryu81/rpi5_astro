#!/bin/bash
# =============================================================================
# astro-beacon Setup Script
# Installs a systemd service that broadcasts this Pi's hostname/IP over UDP
# so it can be located on the local network with find_pi.py.
# Run on the Raspberry Pi:  bash beacon/beacon_setup.sh
# =============================================================================

set -e  # Exit on any error

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BEACON_PORT="${BEACON_PORT:-50505}"
BEACON_INTERVAL="${BEACON_INTERVAL:-5}"

[ -f "${SCRIPT_DIR}/astro-beacon.py" ] || error "astro-beacon.py not found next to this script."

# =============================================================================
# Step 1 — Install beacon script
# =============================================================================
info "Step 1 — Installing /usr/local/bin/astro-beacon..."
sudo install -m 755 "${SCRIPT_DIR}/astro-beacon.py" /usr/local/bin/astro-beacon
success "Beacon script installed."

# =============================================================================
# Step 2 — Create systemd service
# =============================================================================
info "Step 2 — Creating systemd service..."

sudo tee /etc/systemd/system/astro-beacon.service > /dev/null << EOF
[Unit]
Description=rpi5_astro LAN discovery beacon (UDP broadcast)
Wants=network-online.target
After=network-online.target

[Service]
Environment=BEACON_PORT=${BEACON_PORT}
Environment=BEACON_INTERVAL=${BEACON_INTERVAL}
ExecStart=/usr/bin/python3 /usr/local/bin/astro-beacon
DynamicUser=yes
SupplementaryGroups=video
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

success "Service created."

# =============================================================================
# Step 3 — Enable and start
# =============================================================================
info "Step 3 — Enabling and starting astro-beacon..."
sudo systemctl daemon-reload
sudo systemctl enable --now astro-beacon.service
sleep 1

if systemctl is-active --quiet astro-beacon.service; then
    success "astro-beacon is running (UDP ${BEACON_PORT}, every ${BEACON_INTERVAL}s)."
else
    error "astro-beacon failed to start. Check: journalctl -u astro-beacon.service"
fi

echo ""
echo "  On your laptop (same network):  python3 find_pi.py"
echo ""
