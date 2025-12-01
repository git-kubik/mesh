#!/bin/bash
###############################################################################
# Start Local OpenWrt Package Repository HTTP Server
###############################################################################

REPO_DIR="$(pwd)/openwrt-repo"
PORT=8080

# Find available port if 8080 is in use
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    echo "Port $PORT is in use, trying next port..."
    PORT=$((PORT + 1))
done

# Get local IP address
LOCAL_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -1)

if [ ! -d "$REPO_DIR" ]; then
    echo "Error: Repository directory not found: $REPO_DIR"
    echo "Please run ./scripts/setup-local-repo.sh first"
    exit 1
fi

echo "========================================"
echo "OpenWrt Local Repository Server"
echo "========================================"
echo ""
echo "Repository: $REPO_DIR"
echo "Listening on: http://${LOCAL_IP}:${PORT}"
echo ""
echo "Configure nodes with:"
echo "  OPKG_REPO_URL=http://${LOCAL_IP}:${PORT}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$REPO_DIR" || exit 1
python3 -m http.server $PORT
