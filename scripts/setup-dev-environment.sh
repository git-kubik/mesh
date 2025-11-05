#!/bin/bash
# setup-dev-environment.sh - Set up development environment for mesh project
# Usage: ./scripts/setup-dev-environment.sh

set -euo pipefail
IFS=$'\n\t'

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly PROJECT_ROOT

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_step() {
    echo -e "${BLUE}==>${NC} $*"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        log_info "$1 is installed"
        return 0
    else
        log_warn "$1 is not installed"
        return 1
    fi
}

main() {
    log_step "Setting up development environment for OpenWrt Mesh Network"
    echo

    cd "${PROJECT_ROOT}"

    # Check prerequisites
    log_step "Checking prerequisites..."

    local missing_deps=0

    if ! check_command python3; then
        log_error "Python 3 is required. Please install Python 3.11+"
        ((missing_deps++))
    else
        python_version=$(python3 --version | awk '{print $2}')
        log_info "Python version: ${python_version}"
    fi

    if ! check_command git; then
        log_error "Git is required. Please install Git"
        ((missing_deps++))
    fi

    if ! check_command docker; then
        log_warn "Docker is not installed. Docker is needed for deployment."
    fi

    if [ ${missing_deps} -gt 0 ]; then
        log_error "Missing required dependencies. Please install them and try again."
        exit 1
    fi

    echo

    # Check for UV package manager
    log_step "Checking for UV package manager..."
    if ! check_command uv; then
        log_warn "UV is not installed. Installing UV..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="${HOME}/.cargo/bin:${PATH}"

        if check_command uv; then
            log_info "UV installed successfully"
        else
            log_warn "UV installation may require shell restart. Using pip instead."
        fi
    fi

    echo

    # Install Python development dependencies
    log_step "Installing Python development dependencies..."

    if command -v uv &> /dev/null; then
        log_info "Using UV to install dependencies..."
        uv pip install -r requirements-dev.txt
    else
        log_info "Using pip to install dependencies..."
        python3 -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    fi

    echo

    # Install pre-commit hooks
    log_step "Installing pre-commit hooks..."

    if pre-commit install; then
        log_info "Pre-commit hooks installed successfully"
    else
        log_error "Failed to install pre-commit hooks"
        exit 1
    fi

    # Install commit message hook
    if pre-commit install --hook-type commit-msg; then
        log_info "Commit message hooks installed"
    fi

    echo

    # Run pre-commit on all files to verify setup
    log_step "Running pre-commit checks to verify setup..."

    if pre-commit run --all-files; then
        log_info "All pre-commit checks passed!"
    else
        log_warn "Some pre-commit checks failed. This is normal on first run."
        log_warn "Pre-commit has auto-fixed some issues. Review changes with 'git diff'"
    fi

    echo

    # Create .secrets.baseline if it doesn't exist
    if [ ! -f .secrets.baseline ]; then
        log_step "Creating secrets baseline..."
        detect-secrets scan --baseline .secrets.baseline
        log_info "Secrets baseline created"
    fi

    echo

    # Verify test environment
    log_step "Verifying test environment..."

    if pytest tests/unit/ --co -q 2>/dev/null; then
        test_count=$(pytest tests/unit/ --co -q 2>/dev/null | wc -l)
        log_info "Found ${test_count} unit tests"
    else
        log_warn "Unit tests directory not fully set up yet"
    fi

    echo

    # Check Docker setup
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        log_step "Checking Docker setup..."

        if [ -f docker/docker-compose.yml ]; then
            log_info "Docker Compose configuration found"
            log_info "To start Docker environment: cd docker && docker-compose up -d"
        else
            log_warn "Docker Compose configuration not found yet"
        fi
    fi

    echo

    # Summary
    log_step "Development environment setup complete!"
    echo
    echo "Next steps:"
    echo "  1. Review pre-commit configuration: .pre-commit-config.yaml"
    echo "  2. Read contributing guidelines: CONTRIBUTING.md"
    echo "  3. Check project standards: use 'project-standards' skill"
    echo "  4. Run tests: pytest tests/unit/ -v"
    echo "  5. Format code: black . && isort ."
    echo "  6. Check quality: pre-commit run --all-files"
    echo
    echo "Pre-commit hooks are now active and will run automatically on 'git commit'"
    echo "To bypass hooks (not recommended): git commit --no-verify"
    echo
    log_info "Happy coding! 🚀"
}

main "$@"
