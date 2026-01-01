#!/bin/bash

# Script to switch ethernet interface between two IP addresses
# Usage: ./switch_eth_address.sh [interface]
# Example: ./switch_eth_address.sh eth0

set -e

# Configuration
INTERFACE="${1:-enp5s0}"

# Network Profile 1
ADDRESS1="192.168.1.100/24"
NETWORK1="192.168.1.0/24"

# Network Profile 2
ADDRESS2="10.11.12.100/24"
NETWORK2="10.11.12.0/24"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Check if interface exists
if ! ip link show "$INTERFACE" &> /dev/null; then
    echo "Error: Interface $INTERFACE does not exist"
    echo "Available interfaces:"
    ip -br link show
    exit 1
fi

# Function to get current IP (without CIDR)
get_current_ip() {
    ip -4 addr show "$INTERFACE" | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n1
}

# Function to apply configuration
apply_config() {
    local address=$1
    local profile_name=$2

    echo "Switching $INTERFACE to Profile $profile_name"

    # Remove any existing network-specific routes
    echo "  Removing old routes..."
    ip route del "$NETWORK1" 2>/dev/null || true
    ip route del "$NETWORK2" 2>/dev/null || true

    echo "  IP: $address"

    # Flush current IP addresses and associated routes
    ip addr flush dev "$INTERFACE"

    # Add new IP address (kernel will automatically add connected route)
    ip addr add "$address" dev "$INTERFACE"

    # Bring interface up
    ip link set "$INTERFACE" up

    echo "✓ Successfully switched to $address"
}

# Determine current IP and switch to the other
CURRENT_IP=$(get_current_ip)

echo "Current IP on $INTERFACE: ${CURRENT_IP:-none}"
echo ""

if [[ "$CURRENT_IP" == "192.168.1.100" ]]; then
    # Currently on profile 1, switch to profile 2
    apply_config "$ADDRESS2" "2 (10.11.12.x)"
elif [[ "$CURRENT_IP" == "10.11.12.100" ]]; then
    # Currently on profile 2, switch to profile 1
    apply_config "$ADDRESS1" "1 (192.168.1.x)"
else
    # Unknown or no IP, default to profile 1
    echo "No recognized IP detected, switching to Profile 1 (192.168.1.x)"
    apply_config "$ADDRESS1" "1 (192.168.1.x)"
fi

# Display final status
echo ""
echo "═══════════════════════════════════════"
echo "Current configuration:"
echo "═══════════════════════════════════════"
ip -4 addr show "$INTERFACE" | grep inet
echo ""
echo "Routes:"
ip route show
echo "═══════════════════════════════════════"
