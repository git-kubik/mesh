#!/bin/sh
# Entrypoint script for Ansible container
# Handles SSH key setup and Ansible configuration

set -e

# Function to log messages
log() {
    echo "[ENTRYPOINT] $*"
}

log "Initializing Ansible container..."

# Set up SSH directory with proper permissions
mkdir -p /root/.ssh
chmod 700 /root/.ssh

# Copy SSH keys from volume if provided
if [ -d /ssh-keys ]; then
    log "Copying SSH keys from /ssh-keys volume..."
    cp /ssh-keys/* /root/.ssh/ 2>/dev/null || true
    chmod 600 /root/.ssh/id_* 2>/dev/null || true
    chmod 644 /root/.ssh/*.pub 2>/dev/null || true
    log "SSH keys copied and permissions set"
fi

# Initialize Ansible configuration if not exists
if [ ! -f /root/.ansible.cfg ]; then
    log "Creating Ansible configuration..."
    cat > /root/.ansible.cfg <<'EOF'
[defaults]
host_key_checking = False
inventory = /ansible/inventory/hosts.yml
retry_files_enabled = False
stdout_callback = yaml
callbacks_enabled = profile_tasks
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 3600

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
EOF
    log "Ansible configuration created"
fi

# Create backups directory if it doesn't exist
mkdir -p /backups
log "Backups directory ready"

# Display Ansible version
log "Ansible version:"
ansible --version

log "Initialization complete"
log "Executing command: $*"

# Execute provided command
exec "$@"
