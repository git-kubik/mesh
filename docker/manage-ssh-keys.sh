#!/bin/bash
# manage-ssh-keys.sh - SSH key management for mesh network Docker environment
# Usage: ./manage-ssh-keys.sh [generate|import|export|list|test]

set -euo pipefail
IFS=$'\n\t'

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Docker volume name
readonly VOLUME_NAME="mesh_ssh-keys"

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

# Generate new SSH key pair
generate_keys() {
    log_step "Generating new SSH key pair for mesh network..."

    local key_file="mesh_key"
    local key_type="ed25519"

    if [ -f "${key_file}" ]; then
        log_warn "Key file ${key_file} already exists"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Cancelled"
            return 1
        fi
    fi

    ssh-keygen -t "${key_type}" -C "mesh-ansible-$(date +%Y%m%d)" -f "${key_file}" -N ""

    log_info "SSH key pair generated:"
    log_info "  Private key: ${key_file}"
    log_info "  Public key: ${key_file}.pub"
    echo
    log_info "Next steps:"
    echo "  1. Import keys to Docker: ./manage-ssh-keys.sh import ${key_file}"
    echo "  2. Copy public key to nodes: ssh-copy-id -i ${key_file}.pub root@NODE_IP"
}

# Import SSH keys to Docker volume
import_keys() {
    local key_file="${1:-}"

    if [ -z "${key_file}" ]; then
        log_error "Usage: $0 import <key_file>"
        return 1
    fi

    if [ ! -f "${key_file}" ]; then
        log_error "Key file not found: ${key_file}"
        return 1
    fi

    if [ ! -f "${key_file}.pub" ]; then
        log_error "Public key not found: ${key_file}.pub"
        return 1
    fi

    log_step "Importing SSH keys to Docker volume ${VOLUME_NAME}..."

    # Copy keys to volume with proper permissions
    docker run --rm \
        -v "${VOLUME_NAME}:/keys" \
        -v "$(pwd):/src" \
        alpine sh -c "
            cp /src/${key_file} /keys/id_ed25519 && \
            cp /src/${key_file}.pub /keys/id_ed25519.pub && \
            chmod 600 /keys/id_ed25519 && \
            chmod 644 /keys/id_ed25519.pub && \
            ls -la /keys/
        "

    log_info "SSH keys imported successfully"
    log_info "Keys are now available in Docker volume: ${VOLUME_NAME}"
    echo
    log_info "Restart Ansible container to use new keys:"
    echo "  docker-compose restart ansible"
}

# Export SSH keys from Docker volume
export_keys() {
    local output_dir="${1:-.}"

    log_step "Exporting SSH keys from Docker volume ${VOLUME_NAME}..."

    docker run --rm \
        -v "${VOLUME_NAME}:/keys" \
        -v "$(pwd)/${output_dir}:/output" \
        alpine sh -c "
            cp /keys/id_ed25519 /output/mesh_key_backup && \
            cp /keys/id_ed25519.pub /output/mesh_key_backup.pub && \
            chmod 600 /output/mesh_key_backup && \
            chmod 644 /output/mesh_key_backup.pub
        "

    log_info "SSH keys exported to: ${output_dir}/mesh_key_backup"
    log_warn "Store backup securely and delete from disk after backing up"
}

# List SSH keys in Docker volume
list_keys() {
    log_step "SSH keys in Docker volume ${VOLUME_NAME}:"
    echo

    docker run --rm \
        -v "${VOLUME_NAME}:/keys" \
        alpine ls -lah /keys/

    echo
    log_info "To view public key:"
    echo "  docker run --rm -v ${VOLUME_NAME}:/keys alpine cat /keys/id_ed25519.pub"
}

# Test SSH connectivity to nodes
test_connectivity() {
    log_step "Testing SSH connectivity to mesh nodes..."

    local nodes=("10.11.12.1" "10.11.12.2" "10.11.12.3")

    for node in "${nodes[@]}"; do
        log_info "Testing connection to ${node}..."

        if docker-compose exec -T ansible ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "root@${node}" "echo 'Connected successfully'" 2>/dev/null; then
            log_info "✓ ${node} - SSH connection successful"
        else
            log_warn "✗ ${node} - SSH connection failed"
        fi
    done
}

# Show usage
usage() {
    cat <<EOF
SSH Key Management for OpenWrt Mesh Network

Usage: $0 <command> [options]

Commands:
  generate              Generate new SSH key pair
  import <key_file>     Import SSH keys to Docker volume
  export [output_dir]   Export SSH keys from Docker volume (default: .)
  list                  List SSH keys in Docker volume
  test                  Test SSH connectivity to mesh nodes

Examples:
  # Generate new keys
  $0 generate

  # Import existing keys
  $0 import ~/.ssh/id_ed25519

  # Export keys for backup
  $0 export ./backup

  # List current keys
  $0 list

  # Test connectivity
  $0 test

EOF
}

main() {
    local command="${1:-}"

    case "${command}" in
        generate)
            generate_keys
            ;;
        import)
            import_keys "${2:-}"
            ;;
        export)
            export_keys "${2:-.}"
            ;;
        list)
            list_keys
            ;;
        test)
            test_connectivity
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: ${command}"
            echo
            usage
            exit 1
            ;;
    esac
}

main "$@"
