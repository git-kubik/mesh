# Getting Started

Welcome to the OpenWrt Mesh Network project! This section will guide you through setting up your high-availability mesh network.

## Choose Your Path

| Guide | Time | Best For |
|-------|------|----------|
| [Quick Start](quickstart.md) | 30 min | First deployment, getting running fast |
| [Initial Setup](initial-setup.md) | 15 min | Preparing a factory-fresh router |
| [Ansible Basics](ansible-basics.md) | 20 min | Understanding the automation |

## Prerequisites

Before you begin, ensure you have:

- **Hardware**: 3x D-Link DIR-1960 A1 routers (or compatible OpenWrt devices)
- **Software**: SSH client, web browser
- **Network**: Ethernet cables for wired mesh backbone
- **Repository**: This project cloned to your control machine
- **Time**: ~30 minutes for first node, ~15 minutes for each additional

## Deployment Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Deployment Workflow                               │
├─────────────────────────────────────────────────────────────────────┤
│  1. Flash OpenWrt  →  2. Audit Node  →  3. Deploy Config            │
│                                                                      │
│  Factory router       Check packages    Ansible automation          │
│  → OpenWrt 24.10      → Fix conflicts   → Full mesh config          │
└─────────────────────────────────────────────────────────────────────┘
```

## What You'll Build

A 3-node mesh network with:

- **Wired Ring Topology**: Full redundancy via LAN3/LAN4 connections
- **Wireless Backup**: 2.4GHz 802.11s mesh as failover
- **Unified WiFi**: 5GHz AP with 802.11r fast roaming
- **Multi-Gateway**: All nodes provide internet access
- **VLAN Segmentation**: Separate networks for clients, management, and IoT

## Section Contents

- **[Quick Start](quickstart.md)** - Deploy your first node step-by-step
- **[Initial Setup](initial-setup.md)** - Prepare a factory router for deployment
- **[Ansible Basics](ansible-basics.md)** - Understand the automation workflow

## Next Steps

1. Start with [Quick Start](quickstart.md) for the fastest path to a working mesh
2. Review [Architecture](../architecture/index.md) to understand the design
3. Explore [Deployment](../deployment/index.md) for configuration options
