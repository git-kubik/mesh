# TP-Link TL-SG108E Switch Integration Guide

This guide covers the integration of two TP-Link TL-SG108E 8-port smart switches into the mesh network for enhanced redundancy and expanded client capacity.

## Architecture Overview

```
                    ┌─────────────────┐
                    │     Node 1      │
                    │   10.11.12.1    │
                    │  LAN3    LAN4   │
                    └───┬────────┬────┘
                        │        │
        ┌───────────────┘        └───────────────┐
        │                                        │
        ▼                                        ▼
┌───────────────────┐                ┌───────────────────┐
│    SWITCH A       │                │    SWITCH B       │
│   10.11.10.11     │                │   10.11.10.12     │
├───────────────────┤                ├───────────────────┤
│ P1: Node1 LAN3    │                │ P1: Node1 LAN4    │
│ P2: Node2 LAN3    │                │ P2: Node2 LAN4    │
│ P3: Node3 LAN3    │                │ P3: Node3 LAN4    │
│ P4: Management    │                │ P4: Management    │
│ P5-P7: Clients    │                │ P5-P7: Clients    │
│ P8 ◄──────────────┼─(inter-switch)─┼──────────────► P8 │
└───────────────────┘                └───────────────────┘
        ▲                                        ▲
        │        ┌─────────────────┐             │
        └────────┤     Node 2      ├─────────────┘
                 │   10.11.12.2    │
                 └───┬────────┬────┘
                     │        │
        ┌────────────┘        └────────────┐
        │        ┌─────────────────┐       │
        └────────┤     Node 3      ├───────┘
                 │   10.11.12.3    │
                 └─────────────────┘
```

## VLAN Design

| VLAN | Name | Purpose | Network |
|------|------|---------|---------|
| 100 | mesh_backbone | Batman-adv mesh traffic | L2 only |
| 200 | clients | Client device access | 10.11.12.0/24 |
| 300 | iot | IoT/Infrastructure (LAN2) | 10.11.30.0/24 |
| 10 | management | Switch/node management | 10.11.10.0/24 |

## Node Port Assignment

| Port | Purpose | VLAN |
|------|---------|------|
| LAN1 | Client devices | Bridged to bat0 |
| LAN2 | IoT/Infrastructure | 300 (isolated) |
| LAN3 | Switch A trunk | 100, 200, 10 (tagged) |
| LAN4 | Switch B trunk | 100, 200, 10 (tagged) |

## Switch Configuration

### Prerequisites

- 2x TP-Link TL-SG108E switches
- Ethernet cables for connections
- Computer with web browser for configuration
- Use `make switch-to-switch-network` to configure your workstation for factory switch access

### Web GUI Menu Structure

The TL-SG108E web interface has these main menus (left sidebar):

```
System
├── System Info
├── IP Setting
├── User Account
└── System Tools

Switching
├── Port Setting
├── IGMP Snooping
└── LAG

Monitoring
├── Port Statistics
├── Port Mirror
└── Cable Test

VLAN
├── MTU VLAN
├── Port Based VLAN
├── 802.1Q VLAN
└── 802.1Q PVID Setting

QoS
├── Basic
└── Bandwidth Control

Save Config

Logout
```

---

## Switch A Configuration

### Step 1: Factory Reset (if needed)

1. Locate the **Reset** button (small hole on the side of the switch)
2. With the switch powered on, press and hold the reset button for **5+ seconds** using a paperclip
3. Release when all port LEDs blink simultaneously
4. Wait 30 seconds for the switch to restart

### Step 2: Connect to Factory Default Switch

1. Connect your computer to **any port (1-8)** on Switch A with an ethernet cable
   - Factory default: all ports are in VLAN 1, any port works
2. Configure your computer's IP:

   ```bash
   # Using the provided playbook:
   make switch-to-switch-network

   # Or manually set IP to 192.168.0.2/24
   ```

3. Open a web browser and navigate to: `http://192.168.0.1`
4. Login with default credentials:
   - **Username:** `admin`
   - **Password:** `admin`

> **After VLAN configuration:** Use **Port 4** (dedicated management port) for configuration access. Ports 5-7 are client-only (VLAN 200) and cannot reach the switch management interface.

### Step 3: Set Management IP Address

1. In the left sidebar, click **System**
2. Click **IP Setting**
3. You will see the IP Setting page with these fields:
   - **DHCP Setting:** Set to `Disable`
   - **IP Address:** Enter `10.11.10.11`
   - **Subnet Mask:** Enter `255.255.255.0`
   - **Default Gateway:** Enter `10.11.10.1`
4. Click the **Apply** button at the bottom

> **Note:** After applying, you will lose connection. To reconnect:
>
> 1. Stay connected to the same port (any port still works at this stage)
> 2. Run `make switch-to-mgmt-network` to switch your computer to 10.11.10.100/24
> 3. Access the switch at `http://10.11.10.11`

### Step 4: Enable 802.1Q VLAN Mode

1. In the left sidebar, click **VLAN**
2. Click **802.1Q VLAN**
3. You will see the 802.1Q VLAN Configuration page
4. Find the **802.1Q VLAN** dropdown at the top
5. Change from `Disable` to **`Enable`**
6. Click **Apply**
7. The page will refresh and show additional VLAN configuration options

### Step 5: Configure VLAN 100 (Mesh Backbone)

1. Stay on the **VLAN → 802.1Q VLAN** page
2. In the **VLAN ID** field, enter: `100`
3. For each port, select the radio button in the appropriate column:

| Port | Untagged | Tagged | Not Member |
|------|----------|--------|------------|
| Port 1 | ○ | ● | ○ |
| Port 2 | ○ | ● | ○ |
| Port 3 | ○ | ● | ○ |
| Port 4 | ○ | ○ | ● |
| Port 5 | ○ | ○ | ● |
| Port 6 | ○ | ○ | ● |
| Port 7 | ○ | ○ | ● |
| Port 8 | ○ | ● | ○ |

4. Click **Add/Modify**

### Step 6: Configure VLAN 200 (Client Traffic)

1. Stay on the **VLAN → 802.1Q VLAN** page
2. In the **VLAN ID** field, enter: `200`
3. For each port, select the radio button in the appropriate column:

| Port | Untagged | Tagged | Not Member |
|------|----------|--------|------------|
| Port 1 | ○ | ● | ○ |
| Port 2 | ○ | ● | ○ |
| Port 3 | ○ | ● | ○ |
| Port 4 | ○ | ○ | ● |
| Port 5 | ● | ○ | ○ |
| Port 6 | ● | ○ | ○ |
| Port 7 | ● | ○ | ○ |
| Port 8 | ○ | ● | ○ |

4. Click **Add/Modify**

### Step 7: Configure VLAN 10 (Management)

1. Stay on the **VLAN → 802.1Q VLAN** page
2. In the **VLAN ID** field, enter: `10`
3. For each port, select the radio button in the appropriate column:

| Port | Untagged | Tagged | Not Member |
|------|----------|--------|------------|
| Port 1 | ○ | ● | ○ |
| Port 2 | ○ | ● | ○ |
| Port 3 | ○ | ● | ○ |
| Port 4 | ● | ○ | ○ |
| Port 5 | ○ | ○ | ● |
| Port 6 | ○ | ○ | ● |
| Port 7 | ○ | ○ | ● |
| Port 8 | ○ | ● | ○ |

4. Click **Add/Modify**

### Step 8: Configure PVID Settings

The PVID (Port VLAN ID) determines which VLAN untagged incoming frames are assigned to.

1. In the left sidebar, click **VLAN**
2. Click **802.1Q PVID Setting**
3. You will see a table of all 8 ports with PVID fields
4. Configure PVIDs as follows:

| Port | PVID Value |
|------|------------|
| Port 1 | `1` (default) |
| Port 2 | `1` (default) |
| Port 3 | `1` (default) |
| Port 4 | `10` |
| Port 5 | `200` |
| Port 6 | `200` |
| Port 7 | `200` |
| Port 8 | `1` (default) |

5. For each port you need to change:
   - Click on the port row or select it
   - Enter the PVID value
   - Click **Apply**
6. Repeat for ports 4 (PVID `10`), 5, 6, and 7 (PVID `200`)

### Step 9: Enable IGMP Snooping

1. In the left sidebar, click **Switching**
2. Click **IGMP Snooping**
3. You will see the IGMP Snooping page
4. Find the **IGMP Snooping** dropdown/checkbox
5. Set to **Enable**
6. Click **Apply**

### Step 10: Verify Configuration Saved

On firmware 1.0.0 Build 20191021 and later, configuration is **automatically saved** when you click **Apply** or **Add/Modify**. No separate save step is required.

To verify your configuration persists:

1. Power cycle the switch (unplug and replug power)
2. Log back in and check that your VLAN settings are still present

> **Note:** Older firmware versions may require a separate "Save Config" step. If your settings don't persist after power cycle, check for firmware updates at [TP-Link Support](https://www.tp-link.com/support/).

### Step 11: Backup Configuration

After configuration is complete, export a backup:

1. In the left sidebar, click **System**
2. Click **System Tools**
3. Click **Config Backup**
4. Click **Backup Config** to download the `.cfg` file
5. Save the file (e.g., `switchA.cfg` or `switchB.cfg`)

Reference backup files are stored in `openwrt-mesh-ansible/switches/`:

- `switchA.cfg` - Switch A (10.11.10.11) configuration
- `switchB.cfg` - Switch B (10.11.10.12) configuration

**To restore a configuration:**

1. Go to **System → System Tools → Config Restore**
2. Click **Browse** and select the `.cfg` file
3. Click **Config Restore**
4. Wait for the switch to reboot with the restored configuration

### Important: Port Usage After Configuration

Once VLANs are configured, ports have different purposes:

| Port | Purpose | Management Access |
|------|---------|-------------------|
| **1** | Node 1 trunk | Yes (disconnect node to use) |
| **2** | Node 2 trunk | Yes (disconnect node to use) |
| **3** | Node 3 trunk | Yes (disconnect node to use) |
| **4** | **Management** | **Yes - use this for config** |
| **5-7** | Client devices | **No** - VLAN 200 only |
| **8** | Inter-switch trunk | Yes (but reserved for switch-to-switch) |

**To reconfigure a switch after VLAN setup:**

1. Connect your computer to **Port 4** (dedicated management port)
2. Run `make switch-to-mgmt-network`
3. Access `http://10.11.10.11` (Switch A) or `http://10.11.10.12` (Switch B)

---

## Switch B Configuration

Repeat **all steps** from Switch A configuration with these changes:

| Setting | Switch A | Switch B |
|---------|----------|----------|
| Management IP | `10.11.10.11` | `10.11.10.12` |
| All other settings | Same | Same |

---

## Physical Connections

After configuring both switches, make the physical connections:

### 1. Inter-Switch Trunk

Connect the two switches together:

```
Switch A Port 8  ◄────────────────►  Switch B Port 8
```

### 2. Node Connections

Connect each mesh node to both switches:

| Node | Connection 1 | Connection 2 |
|------|--------------|--------------|
| Node 1 | LAN3 → Switch A Port 1 | LAN4 → Switch B Port 1 |
| Node 2 | LAN3 → Switch A Port 2 | LAN4 → Switch B Port 2 |
| Node 3 | LAN3 → Switch A Port 3 | LAN4 → Switch B Port 3 |

### 3. Client Devices

Connect wired client devices to the client ports:

- **Switch A Ports 5-7:** Wired clients (up to 3 devices)
- **Switch B Ports 5-7:** Wired clients (up to 3 devices)

---

## VLAN Configuration Summary

### Switch Port VLAN Membership Table

| Port | Purpose | VLAN 1 | VLAN 10 (Mgmt) | VLAN 100 (Mesh) | VLAN 200 (Client) | PVID |
|------|---------|--------|----------------|-----------------|-------------------|------|
| 1 | Node 1 | Untagged | Tagged | Tagged | Tagged | 1 |
| 2 | Node 2 | Untagged | Tagged | Tagged | Tagged | 1 |
| 3 | Node 3 | Untagged | Tagged | Tagged | Tagged | 1 |
| 4 | Mgmt | Untagged | **Untagged** | - | - | 10 |
| 5 | Client | Untagged | - | - | Untagged | 200 |
| 6 | Client | Untagged | - | - | Untagged | 200 |
| 7 | Client | Untagged | - | - | Untagged | 200 |
| 8 | Inter-SW | Untagged | Tagged | Tagged | Tagged | 1 |

---

## Redundancy and Failover

### Failure Scenarios

| Failure | Impact | Recovery Time |
|---------|--------|---------------|
| Switch A fails | SwA clients disconnected | Traffic via Switch B + wireless, <3s |
| Switch B fails | SwB clients disconnected | Traffic via Switch A + wireless, <3s |
| Inter-switch link fails | No direct SwA↔SwB path | Traffic routes through nodes, <1s |
| Single node failure | Node unreachable | Other 2 nodes continue mesh |

### How Redundancy Works

1. **Dual switch paths**: Each node connects to both switches via separate ports
2. **Batman-adv mesh**: Automatically routes traffic via best available path
3. **Wireless backup**: 2.4GHz mesh provides additional redundancy
4. **Inter-switch trunk**: Allows direct switch-to-switch communication

---

## Verification

### Check VLAN Interfaces on Nodes

```bash
# SSH to any node
ssh root@10.11.12.1

# Verify VLAN interfaces exist
ip link show | grep "lan[34]\."
# Should show: lan3.100, lan3.200, lan4.100, lan4.200

# Check Batman interfaces
batctl if
# Should show: lan3.100, lan4.100, phy0-mesh0
```

### Check Mesh Connectivity

```bash
# View mesh originators
batctl o
# Should show all 3 nodes with TQ 255

# View mesh neighbors
batctl n
# Should show connections via both switches
```

### Test Client Connectivity

1. Connect a device to Switch A Port 5
2. Verify DHCP assigns IP from 10.11.12.x range
3. Ping all nodes: `ping 10.11.12.1`, `10.11.12.2`, `10.11.12.3`
4. Test internet: `ping 1.1.1.1`

### Test Failover

1. **Switch A failure test**:
   - Disconnect Switch A power
   - Verify mesh continues via Switch B
   - Reconnect and verify recovery

2. **Inter-switch link test**:
   - Disconnect one inter-switch cable
   - Verify traffic routes through nodes
   - Reconnect and verify recovery

---

## Troubleshooting

### Cannot Access Switch Web Interface

```bash
# Verify your computer is on the correct network
ip addr show

# For factory default switch (192.168.0.1):
make switch-to-switch-network

# For configured switch (10.11.10.x):
make switch-to-mgmt-network

# Test connectivity
ping 192.168.0.1   # or 10.11.10.11
```

### Configuration Not Saved After Reboot

The TL-SG108E stores configuration in RAM until explicitly saved:

1. Always click **Save Config** in the left sidebar after making changes
2. Verify you see "Save config successfully" message
3. Known issue: Save only once after all changes are complete

### No VLAN Interfaces on Nodes

```bash
# Check if VLAN module is loaded
lsmod | grep 8021q

# Manually create VLAN interface for testing
ip link add link lan3 name lan3.100 type vlan id 100
ip link set lan3.100 up
```

### Mesh Not Forming

```bash
# Check Batman status
batctl if
batctl o

# Check physical link
ip link show lan3
ip link show lan4

# Check for VLAN tagging issues
tcpdump -i lan3 -e vlan
```

### Client DHCP Issues

```bash
# Check bridge membership
brctl show br-lan

# Verify VLAN interfaces in bridge
bridge link show

# Check DHCP server
logread | grep dnsmasq
```

---

## Workstation Network Commands

Use these make targets to switch your workstation network for different tasks:

```bash
# Access factory-default TP-Link switch (192.168.0.1)
make switch-to-switch-network

# Access configured switches (10.11.10.x)
make switch-to-mgmt-network

# Access mesh network (10.11.12.x)
make switch-to-mesh-network

# Access fresh OpenWrt nodes (192.168.1.x)
make switch-to-initial-network
```

---

## Environment Variables

These variables control switch integration in `.env`:

```bash
# VLAN IDs for switch trunks
SWITCH_MESH_VLAN=100
SWITCH_CLIENT_VLAN=200

# Switch management IPs
SWITCH_A_IP=10.11.10.11
SWITCH_B_IP=10.11.10.12

# IoT network (LAN2)
IOT_VLAN=300
IOT_NETWORK=10.11.30.0
IOT_NETMASK=255.255.255.0
IOT_GATEWAY=10.11.30.1
```
