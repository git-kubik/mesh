# OpenWrt Mesh Network - Ansible Deployment

Automated deployment and management of a highly-available OpenWrt mesh network using Ansible.

## Quick Reference

**For experienced users - complete workflow:**

```bash
# 1. Setup
cp .env.example .env && nano .env  # Set passwords
chmod 600 .env
set -a; source .env; set +a
make validate-env

# 2. Initial deployment (one node at a time at 192.168.1.1)
make check-initial-node1 && make deploy-initial-node1
make check-initial-node2 && make deploy-initial-node2
make check-initial-node3 && make deploy-initial-node3

# 3. Production management (all nodes at 10.11.12.x)
make check-all     # Check connectivity
make deploy        # Deploy changes
make verify        # Verify mesh
make backup        # Backup configs
```

**Key features:**

- Environment-based configuration (`.env` file)
- Automatic SSH key authentication
- Two-phase deployment (initial @ 192.168.1.1 → production @ 10.11.12.x)
- Comprehensive validation and error checking

See below for detailed documentation.

---

## Overview

This Ansible project automates the deployment and configuration of a 3-node OpenWrt mesh network with:

- Full ring topology with wired connections
- 2.4GHz wireless mesh backup
- Multi-gateway high availability
- 5GHz client access point with roaming
- Batman-adv mesh routing
- Optional VLAN support
- SSH key authentication (automatic)
- Environment-based configuration

## Directory Structure

```
openwrt-mesh-ansible/
├── inventory/
│   └── hosts.yml              # Node definitions and connection info
├── group_vars/
│   └── all.yml                # Common configuration variables
├── host_vars/                 # Node-specific variables (optional)
├── templates/
│   ├── network.j2             # Network configuration template
│   ├── wireless.j2            # Wireless configuration template
│   ├── dhcp.j2                # DHCP/DNS configuration template
│   └── firewall.j2            # Firewall configuration template
├── playbooks/
│   ├── deploy.yml             # Main deployment playbook
│   ├── verify.yml             # Verification playbook
│   ├── backup.yml             # Backup playbook
│   └── update.yml             # Update playbook
├── backups/                   # Backup storage (created automatically)
└── README.md                  # This file
```

## Prerequisites

### Control Machine (Your Workstation)

1. **Ansible installed:**

   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install ansible

   # macOS
   brew install ansible

   # Python pip
   pip install ansible
   ```

2. **SSH access to OpenWrt nodes:**
   - Ensure you can SSH to each node
   - Initially nodes will be at 192.168.1.1 (default)
   - After configuration, nodes will be at 10.11.12.1, .2, .3

3. **Network connectivity:**
   - Control machine must be able to reach nodes
   - Configure ONE node at a time initially

### Target Nodes (OpenWrt Routers)

1. **OpenWrt installed:**
   - Flash OpenWrt firmware (see main setup guide)
   - Root password set
   - SSH enabled (default)

2. **Python3 available:**
   - Usually pre-installed on OpenWrt
   - If not: `opkg update && opkg install python3-light`

## Quick Start

### 1. Clone or Download This Project

```bash
git clone <repository> openwrt-mesh-ansible
cd openwrt-mesh-ansible
```

### 2. Configure Environment Variables

**ALL configuration is now managed through environment variables in a `.env` file at the repository root.**

```bash
# From repository root (/home/m/repos/mesh/)
cp .env.example .env

# Edit .env and set required passwords (minimum 3 required)
nano .env
```

**REQUIRED variables (must be set):**

```bash
# Root password for console/serial access (NOT used for SSH)
ROOT_PASSWORD=YourSecureRootPassword123!

# 2.4GHz mesh network password (WPA3-SAE)
MESH_PASSWORD=YourSecureMeshPassword123!

# 5GHz client AP password
CLIENT_PASSWORD=YourSecureClientPassword123!
```

**Optional: Customize network settings** in `.env`:

```bash
# Adjust to your WAN speeds (in kbit/s)
BATMAN_GW_BANDWIDTH=100000/100000

# Network settings (defaults work for most setups)
MESH_NETWORK=10.11.12.0
MESH_GATEWAY=10.11.12.1

# WiFi settings
CLIENT_SSID=HA-Client
CLIENT_CHANNEL=36
CLIENT_COUNTRY=AU

# See .env.example for 60+ configurable variables
```

**Secure the .env file:**

```bash
chmod 600 .env
```

### 3. Load and Validate Environment

```bash
# Load environment variables
set -a; source .env; set +a

# Validate configuration (IMPORTANT - run this first!)
make validate-env
```

You should see:

```
✅ Environment Validation PASSED
Required passwords: All set ✓
Ready for deployment!
```

### 4. Initial Node Setup (One at a Time)

Fresh OpenWrt routers start at **192.168.1.1** with **NO root password set**.
After configuration, they move to **10.11.12.x** with **SSH key authentication**.

**Configure Node 1:**

```bash
# 1. Connect ONLY Node 1 to your network (it's at 192.168.1.1)
# 2. Check connectivity
make check-initial-node1

# 3. Deploy (installs OpenSSH, sets up SSH keys, moves to 10.11.12.1)
make deploy-initial-node1

# 4. Node 1 is now at 10.11.12.1 with SSH key auth
```

**Configure Node 2:**

```bash
# 1. Disconnect Node 1, connect Node 2 (also at 192.168.1.1)
# 2. Check connectivity
make check-initial-node2

# 3. Deploy (moves to 10.11.12.2)
make deploy-initial-node2
```

**Configure Node 3:**

```bash
# Same process
make check-initial-node3
make deploy-initial-node3
```

### 5. Physical Wiring

After all nodes are configured:

1. Connect the wired ring (LAN3 and LAN4 between nodes)
2. Connect WAN ports to internet
3. Power on all nodes

### 6. Verify Deployment

```bash
# Check connectivity to all nodes
make check-all

# OR use Ansible directly
ansible-playbook playbooks/verify.yml

# Should show:
# - All nodes reachable
# - Batman interfaces active
# - Mesh topology complete
# - Gateways available
```

## Usage

**IMPORTANT:** Always load environment variables before running commands:

```bash
set -a; source .env; set +a
```

### Deploy Configuration

**Deploy to all nodes:**

```bash
make deploy

# OR using Ansible directly
ansible-playbook playbooks/deploy.yml
```

**Deploy to specific node:**

```bash
make deploy-node1    # Deploy to Node 1 only
make deploy-node2    # Deploy to Node 2 only
make deploy-node3    # Deploy to Node 3 only

# OR using Ansible directly
ansible-playbook playbooks/deploy.yml --limit node1
```

**Dry run (check mode):**

```bash
make check

# OR using Ansible directly
ansible-playbook playbooks/deploy.yml --check
```

**Deploy only specific components:**

```bash
# Network configuration only
make deploy-network

# Wireless configuration only
make deploy-wireless

# DHCP configuration only
make deploy-dhcp

# Firewall configuration only
make deploy-firewall

# Packages only
make packages

# OR using Ansible directly with tags
ansible-playbook playbooks/deploy.yml --tags network
ansible-playbook playbooks/deploy.yml --tags wireless
ansible-playbook playbooks/deploy.yml --skip-tags packages
```

### Check Connectivity

```bash
# Check all configured nodes (at 10.11.12.x)
make check-all

# Check individual nodes
make check-node1
make check-node2
make check-node3

# Audit all nodes
make audit
```

### Verify Mesh Status

```bash
# Verify mesh configuration
make verify

# Check Batman status
make batman-status

# Check logs
make logs

# Check uptime
make uptime

# OR using Ansible directly
ansible-playbook playbooks/verify.yml
```

### Backup Configuration

```bash
# Backup all nodes
make backup

# OR using Ansible directly
ansible-playbook playbooks/backup.yml

# Backups saved to: backups/YYYY-MM-DD/
```

**Restore from backup:**

```bash
# 1. Copy backup to node
scp backups/2025-11-05/backup-node1-*.tar.gz root@10.11.12.1:/tmp/

# 2. SSH to node (uses SSH key)
ssh -i ~/.ssh/openwrt_mesh_rsa root@10.11.12.1

# 3. Restore
sysupgrade -r /tmp/backup-node1-*.tar.gz
reboot
```

### Update Packages

```bash
# Check for updates (dry run)
make update-check

# Perform updates
make update

# OR using Ansible directly
ansible-playbook playbooks/update.yml --tags check
ansible-playbook playbooks/update.yml
```

### Ad-hoc Commands

```bash
# Ping all nodes
make ping

# Check Batman status
make batman-status

# View logs
make logs

# Check uptime
make uptime

# Restart network on all nodes
make restart-network

# Restart wireless
make restart-wireless

# OR using Ansible directly
ansible mesh_nodes -a "batctl o"
ansible mesh_nodes -a "uptime"
ansible mesh_nodes -a "batctl if"
ansible mesh_nodes -a "/etc/init.d/network restart"
```

## Configuration Management

**IMPORTANT:** All configuration is now managed through the `.env` file.

### Modifying Configuration

**To change network settings:**

1. Edit `.env` file:

   ```bash
   nano .env
   ```

2. Update variables (example):

   ```bash
   MESH_NETWORK=10.20.30.0
   MESH_GATEWAY=10.20.30.1
   DNS_PRIMARY=1.1.1.1
   ```

3. Load environment:

   ```bash
   set -a; source .env; set +a
   ```

4. Validate and deploy:

   ```bash
   make validate-env
   make deploy
   ```

**To change WiFi passwords:**

```bash
# 1. Edit .env
nano .env

# 2. Update passwords
MESH_PASSWORD=NewMeshPassword123!
CLIENT_PASSWORD=NewClientPassword123!

# 3. Load and deploy
set -a; source .env; set +a
make deploy-wireless
```

**To adjust WAN speeds:**

```bash
# Edit .env
BATMAN_GW_BANDWIDTH=500000/50000  # 500/50 Mbps

# Load and deploy
set -a; source .env; set +a
make deploy
```

### Version Control

**IMPORTANT: Never commit .env to git** (contains passwords!)

Track configuration changes with Git:

```bash
git init
git add .
git commit -m "Initial mesh configuration"

# After changing .env (only commit .env.example if you add new variables)
git add .env.example
git commit -m "Added new configuration options"

# .env is excluded via .gitignore - passwords stay safe
```

## VLAN Configuration

### Enable VLANs

VLANs provide network segmentation for management and guest access.

**Edit `.env` to enable and configure VLANs:**

```bash
# Enable VLAN support
ENABLE_VLANS=true

# Management VLAN (2.4GHz AP for admin access)
MGMT_PASSWORD=YourSecureMgmtPassword123!
MGMT_VLAN_VID=10
MGMT_VLAN_NETWORK=10.11.10.0/24
MGMT_VLAN_SSID=HA-Management

# Guest VLAN (5GHz AP with isolation)
GUEST_PASSWORD=YourSecureGuestPassword123!
GUEST_VLAN_VID=30
GUEST_VLAN_NETWORK=10.11.30.0/24
GUEST_VLAN_SSID=HA-Guest
GUEST_VLAN_ISOLATION=true
```

**Deploy VLAN configuration:**

```bash
# Load environment and validate
set -a; source .env; set +a
make validate-env

# Deploy to all nodes
make deploy
```

**Disable VLANs:**

```bash
# Edit .env
ENABLE_VLANS=false

# Redeploy
set -a; source .env; set +a
make deploy
```

## Troubleshooting

### Connection Issues

**Can't connect to node:**

```bash
# Test SSH manually
ssh root@10.11.12.1

# Check if node is reachable
ping 10.11.12.1

# Try with password authentication
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml --ask-pass
```

**Wrong IP address in inventory:**

```bash
# Update inventory/hosts.yml with correct ansible_host
# Then test connection
ansible node1 -i inventory/hosts.yml -m ping
```

### Deployment Issues

**Package installation fails:**

```bash
# Update package lists manually
ansible mesh_nodes -i inventory/hosts.yml -a "opkg update"

# Then retry deployment
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --tags packages
```

**Configuration not applying:**

```bash
# Check for syntax errors
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --syntax-check

# Run in check mode
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --check

# Check node logs
ansible mesh_nodes -i inventory/hosts.yml -a "logread | tail -50"
```

**Services not reloading:**

```bash
# Manually reload services
ansible mesh_nodes -i inventory/hosts.yml -a "/etc/init.d/network restart"
ansible mesh_nodes -i inventory/hosts.yml -a "wifi reload"
ansible mesh_nodes -i inventory/hosts.yml -a "/etc/init.d/dnsmasq restart"
```

### Mesh Issues

**Batman interfaces not active:**

```bash
# Check batman module
ansible mesh_nodes -i inventory/hosts.yml -a "lsmod | grep batman"

# Check configuration
ansible mesh_nodes -i inventory/hosts.yml -a "uci show network | grep batadv"

# Restart network
ansible mesh_nodes -i inventory/hosts.yml -a "/etc/init.d/network restart"
```

**Nodes can't see each other:**

```bash
# Check mesh topology
ansible mesh_nodes -i inventory/hosts.yml -a "batctl o"

# Check physical connections
ansible mesh_nodes -i inventory/hosts.yml -a "ip link show | grep lan"

# Check wireless mesh
ansible mesh_nodes -i inventory/hosts.yml -a "iw dev mesh0 station dump"
```

## Advanced Usage

### SSH Key Authentication

**SSH keys are configured automatically during initial deployment!**

- Keys generated at `~/.ssh/openwrt_mesh_rsa` (4096-bit RSA)
- Public key deployed to nodes automatically
- Production nodes use key-based auth only (passwordless)
- No manual SSH key setup required

**Manual SSH access:**

```bash
# Access nodes using SSH key (automatic after deployment)
ssh root@10.11.12.1
ssh root@10.11.12.2
ssh root@10.11.12.3

# OR specify key explicitly
ssh -i ~/.ssh/openwrt_mesh_rsa root@10.11.12.1
```

**Backup your SSH key:**

```bash
# Backup private key (IMPORTANT!)
cp ~/.ssh/openwrt_mesh_rsa ~/secure-backup/
chmod 600 ~/secure-backup/openwrt_mesh_rsa

# If key is lost, you'll need console/serial access to recover
```

**Advanced: Custom SSH key:**

```bash
# Edit .env before initial deployment
SSH_KEY_PATH=~/.ssh/custom_mesh_key
SSH_KEY_TYPE=ed25519
SSH_KEY_BITS=256

# Keys will be generated at custom location
```

See `docs/SSH-KEY-AUTHENTICATION.md` for detailed SSH key management.

### Parallel Execution

```bash
# Deploy to multiple nodes simultaneously
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --forks 3

# Note: Use caution with parallel updates to maintain mesh availability
```

### Custom Playbooks

Create custom playbooks for specific tasks:

```yaml
---
# playbooks/custom_task.yml
- name: Custom Task
  hosts: mesh_nodes
  gather_facts: false
  tasks:
    - name: Your custom task
      raw: echo "Custom command"
```

### Integration with Other Tools

**Export configuration:**

```bash
# Export current config
ansible mesh_nodes -i inventory/hosts.yml -a "uci export network" > network_config.txt
```

**Monitor logs continuously:**

```bash
# Watch logs on all nodes
ansible mesh_nodes -i inventory/hosts.yml -a "logread -f" -f 10
```

## Security Best Practices

1. **Secure .env file:**
   - Never commit `.env` to git (contains passwords!)
   - Set proper permissions: `chmod 600 .env`
   - Keep backups of `.env` in secure location
   - Use strong, unique passwords (16+ characters recommended)

2. **SSH key authentication (automatically configured):**
   - Production nodes use SSH key auth only (passwordless)
   - SSH keys auto-generated during initial deployment
   - Password authentication disabled for SSH (security)
   - Root password only for console/serial access
   - Keep SSH private key secure: `~/.ssh/openwrt_mesh_rsa`

3. **Environment validation:**
   - Always run `make validate-env` before deployment
   - Validates all required passwords are set
   - Catches configuration errors early

4. **Restrict SSH access:**
   - Configure firewall to allow SSH only from management network
   - Consider changing SSH port (edit templates)

5. **Regular updates:**
   - Run `make update-check` monthly
   - Apply updates: `make update`
   - Subscribe to OpenWrt security announcements

6. **Backup regularly:**
   - Schedule regular backups: `make backup`
   - Store backups securely off-site
   - Include `.env` file in backup strategy

7. **Configuration auditing:**
   - Review `.env` changes before deploying
   - Use Git to track `.env.example` changes
   - Run `make check` (dry-run) before actual deployment
   - Test changes on one node first with `make deploy-node1`

## Maintenance Schedule

### Daily

```bash
# Quick status check
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml
```

### Weekly

```bash
# Check for updates
ansible-playbook -i inventory/hosts.yml playbooks/update.yml --tags check

# Backup configuration
ansible-playbook -i inventory/hosts.yml playbooks/backup.yml
```

### Monthly

```bash
# Apply updates
ansible-playbook -i inventory/hosts.yml playbooks/update.yml

# Verify after updates
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml
```

### Quarterly

```bash
# Full configuration audit
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --check

# Review and clean old backups
ls -lh backups/
```

## Tips and Best Practices

1. **Test in check mode first:**
   - Always run `--check` before applying changes
   - Verify output before actual deployment

2. **One node at a time:**
   - For critical updates, use `--limit` to update one node
   - Verify mesh stays operational before proceeding

3. **Keep backups:**
   - Backup before any major changes
   - Keep backups for at least 30 days

4. **Document changes:**
   - Use Git commit messages to explain configuration changes
   - Keep notes on non-standard configurations

5. **Version your configurations:**
   - Tag stable configurations in Git
   - Easy rollback if needed

6. **Monitor performance:**
   - Regularly check mesh topology and link quality
   - Track gateway selection patterns

## Troubleshooting Common Ansible Errors

**"SSH Error: Permission denied"**

```bash
# Check SSH credentials
ansible mesh_nodes -i inventory/hosts.yml -m ping --ask-pass
```

**"Module not found" or "Python not available"**

```bash
# Install Python on nodes
ansible mesh_nodes -i inventory/hosts.yml -m raw -a "opkg update && opkg install python3-light"
```

**"Template error" or "Jinja2 error"**

```bash
# Check template syntax
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --syntax-check

# Check variables are defined
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --check
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **`docs/ENV-CONFIGURATION.md`** - Complete environment variable reference
  - All 60+ configurable variables
  - Password generation examples
  - Security best practices
  - Troubleshooting guide

- **`docs/LOCAL-PACKAGE-REPOSITORY.md`** - Local package repository user guide
  - Setup and usage instructions
  - 60% faster deployments (2 min vs 5 min)
  - Offline deployment capability
  - Troubleshooting and best practices

- **`docs/LOCAL-REPO-IMPLEMENTATION.md`** - Local repository technical guide
  - Implementation details and architecture
  - Retry logic and rate limiting design
  - Performance analysis and benchmarks
  - Maintenance and update procedures

- **`docs/SSH-KEY-AUTHENTICATION.md`** - SSH key management guide
  - Key generation and deployment process
  - Backup and rotation procedures
  - Troubleshooting SSH access
  - Security considerations

- **`inventory/README.md`** - Two-phase deployment architecture
  - Initial setup vs production workflows
  - Inventory file details
  - Requirements and dependencies

- **`REFACTORING-SUMMARY.md`** - Complete change history
  - Detailed refactoring documentation
  - Migration checklist
  - Testing results

## Support and Resources

- **Project Documentation:** See `docs/` directory
- OpenWrt Documentation: <https://openwrt.org/docs>
- Batman-adv Project: <https://www.open-mesh.org/>
- Ansible Documentation: <https://docs.ansible.com/>
- OpenWrt Forum: <https://forum.openwrt.org/>

## License

This project configuration is provided as-is for personal and educational use.

## Contributing

To improve these playbooks:

1. Test changes thoroughly
2. Document modifications
3. Share improvements with the community

---

**Last Updated:** 2025-11-09
**Version:** 2.0 (Environment Variable Refactoring)

**Major Changes in v2.0:**

- All configuration moved to `.env` file (60+ variables)
- Two-phase deployment (initial vs production)
- Automatic SSH key generation and deployment
- Environment validation before deployment
- Enhanced security (no passwords in git)
