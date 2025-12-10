# TP-Link TL-SG108E Switch Integration Guide

This guide covers the integration of three TP-Link TL-SG108E 8-port smart switches into the mesh network for enhanced redundancy, expanded client capacity, and infrastructure support.

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
      ┌───────────────────┐                    ┌───────────────────┐
      │    SWITCH A       │                    │    SWITCH B       │
      │   10.11.10.11     │                    │   10.11.10.12     │
      ├───────────────────┤                    ├───────────────────┤
      │ P1: Node1 LAN3    │                    │ P1: Node1 LAN4    │
      │ P2: Node2 LAN3    │                    │ P2: Node2 LAN4    │
      │ P3: Node3 LAN3    │                    │ P3: Node3 LAN4    │
      │ P4: Management    │                    │ P4: Management    │
      │ P5: Switch C      │                    │ P5: Switch C      │
      │ P6-P7: Clients    │                    │ P6-P7: Clients    │
      │ P8 ◄──────────────┼──(inter-switch)────┼──────────────► P8 │
      └─────────┬─────────┘                    └─────────┬─────────┘
                │                                        │
                │         ┌─────────────────┐            │
                └─────────┤     Node 2      ├────────────┘
                          │   10.11.12.2    │
                          └───┬────────┬────┘
                              │        │
              ┌───────────────┘        └───────────────┐
              │         ┌─────────────────┐            │
              └─────────┤     Node 3      ├────────────┘
                        │   10.11.12.3    │
                        └─────────────────┘

      ┌───────────────────┐                    ┌───────────────────┐
      │    SWITCH A       │                    │    SWITCH B       │
      │      P5           │                    │       P5          │
      └─────────┬─────────┘                    └─────────┬─────────┘
                │                                        │
                │            ┌───────────────┐           │
                │            │   SWITCH C    │           │
                │            │  10.11.10.13  │           │
                │            ├───────────────┤           │
                └───────────►│ P1: LAG (SwA) │◄──────────┘
                             │ P2: LAG (SwB) │
                             │ P3: RPi       │
                             │ P4: Proxmox1  │
                             │ P5: Proxmox2  │
                             │ P6-8: IoT     │
                             └───────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
             ┌──────────┐     ┌──────────┐     ┌──────────┐
             │   RPi    │     │ Proxmox1 │     │ Proxmox2 │
             │ QDevice  │     │10.11.10.21    │10.11.10.22│
             │10.11.10.20    └──────────┘     └──────────┘
             │ (Docker) │           │                │
             └──────────┘           └───(Storage)────┘
                                      10.11.50.0/30
```

## VLAN Design

| VLAN | Name | Purpose | Network |
|------|------|---------|---------|
| 10 | management | Switch/node management, Proxmox, VMs | 10.11.10.0/24 |
| 30 | iot | IoT devices (isolated) | 10.11.30.0/24 |
| 100 | mesh_backbone | Batman-adv mesh traffic | L2 only |
| 200 | clients | Client device access | 10.11.12.0/24 |

## Node Port Assignment

| Port | Purpose | VLAN |
|------|---------|------|
| LAN1 | Client devices | Bridged to bat0 |
| LAN2 | IoT/Infrastructure | 30 (isolated) |
| LAN3 | Switch A trunk | 10, 30, 100, 200 (tagged) |
| LAN4 | Switch B trunk | 10, 30, 100, 200 (tagged) |

---

## Switch Configuration Prerequisites

- 3x TP-Link TL-SG108E switches
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

> **After VLAN configuration:** Use **Port 4** (dedicated management port) for configuration access. Ports 6-7 are client-only (VLAN 200) and cannot reach the switch management interface.

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
| Port 5 | ○ | ○ | ● |
| Port 6 | ● | ○ | ○ |
| Port 7 | ● | ○ | ○ |
| Port 8 | ○ | ○ | ● |

!!! warning "Critical: Port 8 Must NOT Be Member of VLAN 200"
    Do NOT add Port 8 to VLAN 200. Client traffic must traverse the mesh (bat0) to reach clients on the other switch. Adding VLAN 200 to Port 8 creates a Layer 2 loop with duplicate traffic paths.

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
| Port 5 | ○ | ● | ○ |
| Port 6 | ○ | ○ | ● |
| Port 7 | ○ | ○ | ● |
| Port 8 | ○ | ● | ○ |

4. Click **Add/Modify**

### Step 8: Configure VLAN 30 (IoT)

1. Stay on the **VLAN → 802.1Q VLAN** page
2. In the **VLAN ID** field, enter: `30`
3. For each port, select the radio button in the appropriate column:

| Port | Untagged | Tagged | Not Member |
|------|----------|--------|------------|
| Port 1 | ○ | ● | ○ |
| Port 2 | ○ | ● | ○ |
| Port 3 | ○ | ● | ○ |
| Port 4 | ○ | ○ | ● |
| Port 5 | ○ | ● | ○ |
| Port 6 | ○ | ○ | ● |
| Port 7 | ○ | ○ | ● |
| Port 8 | ○ | ● | ○ |

4. Click **Add/Modify**

### Step 9: Configure PVID Settings

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
| Port 5 | `1` (default) |
| Port 6 | `200` |
| Port 7 | `200` |
| Port 8 | `1` (default) |

5. For each port you need to change:
   - Click on the port row or select it
   - Enter the PVID value
   - Click **Apply**

### Step 10: Enable IGMP Snooping

1. In the left sidebar, click **Switching**
2. Click **IGMP Snooping**
3. You will see the IGMP Snooping page
4. Find the **IGMP Snooping** dropdown/checkbox
5. Set to **Enable**
6. Click **Apply**

### Step 11: Verify Configuration Saved

On firmware 1.0.0 Build 20191021 and later, configuration is **automatically saved** when you click **Apply** or **Add/Modify**. No separate save step is required.

To verify your configuration persists:

1. Power cycle the switch (unplug and replug power)
2. Log back in and check that your VLAN settings are still present

> **Note:** Older firmware versions may require a separate "Save Config" step. If your settings don't persist after power cycle, check for firmware updates at [TP-Link Support](https://www.tp-link.com/support/).

### Step 12: Backup Configuration

After configuration is complete, export a backup:

1. In the left sidebar, click **System**
2. Click **System Tools**
3. Click **Config Backup**
4. Click **Backup Config** to download the `.cfg` file
5. Save the file as `switchA.cfg`

Reference backup files are stored in `openwrt-mesh-ansible/switches/`:

- `switchA.cfg` - Switch A (10.11.10.11) configuration
- `switchB.cfg` - Switch B (10.11.10.12) configuration
- `switchC.cfg` - Switch C (10.11.10.13) configuration

### Switch A Port Summary

| Port | Purpose | VLAN 1 | VLAN 10 | VLAN 30 | VLAN 100 | VLAN 200 | PVID |
|------|---------|--------|---------|---------|----------|----------|------|
| 1 | Node 1 trunk | U | T | T | T | T | 1 |
| 2 | Node 2 trunk | U | T | T | T | T | 1 |
| 3 | Node 3 trunk | U | T | T | T | T | 1 |
| 4 | Mgmt access | U | **U** | - | - | - | 10 |
| 5 | Switch C uplink | U | T | T | - | - | 1 |
| 6 | Client | U | - | - | - | U | 200 |
| 7 | Client | U | - | - | - | U | 200 |
| 8 | Inter-switch | U | T | T | T | **-** | 1 |

**Legend:** U = Untagged, T = Tagged, - = Not Member

---

## Switch B Configuration

Repeat **all steps** from Switch A configuration with these changes:

| Setting | Switch A | Switch B |
|---------|----------|----------|
| Management IP | `10.11.10.11` | `10.11.10.12` |
| Backup filename | `switchA.cfg` | `switchB.cfg` |
| All VLAN settings | Same | Same |
| All PVID settings | Same | Same |

---

## Switch C Configuration (Infrastructure Switch)

Switch C is the downstream infrastructure switch that provides:

- **Dual uplinks** to Switch A and Switch B for redundancy
- **Ports for Proxmox infrastructure** (VLAN 10 - Management)
- **Ports for IoT devices** (VLAN 30 - IoT)

### Switch C Architecture Diagram

```
                    ┌───────────────────┐     ┌───────────────────┐
                    │     SWITCH A      │     │     SWITCH B      │
                    │    10.11.10.11    │     │    10.11.10.12    │
                    └─────────┬─────────┘     └─────────┬─────────┘
                              │ Port 5                  │ Port 5
                              │                         │
                              │   (dual uplinks for     │
                              │      redundancy)        │
                              ▼                         ▼
                    ┌─────────────────────────────────────────────┐
                    │              SWITCH C                       │
                    │             10.11.10.13                     │
                    ├─────────────────────────────────────────────┤
                    │                                             │
                    │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
                    │  │ P1  │ │ P2  │ │ P3  │ │ P4  │ │ P5  │   │
                    │  │ SwA │ │ SwB │ │ RPi │ │ PVE1│ │ PVE2│   │
                    │  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘   │
                    │     │      │      │      │      │         │
                    │  ┌─────┐ ┌─────┐ ┌─────┐                   │
                    │  │ P6  │ │ P7  │ │ P8  │   IoT Ports       │
                    │  │ IoT │ │ IoT │ │ IoT │   (VLAN 30)       │
                    │  └──┬──┘ └──┬──┘ └──┬──┘                   │
                    │     │      │      │                        │
                    └─────┼──────┼──────┼────────────────────────┘
                          │      │      │
                          ▼      ▼      ▼
                    IoT Devices (10.11.30.x)

    ┌──────────────────────────────────────────────────────────────┐
    │                   INFRASTRUCTURE DEVICES                      │
    ├──────────────────────────────────────────────────────────────┤
    │                                                              │
    │  Port 3              Port 4              Port 5              │
    │    │                   │                   │                 │
    │    ▼                   ▼                   ▼                 │
    │ ┌──────────┐      ┌──────────┐      ┌──────────┐            │
    │ │   RPi    │      │ Proxmox1 │      │ Proxmox2 │            │
    │ │ QDevice  │      │          │      │          │            │
    │ │10.11.10.20│     │10.11.10.21│     │10.11.10.22│           │
    │ │          │      │          │      │          │            │
    │ │ Docker   │      │   eth0   │      │   eth0   │            │
    │ │ Container│      │ (mgmt)   │      │ (mgmt)   │            │
    │ └──────────┘      │          │      │          │            │
    │                   │   eth2 ──┼──────┼── eth2   │            │
    │                   │ Storage  │      │ Storage  │            │
    │                   │10.11.50.1│      │10.11.50.2│            │
    │                   └──────────┘      └──────────┘            │
    │                         │                │                   │
    │                         └─── Crossover ──┘                   │
    │                           10.11.50.0/30                      │
    └──────────────────────────────────────────────────────────────┘
```

### Switch C VLAN Design

| VLAN | ID | Purpose | Ports |
|------|----|---------|-------|
| Management | 10 | RPi QDevice, Proxmox hosts, VMs | P1-2 (tagged), P3-5 (untagged) |
| IoT | 30 | IoT devices (isolated) | P1-2 (tagged), P6-8 (untagged) |

### Switch C Port Assignment

| Port | Purpose | VLAN 10 (Mgmt) | VLAN 30 (IoT) | PVID |
|------|---------|----------------|---------------|------|
| 1 | Uplink to Switch A | Tagged | Tagged | 1 |
| 2 | Uplink to Switch B | Tagged | Tagged | 1 |
| 3 | RPi QDevice | **Untagged** | - | 10 |
| 4 | Proxmox Node 1 | **Untagged** | - | 10 |
| 5 | Proxmox Node 2 | **Untagged** | - | 10 |
| 6 | IoT Device | - | **Untagged** | 30 |
| 7 | IoT Device | - | **Untagged** | 30 |
| 8 | IoT Device | - | **Untagged** | 30 |

---

### Switch C Step 1: Factory Reset

1. Locate the **Reset** button (small hole on the side of the switch)
2. With the switch powered on, press and hold the reset button for **5+ seconds** using a paperclip
3. Release when all port LEDs blink simultaneously
4. Wait 30 seconds for the switch to restart

### Switch C Step 2: Connect to Factory Default Switch

1. Connect your computer to **any port (1-8)** on Switch C with an ethernet cable
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

### Switch C Step 3: Set Management IP Address

1. In the left sidebar, click **System**
2. Click **IP Setting**
3. Configure the following fields:
   - **DHCP Setting:** Set to `Disable`
   - **IP Address:** Enter `10.11.10.13`
   - **Subnet Mask:** Enter `255.255.255.0`
   - **Default Gateway:** Enter `10.11.10.1`
4. Click the **Apply** button

> **Note:** After applying, you will lose connection. To reconnect:
>
> 1. Run `make switch-to-mgmt-network` to switch your computer to 10.11.10.100/24
> 2. Access the switch at `http://10.11.10.13`

### Switch C Step 4: Enable 802.1Q VLAN Mode

1. In the left sidebar, click **VLAN**
2. Click **802.1Q VLAN**
3. Find the **802.1Q VLAN** dropdown at the top
4. Change from `Disable` to **`Enable`**
5. Click **Apply**
6. The page will refresh and show additional VLAN configuration options

### Switch C Step 5: Configure VLAN 10 (Management/Infrastructure)

This VLAN carries traffic for:

- RPi QDevice (Proxmox quorum)
- Proxmox Node 1 and Node 2
- VMs running on Proxmox (Home Assistant, MQTT broker, etc.)

1. Stay on the **VLAN → 802.1Q VLAN** page
2. In the **VLAN ID** field, enter: `10`
3. For each port, select the radio button in the appropriate column:

| Port | Untagged | Tagged | Not Member | Purpose |
|------|----------|--------|------------|---------|
| Port 1 | ○ | ● | ○ | Uplink to Switch A (tagged) |
| Port 2 | ○ | ● | ○ | Uplink to Switch B (tagged) |
| Port 3 | ● | ○ | ○ | RPi QDevice (untagged) |
| Port 4 | ● | ○ | ○ | Proxmox 1 (untagged) |
| Port 5 | ● | ○ | ○ | Proxmox 2 (untagged) |
| Port 6 | ○ | ○ | ● | IoT only |
| Port 7 | ○ | ○ | ● | IoT only |
| Port 8 | ○ | ○ | ● | IoT only |

4. Click **Add/Modify**

### Switch C Step 6: Configure VLAN 30 (IoT)

This VLAN carries traffic for IoT devices that need to reach:

- Home Assistant (via firewall rules to VLAN 10)
- MQTT broker (via firewall rules to VLAN 10)
- Internet (via mesh nodes)

1. Stay on the **VLAN → 802.1Q VLAN** page
2. In the **VLAN ID** field, enter: `30`
3. For each port, select the radio button in the appropriate column:

| Port | Untagged | Tagged | Not Member | Purpose |
|------|----------|--------|------------|---------|
| Port 1 | ○ | ● | ○ | Uplink to Switch A (tagged) |
| Port 2 | ○ | ● | ○ | Uplink to Switch B (tagged) |
| Port 3 | ○ | ○ | ● | Infrastructure only |
| Port 4 | ○ | ○ | ● | Infrastructure only |
| Port 5 | ○ | ○ | ● | Infrastructure only |
| Port 6 | ● | ○ | ○ | IoT device (untagged) |
| Port 7 | ● | ○ | ○ | IoT device (untagged) |
| Port 8 | ● | ○ | ○ | IoT device (untagged) |

4. Click **Add/Modify**

### Switch C Step 7: Configure PVID Settings

The PVID determines which VLAN untagged incoming frames are assigned to.

1. In the left sidebar, click **VLAN**
2. Click **802.1Q PVID Setting**
3. Configure PVIDs as follows:

| Port | PVID Value | Reason |
|------|------------|--------|
| Port 1 | `1` | Uplink trunk - uses tagged VLANs |
| Port 2 | `1` | Uplink trunk - uses tagged VLANs |
| Port 3 | `10` | RPi connects untagged, needs VLAN 10 |
| Port 4 | `10` | Proxmox 1 connects untagged, needs VLAN 10 |
| Port 5 | `10` | Proxmox 2 connects untagged, needs VLAN 10 |
| Port 6 | `30` | IoT device connects untagged, needs VLAN 30 |
| Port 7 | `30` | IoT device connects untagged, needs VLAN 30 |
| Port 8 | `30` | IoT device connects untagged, needs VLAN 30 |

4. For each port:
   - Click on the port row or select it
   - Enter the PVID value in the field
   - Click **Apply**
5. Repeat for all ports that need PVID changes (Ports 3-8)

### Switch C Step 8: Verify No LAG Configuration

!!! warning "Do NOT Configure LAG on Switch C"
    LAG (Link Aggregation) requires all member ports to connect to the **same remote switch**. Since Port 1 connects to Switch A and Port 2 connects to Switch B, LAG cannot be used here.

    If you accidentally configured LAG, both ports will flash on/off simultaneously (~1 second interval) indicating a loop detection or negotiation failure.

**To remove accidental LAG configuration:**

1. In the left sidebar, click **Switching**
2. Click **LAG**
3. Ensure Ports 1 and 2 are **NOT** members of any LAG group
4. If they are in a LAG group, remove them and click **Apply**

The dual uplinks provide redundancy through the VLAN configuration - if one uplink fails, traffic continues via the other uplink through the inter-switch connection (Switch A Port 8 ↔ Switch B Port 8).

### Switch C Step 9: Enable IGMP Snooping

1. In the left sidebar, click **Switching**
2. Click **IGMP Snooping**
3. Find the **IGMP Snooping** dropdown/checkbox
4. Set to **Enable**
5. Click **Apply**

### Switch C Step 10: Verify and Save Configuration

1. Verify your VLAN settings:
   - Go to **VLAN → 802.1Q VLAN**
   - Check that VLANs 10 and 30 appear in the list
   - Verify port memberships match the tables above

2. Verify your PVID settings:
   - Go to **VLAN → 802.1Q PVID Setting**
   - Confirm Ports 3-5 have PVID 10
   - Confirm Ports 6-8 have PVID 30

3. Verify NO LAG configuration:
   - Go to **Switching → LAG**
   - Confirm Ports 1 and 2 are NOT in any LAG group

4. Power cycle the switch to confirm settings persist

### Switch C Step 11: Backup Configuration

1. In the left sidebar, click **System**
2. Click **System Tools**
3. Click **Config Backup**
4. Click **Backup Config** to download the `.cfg` file
5. Save the file as `switchC.cfg`

Store in `openwrt-mesh-ansible/switches/switchC.cfg`

### Switch C Port Summary Table

| Port | Purpose | VLAN 1 | VLAN 10 (Mgmt) | VLAN 30 (IoT) | PVID |
|------|---------|--------|----------------|---------------|------|
| 1 | Uplink to Switch A | U | T | T | 1 |
| 2 | Uplink to Switch B | U | T | T | 1 |
| 3 | RPi QDevice | U | **U** | - | 10 |
| 4 | Proxmox 1 | U | **U** | - | 10 |
| 5 | Proxmox 2 | U | **U** | - | 10 |
| 6 | IoT Device | U | - | **U** | 30 |
| 7 | IoT Device | U | - | **U** | 30 |
| 8 | IoT Device | U | - | **U** | 30 |

**Legend:** U = Untagged, T = Tagged, - = Not Member

---

## Switch A & B Updates for Switch C

Before connecting Switch C, update Switch A and Switch B to:

1. Add VLAN 30 (IoT) to node trunk ports (P1-3)
2. Add VLAN 30 (IoT) to inter-switch port (P8)
3. Add VLAN 10 and 30 to Port 5 for Switch C uplink

### Update Switch A

1. Log into Switch A at `http://10.11.10.11`
2. Go to **VLAN → 802.1Q VLAN**

#### Add VLAN 30 to Switch A

3. Enter VLAN ID: `30`
4. Configure ports:

| Port | Untagged | Tagged | Not Member |
|------|----------|--------|------------|
| Port 1 | ○ | ● | ○ |
| Port 2 | ○ | ● | ○ |
| Port 3 | ○ | ● | ○ |
| Port 4 | ○ | ○ | ● |
| Port 5 | ○ | ● | ○ |
| Port 6 | ○ | ○ | ● |
| Port 7 | ○ | ○ | ● |
| Port 8 | ○ | ● | ○ |

5. Click **Add/Modify**

#### Update VLAN 10 on Switch A (add Port 5)

6. Enter VLAN ID: `10`
7. Ensure Port 5 is **Tagged** (for Switch C uplink)
8. Click **Add/Modify**

### Update Switch B

Repeat the same steps on Switch B at `http://10.11.10.12`.

---

## Physical Connections

### Switch A and B Inter-Connection

Connect Switch A and Switch B together:

```
Switch A Port 8  ◄────────────────►  Switch B Port 8
```

### Node to Switch Connections

Connect each mesh node to both switches:

| Node | Connection 1 | Connection 2 |
|------|--------------|--------------|
| Node 1 | LAN3 → Switch A Port 1 | LAN4 → Switch B Port 1 |
| Node 2 | LAN3 → Switch A Port 2 | LAN4 → Switch B Port 2 |
| Node 3 | LAN3 → Switch A Port 3 | LAN4 → Switch B Port 3 |

### Switch C Uplink Connections

Connect Switch C to both Switch A and Switch B for redundancy:

```
Switch A Port 5  ◄────────────────►  Switch C Port 1
Switch B Port 5  ◄────────────────►  Switch C Port 2
```

!!! note "Dual Uplinks for Redundancy"
    Both uplinks should be connected for full redundancy. If one uplink fails, traffic will route through the other via the inter-switch connection (Switch A P8 ↔ Switch B P8).

### Infrastructure Device Connections

| Device | Switch C Port | IP Address | Notes |
|--------|---------------|------------|-------|
| RPi QDevice | Port 3 | 10.11.10.20 | Proxmox cluster quorum |
| Proxmox Node 1 | Port 4 | 10.11.10.21 | eth0 (management) |
| Proxmox Node 2 | Port 5 | 10.11.10.22 | eth0 (management) |

### Proxmox Storage Network

Connect Proxmox nodes directly with a crossover cable for storage replication:

```
Proxmox 1 eth2 (10.11.50.1) ◄── Crossover Cable ──► Proxmox 2 eth2 (10.11.50.2)
```

This private /30 network is used for:

- Ceph/ZFS replication
- Live migration traffic
- Cluster communication backup

### IoT Device Connections

Connect IoT devices to Switch C Ports 6-8:

| Port | Example Device | IP Range |
|------|----------------|----------|
| Port 6 | Smart sensors | 10.11.30.100-199 |
| Port 7 | IoT gateway | 10.11.30.100-199 |
| Port 8 | Smart plugs | 10.11.30.100-199 |

---

## VLAN Configuration Summary

### Complete Switch Port VLAN Membership

#### Switch A

| Port | Purpose | VLAN 1 | VLAN 10 | VLAN 30 | VLAN 100 | VLAN 200 | PVID |
|------|---------|--------|---------|---------|----------|----------|------|
| 1 | Node 1 | U | T | T | T | T | 1 |
| 2 | Node 2 | U | T | T | T | T | 1 |
| 3 | Node 3 | U | T | T | T | T | 1 |
| 4 | Mgmt | U | **U** | - | - | - | 10 |
| 5 | Switch C uplink | U | T | T | - | - | 1 |
| 6 | Client | U | - | - | - | U | 200 |
| 7 | Client | U | - | - | - | U | 200 |
| 8 | Inter-SW | U | T | T | T | **-** | 1 |

#### Switch B

Same as Switch A.

#### Switch C

| Port | Purpose | VLAN 1 | VLAN 10 | VLAN 30 | PVID |
|------|---------|--------|---------|---------|------|
| 1 | Uplink (SwA) | U | T | T | 1 |
| 2 | Uplink (SwB) | U | T | T | 1 |
| 3 | RPi | U | **U** | - | 10 |
| 4 | Proxmox 1 | U | **U** | - | 10 |
| 5 | Proxmox 2 | U | **U** | - | 10 |
| 6 | IoT | U | - | **U** | 30 |
| 7 | IoT | U | - | **U** | 30 |
| 8 | IoT | U | - | **U** | 30 |

!!! note "VLAN 200 Not on Port 8"
    Port 8 (inter-switch) does NOT carry VLAN 200 to prevent L2 loops. Client traffic between switches routes through the Batman mesh.

---

## Critical: VLAN 200 Inter-Switch Isolation

!!! danger "Layer 2 Loop Prevention"
    **VLAN 200 (client traffic) MUST NOT be trunked between switches when the inter-switch link (Port 8) is connected.**

### The Problem

The mesh architecture creates multiple Layer 2 paths for client traffic:

```
Path 1: Client → Switch A → VLAN 200 tagged → Switch B (via Port 8)
Path 2: Client → Switch A → VLAN 200 → Node → bat0 mesh → Node → VLAN 200 → Switch B
```

If both paths exist simultaneously:

- **MAC address flapping**: Switches see the same MAC on multiple ports
- **Broadcast storms**: Same broadcast arrives via multiple paths
- **Duplicate frames**: Traffic delivered twice to the destination

### The Solution

The configuration in this guide sets Port 8 as **Not Member** of VLAN 200, ensuring:

- Mesh backbone (VLAN 100) traverses both switch paths
- Client traffic (VLAN 200) only reaches clients via Batman mesh
- No duplicate client traffic paths

---

## Redundancy and Failover

### Failure Scenarios

| Failure | Impact | Recovery Time |
|---------|--------|---------------|
| Switch A fails | SwA clients disconnected | Traffic via Switch B + wireless, <3s |
| Switch B fails | SwB clients disconnected | Traffic via Switch A + wireless, <3s |
| Switch C fails | IoT + Proxmox disconnected | No automatic failover |
| Inter-switch link fails | No direct SwA↔SwB path | Traffic routes through nodes, <1s |
| Single uplink to Switch C fails | No impact | Traffic via other uplink + inter-switch |
| Single node failure | Node unreachable | Other 2 nodes continue mesh |

### How Redundancy Works

1. **Dual switch paths**: Each node connects to both switches via separate ports
2. **Dual uplinks**: Switch C connects to both Switch A and Switch B
3. **Inter-switch trunk**: Switch A ↔ Switch B link provides alternate path
4. **Batman-adv mesh**: Automatically routes traffic via best available path
5. **Wireless backup**: 2.4GHz mesh provides additional redundancy

---

## Verification

### Automated Testing

Run the infrastructure test suite to verify all switches and devices are reachable:

```bash
# Test switches and infrastructure devices (10.11.10.x)
make test-infrastructure

# This tests:
# - Switch A (10.11.10.11)
# - Switch B (10.11.10.12)
# - Switch C (10.11.10.13)
# - RPi QDevice (10.11.10.20) - skipped if not deployed
# - Proxmox nodes (10.11.10.21-22) - skipped if not deployed
```

### Check VLAN Interfaces on Nodes

```bash
# SSH to any node
ssh root@10.11.12.1

# Verify VLAN interfaces exist
ip link show | grep "lan[34]\."
# Should show: lan3.10, lan3.30, lan3.100, lan3.200, lan4.10, lan4.30, lan4.100, lan4.200

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

1. Connect a device to Switch A Port 6
2. Verify DHCP assigns IP from 10.11.12.x range
3. Ping all nodes: `ping 10.11.12.1`, `10.11.12.2`, `10.11.12.3`
4. Test internet: `ping 1.1.1.1`

### Test Infrastructure Connectivity

```bash
# From your workstation on management network
make switch-to-mgmt-network

# Ping all switches
ping 10.11.10.11  # Switch A
ping 10.11.10.12  # Switch B
ping 10.11.10.13  # Switch C

# Ping infrastructure devices (if deployed)
ping 10.11.10.20  # RPi QDevice
ping 10.11.10.21  # Proxmox 1
ping 10.11.10.22  # Proxmox 2
```

### Test IoT Connectivity

```bash
# From an IoT device on VLAN 30
ip addr show  # Should have 10.11.30.x address

# Test gateway
ping 10.11.30.1

# Test internet
ping 1.1.1.1

# Test Home Assistant (allowed by firewall)
curl -s http://10.11.10.21:8123/api/ | head

# Test SSH to Proxmox (should be blocked)
nc -zv 10.11.10.21 22  # Should fail/timeout
```

### Test Failover

1. **Switch A failure test**:
   - Disconnect Switch A power
   - Verify mesh continues via Switch B
   - Reconnect and verify recovery

2. **Switch C uplink failover test**:
   - Disconnect one uplink cable (Switch A P5 to Switch C P1)
   - Verify infrastructure still reachable via other uplink
   - Reconnect and verify both uplinks active

3. **Inter-switch link test**:
   - Disconnect Port 8 cable between Switch A and B
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
ping 192.168.0.1   # Factory default
ping 10.11.10.11   # Switch A
ping 10.11.10.12   # Switch B
ping 10.11.10.13   # Switch C
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

### Switch C Ports Flashing On/Off Together

If Ports 1 and 2 on Switch C flash on and off simultaneously (~1 second interval), this indicates **accidental LAG configuration** causing loop detection.

**Fix:**

1. Log into Switch C at `http://10.11.10.13`
2. Go to **Switching → LAG**
3. Remove Ports 1 and 2 from any LAG group
4. Click **Apply**
5. Ports should stop flashing and show steady link lights

```bash
# After fixing, verify connectivity
ping 10.11.10.11  # Switch A
ping 10.11.10.12  # Switch B
ping 10.11.10.13  # Switch C
```

### IoT Devices Not Getting DHCP

```bash
# On mesh node, check DHCP server
logread | grep dnsmasq

# Verify VLAN 30 interface exists
ip addr show | grep "10.11.30"

# Check bridge membership
bridge link show

# Verify IoT zone in firewall
iptables -L -v -n | grep iot
```

### Infrastructure Cannot Reach Gateway

```bash
# On Proxmox/RPi, check network config
ip addr show
ip route show

# Verify default gateway is 10.11.10.1
# Verify PVID on Switch C port is set to 10

# From mesh node, check management bridge
ip addr show br-management_bridge
# Should show 10.11.10.1, 10.11.10.2, or 10.11.10.3
```

### IoT Cannot Reach Home Assistant

```bash
# On mesh node, check firewall rules
iptables -L FORWARD -v -n | grep 10.11.30

# Verify inter-VLAN routing is enabled
cat /proc/sys/net/ipv4/ip_forward  # Should be 1

# Test from mesh node
ping 10.11.10.21    # Proxmox/HA
ping 10.11.30.100   # IoT device

# Check allowed ports (1883, 8123, 8443, 8883)
iptables -L FORWARD -v -n | grep -E "1883|8123"
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
SWITCH_C_IP=10.11.10.13

# IoT network (LAN2 and VLAN 30)
IOT_VLAN=30
IOT_NETWORK=10.11.30.0
IOT_NETMASK=255.255.255.0
IOT_GATEWAY=10.11.30.1

# Infrastructure IPs (for DHCP reservations)
RPI_QDEVICE_IP=10.11.10.20
PROXMOX1_IP=10.11.10.21
PROXMOX2_IP=10.11.10.22

# Proxmox storage network
PROXMOX_STORAGE_NET=10.11.50.0/30
PROXMOX1_STORAGE_IP=10.11.50.1
PROXMOX2_STORAGE_IP=10.11.50.2
```

---

## Proxmox Network Configuration

### DHCP Reservations

Add infrastructure MAC addresses to `openwrt-mesh-ansible/group_vars/all.yml`:

```yaml
static_hosts:
  - name: rpi-qdevice
    mac: 'dc:a6:32:94:67:eb'
    ip: 10.11.10.20
  - name: proxmox1
    mac: 'YY:YY:YY:YY:YY:YY'  # Get from: ip link show eth0
    ip: 10.11.10.21
  - name: proxmox2
    mac: 'ZZ:ZZ:ZZ:ZZ:ZZ:ZZ'  # Get from: ip link show eth0
    ip: 10.11.10.22
```

Then deploy to update DHCP on mesh nodes:

```bash
make deploy
```

### Proxmox Node 1 Network (`/etc/network/interfaces`)

```
# Loopback
auto lo
iface lo inet loopback

# Management network (VLAN 10) - DHCP with reservation
auto eth0
iface eth0 inet dhcp

# VM Bridge (for VMs on management network)
auto vmbr0
iface vmbr0 inet static
    address 10.11.10.21/24
    bridge-ports eth0
    bridge-stp off
    bridge-fd 0

# Storage network (crossover to Proxmox 2)
auto eth2
iface eth2 inet static
    address 10.11.50.1/30
```

### Proxmox Node 2 Network (`/etc/network/interfaces`)

```
# Loopback
auto lo
iface lo inet loopback

# Management network (VLAN 10) - DHCP with reservation
auto eth0
iface eth0 inet dhcp

# VM Bridge (for VMs on management network)
auto vmbr0
iface vmbr0 inet static
    address 10.11.10.22/24
    bridge-ports eth0
    bridge-stp off
    bridge-fd 0

# Storage network (crossover to Proxmox 1)
auto eth2
iface eth2 inet static
    address 10.11.50.2/30
```

---

## Firewall Rules (Mesh Nodes)

These rules are **automatically configured by Ansible** in the `firewall_config` role (`roles/firewall_config/templates/firewall.j2`).

### IoT → Management Access

| Source | Destination | Port | Service | Action |
|--------|-------------|------|---------|--------|
| 10.11.30.0/24 | 10.11.10.0/24 | 1883 | MQTT | ACCEPT |
| 10.11.30.0/24 | 10.11.10.0/24 | 8883 | MQTT TLS | ACCEPT |
| 10.11.30.0/24 | 10.11.10.0/24 | 8123 | Home Assistant | ACCEPT |
| 10.11.30.0/24 | 10.11.10.0/24 | 8443 | Home Assistant TLS | ACCEPT |
| 10.11.30.0/24 | 10.11.10.0/24 | * | All other | REJECT |

### Zone Configuration

| Zone | Networks | Input | Forward | Notes |
|------|----------|-------|---------|-------|
| management | management_bridge | ACCEPT | ACCEPT | Full access |
| iot | iot | REJECT | REJECT | Isolated, selective access to mgmt |
| lan | br-lan | ACCEPT | ACCEPT | Trusted clients |

---

## Ansible Configuration

The mesh node network and firewall configuration is managed by Ansible roles.

### Network Configuration

**File:** `roles/network_config/templates/network.j2`

VLAN interfaces created on trunk ports (LAN3/LAN4):

| VLAN | Interface | Purpose |
|------|-----------|---------|
| 10 | lan3.10, lan4.10 | Management network |
| 30 | lan3.30, lan4.30 | IoT network |
| 100 | lan3.100, lan4.100 | Mesh backbone |
| 200 | lan3.200, lan4.200 | Client traffic |

Bridge configurations:

| Bridge | Ports | IP (per node) |
|--------|-------|---------------|
| management_bridge | lan3.10, lan4.10 | 10.11.10.{1,2,3} |
| iot | lan2, lan3.30, lan4.30 | 10.11.30.{1,2,3} |
| br-lan | bat0, lan1, lan3.200, lan4.200 | 10.11.12.{1,2,3} |

### Firewall Configuration

**File:** `roles/firewall_config/templates/firewall.j2`

Zones and forwarding rules are automatically configured including:

- Management zone with full LAN access
- IoT zone with selective access to management services
- Inter-VLAN routing between management and LAN

### Deployment

After modifying switch configurations, deploy to mesh nodes:

```bash
# Deploy all configuration
make deploy

# Or deploy specific roles
cd openwrt-mesh-ansible
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --tags network,firewall
```
