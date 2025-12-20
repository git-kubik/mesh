# OpenWrt Mesh Network Documentation

Welcome to the documentation for the OpenWrt Multi-Gateway Batman-adv Mesh Network project.

## Overview

This project provides infrastructure-as-code for deploying a high-availability 3-node mesh network using OpenWrt routers with Batman-adv Layer 2 routing.

**Key Features:**

- **Full Ring Topology**: Wired mesh via managed switches + 2.4GHz 802.11s wireless backup
- **VLAN Segmentation**: Management (10), Guest (20), IoT (30), Mesh (100), Client (200)
- **Multi-Gateway**: 3 independent WAN connections with Batman-adv failover
- **Bridge Loop Avoidance**: BLA prevents L2 loops across mesh + switch topology
- **Switch Integration**: TP-Link TL-SG108E VLAN trunking for wired backbone
- **802.11r Fast Roaming**: Seamless WiFi handoff on 5GHz client network
- **Ansible Automation**: Complete deployment via Makefile commands

## Quick Navigation

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started/index.md) | Deploy your first mesh node |
| [Architecture](architecture/index.md) | Understand the network design |
| [Deployment](deployment/index.md) | Configuration and deployment options |
| [Operations](operations/index.md) | Day-to-day management |
| [Development](development/index.md) | Contributing and testing |
| [Troubleshooting](troubleshooting/index.md) | Problem resolution |
| [Reference](reference/index.md) | Command and API reference |
| [Advanced](advanced/index.md) | Power user features |

## Architecture at a Glance

```
                 ┌─────────────────────────────────────┐
                 │           INTERNET                  │
                 └───────┬───────────┬───────────┬─────┘
                         │           │           │
                    ┌────┴────┐ ┌────┴────┐ ┌────┴────┐
                    │  WAN 1  │ │  WAN 2  │ │  WAN 3  │
                    │  Node1  │ │  Node2  │ │  Node3  │
                    │10.11.12.1│10.11.12.2│10.11.12.3│
                    └────┬────┘ └────┬────┘ └────┬────┘
                    LAN3 │ LAN4 LAN3 │ LAN4 LAN3 │ LAN4
                         │           │           │
                    ┌────┴───────────┴───────────┴────┐
                    │    Switch A (All VLANs: 10,20,  │
                    │        30,100,200) + Switch C   │
                    │        (Mesh VLAN 100 only)     │
                    └─────────────────────────────────┘
                    + 2.4GHz wireless mesh backup (VLAN 100)
                    + 5GHz unified client AP (802.11r roaming)
```

**Network Segments:**

| Network | VLAN | Subnet | Purpose |
|---------|------|--------|---------|
| Client | 200 | 10.11.12.0/24 | Main LAN, trusted devices |
| Management | 10 | 10.11.10.0/24 | Admin access, Proxmox |
| Guest | 20 | 10.11.20.0/24 | Isolated guest WiFi |
| IoT | 30 | 10.11.30.0/24 | Smart home devices |
| Mesh | 100 | - | Batman-adv backbone |

## Getting Started

1. **[Quick Start](getting-started/quickstart.md)** - Deploy your first node in minutes
2. **[Architecture Overview](architecture/overview.md)** - Understand the network design
3. **[VLAN Architecture](architecture/vlan-architecture.md)** - Network segmentation details
4. **[Switch Integration](architecture/switch-integration.md)** - Managed switch configuration

## Common Tasks

| Task | Command |
|------|---------|
| Deploy node | `make deploy-node NODE=1` |
| Check status | `make verify` |
| View mesh | `make batman-status` |
| Create backup | `make snapshot-all` |

## Project Links

- **Repository**: [GitHub](https://github.com/git-kubik/mesh)
- **Issues**: [Bug Reports](https://github.com/git-kubik/mesh/issues)
- **CI/CD**: [GitHub Actions](https://github.com/git-kubik/mesh/actions)

## Technology Stack

| Technology | Purpose |
|------------|---------|
| OpenWrt 24.10.4 | Router operating system |
| Batman-adv BATMAN_V | Layer 2 mesh routing with BLA |
| TP-Link TL-SG108E | Managed switches for VLAN trunking |
| D-Link DIR-1960 A1 | Router hardware (3 nodes) |
| Ansible 8+ | Configuration automation |
| Docker + Semaphore | Web-based deployment interface |
| pytest | Test framework (39 test files) |
| MkDocs Material | Documentation site |

---

Built with OpenWrt, Batman-adv, Ansible, and Docker.
