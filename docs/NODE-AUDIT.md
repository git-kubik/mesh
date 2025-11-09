# OpenWrt Mesh Node Audit & Preparation System

## Overview

The Node Audit & Preparation System provides automated tools to:

1. **Connect** to mesh nodes and verify connectivity
2. **Identify** hardware specifications and software configuration
3. **Compare** installed software against project requirements
4. **Report** comprehensive findings in JSON format
5. **Generate** preparation scripts to configure nodes for automation

This system ensures nodes are ready for full Ansible deployment before proceeding with mesh network configuration.

## Architecture

### Components

1. **`playbooks/audit.yml`** - Main audit playbook
   - Connects to nodes via SSH
   - Gathers hardware/software information
   - Performs package comparison analysis
   - Generates reports and preparation scripts

2. **`filter_plugins/package_audit.py`** - Python filter plugin
   - Parses opkg output
   - Compares installed vs required packages
   - Identifies conflicts and missing dependencies
   - Generates install/remove command lists

3. **`templates/prepare_node.sh.j2`** - Preparation script template
   - Backs up current configuration
   - Updates package repositories
   - Removes conflicting packages
   - Installs required packages
   - Verifies installation success

4. **Audit Reports** - JSON output files
   - Hardware specifications
   - Software inventory
   - Package audit results
   - Service status
   - Actionable recommendations

5. **`playbooks/check-connectivity.yml`** - Connectivity check playbook
   - Validates SSH access to nodes
   - Tests authentication methods
   - Verifies Python interpreter
   - Quick pre-audit validation

## Initial Node Connection Setup

Before running the audit, you need to ensure SSH connectivity to your OpenWrt nodes.

### Connection Methods

The audit playbook connects via SSH using these settings (from `inventory/hosts.yml`):

```yaml
ansible_connection: ssh
ansible_user: root
ansible_python_interpreter: /usr/bin/python3
ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
```

### Authentication Options

#### Option 1: SSH Key Authentication (Recommended)

1. **Generate SSH key** (if you don't have one):

   ```bash
   ssh-keygen -t ed25519 -C "ansible@mesh-network"
   ```

2. **Copy key to each node**:

   ```bash
   # For configured nodes (10.11.12.x)
   ssh-copy-id root@10.11.12.1
   ssh-copy-id root@10.11.12.2
   ssh-copy-id root@10.11.12.3

   # For fresh/unconfigured nodes (factory default)
   ssh-copy-id root@192.168.1.1
   ```

3. **Test connection**:

   ```bash
   ssh root@10.11.12.1 'uname -a'
   ```

#### Option 2: Password Authentication

1. **Edit inventory file** (`inventory/hosts.yml`):

   ```yaml
   all:
     vars:
       ansible_ssh_pass: your_openwrt_password  # Uncomment and set
   ```

2. **Install sshpass** (required for password auth):

   ```bash
   # Ubuntu/Debian
   sudo apt-get install sshpass

   # macOS
   brew install hudochenkov/sshpass/sshpass
   ```

### Node IP Addresses

#### Fresh/Unconfigured Nodes (Factory Default)

**IMPORTANT**: All fresh OpenWrt nodes start with the **same default IP** (192.168.1.1), so you can only connect to **ONE node at a time** during initial setup.

New OpenWrt nodes typically start at:

- **IP**: 192.168.1.1 (factory default)
- **Access**: Connect your computer directly to LAN port

**Setup Process for Each Node**:

1. **Configure your workstation network interface**:

   ```bash
   # Find your network interface (e.g., eth0, enp0s31f6)
   ip link show

   # Ubuntu/Debian - Set static IP on your workstation
   sudo ip addr add 192.168.1.100/24 dev eth0  # Replace eth0 with your interface
   sudo ip link set eth0 up

   # Or use nmcli (NetworkManager)
   nmcli con add type ethernet ifname eth0 con-name openwrt-setup \
     ip4 192.168.1.100/24

   # macOS - Set static IP
   sudo ifconfig en0 192.168.1.100 netmask 255.255.255.0  # Replace en0 with your interface
   ```

2. **Connect computer to node's LAN port** (use any LAN port, NOT WAN)

3. **Verify connectivity**:

   ```bash
   ping 192.168.1.1
   ```

4. **Update `inventory/hosts.yml` temporarily** for this ONE node:

   ```yaml
   node1:
     ansible_host: 192.168.1.1  # Temporary for initial setup
   ```

5. **Run connectivity check** (recommended):

   ```bash
   make check-node1
   ```

6. **Run audit**:

   ```bash
   make audit-node1
   ```

7. **Execute preparation script** (if needed):

   ```bash
   scp audit_reports/node1_prepare.sh root@192.168.1.1:/tmp/
   ssh root@192.168.1.1 'sh /tmp/node1_prepare.sh'
   ```

8. **Deploy configuration** (this changes node IP to 10.11.12.1):

   ```bash
   make deploy-node1
   ```

9. **DISCONNECT the configured node** and **reset your workstation network**:

   ```bash
   # Ubuntu/Debian - Remove static IP
   sudo ip addr del 192.168.1.100/24 dev eth0
   # Or if using NetworkManager
   nmcli con delete openwrt-setup

   # macOS - Reset to DHCP
   sudo ipconfig set en0 DHCP
   ```

10. **Update `inventory/hosts.yml` to final IP**:

    ```yaml
    node1:
      ansible_host: 10.11.12.1  # Permanent mesh network IP
    ```

11. **Reconnect your workstation** to your regular network (or connect to the mesh network)

12. **Repeat steps 1-11 for node2 and node3** (one at a time)

#### Configured Nodes (After Deployment)

After running the deployment playbook, nodes are at:

- **node1**: 10.11.12.1
- **node2**: 10.11.12.2
- **node3**: 10.11.12.3

### Quick Connectivity Check

Before running the full audit, verify connectivity:

```bash
# Fresh nodes (192.168.1.1) - Check ONE at a time
make check-node1         # Check node1 only
make check-node2         # Check node2 only (after node1 is disconnected)
make check-node3         # Check node3 only (after node2 is disconnected)

# Configured nodes (10.11.12.x) - After deployment
make check-all           # Check ALL nodes at once
make check-node1         # Or check specific node

# Alternative methods
ansible node1 -m ping    # Ansible ping

# Test SSH manually
ssh root@10.11.12.1 'echo "Connection successful"'  # Configured node
ssh root@192.168.1.1 'echo "Connection successful"' # Fresh node
```

**Note**: Fresh nodes all start at 192.168.1.1, so you can only check **ONE at a time**

### Troubleshooting Connection Issues

#### "Connection timed out"

**Causes**:

- Node is powered off
- Wrong IP address
- Network cable disconnected
- Firewall blocking SSH

**Solutions**:

1. Verify node is powered on and booting (LED activity)
2. Ping the node: `ping 10.11.12.1`
3. Check network cable connection
4. Verify IP address: `ip addr` or check DHCP leases on your router
5. Test SSH port: `nc -zv 10.11.12.1 22`

#### "Permission denied (publickey,password)"

**Causes**:

- SSH key not installed on node
- Wrong password
- Root login disabled

**Solutions**:

1. Try password auth: `ssh root@10.11.12.1` (enter password manually)
2. Check if root login is allowed in `/etc/config/dropbear` on node
3. Copy SSH key again: `ssh-copy-id root@10.11.12.1`
4. Use password authentication in inventory (see above)

#### "Host key verification failed"

**Causes**:

- Node was rebuilt/reflashed with different SSH key
- IP address was reassigned to different node

**Solutions**:

1. Remove old key: `ssh-keygen -R 10.11.12.1`
2. Or use the SSH options already in inventory (disables strict checking)

#### "No Python interpreter found"

**Causes**:

- Python3 not installed on OpenWrt node
- Wrong Python path

**Solutions**:

1. Install Python: `ssh root@10.11.12.1 'opkg update && opkg install python3'`
2. Verify path: `ssh root@10.11.12.1 'which python3'`
3. Update inventory if different path:

   ```yaml
   ansible_python_interpreter: /usr/bin/python3
   ```

### Multi-Node Setup Strategy

For setting up multiple fresh nodes:

**Sequential Approach** (Required for Fresh Nodes):

Since all fresh nodes start at 192.168.1.1, you MUST configure them one at a time:

```bash
# ============================================================================
# NODE 1 SETUP
# ============================================================================

# 1a. Set workstation IP to 192.168.1.100
sudo ip addr add 192.168.1.100/24 dev eth0

# 1b. Connect node1 to workstation
# 1c. Update inventory: node1.ansible_host = 192.168.1.1
# 1d. Check connectivity
make check-node1

# 1e. Run audit and deploy
make audit-node1
# ... review and execute preparation script if needed ...
make deploy-node1  # Node IP changes to 10.11.12.1

# 1f. DISCONNECT node1
# 1g. Reset workstation network
sudo ip addr del 192.168.1.100/24 dev eth0

# 1h. Update inventory: node1.ansible_host = 10.11.12.1

# ============================================================================
# NODE 2 SETUP (Repeat process)
# ============================================================================

# 2a. Set workstation IP to 192.168.1.100 again
sudo ip addr add 192.168.1.100/24 dev eth0

# 2b. Connect node2 to workstation
# 2c. Update inventory: node2.ansible_host = 192.168.1.1
# 2d. Check connectivity
make check-node2

# 2e. Run audit and deploy
make audit-node2
# ... review and execute preparation script if needed ...
make deploy-node2  # Node IP changes to 10.11.12.2

# 2f. DISCONNECT node2
# 2g. Reset workstation network
sudo ip addr del 192.168.1.100/24 dev eth0

# 2h. Update inventory: node2.ansible_host = 10.11.12.2

# ============================================================================
# NODE 3 SETUP (Repeat process)
# ============================================================================

# 3a. Set workstation IP to 192.168.1.100 again
sudo ip addr add 192.168.1.100/24 dev eth0

# 3b. Connect node3 to workstation
# 3c. Update inventory: node3.ansible_host = 192.168.1.1
# 3d. Check connectivity
make check-node3

# 3e. Run audit and deploy
make audit-node3
# ... review and execute preparation script if needed ...
make deploy-node3  # Node IP changes to 10.11.12.3

# 3f. DISCONNECT node3
# 3g. Reset workstation network to normal
sudo ip addr del 192.168.1.100/24 dev eth0
# Or restore DHCP
sudo dhclient eth0

# 3h. Update inventory: node3.ansible_host = 10.11.12.3

# ============================================================================
# ALL NODES CONFIGURED
# ============================================================================

# 4. Connect all nodes to mesh network (wire mesh links)
# 5. Connect workstation to mesh network or configure routing
# 6. Verify all nodes are reachable
make check-all

# 7. Verify mesh network
make verify
```

**Parallel Approach** (Only for Pre-Configured Nodes):

If nodes are **already configured** with different IPs, you can work on them simultaneously:

```bash
# All nodes already have 10.11.12.1, 10.11.12.2, 10.11.12.3
make check-all          # Check all at once
make audit              # Audit all at once
make deploy             # Deploy to all at once
```

**Advanced: Using Multiple Network Interfaces** (Not Recommended)

If you have multiple Ethernet adapters (USB adapters, multiple NICs), you could theoretically configure multiple fresh nodes in parallel, but this requires manually changing each node's IP first:

```bash
# This is complex and error-prone - sequential approach is recommended
# Adapter 1 (eth0) → node1 @ 192.168.1.1
# Adapter 2 (eth1) → node2 @ 192.168.2.1  # Requires manually changing node2's IP via web UI
# Adapter 3 (eth2) → node3 @ 192.168.3.1  # Requires manually changing node3's IP via web UI
```

### Security Considerations

**SSH Options**:

```yaml
ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
```

These options are **appropriate for**:

- Lab/home environments
- Nodes that are frequently rebuilt/reflashed
- Rapid prototyping

These options are **NOT recommended for**:

- Production environments
- Internet-facing systems
- Security-critical deployments

**For production**, remove these options and:

1. Use proper SSH key management
2. Maintain known_hosts file
3. Enable strict host key checking
4. Use SSH certificates or HashKnown

## Usage

### Quick Start

```bash
# Audit all mesh nodes
make audit

# Audit specific node
make audit-node1

# Audit with custom report directory
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml \
  -e "audit_report_dir=/path/to/reports"
```

### Manual Execution

```bash
# Full audit of all nodes
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml

# Audit single node
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml -l node1

# Run only specific phases (tags)
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml \
  --tags "hardware,software"
```

### Available Tags

- `info` - Basic system information
- `hardware` - Hardware identification
- `software` - Software inventory
- `analysis` - Package comparison
- `services` - Service status checks
- `report` - Report generation
- `script` - Preparation script generation
- `summary` - Display summary output

## Workflow

### 1. Initial Audit

Run audit on new or existing nodes:

```bash
cd openwrt-mesh-ansible
make audit
```

### 2. Review Reports

Check generated reports in `./audit_reports/`:

```bash
# View JSON report
cat audit_reports/node1_audit_YYYY-MM-DD_HH-MM-SS.json | jq

# Review preparation script
cat audit_reports/node1_prepare.sh
```

### 3. Execute Preparation Script

Copy and execute the preparation script on the node:

```bash
# Copy to node
scp audit_reports/node1_prepare.sh root@10.11.12.1:/tmp/

# Execute on node
ssh root@10.11.12.1 'sh /tmp/node1_prepare.sh'
```

### 4. Verify Readiness

Re-run audit to confirm node is ready:

```bash
make audit-node1
```

Look for: `Audit Status: READY`

### 5. Full Deployment

Once audit shows "READY", proceed with deployment:

```bash
make deploy-node1
```

## Report Structure

### JSON Report Format

```json
{
  "metadata": {
    "hostname": "node1",
    "audit_timestamp": "2024-01-15_14-30-45",
    "ansible_host": "10.11.12.1"
  },
  "hardware": {
    "model": "D-Link DIR-1960 A1",
    "cpu": "ARMv7 Processor rev 0 (v7l)",
    "memory_mb": "512",
    "flash_size": "128M",
    "network_interfaces": ["eth0", "eth1", "wlan0", "wlan1"]
  },
  "software": {
    "openwrt_version": "23.05.2",
    "kernel_version": "5.15.150",
    "batman_module": "not_loaded",
    "opkg_update": "success"
  },
  "packages": {
    "installed_count": 87,
    "installed_list": [
      {"name": "base-files", "version": "1509-r24106-10cc5fcd00"},
      ...
    ],
    "audit": {
      "missing_required": ["kmod-batman-adv", "batctl", "wpad-mesh-mbedtls"],
      "conflicting": ["wpad-basic-mbedtls"],
      "installed_required": ["ip-full", "tcpdump-mini"],
      "installed_optional": ["iperf3"],
      "extra_packages": [...],
      "audit_status": "needs_packages",
      "summary": {
        "total_installed": 87,
        "required_count": 5,
        "missing_count": 3,
        "conflict_count": 1,
        "installed_required_count": 2,
        "installed_optional_count": 1
      }
    }
  },
  "services": {
    "status": [
      "network: ENABLED",
      "firewall: ENABLED",
      "dnsmasq: ENABLED"
    ],
    "ssh_config": [...]
  },
  "recommendations": {
    "status": "needs_packages",
    "actions_required": true,
    "remove_packages": ["wpad-basic-mbedtls"],
    "install_packages": ["kmod-batman-adv", "batctl", "wpad-mesh-mbedtls"]
  }
}
```

### Audit Status Values

- **`ready`** - Node is ready for deployment
- **`needs_packages`** - Missing required packages
- **`has_conflicts`** - Conflicting packages must be removed

## Preparation Script Features

The generated preparation script (`prepare_node.sh`) includes:

### Safety Features

- Runs pre-flight checks (root access, internet connectivity, storage space)
- Creates automatic backup before making changes
- Uses error handling (`set -e`)
- Validates all installations before completing

### Execution Phases

1. **Pre-flight Checks** - Verify environment
2. **Backup** - Create sysupgrade backup
3. **Update** - Refresh opkg package lists
4. **Remove** - Uninstall conflicting packages
5. **Install** - Install required packages
6. **Optional** - Install optional packages (best effort)
7. **Verify** - Confirm all changes successful
8. **Summary** - Display results and next steps

### Output

- Colored console output (info, success, warning, error)
- Progress indicators
- Detailed error messages
- Summary with next steps

## Package Requirements

### Required Packages (from `group_vars/all.yml`)

- `kmod-batman-adv` - Batman-adv kernel module
- `batctl` - Batman-adv control utility
- `wpad-mesh-mbedtls` - WiFi daemon with mesh support
- `ip-full` - Full iproute2 package
- `tcpdump-mini` - Packet capture utility

### Conflicting Packages (must be removed)

- `wpad-basic-mbedtls` - Conflicts with mesh mode
- `wpad-basic-wolfssl` - Conflicts with mesh mode
- `wpad-basic` - Conflicts with mesh mode

### Optional Packages

- `iperf3` - Network throughput testing
- `ethtool` - Network diagnostics
- `nano` - Text editor
- `htop` - System monitor
- `rsync` - File synchronization

## Troubleshooting

### Audit Fails to Connect

**Problem:** `wait_for_connection` timeout

**Solutions:**

1. Verify node is powered on and accessible
2. Check IP address in `inventory/hosts.yml`
3. Test SSH manually: `ssh root@10.11.12.1`
4. Verify SSH keys or password authentication

### opkg update Fails

**Problem:** Package list update fails

**Solutions:**

1. Check internet connectivity on node
2. Verify DNS resolution: `nslookup openwrt.org`
3. Check firewall rules allow outbound HTTP/HTTPS
4. Manually update: `opkg update`

### Package Installation Fails

**Problem:** Required packages fail to install

**Solutions:**

1. Check available storage: `df -h`
2. Remove unnecessary packages to free space
3. Verify package name is correct for OpenWrt version
4. Check opkg repositories in `/etc/opkg/distfeeds.conf`

### Conflicting Packages Won't Remove

**Problem:** `opkg remove` fails due to dependencies

**Solutions:**

1. Remove packages in specific order
2. Use `opkg remove --force-depends` (caution!)
3. Check which packages depend on it: `opkg whatdepends <package>`

### Preparation Script Errors

**Problem:** Script exits with error

**Solutions:**

1. Check script output for specific error
2. Ensure internet connectivity
3. Verify sufficient storage space
4. Run script sections manually for debugging
5. Check `/tmp/opkg.lock` isn't stuck

## Integration with Deployment

### Recommended Workflow

```bash
# Step 1: Initial audit (before any changes)
make audit

# Step 2: Review reports and prepare nodes
for node in node1 node2 node3; do
  scp audit_reports/${node}_prepare.sh root@10.11.12.${node#node}:/tmp/
  ssh root@10.11.12.${node#node} 'sh /tmp/'${node}'_prepare.sh'
done

# Step 3: Re-audit to verify readiness
make audit

# Step 4: Deploy if all nodes show "READY"
make deploy-node1  # Deploy first node
make verify        # Verify mesh status

make deploy-node2  # Deploy second node
make verify

make deploy-node3  # Deploy third node
make verify

# Step 5: Final verification
make batman-status
```

### Sequential Deployment

Always deploy nodes one at a time to maintain network connectivity:

1. Audit all nodes
2. Prepare all nodes
3. Deploy node1 → verify
4. Deploy node2 → verify
5. Deploy node3 → verify

## Advanced Usage

### Custom Package Lists

Override package requirements at runtime:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml \
  -e "required_packages=['custom-pkg1','custom-pkg2']"
```

### Audit-Only Mode (No Script Generation)

```bash
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml \
  --skip-tags script
```

### Generate Reports Without Node Access

Use cached data (requires previous run):

```bash
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml \
  --tags report \
  -e "use_cached_data=true"
```

## Filter Plugin Reference

### parse_opkg_list

Converts opkg output to structured data.

```yaml
- set_fact:
    packages: "{{ opkg_output.stdout | parse_opkg_list }}"
```

### compare_packages

Compares installed packages against requirements.

```yaml
- set_fact:
    audit: "{{ installed | compare_packages(required, remove, optional) }}"
```

### generate_install_commands

Creates installation command list.

```yaml
- set_fact:
    cmds: "{{ missing_packages | generate_install_commands }}"
```

### generate_remove_commands

Creates removal command list.

```yaml
- set_fact:
    cmds: "{{ conflicting | generate_remove_commands }}"
```

## Best Practices

1. **Always audit before deployment** - Verify node state first
2. **Review preparation scripts** - Don't execute blindly
3. **Keep backups** - Download sysupgrade backups before changes
4. **Test on one node first** - Validate workflow before scaling
5. **Re-audit after preparation** - Confirm readiness before deploying
6. **Monitor storage** - Ensure sufficient space before installing packages
7. **Check internet connectivity** - Required for opkg operations
8. **Sequential deployment** - One node at a time prevents total outage

## Files Created

```
openwrt-mesh-ansible/
├── playbooks/
│   └── audit.yml                    # Main audit playbook
├── filter_plugins/
│   └── package_audit.py             # Package comparison logic
├── templates/
│   └── prepare_node.sh.j2           # Preparation script template
└── audit_reports/                   # Generated reports (not in git)
    ├── node1_audit_2024-01-15_14-30-45.json
    ├── node1_prepare.sh
    ├── node2_audit_2024-01-15_14-30-45.json
    ├── node2_prepare.sh
    ├── node3_audit_2024-01-15_14-30-45.json
    └── node3_prepare.sh
```

## See Also

- [ANSIBLE-QUICKSTART.md](ANSIBLE-QUICKSTART.md) - Ansible basics
- [openwrt-batman-mesh-setup.md](openwrt-batman-mesh-setup.md) - Technical details
- `group_vars/all.yml` - Package requirements configuration
- `inventory/hosts.yml` - Node definitions
