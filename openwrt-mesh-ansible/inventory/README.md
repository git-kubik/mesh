# Inventory Configuration

This directory contains two inventory files for different deployment phases:

## 🔐 SSH Configuration: Dropbear → OpenSSH Transition

### Factory OpenWrt (Phase 1)

- **SSH Server**: Dropbear (lightweight SSH)
- **Root Password**: **NOT SET** (no password configured)
- **Authentication**: Password authentication with empty password (factory default)
- **Security**: Minimal, designed for initial setup only

### Configured Mesh (Phase 2)

- **SSH Server**: OpenSSH (full-featured)
- **Root Password**: Set from `group_vars/all.yml` → `root_password` (console access only)
- **Authentication**: **SSH KEY** (passwordless, key-based)
- **Security**: Hardened configuration with password authentication disabled

**IMPORTANT**: The deployment automatically handles this transition:

1. Connects to dropbear (no password required on factory OpenWrt)
2. Generates SSH key pair on control machine (if doesn't exist)
3. Deploys public key to node
4. Installs openssh-server and openssh-sftp-server
5. Configures openssh for key-based auth only (passwords disabled for SSH)
6. Sets root password (for console/serial access only)
7. Removes dropbear
8. Future connections use passwordless SSH key authentication

**SSH Key Location**: `~/.ssh/openwrt_mesh_rsa` (configurable in `group_vars/all.yml`)

## 📁 Inventory Files

### `hosts-initial.yml` - Phase 1: Initial Setup

**Use when:** Setting up a fresh OpenWrt node at factory default IP (192.168.1.1)

- **SSH**: Dropbear with **no root password** (factory default)
- **IP**: All nodes start at `192.168.1.1`
- **Limitation**: You **MUST** configure nodes **ONE AT A TIME**
- **After deployment**: Node moves to target IP with openssh + SSH key

**Workflow:**

```bash
# 1. Flash OpenWrt on first router (it will be at 192.168.1.1)
# 2. Connect your computer to the router's LAN port
# 3. Check connectivity
make check-initial-node1

# 4. Deploy configuration (node will move to 10.11.12.1)
make deploy-initial-node1

# 5. Disconnect first router, repeat for node2 and node3
make deploy-initial-node2
make deploy-initial-node3
```

### `hosts.yml` - Phase 2: Production

**Use when:** Managing configured mesh nodes at their final IPs

- **SSH**: OpenSSH with **SSH KEY** (passwordless authentication)
- **SSH Key**: `~/.ssh/openwrt_mesh_rsa` (auto-generated if needed)
- **IPs**: Nodes at unique addresses:
  - Node 1: `10.11.12.1` (Primary Gateway)
  - Node 2: `10.11.12.2` (Secondary Gateway)
  - Node 3: `10.11.12.3` (Secondary Gateway)

**Workflow:**

```bash
# Check all nodes
make check-all

# Deploy to all nodes
make deploy

# Check individual node
make check-node1
```

## 🔄 Two-Phase Deployment Process

### Why Two Inventory Files?

Fresh OpenWrt routers all start at `192.168.1.1`. Since they share the same IP, you can only configure one at a time. Once configured, they move to unique IPs where they can all be managed simultaneously.

### Phase 1: Initial Setup (One Node at a Time)

```
┌─────────────────────────────────────────────────────┐
│  Fresh OpenWrt - All at 192.168.1.1                 │
│  Use: inventory/hosts-initial.yml                   │
└─────────────────────────────────────────────────────┘

Step 1: Node 1 Only
  192.168.1.1  →  Configure  →  10.11.12.1
  ✓ make deploy-initial-node1

Step 2: Node 2 Only (after disconnecting Node 1)
  192.168.1.1  →  Configure  →  10.11.12.2
  ✓ make deploy-initial-node2

Step 3: Node 3 Only (after disconnecting Node 2)
  192.168.1.1  →  Configure  →  10.11.12.3
  ✓ make deploy-initial-node3
```

### Phase 2: Production (All Nodes Together)

```
┌─────────────────────────────────────────────────────┐
│  Configured Mesh - Unique IPs                       │
│  Use: inventory/hosts.yml (default)                 │
└─────────────────────────────────────────────────────┘

All nodes accessible simultaneously:
  - Node 1: 10.11.12.1 ✓
  - Node 2: 10.11.12.2 ✓
  - Node 3: 10.11.12.3 ✓

✓ make check-all
✓ make deploy
✓ make verify
```

## 🎯 Quick Reference

| Task | Command | Inventory Used |
|------|---------|----------------|
| Setup fresh Node 1 | `make deploy-initial-node1` | hosts-initial.yml |
| Setup fresh Node 2 | `make deploy-initial-node2` | hosts-initial.yml |
| Setup fresh Node 3 | `make deploy-initial-node3` | hosts-initial.yml |
| Check all configured nodes | `make check-all` | hosts.yml |
| Deploy to all nodes | `make deploy` | hosts.yml |
| Check individual node | `make check-node1` | hosts.yml |

## ⚠️ Important Notes

### Authentication

1. **Factory OpenWrt (hosts-initial.yml)**:
   - Uses **Dropbear SSH** server
   - Root password is **NOT SET** (no password)
   - No SSH keys configured
   - Authentication: `ansible_ssh_pass: ''` (empty password)

2. **Configured Mesh (hosts.yml)**:
   - Uses **OpenSSH** server
   - Root password from `group_vars/all.yml` → `root_password` (console only)
   - SSH key authentication: `~/.ssh/openwrt_mesh_rsa`
   - Password authentication **disabled** for SSH (security)
   - Authentication: `ansible_ssh_private_key_file: "{{ ssh_key_path }}"`

### Deployment Process

1. **Initial Setup**: Always use `hosts-initial.yml` for fresh nodes
2. **One at a Time**: Only connect to one fresh node at a time (same IP)
3. **Environment Setup**: Configure passwords in `.env` file (see `docs/ENV-CONFIGURATION.md`)
   - Copy `.env.example` to `.env`
   - Set all required passwords
   - Load environment: `set -a; source .env; set +a`
4. **SSH Transition**: Deployment automatically:
   - Generates SSH key pair (if doesn't exist)
   - Deploys public key to node
   - Switches dropbear → openssh with key-based auth
   - Disables password authentication for SSH
5. **SSH Key**: Auto-generated at `~/.ssh/openwrt_mesh_rsa` (or custom path)
6. **Production**: Use `hosts.yml` (default) after all nodes configured
7. **Network Cable**: Must be connected directly for initial setup

## 📋 Requirements

### System Dependencies

Before using these inventory files, ensure you have:

1. **Ansible** (tested with 2.9+)

   ```bash
   pip install ansible
   # or
   apt-get install ansible
   ```

2. **sshpass** (required for password authentication)

   ```bash
   apt-get install sshpass  # Debian/Ubuntu
   # or
   yum install sshpass      # RHEL/CentOS
   ```

3. **SSH client** (openssh-client)

   ```bash
   apt-get install openssh-client
   ```

**Why sshpass?** Ansible requires sshpass to authenticate with passwords (both blank for dropbear and the configured password for openssh).

## 🔧 Customization

Both inventory files use the same structure. Key variables:

- `ansible_host` - IP address to connect to
- `node_ip` - Target IP after configuration
- `node_id` - Node identifier (1, 2, or 3)
- `mesh_ports` - Physical port connections for mesh

See `../group_vars/all.yml` for network configuration.
