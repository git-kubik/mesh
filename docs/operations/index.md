# Operations

This section covers day-to-day operations, monitoring, and maintenance of your mesh network.

## Overview

Once deployed, the mesh network requires minimal maintenance. This section covers regular monitoring, backup procedures, firmware updates, and optional features.

## Quick Reference

| Task | Command |
|------|---------|
| Health check | `make verify` |
| Mesh status | `make batman-status` |
| Create backup | `make snapshot-all` |
| View logs | `make logs` |

## Section Contents

| Document | Description |
|----------|-------------|
| [Backup & Restore](backup-restore.md) | Backup strategies and disaster recovery |
| [Firmware Management](firmware.md) | Upgrades, custom images, sysupgrade |
| [USB Storage](usb-storage.md) | External storage configuration |
| [Monitoring](monitoring.md) | Collectd, statistics, alerts |
| [Distributed Syslog](syslog.md) | Centralized logging |
| [Recovery](recovery.md) | Disaster recovery procedures |

## Daily Operations

### Health Monitoring

```bash
# Quick status check
make verify

# Detailed mesh status
make batman-status

# View recent logs
make logs
```

### Backup Schedule

| Frequency | Action | Command |
|-----------|--------|---------|
| Daily | Quick backup | `make backup` |
| Weekly | Full snapshot | `make snapshot-all` |
| Pre-change | Full snapshot | `make snapshot NODE=1` |

## Common Tasks

### Check Mesh Status

```bash
# On any node
batctl o           # Originators (all mesh participants)
batctl n           # Neighbors (directly connected)
batctl gwl         # Gateway list
batctl if          # Interfaces in mesh
```

### Restart Services

```bash
# Restart mesh interface
/etc/init.d/network restart

# Restart wireless
wifi reload

# Full reboot (safe)
reboot
```

## Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Health check | Daily | `make check-all` |
| Backup configs | Weekly | `make backup` |
| Audit configuration | Weekly | `make audit` |
| Check for updates | Monthly | `opkg update && opkg list-upgradable` |
| Review logs | Monthly | `make logs` |
| Test failover | Quarterly | Manual link disconnect |

## Emergency Procedures

| Situation | Action |
|-----------|--------|
| Node unresponsive | Check power, try SSH, use console |
| Mesh fragmented | Check physical connections |
| WiFi not working | `wifi reload` on affected node |
| Total failure | Restore from snapshot |

See [Recovery](recovery.md) for detailed procedures.

## Related Documentation

- [Troubleshooting](../troubleshooting/index.md) - When things go wrong
- [Reference](../reference/index.md) - Command reference
- [Advanced](../advanced/index.md) - Custom configurations
