# OpenWrt Mesh Network Documentation

Welcome to the documentation for the OpenWrt Multi-Gateway Batman-adv Mesh Network project.

## Overview

This project provides infrastructure-as-code for deploying a high-availability 3-node mesh network using OpenWrt routers with Batman-adv Layer 2 routing.

**Key Features:**

- **Full Ring Topology**: 3 wired connections forming a complete ring
- **Wireless Backup**: 2.4GHz 802.11s mesh for automatic failover
- **Multi-Gateway**: 3 independent WAN connections with automatic failover
- **Unified WiFi**: 5GHz client AP with 802.11r seamless roaming
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
         Node1 (10.11.12.1)
          /  \
     LAN3/    \LAN4
        /      \
       /        \
  Node2 -------- Node3
(10.11.12.2) (10.11.12.3)
     LAN4 - LAN3

+ 2.4GHz wireless mesh backup
+ 5GHz unified client AP (802.11r roaming)
+ Multi-gateway WAN failover
```

## Getting Started

1. **[Quick Start](getting-started/quickstart.md)** - Deploy your first node in 30 minutes
2. **[Architecture Overview](architecture/overview.md)** - Understand the design
3. **[Philosophy](philosophy.md)** - Why decisions were made

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
| OpenWrt 24.10 | Router operating system |
| Batman-adv BATMAN_V | Layer 2 mesh routing |
| Ansible | Configuration automation |
| D-Link DIR-1960 A1 | Hardware platform |
| pytest | Test framework |
| MkDocs Material | Documentation |

---

Built with OpenWrt, Batman-adv, Ansible, and Docker.
