# Network Topology

This document describes the physical and logical network topology of the mesh network.

## Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    3-Node Mesh Network Topology                          │
│                                                                          │
│                         ┌─────────────┐                                  │
│                         │   Internet  │                                  │
│                         └──────┬──────┘                                  │
│                    ┌───────────┼───────────┐                             │
│                    │           │           │                             │
│              ┌─────┴─────┐ ┌───┴───┐ ┌─────┴─────┐                       │
│              │   WAN 1   │ │ WAN 2 │ │   WAN 3   │                       │
│              └─────┬─────┘ └───┬───┘ └─────┬─────┘                       │
│                    │           │           │                             │
│              ┌─────┴─────┐ ┌───┴───┐ ┌─────┴─────┐                       │
│              │   Node1   │ │ Node2 │ │   Node3   │                       │
│              │10.11.12.1 │ │  .2   │ │    .3     │                       │
│              └─────┬─────┘ └───┬───┘ └─────┬─────┘                       │
│                    │           │           │                             │
│              LAN3 ═╪═══════════╪═══════════╪═ LAN3  (Switch A)           │
│              LAN4 ═╪═══════════╪═══════════╪═ LAN4  (Switch B)           │
│                    │           │           │                             │
│                  mesh0 ·····mesh0·····mesh0  (Wireless 2.4GHz)          │
│                                                                          │
│              ═══ Wired Ring (Primary)                                   │
│              ··· Wireless Backup                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

## Physical Topology

### Hardware

| Component | Model | Quantity |
|-----------|-------|----------|
| Router | D-Link DIR-1960 A1 | 3 |
| Managed Switch | TP-Link TL-SG105PE | 2 |
| Ethernet Cable | Cat6 | ~10 |

### Port Allocation Per Node

Each DIR-1960 has 1 WAN port + 4 LAN ports:

| Port | Function | Connected To |
|------|----------|--------------|
| WAN | Internet | ISP modem/router |
| LAN1 | Client devices | Workstations, servers |
| LAN2 | Client devices | Additional devices |
| LAN3 | Mesh backbone | Switch A (VLAN 100) |
| LAN4 | Mesh backbone | Switch B (VLAN 100) |

### Wiring Diagram

```
                     [ISP Modem A]        [ISP Modem B]        [ISP Modem C]
                          │                     │                     │
                          │                     │                     │
                     ┌────┴────┐           ┌────┴────┐           ┌────┴────┐
                     │  Node1  │           │  Node2  │           │  Node3  │
                     │  WAN    │           │  WAN    │           │  WAN    │
                     │ LAN1-2  │           │ LAN1-2  │           │ LAN1-2  │
                     │ LAN3───┼───────────┼──LAN3   │───────────┼──LAN3   │
                     │ LAN4───┼───────────┼──LAN4   │───────────┼──LAN4   │
                     └─────────┘           └─────────┘           └─────────┘
                          │                     │                     │
                          └─────────────────────┼─────────────────────┘
                                                │
                                          [Switch A]
                                          (VLAN 100)
```

### Ring Topology Detail

The wired backbone forms a **full ring**:

```
             Node1                    Node2                    Node3
               │                        │                        │
         ┌─────┴─────┐            ┌─────┴─────┐            ┌─────┴─────┐
         │LAN3  LAN4 │            │LAN3  LAN4 │            │LAN3  LAN4 │
         └──┬────┬───┘            └──┬────┬───┘            └──┬────┬───┘
            │    │                   │    │                   │    │
            │    └───────────────────┼────┼───────────────────┼────┘
            │                        │    │                   │
            └────────────────────────┘    └───────────────────┘

LAN3 connections: Node1 ↔ Node2 ↔ Node3 ↔ Node1 (via Switch A)
LAN4 connections: Node1 ↔ Node2 ↔ Node3 ↔ Node1 (via Switch B)
```

## Logical Topology

### VLAN Structure

| VLAN ID | Name | Subnet | Purpose |
|---------|------|--------|---------|
| 100 | Mesh Backbone | N/A (Layer 2) | Batman-adv mesh traffic |
| - | LAN | 10.11.12.0/24 | Main client network |
| 10 | Management | 10.11.10.0/24 | Switch/device management |
| 20 | Guest | 10.11.20.0/24 | Isolated guest WiFi |
| 30 | IoT | 10.11.30.0/24 | IoT devices (isolated) |

### IP Addressing

#### Main LAN (10.11.12.0/24)

```
10.11.12.1       Node1 (Gateway + DHCP + DNS)
10.11.12.2       Node2 (Gateway + DHCP + DNS)
10.11.12.3       Node3 (Gateway + DHCP + DNS)
10.11.12.10-99   Reserved for static IPs
10.11.12.100-149 DHCP pool (Node1)
10.11.12.150-199 DHCP pool (Node2)
10.11.12.200-249 DHCP pool (Node3)
```

#### Management VLAN 10 (10.11.10.0/24)

```
10.11.10.1       Node1 (VLAN interface)
10.11.10.2       Node2 (VLAN interface)
10.11.10.3       Node3 (VLAN interface)
10.11.10.10      Switch A
10.11.10.11      Switch B
10.11.10.100-149 DHCP pool
```

#### Guest VLAN 20 (10.11.20.0/24)

```
10.11.20.1       Node1 (VLAN interface)
10.11.20.2       Node2 (VLAN interface)
10.11.20.3       Node3 (VLAN interface)
10.11.20.100-149 DHCP pool
```

#### IoT VLAN 30 (10.11.30.0/24)

```
10.11.30.1       Node1 (VLAN interface)
10.11.30.2       Node2 (VLAN interface)
10.11.30.3       Node3 (VLAN interface)
10.11.30.100-149 DHCP pool
```

## Wireless Architecture

### Radio Allocation

Each node has two radios:

| Radio | Band | Channel | Function |
|-------|------|---------|----------|
| radio0 | 2.4 GHz | 1/6/11 | Mesh backbone (802.11s) |
| radio1 | 5 GHz | 36-48 | Client AP |

### 2.4 GHz (Mesh Backbone)

```
┌─────────────────────────────────────────────────────────────────┐
│                    2.4GHz Radio (radio0)                         │
├─────────────────────────────────────────────────────────────────┤
│  mesh0:  Batman-adv mesh backup (802.11s)                       │
│          SSID: HA-Mesh (hidden)                                 │
│          Encryption: WPA3-SAE (mesh security)                   │
│          Connected to: bat0                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 5 GHz (Client Access)

```
┌─────────────────────────────────────────────────────────────────┐
│                    5GHz Radio (radio1)                           │
├─────────────────────────────────────────────────────────────────┤
│  wlan1:  Client AP                                              │
│          SSID: HA-Client                                        │
│          Encryption: WPA2/WPA3                                  │
│          802.11r: Enabled (fast roaming)                        │
│          Connected to: br-lan                                   │
├─────────────────────────────────────────────────────────────────┤
│  guest0: Guest AP (optional)                                    │
│          SSID: HA-Guest                                         │
│          VLAN: 20 (isolated)                                    │
│          Client isolation: Enabled                              │
└─────────────────────────────────────────────────────────────────┘
```

## Traffic Flow

### Client to Internet

```
Client Device
     │
     ├─(Wired)─→ LAN1/LAN2 ─┐
     │                       │
     └─(WiFi)──→ wlan1 ─────┘
                             │
                         br-lan
                             │
                          bat0
                             │
               ┌─────────────┼─────────────┐
               │             │             │
           Gateway       Gateway       Gateway
           Node1         Node2         Node3
               │             │             │
               └─────────────┼─────────────┘
                             │
                          WAN
                             │
                        Internet
```

### Node-to-Node (Mesh)

```
Client on Node1 → Client on Node3

Path 1 (Primary - Wired):
  Node1 ─[lan3.100]─ Switch A ─[lan3.100]─ Node3

Path 2 (Alternate - Wired):
  Node1 ─[lan4.100]─ Switch B ─[lan4.100]─ Node3

Path 3 (Backup - Wireless):
  Node1 ─[mesh0]─ (802.11s wireless) ─[mesh0]─ Node3
```

### Gateway Selection

```
┌──────────────────────────────────────────────────────────────────┐
│                    Gateway Selection                              │
│                                                                   │
│  Client: "I need internet"                                       │
│     │                                                            │
│     └──→ bat0: Query gateway list                                │
│               │                                                  │
│          ┌────┴────────────────────────────┐                     │
│          │                                 │                     │
│     Node1 GW              Node2 GW              Node3 GW         │
│     BW: 100Mbps           BW: 100Mbps           BW: 100Mbps      │
│     TQ: 255 (local)       TQ: 240 (1 hop)       TQ: 220 (1 hop)  │
│     Score: 25500 ✓        Score: 24000          Score: 22000     │
│                                                                   │
│  Result: Route via Node1 (highest score)                         │
└──────────────────────────────────────────────────────────────────┘
```

## Failover Scenarios

### Scenario 1: Single Link Failure

```
Initial: Node1 ─[lan3]─ Node2 ─[lan3]─ Node3
                        ↑
                   Cable fails

After:  Node1 ─[lan4]────────────────── Node3 ─[lan4]─ Node2
        (Traffic routes through alternate path)
```

### Scenario 2: Node WAN Failure

```
Initial:
  Client ─→ Node2 ─[WAN]─→ Internet

Node2 WAN fails:
  Client ─→ Node2 ─[bat0]─→ Node1 ─[WAN]─→ Internet
  (Automatic gateway failover)
```

### Scenario 3: Complete Node Failure

```
Initial:
  Node1 ──── Node2 ──── Node3

Node2 power off:
  Node1 ─[mesh0 wireless]─ Node3
  (Wireless backup activates)
```

### Scenario 4: Wired Infrastructure Failure

```
Initial:
  All traffic via lan3.100 and lan4.100

Both switches fail:
  Node1 ─[mesh0]─ Node2 ─[mesh0]─ Node3
  (Full mesh via wireless backup)
```

## Switch Configuration

### Switch A (TP-Link TL-SG105PE)

| Port | VLAN 100 | VLAN 10 | Description |
|------|----------|---------|-------------|
| 1 | Tagged | Tagged | Node1 LAN3 |
| 2 | Tagged | Tagged | Node2 LAN3 |
| 3 | Tagged | Tagged | Node3 LAN3 |
| 4 | - | Untagged | Management access |
| 5 | - | - | Spare |

### Switch B (TP-Link TL-SG105PE)

| Port | VLAN 100 | VLAN 10 | Description |
|------|----------|---------|-------------|
| 1 | Tagged | Tagged | Node1 LAN4 |
| 2 | Tagged | Tagged | Node2 LAN4 |
| 3 | Tagged | Tagged | Node3 LAN4 |
| 4 | - | Untagged | Management access |
| 5 | - | - | Spare |

## Firewall Zones

```
┌────────────────────────────────────────────────────────────────┐
│                    Firewall Zone Map                            │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │   LAN   │    │   WAN   │    │  GUEST  │    │  MGMT   │      │
│  │ br-lan  │    │  wan    │    │ VLAN 30 │    │ VLAN 10 │      │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘      │
│       │              │              │              │            │
│  INPUT:ACCEPT   INPUT:REJECT   INPUT:REJECT   INPUT:ACCEPT     │
│  OUTPUT:ACCEPT  OUTPUT:ACCEPT  OUTPUT:ACCEPT  OUTPUT:ACCEPT    │
│  FORWARD:ACCEPT FORWARD:REJECT FORWARD:REJECT FORWARD:REJECT   │
│       │              │              │              │            │
│       ├──────→───────┤              │              │            │
│       │    NAT/MASQ  │              │              │            │
│       │              │              ├──────→───────┤            │
│       │              │              │    BLOCKED   │            │
│       │              │              ├──────→───────┤            │
│       │              │              │   INTERNET   │            │
│       ├──────←───────┤              │              │            │
│       │   RELATED    │              │              │            │
│       │  ESTABLISHED │              │              │            │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Diagram: Complete Network

```
                              ┌─────────────────────────────────────────────────────────────────┐
                              │                         INTERNET                                 │
                              └─────────────────────────────────────────────────────────────────┘
                                               │           │           │
                                          ┌────┴────┐ ┌────┴────┐ ┌────┴────┐
                                          │ISP Modem│ │ISP Modem│ │ISP Modem│
                                          └────┬────┘ └────┬────┘ └────┬────┘
                                               │           │           │
┌──────────────────────────────────────────────┼───────────┼───────────┼──────────────────────────┐
│                                              │           │           │                          │
│  ╔═══════════════════╗     ╔═══════════════════════════════════════════════╗     ╔════════════ │
│  ║     NODE 1        ║     ║              NODE 2              ║             ║     ║   NODE 3   ║│
│  ║   10.11.12.1      ║     ║           10.11.12.2             ║             ║     ║ 10.11.12.3 ║│
│  ╠═══════════════════╣     ╠═══════════════════════════════════╣             ╠═════════════════╣│
│  ║ WAN: ISP          ║     ║ WAN: ISP                          ║             ║ WAN: ISP       ║│
│  ║ LAN1: Clients     ║     ║ LAN1: Clients                     ║             ║ LAN1: Clients  ║│
│  ║ LAN2: Clients     ║     ║ LAN2: Clients                     ║             ║ LAN2: Clients  ║│
│  ║ LAN3: ═══════════════════════════════════════════════════════════════════════════ :LAN3    ║│
│  ║ LAN4: ═══════════════════════════════════════════════════════════════════════════ :LAN4    ║│
│  ║ 5GHz: Clients     ║     ║ 5GHz: Clients                     ║             ║ 5GHz: Clients  ║│
│  ║ 2.4G: ············║·····║·············································║·····║··········    ║│
│  ╚═══════════════════╝     ╚═══════════════════════════════════╝             ╚═════════════════╝│
│                                                                                                 │
│        ═══ Wired Mesh Backbone (VLAN 100)                                                      │
│        ··· Wireless Mesh Backup (802.11s)                                                      │
│                                                                                                 │
│  ┌────────────────┐                    ┌────────────────┐                                       │
│  │   SWITCH A     │                    │   SWITCH B     │                                       │
│  │  10.11.10.10   │                    │  10.11.10.11   │                                       │
│  │   (VLAN 100)   │                    │   (VLAN 100)   │                                       │
│  └────────────────┘                    └────────────────┘                                       │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Capacity Planning

### Current Capacity

| Resource | Capacity |
|----------|----------|
| Wired client ports | 6 (2 per node) |
| Wireless clients | ~75 (25 per AP) |
| Mesh bandwidth | 1 Gbps (wired) |
| Backup bandwidth | ~300 Mbps (wireless) |
| DHCP addresses | 150 |

### Expansion Options

1. **More client ports**: Add unmanaged switch to LAN1/LAN2
2. **More nodes**: Add Node4 to ring topology
3. **More WiFi capacity**: Add dedicated APs to mesh
4. **More bandwidth**: Upgrade to 2.5G/10G switches
