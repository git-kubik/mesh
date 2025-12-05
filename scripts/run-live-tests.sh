#!/bin/bash
###############################################################################
# Run Live Network Tests
#
# Executes the live network validation test suite against running mesh nodes.
#
# Usage:
#   ./scripts/run-live-tests.sh [options]
#
# Options:
#   --all           Run all live tests (default: skip destructive)
#   --destructive   Include destructive failover tests
#   --wlan2         Include wlan2 adapter tests
#   --quick         Run only connectivity tests (fastest)
#   --verbose       Show verbose output
#   --html          Generate HTML report
#
# Environment Variables:
#   SSH_KEY_PATH    Path to SSH key (default: ~/.ssh/openwrt_mesh_rsa)
#   MESH_RUN_DESTRUCTIVE_TESTS=true  Enable destructive tests
#
###############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Default options
RUN_DESTRUCTIVE=false
RUN_WLAN2=false
QUICK_MODE=false
VERBOSE=""
HTML_REPORT=false
PYTEST_ARGS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            RUN_DESTRUCTIVE=true
            RUN_WLAN2=true
            shift
            ;;
        --destructive)
            RUN_DESTRUCTIVE=true
            shift
            ;;
        --wlan2)
            RUN_WLAN2=true
            shift
            ;;
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE="-v"
            shift
            ;;
        --html)
            HTML_REPORT=true
            shift
            ;;
        -h|--help)
            head -30 "$0" | tail -25
            exit 0
            ;;
        *)
            PYTEST_ARGS+=("$1")
            shift
            ;;
    esac
done

cd "$PROJECT_ROOT"

# Check SSH key exists
SSH_KEY="${SSH_KEY_PATH:-$HOME/.ssh/openwrt_mesh_rsa}"
if [[ ! -f "$SSH_KEY" ]]; then
    log_error "SSH key not found: $SSH_KEY"
    log_info "Set SSH_KEY_PATH or create the key with: ssh-keygen -t rsa -b 4096 -f $SSH_KEY"
    exit 1
fi

log_info "Using SSH key: $SSH_KEY"

# Check nodes are reachable
log_info "Checking node connectivity..."
NODES=("10.11.12.1" "10.11.12.2" "10.11.12.3")
UNREACHABLE=()

for node in "${NODES[@]}"; do
    if ! ping -c 1 -W 2 "$node" &>/dev/null; then
        UNREACHABLE+=("$node")
    fi
done

if [[ ${#UNREACHABLE[@]} -gt 0 ]]; then
    log_error "Nodes unreachable: ${UNREACHABLE[*]}"
    log_info "Ensure all mesh nodes are powered on and connected"
    exit 1
fi

log_success "All nodes reachable"

# Build pytest command
PYTEST_CMD="uv run pytest tests/live/"

# Add marker filters
if [[ "$QUICK_MODE" == "true" ]]; then
    log_info "Quick mode: running connectivity tests only"
    PYTEST_CMD="$PYTEST_CMD -k 'TestNodeReachability or TestSSHAccess or TestInterNodeConnectivity'"
else
    MARKERS="live"

    if [[ "$RUN_DESTRUCTIVE" != "true" ]]; then
        MARKERS="$MARKERS and not destructive"
        log_info "Skipping destructive tests (use --destructive to include)"
    else
        export MESH_RUN_DESTRUCTIVE_TESTS=true
        log_warn "Running destructive tests - network may be temporarily disrupted"
    fi

    if [[ "$RUN_WLAN2" != "true" ]]; then
        MARKERS="$MARKERS and not wlan2"
        log_info "Skipping wlan2 tests (use --wlan2 to include)"
    fi

    PYTEST_CMD="$PYTEST_CMD -m '$MARKERS'"
fi

# Add verbose flag
if [[ -n "$VERBOSE" ]]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Add HTML report
if [[ "$HTML_REPORT" == "true" ]]; then
    REPORT_FILE="test-reports/live-tests-$(date +%Y%m%d-%H%M%S).html"
    mkdir -p test-reports
    PYTEST_CMD="$PYTEST_CMD --html=$REPORT_FILE --self-contained-html"
    log_info "HTML report will be saved to: $REPORT_FILE"
fi

# Add any extra args
if [[ ${#PYTEST_ARGS[@]} -gt 0 ]]; then
    PYTEST_CMD="$PYTEST_CMD ${PYTEST_ARGS[*]}"
fi

# Export SSH key path
export SSH_KEY_PATH="$SSH_KEY"

echo ""
log_info "Running: $PYTEST_CMD"
echo ""

# Run tests
eval "$PYTEST_CMD"
EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    log_success "All live tests passed!"
else
    log_error "Some tests failed (exit code: $EXIT_CODE)"
fi

if [[ "$HTML_REPORT" == "true" && -f "$REPORT_FILE" ]]; then
    log_info "HTML report: $REPORT_FILE"
fi

exit $EXIT_CODE
