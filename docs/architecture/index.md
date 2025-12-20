# Architecture

This section explains the design decisions and technical architecture of the OpenWrt mesh network.

## Overview

The mesh network is built on these core technologies:

| Technology | Purpose | Why We Chose It |
|------------|---------|-----------------|
| **Batman-adv V** | Layer 2 mesh routing | Protocol-agnostic, BLA for loop prevention, multi-interface |
| **OpenWrt 24.10** | Router operating system | Open source, extensive package support, active community |
| **TP-Link TL-SG108E** | Managed switches | VLAN trunking, 802.1Q support, affordable |
| **Ansible** | Configuration management | Agentless, idempotent, human-readable |

## Section Contents

| Document | Description |
|----------|-------------|
| [Architecture Overview](overview.md) | Complete technical deep-dive into the mesh design |
| [Batman-adv Protocol](batman-mesh.md) | How the mesh routing protocol works |
| [Network Topology](network-topology.md) | Physical and logical network structure |
| [VLAN Architecture](vlan-architecture.md) | Network segmentation design |
| [Switch Integration](switch-integration.md) | Managed switch configuration |

## High-Level Architecture

```
                    ┌─────────────────────────────────────┐
                    │           INTERNET                  │
                    └───────┬───────────┬───────────┬─────┘
                            │           │           │
                       ┌────┴────┐ ┌────┴────┐ ┌────┴────┐
                       │  WAN 1  │ │  WAN 2  │ │  WAN 3  │
                       │ Node 1  │ │ Node 2  │ │ Node 3  │
                       │10.11.12.1│10.11.12.2│10.11.12.3│
                       └────┬────┘ └────┬────┘ └────┬────┘
                       LAN3 │ LAN4 LAN3 │ LAN4 LAN3 │ LAN4
                            │           │           │
                       ┌────┴───────────┴───────────┴────┐
                       │     Switch A (All VLANs)        │
                       │  + Switch C (Mesh VLAN only)    │
                       │  + 2.4GHz Wireless Backup       │
                       └─────────────────────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        │                               │                               │
   ┌────▼────┐                    ┌─────▼────┐                   ┌──────▼────┐
   │  5GHz   │                    │  5GHz    │                   │  5GHz     │
   │ HA-Client│                   │ HA-Client│                   │ HA-Client │
   │(802.11r)│                    │(802.11r) │                   │(802.11r)  │
   └─────────┘                    └──────────┘                   └───────────┘
```

**VLAN Segmentation:**

| VLAN | Network | Subnet | Purpose |
|------|---------|--------|---------|
| 200 | Client | 10.11.12.0/24 | Main LAN, trusted devices |
| 10 | Management | 10.11.10.0/24 | Admin access, switches |
| 20 | Guest | 10.11.20.0/24 | Isolated guest WiFi |
| 30 | IoT | 10.11.30.0/24 | Smart home devices |
| 100 | Mesh | - | Batman-adv backbone |

## Key Design Decisions

### Why Ring Topology?

- **Redundancy**: Any single link failure doesn't partition the network
- **Low Latency**: Maximum 2 hops between any two nodes
- **Simple Wiring**: Only 3 cables needed for full mesh

### Why Multi-Gateway?

- **No Single Point of Failure**: Each node has its own WAN connection
- **Load Distribution**: Clients automatically select best gateway
- **Bandwidth Aggregation**: Total bandwidth = sum of all WANs

### Why VLAN Segmentation?

- **Security**: IoT devices isolated from main network
- **Management**: Dedicated management network for switches and nodes
- **Flexibility**: Easy to add new network segments

### Why Bridge Loop Avoidance (BLA)?

- **Loop Prevention**: Switches + mesh create L2 loop potential
- **High Availability**: All nodes bridge switch VLANs (no SPOF)
- **Critical Requirement**: Node interfaces MUST use static IPs (BLA doesn't protect node-originated DHCP)

## Related Documentation

- [Quick Start](../getting-started/quickstart.md) - Deploy your first node
- [Makefile Reference](../reference/makefile.md) - Available automation commands
- [Troubleshooting](../troubleshooting/index.md) - When things don't work
