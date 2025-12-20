# Monitoring Guide for OpenWrt Mesh Nodes

This document describes the lightweight monitoring solution for OpenWrt mesh nodes using collectd, vnStat, and custom health checks.

## Overview

![Monitoring Stack](../assets/diagrams/monitoring-stack.svg)

*Monitoring architecture showing data collection, storage, and access paths.*

The monitoring solution provides:

- **Collectd**: Metrics collection (CPU, memory, disk, network, wireless)
- **LuCI Statistics**: Web UI with graphs for all metrics
- **vnStat**: Long-term bandwidth usage tracking
- **Mesh Health Monitoring**: Custom scripts monitoring mesh topology and node health
- **USB Storage**: All data stored on `/x00` for persistence

### Key Features

- **Lightweight**: Low resource usage suitable for embedded devices
- **Independent**: Each node monitors itself (no central collector)
- **Persistent**: Data stored on USB storage survives reboots
- **Comprehensive**: System, network, wireless, and mesh-specific metrics
- **Automated**: Health checks run every 5 minutes via cron
- **Flexible**: Can be deployed automatically during node setup or manually afterward

## Prerequisites

**CRITICAL:** USB storage must be mounted at `/x00` before deploying monitoring.

```bash
# First, ensure USB storage is configured
make usb-storage NODE=1

# Verify USB is mounted
make usb-status NODE=1
```

## Deployment Methods

Monitoring can be deployed in two ways:

### Method 1: Automatic Deployment (During Node Setup)

Monitoring is **automatically deployed** during `make deploy-node NODE=1` if:

1. USB storage is detected and mounted at `/x00`
2. `ENABLE_MONITORING=true` in `.env` file (default)

To enable/disable automatic monitoring deployment:

```bash
# Edit .env file
ENABLE_MONITORING=true   # Deploy monitoring automatically (default)
ENABLE_MONITORING=false  # Skip monitoring during deployment
```

**Benefits:**

- One-step deployment - monitoring configured along with node
- No separate manual step required
- Consistent configuration across all nodes

**When monitoring auto-deploys:**

- Collectd, vnStat, and health scripts are installed
- Services are enabled and started
- Data directories created on `/x00/monitoring/`
- Cron jobs configured for health checks

### Method 2: Manual Deployment (After Node Setup)

If monitoring was skipped during initial deployment, you can add it later:

```bash
# Deploy monitoring to a single node
make deploy-monitoring NODE=1

# Deploy monitoring to all nodes
make deploy-monitoring
```

**Use cases for manual deployment:**

- Monitoring was disabled during initial deployment (`ENABLE_MONITORING=false`)
- USB storage was added after initial node deployment
- Re-deploying monitoring after configuration changes

## Deployment

**Note:** The sections below describe manual deployment. For automatic deployment, see "Method 1: Automatic Deployment" above.

### Deploy Monitoring to a Single Node

```bash
# Deploy monitoring to node 1
make deploy-monitoring NODE=1

# With verbose output
make deploy-monitoring NODE=1 VERBOSE=1
```

### Deploy Monitoring to All Nodes

```bash
# Deploy to all nodes at once
make deploy-monitoring
```

### What Gets Installed

**Packages** (~3-4MB):

- `collectd` - Core metrics collector
- `collectd-mod-*` - Plugins for CPU, memory, disk, network, wireless, etc.
- `luci-app-statistics` - Web UI for collectd graphs
- `luci-app-vnstat2` - Web UI for vnStat bandwidth graphs
- `luci-app-commands` - Custom command shortcuts in LuCI
- `vnstat` - Bandwidth tracking daemon
- `vnstati` - Graph generation for vnStat

**Configuration:**

- Data storage: `/x00/monitoring/`
- Collection interval: 30 seconds
- Disk write interval: 5 minutes (reduces wear)
- Log rotation: 30 days

**Services:**

- `collectd` - Metrics collection daemon
- `vnstat` - Bandwidth tracking daemon

**Scripts:**

- `/usr/bin/mesh-monitor.sh` - Health check script (runs every 5 min)
- `/usr/bin/monitoring-report.sh` - Status report generator

**LuCI Custom Commands:**

The following quick-access commands are configured in the LuCI web interface:

- **Mesh Neighbors** - `batctl o` - Shows all visible mesh neighbors
- **Gateway List** - `batctl gwl` - Shows available gateway nodes
- **Mesh Status Report** - `/usr/bin/monitoring-report.sh` - Full monitoring status
- **Batman Interface** - `batctl if` - Shows interfaces participating in mesh
- **Bandwidth Stats (bat0)** - `vnstat -i bat0` - Bandwidth usage on mesh interface

Access these commands via: **LuCI → System → Custom Commands**

## Accessing Monitoring Data

### Web Interface (LuCI)

Access monitoring via web browser:

```bash
# Open collectd statistics for node 1
make monitoring-graphs NODE=1

# Or manually navigate to:
# Collectd Statistics: http://10.11.12.1/cgi-bin/luci/admin/statistics/graph
# vnStat Bandwidth:     http://10.11.12.1/cgi-bin/luci/admin/status/vnstat
# Custom Commands:      http://10.11.12.1/cgi-bin/luci/admin/system/commands
```

**LuCI → Statistics → Graphs (Collectd):**

- CPU usage (user, system, idle)
- Memory usage (free, cached, buffered)
- Load average (1, 5, 15 minutes)
- Disk usage (/x00, /overlay)
- Disk I/O (read/write operations)
- Network traffic (bat0, br-lan, wlan0, wlan1)
- Wireless stats (signal, noise, bitrate)
- Temperature sensors
- Ping latency (to other mesh nodes)
- Process count
- System uptime

**LuCI → Status → vnStat Traffic Monitor:**

- Real-time bandwidth usage
- Hourly, daily, monthly, yearly statistics
- Per-interface graphs (bat0, br-lan, wlan0, wlan1)
- Top traffic days/hours

**LuCI → System → Custom Commands:**

- Quick-access buttons for mesh status commands
- One-click access to `batctl o`, `batctl gwl`, monitoring reports
- No need to SSH for common operations

### Command Line Reports

```bash
# View comprehensive status report
make monitoring-status NODE=1

# View mesh health logs
make monitoring-logs NODE=1

# SSH to node and run report
ssh root@10.11.12.1 monitoring-report.sh
```

### Direct SSH Access

```bash
# SSH to the node
ssh root@10.11.12.1

# View monitoring status
monitoring-report.sh

# View bandwidth stats
vnstat -i bat0              # All-time stats
vnstat -i bat0 -d           # Daily stats
vnstat -i bat0 -h           # Hourly stats
vnstat -i bat0 -m           # Monthly stats
vnstat -i bat0 -l           # Live stats

# View health logs
tail -f /x00/monitoring/logs/mesh-health.log

# Check collectd status
/etc/init.d/collectd status
/etc/init.d/collectd restart

# Check vnstat status
/etc/init.d/vnstat status

# View RRD files
ls -lh /x00/monitoring/collectd/rrd/

# Check disk usage
du -sh /x00/monitoring/*
```

## Monitored Metrics

### System Metrics

- **CPU**: Usage per core, user/system/idle time
- **Memory**: Used, free, cached, buffered
- **Load**: 1, 5, 15 minute averages
- **Uptime**: System uptime
- **Processes**: Total count, running, sleeping
- **Temperature**: CPU/system temperature sensors

### Storage Metrics

- **Disk Usage**: Free space on /x00 and /overlay
- **Disk I/O**: Read/write operations and throughput
- **Alerts**: Warning when /x00 usage > 90%

### Network Metrics

- **Interfaces**: bat0, br-lan, wlan0, wlan1, eth0, eth1
- **Traffic**: Bytes/packets in/out per interface
- **Errors**: Packet errors and drops
- **Bandwidth**: Historical usage via vnStat

### Wireless Metrics (via iwinfo)

- **Signal Strength**: Per-station RSSI
- **Noise Level**: Background noise
- **Bitrate**: Current transmission rate
- **Channel Utilization**: Airtime usage

### Mesh-Specific Metrics

- **Neighbor Count**: Number of mesh neighbors
- **Neighbor Connectivity**: Ping latency to other nodes
- **Gateway Status**: Current gateway mode
- **Interface Status**: Bat0, wlan0, wlan1 operational state

## Health Monitoring

### Automated Health Checks

The `mesh-monitor.sh` script runs every 5 minutes and checks:

1. **Batman-adv Module**: Verifies module is loaded
2. **Bat0 Interface**: Confirms mesh interface is up
3. **Mesh Neighbors**: Counts visible neighbors (expects 2 for 3-node mesh)
4. **USB Storage**: Verifies /x00 is mounted
5. **Disk Space**: Warns if usage > 90%
6. **Wireless Interfaces**: Checks wlan0/wlan1 operational state
7. **Gateway Mode**: Logs current gateway status

### Health Log Format

```
2025-11-22 12:00:00 - INFO: 2 mesh neighbors detected
2025-11-22 12:00:00 - INFO: Gateway mode: client
2025-11-22 12:05:00 - WARNING: USB storage usage at 85%
2025-11-22 12:10:00 - ERROR: No mesh neighbors detected (expected 2 for 3-node mesh)
```

### Viewing Logs

```bash
# Last 50 lines
make monitoring-logs NODE=1

# Follow logs in real-time
ssh root@10.11.12.1
tail -f /x00/monitoring/logs/mesh-health.log
```

## Data Storage

### Storage Layout

```
/x00/monitoring/
├── collectd/
│   └── rrd/              # RRD database files (time-series data)
│       ├── cpu-0/
│       ├── memory/
│       ├── interface-bat0/
│       └── ...
├── vnstat/               # vnStat database
│   ├── bat0
│   ├── br-lan
│   └── wlan0
└── logs/                 # Health check logs
    └── mesh-health.log
```

### Data Retention

- **RRD Files**: 1200 rows per RRA (configurable)
  - 30-second intervals = ~10 hours of detailed data
  - Automatically aggregates to longer intervals
  - 1 year of historical trends
- **Health Logs**: 30 days (auto-rotated)
- **vnStat Database**: Unlimited (until disk full)

### Disk Usage

Typical disk usage after 30 days:

- Collectd RRD files: ~50-100MB
- vnStat database: ~5-10MB
- Health logs: ~1-5MB
- **Total**: ~100MB per node

## Performance Impact

### Resource Usage

Typical resource consumption per node:

- **CPU**: < 1% average
- **Memory**: ~10-15MB RSS
- **Disk I/O**: Minimal (5-minute write interval)
- **Network**: Negligible (ping monitoring only)

### Optimization Settings

The configuration is optimized for flash storage:

- **Collection Interval**: 30 seconds (reduces CPU load)
- **Cache Flush**: 5 minutes (reduces disk writes)
- **RRA Single**: Enabled (one file per metric, reduces I/O)
- **Background GC**: Enabled on F2FS (wear leveling)

## Troubleshooting

### Monitoring Not Working

```bash
# Check USB storage is mounted
mount | grep /x00

# Check services running
/etc/init.d/collectd status
/etc/init.d/vnstat status

# Restart services
/etc/init.d/collectd restart
/etc/init.d/vnstat restart

# Check logs
logread | grep collectd
logread | grep vnstat
```

### No Data in Graphs

```bash
# Wait 5-10 minutes for initial data collection

# Verify RRD files exist
ls -l /x00/monitoring/collectd/rrd/

# Check collectd is collecting
/etc/init.d/collectd restart
sleep 60
ls -l /x00/monitoring/collectd/rrd/
```

### vnStat "Unable to read database" Error

If you see `Error: Unable to read database "/x00/monitoring/vnstat/bat0": No such file or directory`:

```bash
# Stop vnStat
/etc/init.d/vnstat stop

# Ensure directory exists
mkdir -p /x00/monitoring/vnstat
chmod 755 /x00/monitoring/vnstat

# Recreate databases for existing interfaces
for iface in bat0 br-lan wlan0 wlan1; do
  if ip link show "$iface" >/dev/null 2>&1; then
    rm -f "/x00/monitoring/vnstat/$iface"
    vnstat --create -i "$iface"
  fi
done

# Restart service
/etc/init.d/vnstat start

# Verify databases created
ls -lh /x00/monitoring/vnstat/

# Wait 5-10 minutes for data collection
vnstat -i bat0
```

### Monitoring Report Script Issues

If `/usr/bin/monitoring-report.sh` shows errors:

**"hostname: not found"** - Fixed in updated playbooks, hostname is now read from UCI/proc

**"Unknown parameter '1'" in vnStat** - Fixed in updated playbooks, changed `vnstat -i bat0 -d 1` to `vnstat -i bat0 -d`

To manually fix on deployed nodes:

```bash
# Redeploy monitoring (will update scripts)
make deploy-monitoring NODE=1
```

### Web UI Not Accessible

```bash
# Check LuCI is running
/etc/init.d/uhttpd status
/etc/init.d/uhttpd restart

# Check firewall allows access
uci show firewall | grep "wan.*input"

# Access from mesh network (not WAN)
# http://10.11.12.1/cgi-bin/luci/admin/statistics/graph
```

### Disk Full on /x00

```bash
# Check current usage
df -h /x00

# Clean old health logs
find /x00/monitoring/logs -name "*.log" -mtime +30 -delete

# Reduce RRD retention (if needed)
# Edit /etc/config/luci_statistics
uci set luci_statistics.collectd_rrdtool.RRARows='600'
uci commit luci_statistics
/etc/init.d/collectd restart
```

### Health Checks Not Running

```bash
# Check cron job exists
crontab -l | grep mesh-monitor

# Run manually to test
/usr/bin/mesh-monitor.sh

# Check logs
tail /x00/monitoring/logs/mesh-health.log
```

## Customization

### Adjust Collection Interval

Edit `/etc/config/luci_statistics`:

```bash
# Change from 30 to 60 seconds
uci set luci_statistics.collectd.Interval='60'
uci commit luci_statistics
/etc/init.d/collectd restart
```

### Add Custom Metrics

Create a custom collectd plugin:

```bash
# Example: Monitor specific process
cat > /etc/collectd/conf.d/custom.conf << 'EOF'
LoadPlugin processes
<Plugin processes>
  Process "hostapd"
  Process "dnsmasq"
</Plugin>
EOF

/etc/init.d/collectd restart
```

### Change Monitored Interfaces

```bash
# Edit interface list
uci set luci_statistics.collectd_interface.Interfaces='bat0 br-lan wlan0'
uci commit luci_statistics
/etc/init.d/collectd restart
```

### Modify Health Check Frequency

```bash
# Change from 5 minutes to 10 minutes
crontab -e
# Change: */5 * * * * to */10 * * * *
```

## Integration with External Systems

### Exporting to Grafana (Future Enhancement)

To send metrics to a central Grafana instance:

1. Install `collectd-mod-network` on nodes
2. Configure network plugin to forward to Grafana server
3. Set up Grafana with collectd data source

### Alerting (Future Enhancement)

Options for alerts:

1. **Email**: Configure collectd notification plugin
2. **Webhook**: Use collectd exec plugin to call webhook on threshold
3. **MQTT**: Publish health status to MQTT broker
4. **Custom Script**: Extend `mesh-monitor.sh` to send notifications

## Best Practices

1. **Deploy After USB Storage**: Always ensure USB is mounted before deploying monitoring
2. **Monitor Disk Space**: Keep /x00 usage under 80%
3. **Review Health Logs**: Check logs weekly for issues
4. **Backup RRD Data**: Periodically backup /x00/monitoring/ directory
5. **Test Failover**: Verify monitoring works after node reboots

## Related Documentation

- [Collectd Documentation](https://collectd.org/documentation.shtml)
- [LuCI Statistics](https://openwrt.org/docs/guide-user/luci/luci_app_statistics)
- [vnStat Guide](https://humdi.net/vnstat/)
- [OpenWrt Monitoring](https://openwrt.org/docs/guide-user/services/network_monitoring/start)
