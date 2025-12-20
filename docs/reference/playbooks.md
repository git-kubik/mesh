# Ansible Playbook Reference

This document provides a comprehensive reference for all Ansible playbooks available in the `openwrt-mesh-ansible/playbooks/` directory.

## Quick Reference

```bash
cd openwrt-mesh-ansible

# Run any playbook directly
ansible-playbook -i inventory/hosts.yml playbooks/<playbook>.yml

# Target specific node
ansible-playbook -i inventory/hosts.yml playbooks/<playbook>.yml --limit node1

# Check mode (dry run)
ansible-playbook -i inventory/hosts.yml playbooks/<playbook>.yml --check
```

## Core Playbooks

### deploy.yml

**Purpose**: Complete deployment of mesh network configuration to nodes.

**What it does**:

1. SSH server transition (Dropbear → OpenSSH)
2. Root password configuration
3. Network configuration (batman-adv mesh)
4. Wireless configuration (mesh + AP)
5. DHCP and firewall setup
6. USB storage setup (optional)
7. Monitoring deployment (optional)

**Usage**:

```bash
# Initial deployment (fresh node at 192.168.1.1)
ansible-playbook -i inventory/hosts-initial.yml playbooks/deploy.yml --limit node1

# Production deployment (configured node)
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml

# Deploy to specific node
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --limit node2

# Skip reboot (for testing)
SKIP_REBOOT=true ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml
```

**Roles included**:

| Role | Tags | Description |
|------|------|-------------|
| backup | backup | Pre-deployment backup |
| package_management | packages | Install required packages |
| ssh_transition | ssh | Dropbear → OpenSSH migration |
| system_config | system, security | Hostname, timezone, passwords |
| network_config | config, network | Batman-adv, VLANs, bridges |
| wireless_config | config, wireless | Mesh + AP configuration |
| dhcp_config | config, dhcp | DHCP server setup |
| firewall_config | config, firewall | Firewall zones and rules |
| usb_storage | usb, storage | USB storage setup |
| monitoring | monitoring | Collectd, vnStat deployment |

**Environment variables**:

| Variable | Default | Description |
|----------|---------|-------------|
| `SKIP_REBOOT` | false | Skip final reboot |
| `ENABLE_USB_STORAGE` | true | Enable USB storage role |
| `ENABLE_MONITORING` | true | Enable monitoring role |
| `OPKG_REPO_URL` | (empty) | Custom package repository URL |

---

### audit.yml

**Purpose**: Comprehensive system audit for troubleshooting and compliance verification.

**What it does**:

1. Collects system identification (hardware, OpenWrt version)
2. Gathers network configuration and state
3. Checks service status
4. Verifies security configuration
5. Audits mesh network status
6. Checks package compliance
7. Generates JSON report and preparation script

**Usage**:

```bash
# Audit single node
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml --limit node1

# Audit all nodes
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml

# Custom report directory
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml \
  -e "audit_report_dir=/path/to/reports"
```

**Output files**:

| File | Description |
|------|-------------|
| `audit_reports/<hostname>_audit_<timestamp>.json` | Full JSON audit report |
| `audit_reports/<hostname>_prepare.sh` | Script to fix missing packages |

**Audit phases**:

1. System Identification
2. Network Infrastructure
3. Services and Processes
4. Security Configuration
5. Mesh Network Status
6. Wireless Configuration
7. Software Packages
8. System Health
9. USB Storage
10. Monitoring Status
11. Distributed Syslog
12. Package Compliance Analysis

---

### verify.yml

**Purpose**: Quick verification of mesh network health.

**What it does**:

1. Checks node reachability
2. Verifies batman-adv module
3. Displays mesh topology
4. Shows gateway status
5. Tests WAN connectivity

**Usage**:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml
```

**Output includes**:

- System uptime
- Batman module status
- Batman interfaces
- Mesh topology (originators)
- Gateway status
- Active interfaces
- WAN connectivity

---

### backup.yml

**Purpose**: Backup all mesh node configurations.

**What it does**:

1. Creates `sysupgrade -b` backup on each node
2. Fetches backup to control machine
3. Also fetches individual config files:
   - `/etc/config/network`
   - `/etc/config/wireless`
   - `/etc/config/dhcp`
   - `/etc/config/firewall`
   - `/etc/config/system`

**Usage**:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/backup.yml
```

**Output location**: `backups/<date>/`

**Restore instructions**:

```bash
# Copy backup to node
scp backup.tar.gz root@10.11.12.X:/tmp/

# Restore
ssh root@10.11.12.X 'sysupgrade -r /tmp/backup.tar.gz'

# Reboot
ssh root@10.11.12.X 'reboot'
```

---

### check-connectivity.yml

**Purpose**: Simple SSH connectivity check to all nodes.

**Usage**:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/check-connectivity.yml
```

---

## Firmware Playbooks

### sysupgrade.yml

**Purpose**: Flash firmware images to nodes.

**Image types**:

| Type | Description | Post-upgrade |
|------|-------------|--------------|
| `mesh` (default) | Custom-built image with config | Boots to 10.11.12.x, ready to use |
| `vanilla` | Stock OpenWrt image | Boots to 192.168.1.1, needs deployment |

**Usage**:

```bash
# Flash custom mesh image
ansible-playbook -i inventory/hosts.yml playbooks/sysupgrade.yml --limit node3

# Flash vanilla OpenWrt
IMAGE_TYPE=vanilla ansible-playbook -i inventory/hosts.yml playbooks/sysupgrade.yml --limit node3

# Flash specific image file
IMAGE_PATH=/path/to/image.bin ansible-playbook -i inventory/hosts.yml playbooks/sysupgrade.yml --limit node3
```

**Image locations**:

| Type | Location |
|------|----------|
| Mesh (node-specific) | `images/mesh-node1-sysupgrade.bin` |
| Mesh (generic) | `images/mesh-sysupgrade.bin` |
| Vanilla | `openwrt-repo/targets/ramips/mt7621/openwrt-*-sysupgrade.bin` |

**Process**:

1. Validates image file exists
2. Verifies SHA256 checksum (if `.sha256` file present)
3. Uploads to node via SSH
4. Verifies remote checksum
5. Tests image validity (`sysupgrade -T`)
6. Executes `sysupgrade -n` (always wipes config)

---

### factory-reset.yml

**Purpose**: Reset node to factory defaults.

**Usage**:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/factory-reset.yml --limit node1
```

!!! danger "Destructive Operation"
    This erases all configuration. Node will reboot to 192.168.1.1.

---

## Snapshot Playbooks

### snapshot.yml

**Purpose**: Create complete configuration snapshot for backup and image building.

**What it captures**:

| Directory | Contents |
|-----------|----------|
| `system/` | OpenWrt version, board info, kernel |
| `config/` | Complete UCI export + individual configs |
| `etc/` | passwd, fstab, crontabs, SSH keys |
| `packages/` | Installed packages with versions |
| `scripts/` | Custom scripts from `/usr/bin/` |
| `network/` | Interfaces, IPs, routes, ARP |
| `wireless/` | Device info, stations |
| `mesh/` | Batman interfaces, neighbors, originators |
| `services/` | Enabled/running services, ports |
| `storage/` | USB storage status |
| `monitoring/` | Monitoring configuration |
| `restore/` | README and restore script |

**Usage**:

```bash
# Snapshot single node
ansible-playbook -i inventory/hosts.yml playbooks/snapshot.yml --limit node1

# Snapshot all nodes
ansible-playbook -i inventory/hosts.yml playbooks/snapshot.yml
```

**Output**: `snapshots/<hostname>/`

---

### snapshot-full.yml

**Purpose**: Extended snapshot including additional system state.

Similar to `snapshot.yml` but includes more detailed information.

---

## Infrastructure Playbooks

### usb-storage.yml

**Purpose**: Configure USB storage on nodes.

**What it does**:

1. Installs USB storage drivers
2. Detects USB device
3. Creates partition table
4. Formats with F2FS (flash-optimized)
5. Mounts at `/x00`
6. Configures auto-mount on boot

**Usage**:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/usb-storage.yml --limit node1
```

!!! warning "Data Loss"
    This playbook will FORMAT the USB drive, erasing all data.

**Filesystem options** (configurable via vars):

| Filesystem | Best For |
|------------|----------|
| `f2fs` (default) | Flash drives, SSDs |
| `ext4` | Traditional storage |
| `exfat` | Cross-platform compatibility |
| `vfat` | Maximum compatibility |

---

### monitoring.yml

**Purpose**: Deploy lightweight monitoring to nodes.

**Prerequisites**: USB storage must be mounted at `/x00`

**What it installs**:

- Collectd (metrics collection)
- LuCI Statistics (web graphs)
- vnStat (bandwidth tracking)
- luci-app-vnstat2
- luci-app-commands

**Monitored metrics**:

- CPU, Memory, Load Average
- Disk Usage
- Network Interfaces (bat0, br-lan, wlan0, wlan1)
- Wireless Stats
- Temperature
- Mesh Neighbor Connectivity

**Usage**:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/monitoring.yml --limit node1
```

**Access monitoring**:

- Web UI: `http://<node-ip>/cgi-bin/luci/admin/statistics/graph`
- CLI: `ssh root@<node-ip> monitoring-report.sh`

---

## Network Switching Playbooks

These playbooks switch your workstation's network configuration.

### switch-to-initial-network.yml

Switches to 192.168.1.0/24 network for accessing fresh nodes.

```bash
ansible-playbook playbooks/switch-to-initial-network.yml
```

### switch-to-mesh-network.yml

Switches to 10.11.12.0/24 network for accessing deployed nodes.

```bash
ansible-playbook playbooks/switch-to-mesh-network.yml
```

### switch-to-switch-network.yml

Switches to 192.168.0.0/24 network for accessing factory switches.

```bash
ansible-playbook playbooks/switch-to-switch-network.yml
```

### switch-to-mgmt-network.yml

Switches to 10.11.10.0/24 network for management VLAN.

```bash
ansible-playbook playbooks/switch-to-mgmt-network.yml
```

### setup-workstation-vlans.yml

**Purpose**: Configure workstation with multiple VLAN interfaces for simultaneous access to all networks via trunk port.

**What it does**:

1. Configures eth2 with /32 address for switch management (untagged)
2. Creates eth2.10 for Management VLAN (10.11.10.0/24)
3. Creates eth2.30 for IoT VLAN (10.11.30.0/24)
4. Creates eth2.200 for LAN/Client VLAN (10.11.12.0/24)
5. Adds host routes for switch management IPs
6. Verifies connectivity to switches and nodes

**Usage**:

```bash
ansible-playbook playbooks/setup-workstation-vlans.yml

# Or via Makefile
make setup-workstation-vlans
```

**Interfaces created**:

| Interface | Address | Purpose |
|-----------|---------|---------|
| eth2 | 10.11.10.101/32 | Switch management (untagged VLAN 1) |
| eth2.10 | 10.11.10.100/24 | Management network (nodes, infrastructure) |
| eth2.30 | 10.11.30.100/24 | IoT network |
| eth2.200 | 10.11.12.100/24 | LAN/Client network |

!!! note "Why separate eth2 and eth2.10?"
    TL-SG108E Easy Smart switches only respond to management on **untagged** traffic.
    Mesh nodes expect VLAN 10 **tagged** traffic. Both use 10.11.10.0/24 but different L2 paths.

### teardown-workstation-vlans.yml

**Purpose**: Remove all VLAN interfaces from workstation and reset eth2.

**What it does**:

1. Brings down and deletes eth2.10, eth2.30, eth2.200
2. Flushes IP addresses from eth2
3. Removes switch host routes
4. Brings down eth2

**Usage**:

```bash
ansible-playbook playbooks/teardown-workstation-vlans.yml

# Or via Makefile
make teardown-workstation-vlans
```

---

## Utility Playbooks

### update.yml

**Purpose**: Update packages on all nodes.

```bash
ansible-playbook -i inventory/hosts.yml playbooks/update.yml
```

### validate-env.yml

**Purpose**: Validate `.env` file configuration.

```bash
ansible-playbook playbooks/validate-env.yml
```

---

## Running Playbooks with Tags

Most playbooks support tags for selective execution:

```bash
# Only run network configuration
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --tags network

# Skip backup phase
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --skip-tags backup

# Only verify mesh status
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml --tags mesh
```

**Common tags**:

| Tag | Description |
|-----|-------------|
| `always` | Runs regardless of tag selection |
| `config` | Configuration tasks |
| `packages` | Package installation |
| `network` | Network configuration |
| `wireless` | Wireless configuration |
| `security` | Security settings |
| `mesh` | Batman-adv mesh tasks |
| `verify` | Verification tasks |

## Playbook Best Practices

### Order of Operations

For initial deployment:

1. `validate-env.yml` - Verify configuration
2. `deploy.yml` (node1) - Deploy first node
3. `deploy.yml` (node2) - Deploy second node
4. `deploy.yml` (node3) - Deploy third node
5. `verify.yml` - Verify mesh formation
6. `backup.yml` - Create initial backup

### Troubleshooting Failed Playbooks

```bash
# Verbose output
ansible-playbook -vvv -i inventory/hosts.yml playbooks/deploy.yml

# Start from specific task
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml \
  --start-at-task="Configure network"

# Step through tasks
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --step
```

### Check Mode

Always test with check mode first:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --check
```

!!! note
    Check mode may not work perfectly with `raw` module tasks (common in OpenWrt playbooks).
