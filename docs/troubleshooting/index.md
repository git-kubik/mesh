# Troubleshooting

This section helps you diagnose and resolve common issues with your mesh network.

## Section Contents

| Document | Description |
|----------|-------------|
| [Common Issues](common-issues.md) | Solutions to frequently encountered problems |
| [Debugging Guide](debugging.md) | Advanced debugging techniques and tools |

## Quick Diagnostic Commands

Run these commands to quickly assess network health:

```bash
# Check all nodes are reachable
make check-all

# View mesh status on a single node
ssh root@10.11.12.1 "batctl o && batctl gwl"

# Check for errors in logs
ssh root@10.11.12.1 "logread | grep -i error | tail -20"
```

## Troubleshooting Flowchart

```
Problem Detected
       │
       ▼
  Can you SSH to nodes?
       │
   ┌───┴───┐
   No      Yes
   │       │
   ▼       ▼
Check    Is mesh formed?
physical    │
connectivity ├───┬───┐
           No    Yes
           │     │
           ▼     ▼
       Check   Is traffic
       batman  flowing?
       interfaces  │
               ┌───┴───┐
              No      Yes
               │       │
               ▼       ▼
           Check    Is WiFi
           firewall working?
```

## Common Symptoms and Solutions

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| Node unreachable | Network/power issue | Check cables, reboot |
| Slow mesh | Interference, congestion | Check channel, bandwidth |
| No WiFi clients | AP not started | `wifi reload` |
| DHCP not working | dnsmasq issue | `service dnsmasq restart` |
| High latency | Bad mesh path | Check `batctl o` TQ values |
| Intermittent drops | Wireless interference | Change mesh channel |

## Emergency Recovery

If you've lost access to all nodes:

### Option 1: Console Access (Recommended)

1. Connect USB-TTL adapter to router serial port
2. Open terminal at 115200 baud
3. Boot router and interrupt U-Boot
4. Flash known-good firmware

### Option 2: Failsafe Mode

1. Power cycle router
2. Press reset button when LEDs blink
3. Router starts in failsafe mode (192.168.1.1)
4. Connect directly and run `firstboot`

### Option 3: Physical Reset

1. Hold reset button for 10+ seconds
2. Router restores factory firmware
3. Reconfigure from scratch

See [Common Issues](common-issues.md) for detailed procedures.

## Getting Help

If you can't resolve an issue:

1. **Check documentation**: Search this site for your error message
2. **Review logs**: `logread` often reveals the root cause
3. **Open an issue**: [GitHub Issues](https://github.com/git-kubik/mesh/issues)
4. **Provide details**:
   - OpenWrt version (`cat /etc/openwrt_release`)
   - Error messages
   - Steps to reproduce
   - Output of `batctl o` and `batctl n`

## Related Documentation

- [Operations](../operations/index.md) - Normal operational procedures
- [Reference](../reference/index.md) - Command reference
- [Architecture](../architecture/index.md) - Understanding the design
