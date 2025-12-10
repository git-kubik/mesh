# Architecture

This section explains the design decisions and technical architecture of the OpenWrt mesh network.

## Overview

The mesh network is built on three core technologies:

| Technology | Purpose | Why We Chose It |
|------------|---------|-----------------|
| **Batman-adv** | Layer 2 mesh routing | Protocol-agnostic, multi-interface, proven at scale |
| **OpenWrt** | Router operating system | Open source, extensive package support, active community |
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
                    └─────────────┬───────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
   ┌─────────┐              ┌─────────┐              ┌─────────┐
   │  WAN 1  │              │  WAN 2  │              │  WAN 3  │
   │         │              │         │              │         │
   │ Node 1  │◄────────────►│ Node 2  │◄────────────►│ Node 3  │
   │10.11.12.1│   Wired     │10.11.12.2│   Wired     │10.11.12.3│
   │         │   Mesh       │         │   Mesh       │         │
   └────┬────┘              └────┬────┘              └────┬────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │     Batman-adv          │
                    │     Mesh Domain         │
                    │     (Layer 2)           │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
   ┌────▼────┐             ┌─────▼────┐            ┌─────▼────┐
   │  5GHz   │             │  5GHz    │            │  5GHz    │
   │   AP    │             │   AP     │            │   AP     │
   │(roaming)│             │(roaming) │            │(roaming) │
   └─────────┘             └──────────┘            └──────────┘
```

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

## Related Documentation

- [Philosophy](../philosophy.md) - Why we made these design choices
- [Deployment](../deployment/index.md) - How to deploy this architecture
- [Troubleshooting](../troubleshooting/index.md) - When things don't work
