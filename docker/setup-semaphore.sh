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

# Authenticate and get token
get_auth_token() {
    log_step "Authenticating with Semaphore..."

    local response
    response=$(curl -s -X POST "${SEMAPHORE_URL}/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"auth\":\"${SEMAPHORE_ADMIN}\",\"password\":\"${SEMAPHORE_ADMIN_PASSWORD}\"}")

    # Extract token from response
    local token
    token=$(echo "$response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

    if [ -z "$token" ]; then
        log_error "Failed to authenticate with Semaphore"
        log_error "Response: $response"
        return 1
    fi

    log_info "Authentication successful"
    echo "$token"
}

# Create project
create_project() {
    local token="$1"
    log_step "Creating Mesh Network project..."

    local response
    response=$(curl -s -X POST "${SEMAPHORE_URL}/api/projects" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${token}" \
        -d '{
            "name": "OpenWrt Mesh Network",
            "alert": false,
            "alert_chat": null,
            "max_parallel_tasks": 1
        }')

    # Extract project ID
    local project_id
    project_id=$(echo "$response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

    if [ -z "$project_id" ]; then
        log_warn "Project may already exist or creation failed"
        log_info "Attempting to find existing project..."

        # Try to get existing projects
        response=$(curl -s -X GET "${SEMAPHORE_URL}/api/projects" \
            -H "Authorization: Bearer ${token}")

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
    local token="$1"
    local project_id="$2"
    log_step "Creating inventory..."

    local response
    response=$(curl -s -X POST "${SEMAPHORE_URL}/api/project/${project_id}/inventory" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${token}" \
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
            -H "Authorization: Bearer ${token}")
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
    local token="$1"
    local project_id="$2"
    log_step "Creating environment..."

    local response
    response=$(curl -s -X POST "${SEMAPHORE_URL}/api/project/${project_id}/environment" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${token}" \
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
            -H "Authorization: Bearer ${token}")
        env_id=$(echo "$response" | grep -o '"name":"Production".*"id":[0-9]*' | grep -o '"id":[0-9]*' | cut -d':' -f2 | head -1)

        if [ -n "$env_id" ]; then
            log_info "Found existing environment with ID: $env_id"
        fi
    else
        log_info "Environment created with ID: $env_id"
    fi

    echo "$env_id"
}

# Create template for deployment
create_template() {
    local token="$1"
    local project_id="$2"
    local inventory_id="$3"
    local env_id="$4"
    local name="$5"
    local playbook="$6"

    log_step "Creating template: $name..."

    local response
    response=$(curl -s -X POST "${SEMAPHORE_URL}/api/project/${project_id}/templates" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${token}" \
        -d '{
            "project_id": '"${project_id}"',
            "inventory_id": '"${inventory_id}"',
            "environment_id": '"${env_id}"',
            "name": "'"${name}"'",
            "playbook": "'"${playbook}"'",
            "arguments": "",
            "allow_override_args_in_task": false,
            "suppress_success_alerts": true,
            "survey_vars": null,
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
    local token
    if ! token=$(get_auth_token); then
        exit 1
    fi

    echo

    # Create project
    local project_id
    if ! project_id=$(create_project "$token"); then
        exit 1
    fi

    echo

    # Create inventory
    local inventory_id
    if ! inventory_id=$(create_inventory "$token" "$project_id"); then
        log_error "Failed to create inventory"
        exit 1
    fi

    echo

    # Create environment
    local env_id
    if ! env_id=$(create_environment "$token" "$project_id"); then
        log_error "Failed to create environment"
        exit 1
    fi

    echo

    # Create templates
    create_template "$token" "$project_id" "$inventory_id" "$env_id" \
        "Deploy Mesh Network" "/ansible/playbooks/deploy.yml"

    create_template "$token" "$project_id" "$inventory_id" "$env_id" \
        "Verify Deployment" "/ansible/playbooks/verify.yml"

    create_template "$token" "$project_id" "$inventory_id" "$env_id" \
        "Backup Node Configs" "/ansible/playbooks/backup.yml"

    echo
    log_step "Semaphore setup complete!"
    echo
    log_info "Access Semaphore at: ${SEMAPHORE_URL}"
    log_info "Username: ${SEMAPHORE_ADMIN}"
    log_info "Password: ${SEMAPHORE_ADMIN_PASSWORD}"
    echo
    log_info "Project: OpenWrt Mesh Network"
    log_info "Project ID: ${project_id}"
    log_info "Inventory ID: ${inventory_id}"
    echo
}

main "$@"
