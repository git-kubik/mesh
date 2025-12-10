# Deployment

This section covers configuration options and deployment procedures for the mesh network.

## Overview

Deployment is managed through Ansible automation with configuration stored in `group_vars/all.yml`.

## Section Contents

| Document | Description |
|----------|-------------|
| [Configuration](configuration.md) | Environment variables and secrets management |
| [SSH Keys](ssh-keys.md) | SSH key authentication setup |

## Configuration Requirements

Before deploying, you **must** configure these settings:

| Variable | Description | Example |
|----------|-------------|---------|
| `ROOT_PASSWORD` | Router root password | `SecurePass123!` |
| `MESH_PASSWORD` | 2.4GHz mesh WPA3 key | `MeshKey456!` |
| `CLIENT_PASSWORD` | 5GHz AP WPA2 key | `WiFiKey789!` |
| `SSH_KEY_PATH` | Path to SSH private key | `~/.ssh/openwrt_mesh` |

See [Configuration](configuration.md) for the complete variable reference.

## Deployment Workflow

### Single Node

```bash
# 1. Check node is reachable
make check-node NODE=1

# 2. Audit packages
make audit-node NODE=1

# 3. Deploy configuration
make deploy-node NODE=1

# 4. Verify deployment
make verify
```

### All Nodes

```bash
# Deploy to all configured nodes
make deploy

# Verify entire mesh
make verify
make batman-status
```

## Deployment Modes

| Mode | Command | Use Case |
|------|---------|----------|
| Initial | `make deploy-node NODE=1` | First-time setup from 192.168.1.1 |
| Production | `make deploy` | Update all nodes |
| Component | `make deploy-wireless` | Update specific config |
| Dry-run | `make check` | Preview changes |

## Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/your-repo/mesh.git
cd mesh
cp .env.example .env
# Edit .env with your passwords and settings
```

### 2. Deploy

```bash
cd openwrt-mesh-ansible

# Deploy to node 1
make deploy-node NODE=1

# Wait for reboot, then remaining nodes
make deploy-node NODE=2
make deploy-node NODE=3
```

### 3. Verify

```bash
make check-all      # Verify connectivity
make batman-status  # Check mesh topology
```

## Security Considerations

- SSH key authentication is required (password auth disabled)
- All secrets stored in `.env` file (never committed)
- Root password only used for console access
- See [SSH Keys](ssh-keys.md) for key management

## Next Steps

- Configure [environment variables](configuration.md)
- Set up [SSH keys](ssh-keys.md)
- Review [Playbooks Reference](../reference/playbooks.md)
