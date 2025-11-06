#!/bin/bash
# setup-semaphore.sh - Automated Semaphore configuration for mesh network
# This script uses Semaphore API to create project, inventory, and templates

set -euo pipefail

# Load environment variables from .env
if [ -f .env ]; then
    # shellcheck disable=SC1091
    source .env
else
    echo "ERROR: .env file not found!"
    echo "Please create .env file with SEMAPHORE_ADMIN and SEMAPHORE_ADMIN_PASSWORD"
    echo "See .env.example for reference"
    exit 1
fi

# Configuration (from .env)
SEMAPHORE_URL="${SEMAPHORE_URL:-http://localhost:3000}"
SEMAPHORE_ADMIN="${SEMAPHORE_ADMIN:?SEMAPHORE_ADMIN not set in .env}"
SEMAPHORE_ADMIN_PASSWORD="${SEMAPHORE_ADMIN_PASSWORD:?SEMAPHORE_ADMIN_PASSWORD not set in .env}"

# Colors
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_step() {
    echo -e "${BLUE}==>${NC} $*" >&2
}

# Wait for Semaphore to be ready
wait_for_semaphore() {
    log_step "Waiting for Semaphore to be ready..."
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "${SEMAPHORE_URL}/api/ping" > /dev/null 2>&1; then
            log_info "Semaphore is ready"
            return 0
        fi
        log_info "Attempt $attempt/$max_attempts - waiting for Semaphore..."
        sleep 2
        ((attempt++))
    done

    log_error "Semaphore did not become ready in time"
    return 1
}

# Authenticate and get cookie
get_auth_cookie() {
    log_step "Authenticating with Semaphore..."

    local cookie_file="/tmp/semaphore-cookie-$$"
    local status_code

    status_code=$(curl -s -o /dev/null -w "%{http_code}" -c "$cookie_file" \
        -X POST "${SEMAPHORE_URL}/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"auth\":\"${SEMAPHORE_ADMIN}\",\"password\":\"${SEMAPHORE_ADMIN_PASSWORD}\"}")

    log_info "Auth status code: $status_code"
    log_info "Cookie file: $cookie_file"

    if [ "$status_code" != "204" ]; then
        log_error "Failed to authenticate with Semaphore (HTTP $status_code)"
        rm -f "$cookie_file"
        return 1
    fi

    if [ ! -f "$cookie_file" ]; then
        log_error "Cookie file was not created"
        return 1
    fi

    log_info "Authentication successful"
    echo "$cookie_file"
}

# Create project
create_project() {
    local cookie_file="$1"
    log_step "Creating Mesh Network project..."

    local response
    response=$(curl -s -b "$cookie_file" -X POST "${SEMAPHORE_URL}/api/projects" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "OpenWrt Mesh Network",
            "alert": false,
            "alert_chat": null,
            "max_parallel_tasks": 1
        }')

    # Extract project ID
    local project_id
    project_id=$(echo "$response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

    log_info "Project creation response: $response"
    log_info "Extracted project_id: $project_id"

    if [ -z "$project_id" ]; then
        log_warn "Project may already exist or creation failed"
        log_info "Attempting to find existing project..."

        # Try to get existing projects
        response=$(curl -s -b "$cookie_file" -X GET "${SEMAPHORE_URL}/api/projects")

        # Look for mesh network project
        project_id=$(echo "$response" | grep -o '"name":"OpenWrt Mesh Network".*"id":[0-9]*' | grep -o '"id":[0-9]*' | cut -d':' -f2 | head -1)

        if [ -n "$project_id" ]; then
            log_info "Found existing project with ID: $project_id"
        else
            log_error "Failed to create or find project"
            return 1
        fi
    else
        log_info "Project created with ID: $project_id"
    fi

    echo "$project_id"
}

# Create inventory
create_inventory() {
    local cookie_file="$1"
    local project_id="$2"
    log_step "Creating inventory..."

    local response
    response=$(curl -s -X POST "${SEMAPHORE_URL}/api/project/${project_id}/inventory" \
        -H "Content-Type: application/json" \
        -b "$cookie_file" \
        -d '{
            "name": "Mesh Nodes",
            "project_id": '"${project_id}"',
            "inventory": "/ansible/inventory/hosts.yml",
            "type": "file"
        }')

    local inventory_id
    inventory_id=$(echo "$response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

    if [ -z "$inventory_id" ]; then
        log_warn "Inventory may already exist"
        # Try to get existing inventory
        response=$(curl -s -X GET "${SEMAPHORE_URL}/api/project/${project_id}/inventory" \
            -b "$cookie_file")
        inventory_id=$(echo "$response" | grep -o '"name":"Mesh Nodes".*"id":[0-9]*' | grep -o '"id":[0-9]*' | cut -d':' -f2 | head -1)

        if [ -n "$inventory_id" ]; then
            log_info "Found existing inventory with ID: $inventory_id"
        fi
    else
        log_info "Inventory created with ID: $inventory_id"
    fi

    echo "$inventory_id"
}

# Create environment (for variables)
create_environment() {
    local cookie_file="$1"
    local project_id="$2"
    log_step "Creating environment..."

    local response
    response=$(curl -s -X POST "${SEMAPHORE_URL}/api/project/${project_id}/environment" \
        -H "Content-Type: application/json" \
        -b "$cookie_file" \
        -d '{
            "name": "Production",
            "project_id": '"${project_id}"',
            "json": "{}",
            "env": null
        }')

    local env_id
    env_id=$(echo "$response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

    if [ -z "$env_id" ]; then
        log_warn "Environment may already exist"
        response=$(curl -s -X GET "${SEMAPHORE_URL}/api/project/${project_id}/environment" \
            -b "$cookie_file")
        env_id=$(echo "$response" | grep -o '"name":"Production".*"id":[0-9]*' | grep -o '"id":[0-9]*' | cut -d':' -f2 | head -1)

        if [ -n "$env_id" ]; then
            log_info "Found existing environment with ID: $env_id"
        fi
    else
        log_info "Environment created with ID: $env_id"
    fi

    echo "$env_id"
}

# Create empty key (for local files - no repo needed)
create_empty_key() {
    local cookie_file="$1"
    local project_id="$2"
    log_step "Creating empty SSH key..."

    local response
    response=$(curl -s -b "$cookie_file" -X POST "${SEMAPHORE_URL}/api/project/${project_id}/keys" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "None (local files)",
            "type": "none",
            "project_id": '"${project_id}"'
        }')

    local key_id
    key_id=$(echo "$response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

    if [ -z "$key_id" ]; then
        log_warn "Key may already exist"
        # Try to get existing key
        response=$(curl -s -b "$cookie_file" -X GET "${SEMAPHORE_URL}/api/project/${project_id}/keys")
        key_id=$(echo "$response" | grep -o '"name":"None (local files)".*"id":[0-9]*' | grep -o '"id":[0-9]*' | cut -d':' -f2 | head -1)

        if [ -n "$key_id" ]; then
            log_info "Found existing key with ID: $key_id"
        fi
    else
        log_info "Key created with ID: $key_id"
    fi

    echo "$key_id"
}

# Create repository (none type for local files)
create_repository() {
    local cookie_file="$1"
    local project_id="$2"
    local key_id="$3"
    log_step "Creating repository..."

    local response
    response=$(curl -s -b "$cookie_file" -X POST "${SEMAPHORE_URL}/api/project/${project_id}/repositories" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Local Ansible Files",
            "project_id": '"${project_id}"',
            "git_url": "file:///ansible",
            "git_branch": "main",
            "ssh_key_id": '"${key_id}"'
        }')

    local repo_id
    repo_id=$(echo "$response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

    log_info "Repository creation response: $response"
    log_info "Extracted repo_id: $repo_id"

    if [ -z "$repo_id" ]; then
        log_warn "Repository may already exist"
        # Try to get existing repository
        response=$(curl -s -b "$cookie_file" -X GET "${SEMAPHORE_URL}/api/project/${project_id}/repositories")
        repo_id=$(echo "$response" | grep -o '"name":"Local Ansible Files".*"id":[0-9]*' | grep -o '"id":[0-9]*' | cut -d':' -f2 | head -1)

        if [ -n "$repo_id" ]; then
            log_info "Found existing repository with ID: $repo_id"
        fi
    else
        log_info "Repository created with ID: $repo_id"
    fi

    echo "$repo_id"
}

# Create template for deployment
create_template() {
    local cookie_file="$1"
    local project_id="$2"
    local inventory_id="$3"
    local repo_id="$4"
    local env_id="$5"
    local name="$6"
    local playbook="$7"

    log_step "Creating template: $name..."

    local response
    response=$(curl -s -X POST "${SEMAPHORE_URL}/api/project/${project_id}/templates" \
        -H "Content-Type: application/json" \
        -b "$cookie_file" \
        -d '{
            "project_id": '"${project_id}"',
            "inventory_id": '"${inventory_id}"',
            "repository_id": '"${repo_id}"',
            "environment_id": '"${env_id}"',
            "name": "'"${name}"'",
            "playbook": "'"${playbook}"'",
            "app": "ansible",
            "suppress_success_alerts": false,
            "type": ""
        }')

    local template_id
    template_id=$(echo "$response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

    if [ -z "$template_id" ]; then
        log_warn "Template '$name' may already exist"
    else
        log_info "Template '$name' created with ID: $template_id"
    fi
}

main() {
    log_step "Semaphore Automated Setup for Mesh Network"
    echo

    # Wait for Semaphore
    if ! wait_for_semaphore; then
        exit 1
    fi

    echo

    # Authenticate
    local cookie_file
    if ! cookie_file=$(get_auth_cookie); then
        exit 1
    fi

    echo

    # Create project
    local project_id
    if ! project_id=$(create_project "$cookie_file"); then
        exit 1
    fi

    echo

    # Create inventory
    local inventory_id
    if ! inventory_id=$(create_inventory "$cookie_file" "$project_id"); then
        log_error "Failed to create inventory"
        exit 1
    fi

    echo

    # Create environment
    local env_id
    if ! env_id=$(create_environment "$cookie_file" "$project_id"); then
        log_error "Failed to create environment"
        exit 1
    fi

    echo

    # Create key
    local key_id
    if ! key_id=$(create_empty_key "$cookie_file" "$project_id"); then
        log_error "Failed to create key"
        exit 1
    fi

    echo

    # Create repository
    local repo_id
    if ! repo_id=$(create_repository "$cookie_file" "$project_id" "$key_id"); then
        log_error "Failed to create repository"
        exit 1
    fi

    echo

    # Create templates
    create_template "$cookie_file" "$project_id" "$inventory_id" "$repo_id" "$env_id" \
        "Deploy Mesh Network" "playbooks/deploy.yml"

    create_template "$cookie_file" "$project_id" "$inventory_id" "$repo_id" "$env_id" \
        "Verify Deployment" "playbooks/verify.yml"

    create_template "$cookie_file" "$project_id" "$inventory_id" "$repo_id" "$env_id" \
        "Backup Node Configs" "playbooks/backup.yml"

    create_template "$cookie_file" "$project_id" "$inventory_id" "$repo_id" "$env_id" \
        "Update Nodes" "playbooks/update.yml"

    # Cleanup cookie file
    rm -f "$cookie_file"

    echo
    log_step "Semaphore setup complete!"
    echo
    log_info "Access Semaphore at: ${SEMAPHORE_URL}"
    log_info "Username: ${SEMAPHORE_ADMIN}"
    log_info "Password: ${SEMAPHORE_ADMIN_PASSWORD}"
    echo
    log_info "Project: OpenWrt Mesh Network"
    log_info "  Project ID: ${project_id}"
    log_info "  Inventory ID: ${inventory_id}"
    log_info "  Repository ID: ${repo_id}"
    log_info "  Environment ID: ${env_id}"
    log_info "  Key ID: ${key_id}"
    echo
    log_info "Task Templates:"
    log_info "  ✓ Deploy Mesh Network (playbooks/deploy.yml)"
    log_info "  ✓ Verify Deployment (playbooks/verify.yml)"
    log_info "  ✓ Backup Node Configs (playbooks/backup.yml)"
    log_info "  ✓ Update Nodes (playbooks/update.yml)"
    echo
    log_info "You can now run playbooks from: ${SEMAPHORE_URL}"
    echo
}

main "$@"
