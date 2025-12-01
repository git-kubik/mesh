#!/bin/bash
# build-image.sh - Build custom OpenWrt firmware image from node snapshot
#
# Usage:
#   ./build-image.sh node1|node2|node3 [--dry-run]
#
# Prerequisites:
#   - Node snapshot in /snapshots/mesh-node{N}/ (created by make snapshot)
#   - Local package repository in /repo/
#   - Running inside Image Builder Docker container

set -euo pipefail

# Configuration
PROFILE="dlink_dir-1960-a1"
OUTPUT_DIR="/output"
SNAPSHOT_DIR="/snapshots"
SCRIPTS_DIR="/scripts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

usage() {
    echo "Usage: $0 <node> [--dry-run]"
    echo ""
    echo "Arguments:"
    echo "  node        Node name: node1, node2, or node3"
    echo "  --dry-run   Show what would be built without building"
    echo ""
    echo "Examples:"
    echo "  $0 node3           # Build image for node3"
    echo "  $0 node1 --dry-run # Show build configuration for node1"
    exit 1
}

# Parse arguments
DRY_RUN=false
NODE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        node1|node2|node3)
            NODE=$1
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "Unknown argument: $1"
            usage
            ;;
    esac
done

if [[ -z "$NODE" ]]; then
    log_error "Node name required"
    usage
fi

# Extract node number (1, 2, or 3)
NODE_NUM="${NODE#node}"
HOSTNAME="mesh-node${NODE_NUM}"
SNAPSHOT_PATH="${SNAPSHOT_DIR}/${HOSTNAME}"

log_info "Building image for ${HOSTNAME}"
log_info "Profile: ${PROFILE}"

# Verify snapshot exists
if [[ ! -d "${SNAPSHOT_PATH}" ]]; then
    log_error "Snapshot not found: ${SNAPSHOT_PATH}"
    log_error "Run 'make snapshot NODE=${NODE}' first to capture node configuration"
    exit 1
fi

log_success "Found snapshot at ${SNAPSHOT_PATH}"

###############################################################################
# Check for overlay directory (new full-snapshot format)
###############################################################################

OVERLAY_DIR="${SNAPSHOT_PATH}/overlay"

if [[ -d "${OVERLAY_DIR}" ]]; then
    log_success "Using full overlay from snapshot"
    FILE_COUNT=$(find "${OVERLAY_DIR}" -type f | wc -l)
    log_info "Overlay contains ${FILE_COUNT} files"
else
    log_error "Overlay directory not found: ${OVERLAY_DIR}"
    log_error "Run 'make snapshot NODE=${NODE}' to create a full filesystem snapshot"
    exit 1
fi

###############################################################################
# Process package list from snapshot
###############################################################################

log_info "Processing package list from snapshot..."

PACKAGES_FILE="${SNAPSHOT_PATH}/packages/installed.txt"
if [[ ! -f "${PACKAGES_FILE}" ]]; then
    log_error "Package list not found: ${PACKAGES_FILE}"
    exit 1
fi

# Get package list, filtering out base packages and kernel modules
if [[ -x "${SCRIPTS_DIR}/process-packages.py" ]]; then
    PACKAGES=$(python3 "${SCRIPTS_DIR}/process-packages.py" --snapshot "${SNAPSHOT_PATH}")
else
    log_warn "process-packages.py not found, using basic filtering"
    # Fallback: basic package filtering
    PACKAGES=$(grep -v -E '^(base-files|busybox|kernel|procd|netifd|odhcpd-ipv6only|uci|libc|libgcc|libubox|libubus|libuclient|libnl-tiny|firewall4|nftables|kmod-.*)$' "${PACKAGES_FILE}" | tr '\n' ' ')
fi

PACKAGE_COUNT=$(echo "${PACKAGES}" | tr ' ' '\n' | grep -c -v '^$')
log_info "Package list prepared (${PACKAGE_COUNT} packages)"

###############################################################################
# Show build configuration
###############################################################################

echo ""
log_info "=== Build Configuration ==="
echo "  Profile:    ${PROFILE}"
echo "  Node:       ${NODE}"
echo "  Hostname:   ${HOSTNAME}"
echo "  Snapshot:   ${SNAPSHOT_PATH}"
echo "  Overlay:    ${OVERLAY_DIR} (${FILE_COUNT} files)"
echo "  Packages:   ${PACKAGE_COUNT}"
echo ""

if [[ "${DRY_RUN}" == "true" ]]; then
    log_info "=== Overlay contents ==="
    find "${OVERLAY_DIR}" -type f | head -30
    echo "..."
    echo ""
    log_info "=== Packages to install (first 50) ==="
    echo "${PACKAGES}" | tr ' ' '\n' | grep -v '^$' | sort | head -50
    echo "..."
    echo ""
    log_warn "Dry run mode - not building image"
    exit 0
fi

###############################################################################
# Build the image
###############################################################################

log_info "Starting image build..."
echo ""

# Run make image with our configuration
# FILES= points directly to the overlay directory from snapshot
make image \
    PROFILE="${PROFILE}" \
    PACKAGES="${PACKAGES}" \
    FILES="${OVERLAY_DIR}" \
    BIN_DIR="${OUTPUT_DIR}"

# Check for output
OUTPUT_FILE=$(find "${OUTPUT_DIR}" -name "*${PROFILE}*sysupgrade.bin" -type f 2>/dev/null | head -1)

if [[ -n "${OUTPUT_FILE}" && -f "${OUTPUT_FILE}" ]]; then
    # Rename to node-specific name
    FINAL_NAME="${OUTPUT_DIR}/${HOSTNAME}-sysupgrade.bin"
    mv "${OUTPUT_FILE}" "${FINAL_NAME}"

    # Generate SHA256 (use basename for portable checksum file)
    cd "${OUTPUT_DIR}"
    sha256sum "$(basename "${FINAL_NAME}")" > "$(basename "${FINAL_NAME}").sha256"
    cd - > /dev/null

    echo ""
    log_success "Image built successfully!"
    log_info "Output: ${FINAL_NAME}"
    log_info "Size: $(du -h "${FINAL_NAME}" | cut -f1)"
    log_info "SHA256: $(cut -d' ' -f1 < "${FINAL_NAME}.sha256")"
else
    log_error "Build failed - no output image found"
    exit 1
fi
