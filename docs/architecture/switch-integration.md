# TP-Link Switch Integration Guide

This guide covers the integration of TP-Link switches into the mesh network for enhanced redundancy, expanded client capacity, and infrastructure support.

![Switch Port Mapping](../assets/diagrams/switch-port-mapping.svg)

*Switch topology showing port assignments, VLAN tags, and device connections across all three switches.*

!!! warning "Switch Limitations - No STP Support"
    The TL-SG108E and TL-SG108PE are "Easy Smart" switches that do **NOT** support STP/RSTP. To avoid L2 loops:

    - **Switch A** carries ALL user VLANs (10, 30, 100, 200) - bridged to mesh via bat0
    - **Switch C** carries ONLY mesh backbone (VLAN 100) - no user VLANs

    Batman-adv Bridge Loop Avoidance (BLA) prevents loops between Switch A and the mesh.
    **Switch C management** requires out-of-band access - it is NOT reachable via the mesh network.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              NETWORK TOPOLOGY                               │
│            (HA Design with BLA Loop Prevention on Switch A)                 │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                        WAN───┤   Node 1    │
                              │ 10.11.12.1  │
                              │  GW Primary │
                              └──┬───────┬──┘
                            LAN3 │       │ LAN4
                                 │       │
                                 ▼       ▼
┌────────────────────────────────┐       ┌────────────────────────────────────┐
│      SWITCH A (TL-SG108E)      │       │       SWITCH C (TL-SG108E)         │
│  Main Distribution - All VLANs │       │   Mesh Backbone + Mgmt Link        │
│         10.11.10.11            │       │          10.11.10.13               │
├────────────────────────────────┤       ├────────────────────────────────────┤
│ P1: Node1 LAN3 (10,30,100,200) │       │ P1: Node1 LAN4 (100 only)          │
│ P2: Node2 LAN3 (10,30,100,200) │       │ P2: Node2 LAN4 (100 only)          │
│ P3: Node3 LAN3 (10,30,100,200) │       │ P3: Node3 LAN4 (100 only)          │
│ P4: Switch B   (10,30 tagged)  │       │ P4: Switch A   (10 tagged) ◄───────┼──┐
│ P5: Mgmt WS    (All VLANs)     │       │ P5: spare                          │  │
│ P6: Switch C   (10 tagged) ────┼───────┼──────────────────────────────────────┘ │
│ P7: Client     (200 untagged)  │       │ P6: spare                          │
│ P8: Client     (200 untagged)  │       │ P7: spare                          │
└───────────┬────────────────────┘       │ P8: spare                          │
                                         └────────────────────────────────────┘
            │ P4
            ▼
┌────────────────────────────────┐
│      SWITCH B (TL-SG108PE)     │
│  Infrastructure + PoE - 10,30  │
│         10.11.10.12            │
├────────────────────────────────┤
│ P1: Switch A   (10,30 tagged)  │
│ P2: Infra      (10 untagged)   │
│ P3: Infra      (10 untagged)   │
│ P4: Infra      (10 untagged)   │
│ P5: IoT PoE    (30 untagged)   │
│ P6: IoT PoE    (30 untagged)   │
│ P7: IoT PoE    (30 untagged)   │
│ P8: IoT PoE    (30 untagged)   │
└────────────────────────────────┘
```

## Physical Connections

| From | To | Cable | VLANs |
|------|-----|-------|-------|
| Node 1 LAN3 | Switch A P1 | Ethernet | 10, 30, 100, 200 (tagged) |
| Node 1 LAN4 | Switch C P1 | Ethernet | 100 only (tagged) |
| Node 2 LAN3 | Switch A P2 | Ethernet | 10, 30, 100, 200 (tagged) |
| Node 2 LAN4 | Switch C P2 | Ethernet | 100 only (tagged) |
| Node 3 LAN3 | Switch A P3 | Ethernet | 10, 30, 100, 200 (tagged) |
| Node 3 LAN4 | Switch C P3 | Ethernet | 100 only (tagged) |
| Switch A P4 | Switch B P1 | Ethernet | 10, 30 (tagged) |
| **Switch A P6** | **Switch C P4** | **Ethernet** | **1 (untagged) - Management link** |

## VLAN Design

| VLAN | Name | Purpose | Network | Switch A | Switch B | Switch C |
|------|------|---------|---------|----------|----------|----------|
| 1 | default | Switch management | - | ✓ | ✓ | ✓ (via SwA link) |
| 10 | management | Node management, Proxmox, VMs | 10.11.10.0/24 | ✓ | ✓ | ✗ |
| 30 | iot | IoT devices (isolated) | 10.11.30.0/24 | ✓ | ✓ | ✗ |
| 100 | mesh_backbone | Batman-adv mesh traffic | L2 only | ✓ | ✗ | ✓ |
| 200 | clients | Client device access | 10.11.12.0/24 | ✓ | ✗ | ✗ |

*Switch C receives VLAN 1 via direct link from Switch A (P6→P4) for management access.*

!!! info "Loop Prevention Design"
    **Switch A** carries all user VLANs (10, 30, 200) which are bridged to the mesh (bat0.X).
    Batman-adv BLA (Bridge Loop Avoidance) prevents loops between Switch A paths and mesh paths.

    **Switch C** carries:

    - VLAN 100 (mesh backbone) on ports 1-3 from mesh nodes
    - VLAN 1 (default/management) on port 4 from Switch A (direct link)

    The TL-SG108E "Easy Smart" switches only respond to management on **untagged** traffic.
    All three switches use VLAN 1 (untagged) for management access.

    **Never add VLAN 10, 30, or 200 to Switch C** - these would create L2 loops.

## Node Port Assignment

| Port | Purpose | VLANs | Bridged to |
|------|---------|-------|------------|
| LAN1 | Client devices | untagged | br-lan (bat0) |
| LAN2 | IoT/Infrastructure | untagged | br-iot (bat0.30) |
| LAN3 | Switch A trunk | 10, 30, 100, 200 (tagged) | br-mgmt, br-iot, br-lan (via VLANs) |
| LAN4 | Switch C trunk | 100 only (tagged) | lan4.100 → bat0 hardif |

!!! info "Switch C Management Path"
    LAN4 only has `lan4.100` configured. There is NO `lan4.10` on mesh nodes.
    Switch C receives VLAN 10 via **direct link from Switch A** (P6→P4).
    This provides management access without creating L2 loops through the mesh.

---

## Switch A Configuration (TL-SG108E)

Switch A is the **main distribution switch** carrying all VLANs.

### Step 1: Factory Reset (if needed)

1. Locate the **Reset** button (small hole on the side)
2. With switch powered on, press and hold for **5+ seconds**
3. Release when all port LEDs blink
4. Wait 30 seconds for restart

### Step 2: Initial Access

1. Connect your computer to any port
2. Configure IP: `192.168.0.2/24`

   ```bash
   make switch-to-switch-network
   ```

3. Browse to `http://192.168.0.1`
4. Login: `admin` / `admin`

### Step 3: Set Management IP

1. Go to **System → IP Setting**
2. Configure:
   - DHCP Setting: `Disable`
   - IP Address: `10.11.10.11`
   - Subnet Mask: `255.255.255.0`
   - Default Gateway: `10.11.10.1`
3. Click **Apply**
4. Reconnect using:

   ```bash
   make switch-to-mgmt-network
   ```

5. Access at `http://10.11.10.11`

### Step 4: Enable 802.1Q VLAN

1. Go to **VLAN → 802.1Q VLAN**
2. Set 802.1Q VLAN to **Enable**
3. Click **Apply**

### Step 5: Configure VLAN 100 (Mesh Backbone)

1. VLAN ID: `100`
2. VLAN Name: `MeshBackbone`
3. Port configuration:

| Port | Untagged | Tagged | Not Member | Purpose |
|------|:--------:|:------:|:----------:|---------|
| 1 | | ● | | Node 1 trunk |
| 2 | | ● | | Node 2 trunk |
| 3 | | ● | | Node 3 trunk |
| 4 | | | ● | Switch B |
| 5 | | ● | | Mgmt workstation |
| 6 | | | ● | Switch C link |
| 7 | | | ● | Client |
| 8 | | | ● | Client |

4. Click **Add/Modify**

### Step 6: Configure VLAN 200 (Clients)

1. VLAN ID: `200`
2. VLAN Name: `Clients`
3. Port configuration:

| Port | Untagged | Tagged | Not Member | Purpose |
|------|:--------:|:------:|:----------:|---------|
| 1 | | ● | | Node 1 trunk |
| 2 | | ● | | Node 2 trunk |
| 3 | | ● | | Node 3 trunk |
| 4 | | | ● | Switch B |
| 5 | | ● | | Mgmt workstation |
| 6 | | | ● | Switch C link |
| 7 | ● | | | Client |
| 8 | ● | | | Client |

4. Click **Add/Modify**

### Step 7: Configure VLAN 10 (Management)

1. VLAN ID: `10`
2. VLAN Name: `MgmtInfra`
3. Port configuration:

| Port | Untagged | Tagged | Not Member | Purpose |
|------|:--------:|:------:|:----------:|---------|
| 1 | | ● | | Node 1 trunk |
| 2 | | ● | | Node 2 trunk |
| 3 | | ● | | Node 3 trunk |
| 4 | | ● | | Switch B uplink |
| 5 | | ● | | Mgmt workstation |
| 6 | | | ● | Switch C link |
| 7 | | | ● | Client |
| 8 | | | ● | Client |

4. Click **Add/Modify**

### Step 8: Configure VLAN 30 (IoT)

1. VLAN ID: `30`
2. VLAN Name: `IoT`
3. Port configuration:

| Port | Untagged | Tagged | Not Member | Purpose |
|------|:--------:|:------:|:----------:|---------|
| 1 | | ● | | Node 1 trunk |
| 2 | | ● | | Node 2 trunk |
| 3 | | ● | | Node 3 trunk |
| 4 | | ● | | Switch B uplink |
| 5 | | ● | | Mgmt workstation |
| 6 | | | ● | Switch C link |
| 7 | | | ● | Client |
| 8 | | | ● | Client |

4. Click **Add/Modify**

### Step 9: Configure PVID Settings

Go to **VLAN → 802.1Q PVID Setting**:

| Port | PVID | Purpose |
|------|------|---------|
| P1 | 1 | Node trunk |
| P2 | 1 | Node trunk |
| P3 | 1 | Node trunk |
| P4 | 1 | Switch B uplink |
| P5 | 1 | Mgmt workstation trunk |
| P6 | 1 | Switch C link |
| P7 | 200 | Client |
| P8 | 200 | Client |

### Step 10: Enable IGMP Snooping

1. Go to **Switching → IGMP Snooping**
2. Set to **Enable**
3. Click **Apply**

### Switch A VLAN Summary (After Configuration)

| Port | Purpose | VLAN 1 | VLAN 10 | VLAN 30 | VLAN 100 | VLAN 200 | PVID |
|------|---------|:------:|:-------:|:-------:|:--------:|:--------:|:----:|
| 1 | Node 1 | ●U | ●T | ●T | ●T | ●T | 1 |
| 2 | Node 2 | ●U | ●T | ●T | ●T | ●T | 1 |
| 3 | Node 3 | ●U | ●T | ●T | ●T | ●T | 1 |
| 4 | Switch B | ●U | ●T | ●T | | | 1 |
| 5 | Mgmt WS | ●U | ●T | ●T | ●T | ●T | 1 |
| 6 | **Switch C** | ●U | **●U** | | | | 1 |
| 7 | Client | | | | | ●U | 200 |
| 8 | Client | | | | | ●U | 200 |

**Legend:** ●T = Tagged, ●U = Untagged, (empty) = Not Member

---

## Switch B Configuration (TL-SG108PE)

Switch B is the **infrastructure switch** for Proxmox, RPi, and IoT devices with **PoE support**.

### Step 1-4: Initial Setup

Same as Switch A, but use:

- IP Address: `10.11.10.12`

### Step 5: Configure VLAN 10 (Management)

1. VLAN ID: `10`
2. VLAN Name: `MgmtInfra`
3. Port configuration:

| Port | Untagged | Tagged | Not Member | Purpose |
|------|:--------:|:------:|:----------:|---------|
| 1 | | ● | | Uplink to Switch A |
| 2 | ● | | | Infrastructure |
| 3 | ● | | | Infrastructure |
| 4 | ● | | | Infrastructure |
| 5 | | | ● | IoT PoE |
| 6 | | | ● | IoT PoE |
| 7 | | | ● | IoT PoE |
| 8 | | | ● | IoT PoE |

4. Click **Add/Modify**

### Step 6: Configure VLAN 30 (IoT)

1. VLAN ID: `30`
2. VLAN Name: `IoT`
3. Port configuration:

| Port | Untagged | Tagged | Not Member | Purpose |
|------|:--------:|:------:|:----------:|---------|
| 1 | | ● | | Uplink to Switch A |
| 2 | | | ● | Infrastructure |
| 3 | | | ● | Infrastructure |
| 4 | | | ● | Infrastructure |
| 5 | ● | | | IoT PoE |
| 6 | ● | | | IoT PoE |
| 7 | ● | | | IoT PoE |
| 8 | ● | | | IoT PoE |

4. Click **Add/Modify**

### Step 7: Configure PVID Settings

| Port | PVID | Purpose |
|------|------|---------|
| P1 | 1 | Uplink trunk |
| P2 | 10 | Infrastructure |
| P3 | 10 | Infrastructure |
| P4 | 10 | Infrastructure |
| P5 | 30 | IoT PoE |
| P6 | 30 | IoT PoE |
| P7 | 30 | IoT PoE |
| P8 | 30 | IoT PoE |

### Switch B VLAN Summary (After Configuration)

| Port | Purpose | VLAN 1 | VLAN 10 | VLAN 30 | PVID | PoE |
|------|---------|:------:|:-------:|:-------:|:----:|:---:|
| 1 | Uplink (SwA) | ●U | ●T | ●T | 1 | |
| 2 | Infrastructure | ●U | ●U | | 10 | |
| 3 | Infrastructure | ●U | ●U | | 10 | |
| 4 | Infrastructure | ●U | ●U | | 10 | ✓ |
| 5 | IoT PoE | ●U | | ●U | 30 | ✓ |
| 6 | IoT PoE | ●U | | ●U | 30 | ✓ |
| 7 | IoT PoE | ●U | | ●U | 30 | ✓ |
| 8 | IoT PoE | ●U | | ●U | 30 | |

**Legend:** ●T = Tagged, ●U = Untagged, (empty) = Not Member

!!! note "PoE Ports"
    Switch B (TL-SG108PE) has PoE+ on ports 4-7. Use these for PoE-powered IoT devices like cameras, sensors, or access points. Port 8 is non-PoE IoT.

---

## Switch C Configuration (TL-SG108E)

Switch C carries **mesh backbone (VLAN 100)** for wired mesh redundancy and receives **VLAN 10 (management)** via direct link from Switch A.

!!! info "Switch C Management via Switch A Link"
    Switch C receives VLAN 10 via a **direct cable from Switch A** (P6 → P4).
    TL-SG108E switches only respond to management on **untagged** traffic.

    - Mesh nodes have only `lan4.100` - no other VLANs on LAN4
    - VLAN 10 travels: Workstation → Switch A (P5) → Switch A (P6) → Switch C (P4)
    - No L2 loops because this path doesn't go through the mesh

    **Never add VLAN 30 or 200 to Switch C** - these would create broadcast storms.

### Step 1: Factory Reset (if needed)

1. Locate the **Reset** button (small hole on the side)
2. With switch powered on, press and hold for **5+ seconds**
3. Release when all port LEDs blink
4. Wait 30 seconds for restart

### Step 2: Initial Access (Direct Connection Required)

!!! note "Why Direct Connection?"
    Switch C connects to node LAN4 ports, which only carry VLAN 100 (tagged).
    You must connect directly to a spare port (P4-P8) for configuration.

1. Connect your computer directly to Switch C **Port 4, 5, 6, 7, or 8**
2. Configure IP: `192.168.0.2/24`

   ```bash
   make switch-to-switch-network
   ```

3. Browse to `http://192.168.0.1`
4. Login: `admin` / `admin`

### Step 3: Enable 802.1Q VLAN First

1. Go to **VLAN → 802.1Q VLAN**
2. Set 802.1Q VLAN to **Enable**
3. Click **Apply**

### Step 4: Configure VLAN 100 (Mesh)

1. VLAN ID: `100`
2. VLAN Name: `Mesh`
3. Port configuration:

| Port | Untagged | Tagged | Not Member | Purpose |
|------|:--------:|:------:|:----------:|---------|
| 1 | | ● | | Node 1 LAN4 |
| 2 | | ● | | Node 2 LAN4 |
| 3 | | ● | | Node 3 LAN4 |
| 4 | | | ● | Switch A link |
| 5 | | | ● | spare |
| 6 | | | ● | spare |
| 7 | | | ● | spare |
| 8 | | | ● | spare |

4. Click **Add/Modify**

### Step 5: Configure VLAN 10 (AlinkC - Switch A Link)

1. VLAN ID: `10`
2. VLAN Name: `AlinkC`
3. Port configuration:

| Port | Untagged | Tagged | Not Member | Purpose |
|------|:--------:|:------:|:----------:|---------|
| 1 | | | ● | Node 1 LAN4 |
| 2 | | | ● | Node 2 LAN4 |
| 3 | | | ● | Node 3 LAN4 |
| 4 | ● | | | **Switch A link** |
| 5 | | | ● | spare |
| 6 | | | ● | spare |
| 7 | | | ● | spare |
| 8 | | | ● | spare |

4. Click **Add/Modify**

### Step 6: Verify VLAN 1 (Default)

VLAN 1 should already have all ports as untagged members by default. Verify:

| Port | Untagged | Tagged | Not Member | Purpose |
|------|:--------:|:------:|:----------:|---------|
| 1 | ● | | | Node 1 LAN4 |
| 2 | ● | | | Node 2 LAN4 |
| 3 | ● | | | Node 3 LAN4 |
| 4 | ● | | | Switch A link |
| 5 | ● | | | spare |
| 6 | ● | | | spare |
| 7 | ● | | | spare |
| 8 | ● | | | spare |

### Step 7: Set Management IP

1. Go to **System → IP Setting**
2. Configure:
   - DHCP Setting: `Disable`
   - IP Address: `10.11.10.13`
   - Subnet Mask: `255.255.255.0`
   - Default Gateway: `10.11.10.1`
3. Click **Apply**
4. You will lose connection via direct access
5. Connect the Switch A → Switch C cable (P6 → P4)
6. Verify from management network:

   ```bash
   ping 10.11.10.13
   ```

### Step 8: Verify PVID Settings

All ports should have PVID 1 (default). No changes needed.

### Switch C VLAN Summary (After Configuration)

| Port | Purpose | VLAN 1 | VLAN 10 | VLAN 100 | PVID |
|------|---------|:------:|:-------:|:--------:|:----:|
| 1 | Node 1 LAN4 | ●U | | ●T | 1 |
| 2 | Node 2 LAN4 | ●U | | ●T | 1 |
| 3 | Node 3 LAN4 | ●U | | ●T | 1 |
| 4 | **Switch A link** | ●U | **●U** | | 1 |
| 5 | spare | ●U | | | 1 |
| 6 | spare | ●U | | | 1 |
| 7 | spare | ●U | | | 1 |
| 8 | spare | ●U | | | 1 |

**Legend:** ●T = Tagged, ●U = Untagged, (empty) = Not Member

### Switch C Verification Checklist

**From the management workstation (connected to Switch A Port 5):**

```bash
# Ping Switch C
ping -c 2 10.11.10.13
# Expected: 2 packets received

# Access web interface
firefox http://10.11.10.13
```

**From any mesh node:**

```bash
ssh root@10.11.12.1

# 1. Check LAN4 physical link
echo "LAN4 carrier: $(cat /sys/class/net/lan4/carrier)"
# Expected: 1

# 2. Verify mesh backbone via Switch C
batctl o | grep lan4.100 | head -3
# Expected: Shows originators (mesh working via Switch C)
```

**Expected Results Summary:**

| Check | From | Expected |
|-------|------|----------|
| Physical link | Mesh node | `cat /sys/class/net/lan4/carrier` = `1` |
| Mesh traffic | Mesh node | `batctl o \| grep lan4.100` shows entries |
| Management ping | Mgmt workstation | `ping 10.11.10.13` success |
| Web access | Mgmt workstation | http://10.11.10.13 loads |

!!! success "All Checks Pass?"
    If all checks pass, Switch C is correctly configured with:

    - VLAN 100 carrying mesh backbone traffic (ports 1-3, tagged)
    - VLAN 1 for management via Switch A link (port 4, untagged)
    - IP address 10.11.10.13 reachable from management workstation

---

## Management Workstation Connection

Connect your management workstation to **Port 5** on Switch A. This is a **trunk port** with all VLANs tagged, giving you access to all networks.

### Network Access Summary

| Network | VLAN | Subnet | Workstation IP | Gateway |
|---------|------|--------|----------------|---------|
| Management | 10 | 10.11.10.0/24 | 10.11.10.100 | 10.11.10.1 |
| IoT | 30 | 10.11.30.0/24 | 10.11.30.100 | 10.11.30.1 |
| Mesh Backbone | 100 | L2 only | - | - |
| Client/LAN | 200 | 10.11.12.0/24 | 10.11.12.100 | 10.11.12.1 |

### Setup VLAN Interfaces

Configure your workstation's enp5s0 interface with VLAN sub-interfaces.

#### Option 1: Temporary (until reboot)

```bash
# Setup all VLAN interfaces on enp5s0 (Switch A Port 5)
make setup-mgmt-vlans

# Or manually:
sudo ip link add link enp5s0 name enp5s0.10 type vlan id 10
sudo ip link add link enp5s0 name enp5s0.30 type vlan id 30
sudo ip link add link enp5s0 name enp5s0.200 type vlan id 200

sudo ip addr add 10.11.10.100/24 dev enp5s0.10
sudo ip addr add 10.11.30.100/24 dev enp5s0.30
sudo ip addr add 10.11.12.100/24 dev enp5s0.200

sudo ip link set enp5s0.10 up
sudo ip link set enp5s0.30 up
sudo ip link set enp5s0.200 up
```

#### Option 2: Persistent (survives reboot)

Add to `/etc/network/interfaces`:

```
# Management workstation VLAN interfaces on enp5s0
# Requires: enp5s0 connected to Switch A Port 5 (trunk port)

auto enp5s0
iface enp5s0 inet manual

# VLAN 10 - Management Network
auto enp5s0.10
iface enp5s0.10 inet static
    address 10.11.10.100
    netmask 255.255.255.0
    vlan-raw-device enp5s0

# VLAN 30 - IoT Network
auto enp5s0.30
iface enp5s0.30 inet static
    address 10.11.30.100
    netmask 255.255.255.0
    vlan-raw-device enp5s0

# VLAN 200 - Client/LAN Network
auto enp5s0.200
iface enp5s0.200 inet static
    address 10.11.12.100
    netmask 255.255.255.0
    vlan-raw-device enp5s0
```

Then apply with:

```bash
sudo ifup enp5s0.10 enp5s0.30 enp5s0.200
```

### Verify Access to All Networks

```bash
# Management network
ping 10.11.10.1   # Node 1
ping 10.11.10.11  # Switch A
ping 10.11.10.12  # Switch B
ping 10.11.10.13  # Switch C

# Client/LAN network
ping 10.11.12.1   # Node 1
ping 10.11.12.2   # Node 2
ping 10.11.12.3   # Node 3

# IoT network (nodes only - IoT zone blocks ICMP from devices)
ping 10.11.30.1   # Node 1
ping 10.11.30.2   # Node 2
ping 10.11.30.3   # Node 3
```

### Remove VLAN Interfaces

```bash
# Teardown VLAN interfaces
make teardown-mgmt-vlans

# Or manually:
sudo ip link del enp5s0.10
sudo ip link del enp5s0.30
sudo ip link del enp5s0.200
```

---

## Traffic Flow

| Traffic Type | Path |
|--------------|------|
| **Mesh Backbone** | Nodes ↔ Switch A (LAN3) + Switch B (LAN4) + Wireless |
| **Management** | Workstation → Switch A P5 → Nodes (via LAN3) |
| **Clients** | Devices → Switch A P6-8 → Nodes (via LAN3) → Internet |
| **IoT** | Devices → Switch C P6-8 → Switch A P4 → Nodes |
| **Infrastructure** | Proxmox/RPi → Switch C P3-5 → Switch A P4 → Nodes |

---

## Redundancy

### What's Protected

| Component | Redundancy | Mechanism |
|-----------|------------|-----------|
| Mesh backbone | ✓ Dual wired + wireless | Switch A (lan3.100) + Switch C (lan4.100) + phy0-mesh0 |
| WAN connectivity | ✓ Multi-WAN | All nodes have WAN, batman-adv gateway selection |
| Node failure | ✓ Full | Batman-adv routes around failed node, BLA handles switch paths |
| Client/Mgmt/IoT | ✓ Via mesh | If Switch A path fails, traffic flows via mesh to other nodes |

### What's NOT Protected

| Component | Impact if Failed |
|-----------|------------------|
| Switch A | Direct switch access lost, but clients can still reach mesh via WiFi or node LAN1 ports |
| Switch C | Mesh loses one wired path, but still has Switch A + wireless backup |

!!! tip "High Availability Design"
    This design provides HA through batman-adv mesh redundancy:

    - **Switch A failure**: Clients lose direct wired access via switch, but:
      - WiFi clients (phy1-ap0) still work via mesh
      - Devices on node LAN1 ports still work via mesh
      - Traffic routes through mesh to reach other nodes

    - **Any node failure**: Batman-adv automatically routes around failed node

    - **Switch C failure**: Mesh loses one wired backbone path, but:
      - Switch A wired path (lan3.100) still works
      - Wireless mesh (phy0-mesh0) provides backup

!!! tip "Future Upgrade"
    For full redundancy on switch paths, replace switches with STP-capable models (e.g., TL-SG2008).
    Then both switches can carry all VLANs with STP preventing loops instead of relying on BLA.

---

## Verification

### Test Management Access

```bash
# From management workstation (Switch A P5)
ping 10.11.10.1   # Node 1
ping 10.11.10.2   # Node 2
ping 10.11.10.3   # Node 3
ping 10.11.10.11  # Switch A
ping 10.11.10.12  # Switch B
ping 10.11.10.13  # Switch C
```

### Test Mesh Backbone

```bash
# SSH to any node
ssh root@10.11.10.1

# Check batman interfaces
batctl if
# Should show: lan3.100, lan4.100, phy0-mesh0

# Check mesh neighbors
batctl n

# Check originators
batctl o
```

### Test Client Connectivity

1. Connect device to Switch A P6-8
2. Should receive DHCP IP from 10.11.12.x
3. Test: `ping 10.11.12.1` and `ping 8.8.8.8`

---

## Troubleshooting

### Cannot Access Switch

```bash
# For factory default (192.168.0.1):
make switch-to-switch-network

# For configured switch (10.11.10.x):
make switch-to-mgmt-network
```

### Switch C Management Unreachable

**Symptoms:**

- `ping 10.11.10.13` fails from management workstation
- Mesh backbone still works (nodes see each other via lan4.100)

**Diagnosis:**

```bash
# From mesh node - check mesh backbone
ssh root@10.11.12.1
batctl o | grep lan4.100
# Should show originators - means VLAN 100 is working

# From workstation - check Switch A is reachable
ping 10.11.10.11
# If fails, check workstation connection to Switch A Port 5
```

**Common Causes:**

| Symptom | Mesh via lan4.100 | Ping 10.11.10.13 | Cause |
|---------|:-----------------:|:----------------:|-------|
| Switch off | No entries | Fail | Power/cable issue |
| Cable missing | Has entries | Fail | Switch A ↔ Switch C cable not connected |
| VLAN 1 wrong | Has entries | Fail | VLAN 1 not untagged on Switch A P6 or Switch C P4 |
| Working | Has entries ✓ | Success ✓ | Correct config |

**Fix Checklist:**

1. **Verify cable**: Switch A Port 6 → Switch C Port 4
2. **Check Switch A**: Port 6 in VLAN 1 (untagged), PVID 1
3. **Check Switch C**: Port 4 in VLAN 1 (untagged), PVID 1
4. **Check workstation**: Connected to Switch A Port 5, using untagged traffic

### No Mesh Connectivity

```bash
# Check VLAN interfaces exist
ssh root@10.11.12.1 'ip link show | grep "lan[34]\."'

# Check batman interfaces
ssh root@10.11.12.1 'batctl if'

# Should show:
# lan3.100: active
# lan4.100: active
# phy0-mesh0: active
```

### Broadcast Storm / High Latency

If you experience broadcast storms, verify:

1. **Switch C** only has VLAN 100 tagged on ports 1-3 - NO VLAN 30 or 200
2. **Node LAN4** only has `lan4.100` - verify no `lan4.10`, `lan4.30`, or `lan4.200` exists
3. **BLA is enabled**: `batctl bla` should show `enabled`
4. **All node IPs are static**: Check `uci show network | grep proto` - must NOT have `dhcp` for br-mgmt, br-lan, br-iot

```bash
# Check for loops - BLA backbone table should show entries after traffic flows
ssh root@10.11.12.1 'batctl bbt'

# Check BLA claims
ssh root@10.11.12.1 'batctl cl'

# Verify no DHCP on management interfaces
ssh root@10.11.12.1 'uci show network.mgmt.proto'
# Should output: network.mgmt.proto='static'
```

---

## Workstation Network Commands

```bash
# Access factory-default switch (192.168.0.1)
make switch-to-switch-network

# Access configured switches (10.11.10.x)
make switch-to-mgmt-network

# Access mesh network (10.11.12.x)
make switch-to-mesh-network

# Access fresh OpenWrt nodes (192.168.1.x)
make switch-to-initial-network
```
