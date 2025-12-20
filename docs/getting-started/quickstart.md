# Quick Start Guide

This guide walks you through deploying your first OpenWrt mesh node in under 30 minutes.

## Prerequisites

Before starting, ensure you have:

| Requirement | Details |
|-------------|---------|
| **Hardware** | D-Link DIR-1960 A1 router (or compatible OpenWrt device) |
| **Computer** | With Ethernet port |
| **Network** | Ethernet cable, internet access |
| **Software** | SSH client, web browser |
| **Repository** | This repo cloned to your machine |

## Overview

The deployment process follows these steps:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Deployment Workflow                               │
├─────────────────────────────────────────────────────────────────────┤
│  1. Flash OpenWrt  →  2. Prepare Node  →  3. Deploy Config          │
│                                                                      │
│  Factory router       Package audit       Ansible automation        │
│  → OpenWrt 24.10      → Fix conflicts     → Full mesh config        │
│                       → Install deps      → Network, WiFi, etc.     │
└─────────────────────────────────────────────────────────────────────┘
```

**Important**: Fresh OpenWrt routers start at 192.168.1.1. Configure **one node at a time** to avoid IP conflicts.

---

## Step 1: Flash OpenWrt Firmware

### Download Firmware

1. Visit [OpenWrt Firmware Selector](https://firmware-selector.openwrt.org/)
2. Search for "D-Link DIR-1960 A1"
3. Download the **factory image** (for initial installation)
4. Verify SHA256 checksum

**Recommended Version**: OpenWrt 24.10.0 or later

### Flash via Web Interface

1. Power on the DIR-1960
2. Connect computer to LAN port via Ethernet
3. Access router admin: `http://192.168.0.1`
4. Navigate to **Firmware Upgrade**
5. Upload OpenWrt factory image
6. Wait 5 minutes for flash and reboot

### Alternative: TFTP Recovery

If web interface fails:

```bash
# Set static IP: 192.168.0.2/24
sudo ip addr add 192.168.0.2/24 dev eth0

# Power on router while holding reset button
# Wait for LED to blink, then upload via TFTP
tftp 192.168.0.1 -c put openwrt-factory.bin
```

---

## Step 2: Prepare Your Workstation

### Set Static IP

OpenWrt defaults to 192.168.1.1. Configure your workstation:

```bash
# Linux
sudo ip addr add 192.168.1.100/24 dev eth0
sudo ip link set eth0 up

# macOS
sudo ifconfig en0 192.168.1.100 netmask 255.255.255.0

# NetworkManager
nmcli con add type ethernet ifname eth0 con-name openwrt-setup \
  ip4 192.168.1.100/24
```

### Verify Connectivity

```bash
ping -c 3 192.168.1.1
# Expected: 64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.5 ms
```

**If ping fails:**

- Check cable is in LAN port (not WAN)
- Wait 2 minutes for full boot
- Try `http://192.168.1.1` in browser

---

## Step 3: Run Connectivity Check

Navigate to the Ansible directory:

```bash
cd openwrt-mesh-ansible
```

Temporarily update inventory for initial access:

```bash
# Edit inventory/hosts.yml
# Change node1's ansible_host from 10.11.12.1 to 192.168.1.1
```

```yaml
node1:
  ansible_host: 192.168.1.1  # Temporary for initial setup
  node_ip: 10.11.12.1        # Final mesh IP
  node_id: 1
```

Run connectivity check:

```bash
make check-node NODE=1
```

Expected output:

```
================================================================================
CONNECTIVITY CHECK SUMMARY: node1
================================================================================
Checks:
  [✓] Network - SSH port reachable
  [✓] Authentication - SSH login successful
  [✓] Python - Interpreter available
  [✓] OpenWrt - Valid OpenWrt system

Overall Status: READY
================================================================================
```

---

## Step 4: Audit the Node

Run the audit playbook to check package requirements:

```bash
make audit-node NODE=1
```

The audit will:

1. Identify hardware (model, CPU, RAM, storage)
2. List installed packages
3. Compare against mesh requirements
4. Generate preparation script if needed

**Sample output:**

```
================================================================================
AUDIT SUMMARY: node1
================================================================================
Hardware:
  Model: D-Link DIR-1960 A1
  Memory: 512 MB
  OpenWrt: 24.10.0

Package Status:
  Required Installed: 2/5
  Missing Required: 3
  Conflicts Found: 1

Audit Status: HAS_CONFLICTS

Missing Packages:
  - kmod-batman-adv
  - batctl-full
  - wpad-mesh-mbedtls

Conflicting Packages (must remove):
  - wpad-basic-mbedtls

Reports Generated:
  - ./audit_reports/node1_audit_*.json
  - ./audit_reports/node1_prepare.sh
================================================================================
```

---

## Step 5: Prepare the Node (If Needed)

If the audit shows conflicts or missing packages, run the generated script:

```bash
# Copy script to node
scp audit_reports/node1_prepare.sh root@192.168.1.1:/tmp/

# Execute on node
ssh root@192.168.1.1 'sh /tmp/node1_prepare.sh'
```

The script will:

- Create a backup
- Remove conflicting packages (e.g., wpad-basic-mbedtls)
- Install required packages (batman-adv, batctl, etc.)
- Verify installation

**Download the pre-change backup:**

```bash
mkdir -p backups
scp root@192.168.1.1:/tmp/backup-before-prep-*.tar.gz ./backups/
```

**Re-audit to confirm:**

```bash
make audit-node NODE=1
# Should show: Audit Status: READY
```

---

## Step 6: Deploy Configuration

Deploy the full mesh configuration:

```bash
make deploy-node NODE=1
```

**What gets configured:**

| Component | Configuration |
|-----------|---------------|
| Hostname | mesh-node1 |
| Client LAN | 10.11.12.1/24 (VLAN 200) |
| Management | 10.11.10.1/24 (VLAN 10) |
| Guest | 10.11.20.1/24 (VLAN 20) |
| IoT | 10.11.30.1/24 (VLAN 30) |
| WAN | DHCP client |
| Batman-adv | bat0 with BLA enabled |
| Mesh Backbone | VLAN 100 (lan3.100, lan4.100) |
| 2.4GHz WiFi | HA-Mesh (hidden), HA-Management, HA-IoT |
| 5GHz WiFi | HA-Client (802.11r), HA-Guest |
| DHCP | Per-node pools (100-149, 150-199, 200-249) |
| Firewall | Zone-based (lan, management, guest, iot, wan) |

**Important**: After deployment, the node IP changes from 192.168.1.1 to 10.11.12.1!

Wait 2-3 minutes for services to restart.

---

## Step 7: Disconnect and Update Inventory

### Disconnect Node 1

1. Physically unplug Ethernet from node 1
2. Leave node 1 powered on
3. Set it aside

### Reset Workstation

```bash
# Remove static IP
sudo ip addr del 192.168.1.100/24 dev eth0

# Restore DHCP if needed
sudo dhclient eth0
```

### Update Inventory

```bash
# Edit inventory/hosts.yml
# Change node1's ansible_host back to final IP
```

```yaml
node1:
  ansible_host: 10.11.12.1  # Back to mesh IP
  node_ip: 10.11.12.1
  node_id: 1
```

---

## Step 8: Repeat for Remaining Nodes

### Node 2

```bash
# 1. Set workstation IP
sudo ip addr add 192.168.1.100/24 dev eth0

# 2. Connect and power on Node 2
ping -c 3 192.168.1.1

# 3. Update inventory: node2.ansible_host = 192.168.1.1

# 4. Check, audit, prepare (if needed), deploy
make check-node NODE=2
make audit-node NODE=2
# Run prepare script if needed
make deploy-node NODE=2

# 5. Disconnect Node 2
# 6. Remove static IP
# 7. Update inventory: node2.ansible_host = 10.11.12.2
```

### Node 3

Same process with Node 3 (final IP: 10.11.12.3)

---

## Step 9: Connect the Mesh

With all three nodes configured, wire the physical mesh through managed switches:

### Topology with Switches

```
                         ┌──────────────────────────┐
                         │        INTERNET          │
                         └────┬─────────┬─────────┬─┘
                              │         │         │
                         ┌────┴───┐ ┌───┴────┐ ┌──┴─────┐
                         │ Node 1 │ │ Node 2 │ │ Node 3 │
                         │10.11.12│ │10.11.12│ │10.11.12│
                         │   .1   │ │   .2   │ │   .3   │
                         └────┬───┘ └───┬────┘ └──┬─────┘
                         LAN3 │ LAN4    │ LAN3  LAN4 │ LAN3
                              │         │           │
┌────────────────────────────┴─────────┴───────────┴──────────────────────────┐
│                             Switch A                                         │
│                  (All VLANs: 10, 20, 30, 100, 200)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                             Switch C                                         │
│                        (Mesh VLAN 100 only)                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                    + 2.4GHz wireless mesh backup (HA-Mesh)
```

### Physical Connections

| From | Port | To | VLANs Carried |
|------|------|----|---------------|
| Node 1 | LAN3 | Switch A | 10, 20, 30, 100, 200 (trunk) |
| Node 1 | LAN4 | Switch C | 100 only (mesh backbone) |
| Node 2 | LAN3 | Switch A | 10, 20, 30, 100, 200 (trunk) |
| Node 2 | LAN4 | Switch C | 100 only (mesh backbone) |
| Node 3 | LAN3 | Switch A | 10, 20, 30, 100, 200 (trunk) |
| Node 3 | LAN4 | Switch C | 100 only (mesh backbone) |

**Switch Configuration**: See [Switch Integration](../architecture/switch-integration.md) for TP-Link TL-SG108E VLAN setup.

### Connect WAN

Connect each node's WAN port to your upstream network (ISP router or modem).

---

## Step 10: Verify the Mesh

### Connect to Mesh Network

Connect your workstation to any node's LAN1/LAN2 port. You'll get DHCP address 10.11.12.100-249.

### Run Verification

```bash
make verify
```

Expected output:

```
All nodes reachable: YES
Batman interfaces active: YES
Mesh topology: FULL (3 nodes)
Gateways available: 3
```

### Check Batman Status

```bash
make batman-status
```

Shows:

- Active interfaces per node
- Originator table (routing)
- Gateway list

### Test WiFi

Scan for networks. You should see:

- **HA-Client** (from all 3 nodes)

Connect with the password from `group_vars/all.yml` → `client_password`

---

## Congratulations

Your mesh network is operational:

- **3-node mesh** with automatic routing via Batman-adv
- **Switch-based backbone** with VLAN trunking
- **Wireless backup** via 2.4GHz 802.11s mesh
- **Multi-gateway** WAN failover
- **VLAN segmentation** for security
- **802.11r** fast roaming

### What You Have

| Feature | Status |
|---------|--------|
| Mesh nodes | 3 (10.11.12.1-3) |
| Managed switches | 2 (Switch A + Switch C) |
| Wired mesh | VLAN 100 trunks |
| Wireless backup | 2.4GHz HA-Mesh (hidden) |
| Client WiFi | 5GHz HA-Client (802.11r) |
| Guest WiFi | 5GHz HA-Guest (isolated) |
| Management WiFi | 2.4GHz HA-Management |
| IoT WiFi | 2.4GHz HA-IoT (isolated) |
| VLANs | 5 (10, 20, 30, 100, 200) |
| BLA | Enabled (loop prevention) |
| Gateway redundancy | All 3 nodes |

---

## Next Steps

### Daily Operations

```bash
make verify        # Health check
make batman-status # Mesh topology
make backup        # Configuration backup
```

### Make Changes

```bash
# Edit configuration
nano group_vars/all.yml

# Deploy to all nodes
make deploy

# Or deploy specific component
make deploy-wireless
```

### Learn More

- [Architecture Overview](../architecture/overview.md) - Complete technical deep-dive
- [VLAN Architecture](../architecture/vlan-architecture.md) - Network segmentation details
- [Switch Integration](../architecture/switch-integration.md) - Managed switch configuration
- [Makefile Reference](../reference/makefile.md) - All available commands

---

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Can't ping 192.168.1.1 | Check cable in LAN port, verify static IP |
| SSH connection refused | Wait 2 min for boot, check firewall |
| Node unreachable after deploy | Wait 3 min, try new IP (10.11.12.x) |
| Mesh not forming | Check physical connections, `batctl if` |
| WiFi not visible | `wifi reload`, check 5GHz support |

For detailed troubleshooting, see [Common Issues](../troubleshooting/common-issues.md).
