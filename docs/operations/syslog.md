# Distributed Syslog Guide for OpenWrt Mesh Nodes

This document describes the distributed syslog implementation for OpenWrt mesh nodes, providing persistent logging without centralized infrastructure.

## Overview

The distributed syslog solution provides:

- **Persistent Logs**: System logs written directly to USB storage (`/x00/logs/syslog`)
- **No Additional Packages**: Uses built-in `logd` with UCI configuration
- **Per-Node Storage**: Each node maintains its own logs locally
- **Automatic Rotation**: logd handles rotation at 2MB, cron cleans old files after 30 days
- **Zero Overhead**: Direct write to USB, no capture scripts needed

### Key Features

- **Lightweight**: No syslog-ng or rsyslog needed (~0 KB additional packages)
- **Independent**: Each node operates independently
- **Resilient**: Logs survive reboots (USB storage)
- **Simple**: Single log file, easy to view and search
- **Native**: Uses OpenWrt's built-in logd configuration

## Prerequisites

**CRITICAL:** USB storage must be mounted at `/x00` before deployment.

```bash
# Ensure USB storage is configured
make usb-storage NODE=1

# Verify USB is mounted
make usb-status NODE=1
```

## How It Works

### 1. **Direct Log Writing**

OpenWrt's `logd` is configured via UCI to write directly to USB:

```bash
uci set system.@system[0].log_file='/x00/logs/syslog'
uci set system.@system[0].log_size='2048'  # 2MB before rotation
uci commit system
/etc/init.d/log restart
```

### 2. **Log Rotation**

- **logd rotation**: When log reaches 2MB, logd rotates to `syslog.1`, `syslog.2`, etc.
- **Cron cleanup**: Daily at 3 AM, files older than 30 days are deleted

### 3. **Storage Layout**

```
/x00/logs/
├── syslog        # Current log file (up to 2MB)
├── syslog.1      # Previous rotation
├── syslog.2      # Older rotation
└── ...
```

## Deployment

### Automatic Deployment (During Node Setup)

Distributed syslog is **automatically deployed** as part of the monitoring role when:

1. USB storage is detected and mounted at `/x00`
2. Monitoring is enabled (default: `ENABLE_MONITORING=true`)

### Manual Deployment (If USB Added Later)

If you add USB storage after initial deployment, just redeploy the node:

```bash
# Configure USB storage first
make usb-storage NODE=1

# Redeploy node (will configure syslog)
make deploy-node NODE=1
```

## Viewing Logs

### Via SSH

```bash
# SSH to node
ssh root@10.11.12.1

# View current log
cat /x00/logs/syslog

# Tail log in real-time
tail -f /x00/logs/syslog

# View rotated logs
cat /x00/logs/syslog.1

# List all log files
ls -lh /x00/logs/

# Search logs
grep "batman" /x00/logs/syslog*
grep -i "error" /x00/logs/syslog*
```

### Via Web Interface (LuCI)

1. Navigate to `http://10.11.12.1/cgi-bin/luci/admin/status/syslog`
2. View real-time system log

## Log Analysis Examples

### Find All Errors

```bash
ssh root@10.11.12.1
grep -i "err\|fail\|crit" /x00/logs/syslog* | tail -50
```

### Track Batman-adv Events

```bash
grep "batman" /x00/logs/syslog*
```

### Wireless Events

```bash
grep "wlan\|wifi\|hostapd" /x00/logs/syslog*
```

### SSH Login Attempts

```bash
grep "sshd\|login" /x00/logs/syslog*
```

### Firewall Events

```bash
grep "firewall\|DROP\|ACCEPT" /x00/logs/syslog*
```

### Track Specific Time Range

```bash
# Logs from specific date
cat /x00/logs/mesh-node1-2025-11-15.log

# Logs from date range
cat /x00/logs/mesh-node1-2025-11-{15,16,17}.log | grep "error"
```

## Manual Operations

### Trigger Immediate Capture

```bash
# Via Makefile
make syslog-capture NODE=1

# Or SSH to node
ssh root@10.11.12.1
/usr/bin/syslog-capture.sh
```

### Manual Rotation

```bash
ssh root@10.11.12.1
/usr/bin/syslog-rotate.sh
```

### Clear Old Logs

```bash
# Delete logs older than 14 days
ssh root@10.11.12.1
find /x00/logs -name "*.log" -mtime +14 -delete
```

### Disable Syslog Capture Temporarily

```bash
ssh root@10.11.12.1

# Remove cron jobs
crontab -l | grep -v syslog > /tmp/cron.tmp
crontab /tmp/cron.tmp

# Re-enable later
crontab -l > /tmp/cron.tmp
echo "*/15 * * * * /usr/bin/syslog-capture.sh" >> /tmp/cron.tmp
echo "0 3 * * * /usr/bin/syslog-rotate.sh" >> /tmp/cron.tmp
crontab /tmp/cron.tmp
```

## Configuration

### Adjust Capture Interval

By default, logs are captured every 15 minutes. To change:

```bash
ssh root@10.11.12.1

# Edit cron
crontab -e

# Change */15 to desired interval:
# */5   = every 5 minutes
# */30  = every 30 minutes
# 0 *   = every hour
```

### Adjust Retention Period

Default retention is 30 days. To change:

```bash
ssh root@10.11.12.1

# Edit rotation script
vi /usr/bin/syslog-rotate.sh

# Change this line:
RETENTION_DAYS=30  # Change to desired days
```

### Adjust Compression Threshold

Logs older than 7 days are compressed. To change:

```bash
ssh root@10.11.12.1
vi /usr/bin/syslog-rotate.sh

# Change this line:
-mtime +7  # Change to desired days
```

## Storage Usage

### Typical Disk Usage

For a 3-node mesh with moderate activity:

| Duration | Uncompressed | Compressed | Notes |
|----------|--------------|------------|-------|
| 1 day | ~5-10 MB | ~1-2 MB | Depends on log verbosity |
| 7 days | ~50-70 MB | ~10-15 MB | First 7 days uncompressed |
| 30 days | ~200-300 MB | ~50-80 MB | Full retention with compression |

**With 32GB USB storage:**

- Logs use < 0.3% of total space
- Can retain 100+ days of logs easily

### Monitor Disk Usage

```bash
# Via Makefile
make syslog-list NODE=1

# Via SSH
ssh root@10.11.12.1
du -sh /x00/logs
df -h /x00
```

## Troubleshooting

### No Log Files Created

```bash
# Check USB storage is mounted
mount | grep /x00

# Check syslog directory exists
ls -ld /x00/logs

# Check cron job exists
crontab -l | grep syslog-capture

# Manually trigger capture
/usr/bin/syslog-capture.sh

# Check for errors
logread | grep -i "syslog\|error"
```

### Logs Not Being Captured

```bash
# Verify script is executable
ls -l /usr/bin/syslog-capture.sh

# Run manually and check for errors
/usr/bin/syslog-capture.sh

# Check cron is running
ps | grep cron

# Verify log directory permissions
ls -ld /x00/logs
```

### Disk Full

```bash
# Check disk usage
df -h /x00

# Manually run rotation
/usr/bin/syslog-rotate.sh

# Delete old logs manually
find /x00/logs -name "*.log" -mtime +14 -delete

# Compress logs manually
gzip /x00/logs/*.log
```

### Missing Syslog Scripts

If scripts are missing after deployment:

```bash
# Redeploy to node
make deploy-node NODE=1

# Or manually check deployment playbook ran
make audit-node NODE=1 | grep -A 10 "DISTRIBUTED SYSLOG"
```

## Integration with Monitoring

Distributed syslog works alongside the monitoring system:

```
/x00/
├── logs/                  # Distributed syslog (this guide)
│   ├── mesh-node1-*.log   # System logs
│   └── rotation.log
└── monitoring/            # Monitoring system (separate)
    ├── collectd/          # Metrics
    ├── vnstat/            # Bandwidth
    └── logs/
        └── mesh-health.log  # Health checks
```

**Key Differences:**

| Feature | Distributed Syslog | Mesh Health Logs |
|---------|-------------------|------------------|
| **Purpose** | All system logs | Mesh-specific health |
| **Frequency** | Every 15 min | Every 5 min |
| **Content** | Full logd output | Mesh topology checks |
| **Location** | `/x00/logs/` | `/x00/monitoring/logs/` |
| **View Command** | `make syslog-view` | `make monitoring-logs` |

## Backup and Recovery

### Backup Logs

```bash
# Backup from one node
scp -r root@10.11.12.1:/x00/logs/ ~/backups/node1-logs-$(date +%Y-%m-%d)/

# Backup from all nodes
for NODE in 1 2 3; do
  scp -r root@10.11.12.$NODE:/x00/logs/ ~/backups/node${NODE}-logs-$(date +%Y-%m-%d)/
done
```

### Restore Logs

```bash
# Restore to node
scp -r ~/backups/node1-logs-2025-11-22/* root@10.11.12.1:/x00/logs/
```

## Best Practices

1. **Regular Reviews**: Check logs weekly for issues
2. **Backup Important Logs**: Backup `/x00/logs/` before major changes
3. **Monitor Disk Space**: Keep `/x00` usage under 80%
4. **Adjust Retention**: Reduce retention if disk space is limited
5. **Correlation**: Compare logs across nodes for mesh-wide issues

## Comparison: Distributed vs Centralized

| Aspect | Distributed (This) | Centralized (Option 1) |
|--------|-------------------|----------------------|
| **Complexity** | ✅ Simple | ❌ More complex |
| **Dependencies** | ✅ None | ❌ syslog-ng on gateway |
| **Network** | ✅ Independent | ❌ Requires mesh connectivity |
| **Search** | ⚠️ Per-node | ✅ All logs in one place |
| **Resilience** | ✅ Node failures isolated | ❌ Gateway down = no logs |
| **Storage** | ⚠️ Each node's USB | ✅ Gateway USB only |
| **Correlation** | ❌ Manual | ✅ Easy across nodes |

**When to use Distributed:**

- Simple mesh setup
- Each node has USB storage
- Network reliability is a concern
- Minimal additional packages desired

**When to use Centralized:**

- Need easy log correlation
- Want unified search across all nodes
- Gateway node is highly reliable
- Willing to run syslog-ng (~400 KB)

## Advanced Features

### Log Forwarding (Optional)

To forward logs to external syslog server while keeping local copies:

```bash
ssh root@10.11.12.1

# Edit /etc/config/system
uci add system system
uci set system.@system[-1].log_ip='192.168.1.100'
uci set system.@system[-1].log_port='514'
uci set system.@system[-1].log_proto='udp'
uci commit system
/etc/init.d/log restart
```

### Custom Log Filtering

Create filtered logs for specific events:

```bash
ssh root@10.11.12.1

# Create custom capture script
cat > /usr/bin/syslog-capture-batman.sh << 'EOF'
#!/bin/sh
LOG_DIR="/x00/logs"
DATE=$(date +%Y-%m-%d)
HOSTNAME=$(uci -q get system.@system[0].hostname)

# Capture only batman-adv logs
logread | grep batman >> "${LOG_DIR}/${HOSTNAME}-batman-${DATE}.log"
EOF

chmod +x /usr/bin/syslog-capture-batman.sh

# Add to cron
crontab -l | { cat; echo "*/15 * * * * /usr/bin/syslog-capture-batman.sh"; } | crontab -
```

## Related Documentation

- [Monitoring Guide](monitoring.md) - Collectd and vnStat monitoring
- [USB Storage Guide](usb-storage.md) - USB storage configuration
- [Node Audit](../reference/node-audit.md) - System auditing

## Summary

Distributed syslog provides:

- ✅ **Persistent logging** without additional packages
- ✅ **Per-node independence** - no central infrastructure
- ✅ **Automatic management** - capture and rotation via cron
- ✅ **Easy access** - via web UI, SSH, or Makefile commands
- ✅ **Resilient** - logs survive reboots and network issues

Perfect for simple mesh deployments where each node manages its own logs!
