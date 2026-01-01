# Makefile Command Reference

This document provides a comprehensive reference for all Makefile targets available in the `openwrt-mesh-ansible/` directory.

## Quick Reference

```bash
cd openwrt-mesh-ansible
make help              # Show all available commands
make <command>         # Run a specific command
make <command> NODE=1  # Run command for specific node
make <command> VERBOSE=1  # Run with verbose output
```

## Node Operations

### Unified Commands (Auto-Detect Phase)

These commands automatically detect whether a node is in initial state (192.168.1.1) or production state (10.11.12.x).

| Command | Description |
|---------|-------------|
| `make deploy-node NODE=1` | Deploy full configuration to Node 1 |
| `make deploy-node NODE=2` | Deploy full configuration to Node 2 |
| `make deploy-node NODE=3` | Deploy full configuration to Node 3 |
| `make check-node NODE=1` | Check connectivity to Node 1 |
| `make audit-node NODE=1` | Audit configuration on Node 1 |

**Options:**

- `NODE=1|2|3` - Required. Specifies which node.
- `VERBOSE=1` - Optional. Enables verbose Ansible output.

**Example:**

```bash
# Deploy with verbose output
make deploy-node NODE=1 VERBOSE=1
```

### Multi-Node Operations

Use these after all nodes are configured at production IPs.

| Command | Description |
|---------|-------------|
| `make check-all` | Check connectivity to all nodes |
| `make deploy` | Deploy to all nodes |
| `make audit` | Audit all nodes |
| `make verify` | Verify mesh status |
| `make backup` | Backup all configurations |
| `make ping` | Ping all nodes |
| `make uptime` | Show uptime for all nodes |
| `make reboot` | Reboot all nodes |

### Targeted Deployments

Deploy specific components only:

| Command | Description |
|---------|-------------|
| `make deploy-network` | Deploy network config only |
| `make deploy-wireless` | Deploy wireless config only |
| `make deploy-dhcp` | Deploy DHCP config only |
| `make deploy-firewall` | Deploy firewall config only |
| `make packages` | Install packages only |

## Environment & Setup

| Command | Description |
|---------|-------------|
| `make validate-env` | Validate .env configuration |
| `make install` | Show installation instructions |
| `make clean` | Clean temporary files |

## Network Switching

Manual network switching for workstation:

| Command | Description |
|---------|-------------|
| `make switch-to-initial-network` | Switch to 192.168.1.100 (fresh nodes) |
| `make switch-to-mesh-network` | Switch to 10.11.12.100 (deployed nodes) |
| `make switch-to-switch-network` | Switch to 192.168.0.2 (factory switches) |
| `make switch-to-mgmt-network` | Switch to 10.11.10.100 (configured switches) |

!!! note
    `deploy-node` handles network switching automatically. These are for manual operations.

### Multi-VLAN Workstation Access

For accessing all networks simultaneously via trunk port:

| Command | Description |
|---------|-------------|
| `make setup-workstation-vlans` | Setup VLAN interfaces on enp5s0 for multi-network access |
| `make teardown-workstation-vlans` | Remove VLAN interfaces from enp5s0 |

**Interfaces created by `setup-workstation-vlans`:**

| Interface | Address | Purpose |
|-----------|---------|---------|
| enp5s0 | 10.11.10.101/32 | Switch management (untagged) |
| enp5s0.10 | 10.11.10.100/24 | Management VLAN 10 |
| enp5s0.30 | 10.11.30.100/24 | IoT VLAN 30 |
| enp5s0.200 | 10.11.12.100/24 | LAN/Client VLAN 200 |

!!! tip "Trunk Port Required"
    Connect workstation to Switch A Port 5 (configured as trunk with VLANs 10, 30, 200 tagged).

## USB Storage

| Command | Description |
|---------|-------------|
| `make usb-storage NODE=1` | Setup USB storage on Node 1 (FORMAT!) |
| `make usb-storage` | Setup USB storage on ALL nodes (FORMAT!) |
| `make usb-status NODE=1` | Check USB storage status on Node 1 |
| `make usb-status` | Check USB storage status on all nodes |

!!! warning "Data Loss Warning"
    `usb-storage` will FORMAT the USB drive, erasing all data!

## Monitoring

Requires USB storage to be configured first.

| Command | Description |
|---------|-------------|
| `make deploy-monitoring NODE=1` | Deploy collectd monitoring to Node 1 |
| `make deploy-monitoring` | Deploy monitoring to ALL nodes |
| `make monitoring-status NODE=1` | Check monitoring status |
| `make monitoring-status` | Check monitoring on all nodes |
| `make monitoring-graphs NODE=1` | Open monitoring web UI |
| `make monitoring-logs NODE=1` | View mesh health logs |

## Distributed Syslog

Persistent logging to USB storage.

| Command | Description |
|---------|-------------|
| `make syslog-view NODE=1` | View syslog summary |
| `make syslog-view` | View syslog for all nodes |
| `make syslog-tail NODE=1` | Tail today's syslog |
| `make syslog-list NODE=1` | List all syslog files |
| `make syslog-capture NODE=1` | Manually trigger syslog capture |

## Telegram Alerting

| Command | Description |
|---------|-------------|
| `make test-alert NODE=1` | Manually trigger alert check |
| `make alert-status NODE=1` | View alert status summary |
| `make alert-logs NODE=1` | View full alert log |
| `make alert-clear NODE=1` | Clear alert state |

## Debugging & Status

| Command | Description |
|---------|-------------|
| `make batman-status` | Check batman-adv mesh status |
| `make logs` | Fetch recent logs from nodes |
| `make show-logs` | Show last 100 lines of Ansible logs |
| `make tail-logs` | Follow Ansible logs (live) |
| `make clear-logs` | Clear Ansible log files |

## Local Package Repository

For faster, offline-capable deployments.

| Command | Description |
|---------|-------------|
| `make repo-setup` | Download ALL packages (~500MB-1GB) |
| `make repo-setup-selective` | Download only .env packages (~50-100MB) |
| `make repo-start` | Start local repository HTTP server |
| `make repo-status` | Check repository status |
| `make repo-clean` | Remove local repository cache |

**Workflow:**

```bash
# Option 1: Full archive (recommended for offline use)
make repo-setup        # Download all packages
make repo-start        # Start HTTP server on port 8080

# Option 2: Selective (faster, smaller)
make repo-setup-selective
make repo-start

# Set OPKG_REPO_URL in .env, then deploy
make deploy-node NODE=1
```

## Configuration Snapshots

Create complete filesystem snapshots for backup and image building.

| Command | Description |
|---------|-------------|
| `make snapshot NODE=1` | Create full config snapshot for Node 1 |
| `make snapshot-all` | Create snapshots for ALL nodes |
| `make snapshot-diff NODE=1` | Show changes since last snapshot |

**Output location:** `snapshots/<hostname>/`

**Contents:**

- Complete UCI configuration
- All /etc files (passwd, fstab, crontab, SSH keys)
- Package list with versions
- Custom scripts
- Network, wireless, mesh state
- Restore script and instructions

## Custom Firmware Images

Build custom OpenWrt images from snapshots.

| Command | Description |
|---------|-------------|
| `make image-build NODE=1` | Build custom image for Node 1 |
| `make image-build-all` | Build images for ALL nodes |
| `make image-info` | Show Image Builder info/profiles |
| `make image-shell` | Enter Image Builder container shell |
| `make image-clean` | Remove built images |

**Prerequisites:**

1. Node snapshot: `make snapshot NODE=1`
2. Local package repo: `make repo-setup`
3. Docker installed

**Output:** `images/<hostname>-sysupgrade.bin`

## Factory Reset & Sysupgrade

| Command | Description |
|---------|-------------|
| `make factory-reset NODE=1` | Reset Node 1 to factory defaults |
| `make sysupgrade NODE=1` | Flash mesh image to Node 1 |
| `make sysupgrade NODE=1 IMAGE_TYPE=vanilla` | Flash vanilla OpenWrt |
| `make sysupgrade NODE=1 IMAGE_PATH=/path/to.bin` | Flash specific image |

!!! danger "Destructive Operations"
    These commands erase all configuration. The node will reboot.

**Image Types:**

- `mesh` (default): Custom-built image with config baked in
- `vanilla`: Stock OpenWrt image

## Testing

| Command | Description |
|---------|-------------|
| `make test` | Run standard live tests |
| `make test-quick` | Run quick connectivity tests only |
| `make test-full` | Run all tests with HTML report |
| `make test-destructive` | Run destructive failover tests |

!!! warning "Destructive Tests"
    `test-destructive` temporarily disrupts network connectivity!

**Test reports:** `../test-reports/`

## Service Management

| Command | Description |
|---------|-------------|
| `make restart-network` | Restart network service on all nodes |
| `make restart-wireless` | Restart wireless service on all nodes |

## Typical Workflows

### Initial Deployment

```bash
# 1. Validate environment
make validate-env

# 2. Deploy nodes one at a time
# Connect Node 1 via Ethernet
make deploy-node NODE=1
# Wait for reboot, disconnect, connect Node 2
make deploy-node NODE=2
# Repeat for Node 3
make deploy-node NODE=3

# 3. Verify mesh
make check-all
make batman-status
```

### Day-to-Day Operations

```bash
# Check status
make check-all
make batman-status

# View logs
make syslog-view

# Make changes and redeploy
make deploy
make verify
```

### Backup and Recovery

```bash
# Create snapshots
make snapshot-all

# Check for drift
make snapshot-diff NODE=1

# Restore from snapshot
# See snapshots/<hostname>/RESTORE.md
```

### Custom Firmware

```bash
# Full workflow
make snapshot NODE=1         # Capture config
make repo-setup              # Download packages
make image-build NODE=1      # Build image
make sysupgrade NODE=1       # Flash to node
```

## Environment Variables

The Makefile reads configuration from `../.env`:

| Variable | Used By |
|----------|---------|
| `SSH_KEY_PATH` | All SSH operations |
| `OPKG_REPO_URL` | Package installation |
| `TELEGRAM_*` | Alerting |
| All network variables | Deployment |

## Log Files

Ansible logs are written to `logs/` with timestamped filenames:

```
logs/deploy-node_node1_20240101_120000.log
logs/check-all_20240101_120500.log
```

Use `make show-logs` and `make tail-logs` to view.
