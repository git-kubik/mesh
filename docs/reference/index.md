# Reference

This section provides comprehensive reference documentation for commands, configuration, and APIs.

## Section Contents

| Document | Description |
|----------|-------------|
| [Makefile Commands](makefile.md) | Complete reference for all Makefile targets |
| [Playbooks Reference](playbooks.md) | All Ansible playbooks with parameters |
| [CLI Commands](cli-commands.md) | batctl, UCI, OpenWrt, and network commands |
| [Node Audit](node-audit.md) | Audit system documentation |
| [Factory Reset](factory-reset.md) | Password persistence and reset procedures |

## Quick Reference

### Most Used Makefile Commands

```bash
# Deployment
make deploy-node NODE=1       # Deploy single node
make deploy                   # Deploy all nodes
make check-all               # Verify all nodes

# Status
make batman-status           # View mesh topology
make verify                  # Full verification

# Maintenance
make snapshot-all            # Backup all configs
make audit                   # Audit configuration
```

### Essential batctl Commands

```bash
batctl o              # Originators (mesh participants)
batctl n              # Neighbors (direct connections)
batctl gwl            # Gateway list
batctl if             # Interfaces in mesh
batctl ping <MAC>     # Ping mesh node by MAC
batctl traceroute <MAC>  # Trace path to node
```

### Common UCI Commands

```bash
# View configuration
uci show network          # Network config
uci show wireless         # WiFi config
uci show dhcp             # DHCP config
uci show firewall         # Firewall config

# Modify configuration
uci set wireless.radio0.channel='6'
uci commit wireless
wifi reload
```

### Network Diagnostics

```bash
# Interface status
ip link show              # All interfaces
ip addr show              # IP addresses
ip route show             # Routing table

# Connectivity
ping -c 3 10.11.12.1      # Ping node
traceroute 10.11.12.1     # Trace route

# Wireless
iw dev                    # Wireless devices
iw dev wlan0 info         # Interface info
iw dev wlan0 station dump # Connected clients
```

## Configuration Files

| File | Purpose |
|------|---------|
| `/etc/config/network` | Network interfaces, VLANs |
| `/etc/config/wireless` | WiFi radios and SSIDs |
| `/etc/config/dhcp` | DHCP server settings |
| `/etc/config/firewall` | Firewall zones and rules |
| `/etc/config/batman-adv` | Batman-adv mesh config |
| `/etc/config/system` | Hostname, timezone |

## Log Files

| Log | Location | Command |
|-----|----------|---------|
| System log | Ring buffer | `logread` |
| Kernel log | Ring buffer | `dmesg` |
| Wireless | System log | `logread \| grep hostapd` |
| DHCP | System log | `logread \| grep dnsmasq` |

## Related Documentation

- [Operations](../operations/index.md) - Using these commands in practice
- [Troubleshooting](../troubleshooting/index.md) - Debugging with these tools
- [Development](../development/index.md) - Contributing and testing
