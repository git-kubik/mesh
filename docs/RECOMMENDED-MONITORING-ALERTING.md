# Recommended Monitoring & Alerting Strategy

## Overview

This document provides a tiered approach to monitoring and alerting for your OpenWrt mesh network, building on the existing infrastructure.

---

## Current Monitoring Stack

You already have:

- ✅ **Collectd** - Metrics collection (CPU, memory, disk, network, wireless)
- ✅ **vnStat** - Bandwidth usage tracking
- ✅ **mesh-monitor.sh** - Mesh health checks (every 5 minutes)
- ✅ **Distributed syslog** - All system logs to `/x00/logs/`
- ✅ **LuCI Statistics** - Web UI with graphs
- ✅ **USB Storage** - Persistent data on `/x00/`

**Strengths:**

- Comprehensive data collection
- Persistent storage
- Web interface for viewing
- Mesh-specific health monitoring

**Gap:**

- ❌ No proactive alerting
- ❌ Must manually check logs/graphs
- ❌ No notifications when issues occur

---

## Tier 1: Essential Monitoring (RECOMMENDED) 🎯

**Goal:** Get notified about critical issues only, minimal maintenance.

### What to Monitor

| Alert | Trigger | Why Critical |
|-------|---------|--------------|
| **Node Offline** | Can't ping node for 5+ min | Mesh partition, hardware failure |
| **Disk Full** | USB `/x00` > 95% | Logs/monitoring will fail |
| **No Mesh Neighbors** | 0 neighbors for 10+ min | Mesh network broken |
| **High CPU** | > 90% for 15+ min | Performance issues, runaway process |
| **Low Memory** | < 5MB free | System instability, OOM kills |
| **Gateway Down** | No WAN connectivity | Internet access lost |

### Implementation Option A: Simple Email Alerts (Lightest)

**Best for:** Home users, low complexity, no additional infrastructure.

Add alerting script to mesh nodes:

```bash
#!/bin/sh
###############################################################################
# Simple Email Alerting Script
# Sends email via external SMTP when critical issues detected
###############################################################################

ALERT_EMAIL="your-email@example.com"
SMTP_SERVER="smtp.gmail.com:587"
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-app-password"  # Use app password, not real password
HOSTNAME=$(uci -q get system.@system[0].hostname || hostname)
ALERT_LOG="/x00/logs/alerts-sent.log"

# Check if alert already sent recently (debounce)
check_alert_sent() {
    local alert_key="$1"
    local cooldown_seconds=3600  # 1 hour

    if [ -f "$ALERT_LOG" ]; then
        last_alert=$(grep "$alert_key" "$ALERT_LOG" | tail -1 | cut -d' ' -f1)
        if [ -n "$last_alert" ]; then
            current_time=$(date +%s)
            time_diff=$((current_time - last_alert))
            if [ $time_diff -lt $cooldown_seconds ]; then
                return 0  # Alert sent recently
            fi
        fi
    fi
    return 1  # OK to send alert
}

# Send alert email
send_alert() {
    local subject="$1"
    local message="$2"
    local alert_key="$3"

    # Check cooldown
    if check_alert_sent "$alert_key"; then
        return
    fi

    # Send email using curl
    echo "$message" | curl --ssl-reqd \
        --url "smtp://$SMTP_SERVER" \
        --user "$SMTP_USER:$SMTP_PASS" \
        --mail-from "$SMTP_USER" \
        --mail-rcpt "$ALERT_EMAIL" \
        --upload-file - \
        --header "Subject: [MESH ALERT] $HOSTNAME - $subject" \
        2>/dev/null

    # Log alert sent
    echo "$(date +%s) $alert_key" >> "$ALERT_LOG"
}

# Check disk space
check_disk() {
    usage=$(df /x00 | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$usage" -gt 95 ]; then
        send_alert "Disk Full" "USB storage at ${usage}% - cleanup needed!" "disk-full"
    fi
}

# Check mesh neighbors
check_neighbors() {
    neighbor_count=$(batctl o | grep -v "No" | grep -c "^[0-9a-f]" || echo "0")
    if [ "$neighbor_count" -eq 0 ]; then
        send_alert "No Mesh Neighbors" "Node is isolated - no mesh neighbors detected!" "no-neighbors"
    fi
}

# Check memory
check_memory() {
    free_kb=$(free | grep Mem | awk '{print $4}')
    free_mb=$((free_kb / 1024))
    if [ "$free_mb" -lt 5 ]; then
        send_alert "Low Memory" "Only ${free_mb}MB RAM free - system may crash!" "low-memory"
    fi
}

# Check CPU
check_cpu() {
    cpu_idle=$(top -bn1 | grep "CPU:" | awk '{print $8}' | sed 's/%//')
    cpu_usage=$((100 - cpu_idle))
    if [ "$cpu_usage" -gt 90 ]; then
        send_alert "High CPU" "CPU usage at ${cpu_usage}% - performance degraded!" "high-cpu"
    fi
}

# Check WAN connectivity (gateway nodes only)
check_wan() {
    if batctl gw | grep -q "server"; then
        if ! ping -c 3 -W 5 1.1.1.1 >/dev/null 2>&1; then
            send_alert "WAN Down" "Internet connectivity lost!" "wan-down"
        fi
    fi
}

# Run all checks
check_disk
check_neighbors
check_memory
check_cpu
check_wan
```

**Installation:**

```bash
# Add to deployment playbook
cat > /usr/bin/mesh-alert.sh << 'EOF'
[script above]
EOF
chmod +x /usr/bin/mesh-alert.sh

# Add to cron (every 15 minutes)
(crontab -l; echo "*/15 * * * * /usr/bin/mesh-alert.sh") | crontab -
```

**Pros:**

- ✅ Simple, self-contained
- ✅ No external infrastructure
- ✅ Email = accessible anywhere
- ✅ Low resource usage

**Cons:**

- ❌ Requires email credentials on nodes
- ❌ Depends on node having WAN access
- ❌ Email may be delayed

---

### Implementation Option B: Webhook Alerts (Recommended)

**Best for:** Users with smartphone, more flexible than email.

Use webhook services like:

- **Pushover** (push notifications to phone - $5 one-time)
- **Telegram Bot** (free, unlimited)
- **Discord Webhook** (free)
- **Slack Webhook** (free)

**Example: Telegram Bot Integration**

```bash
#!/bin/sh
###############################################################################
# Telegram Webhook Alerting
###############################################################################

TELEGRAM_BOT_TOKEN="your-bot-token"
TELEGRAM_CHAT_ID="your-chat-id"
HOSTNAME=$(uci -q get system.@system[0].hostname || hostname)

send_telegram() {
    local message="$1"

    curl -s -X POST \
        "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=🚨 *${HOSTNAME}*: ${message}" \
        -d "parse_mode=Markdown" \
        >/dev/null 2>&1
}

# Check disk space
usage=$(df /x00 | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$usage" -gt 95 ]; then
    send_telegram "⚠️ Disk Full: ${usage}% used on /x00"
fi

# Check mesh neighbors
neighbor_count=$(batctl o | grep -v "No" | grep -c "^[0-9a-f]" || echo "0")
if [ "$neighbor_count" -eq 0 ]; then
    send_telegram "❌ No mesh neighbors detected!"
fi

# Check memory
free_mb=$(free | awk '/Mem:/ {print int($4/1024)}')
if [ "$free_mb" -lt 5 ]; then
    send_telegram "⚠️ Low Memory: Only ${free_mb}MB free"
fi

# Check gateway WAN (if gateway)
if batctl gw | grep -q "server"; then
    if ! ping -c 3 -W 5 1.1.1.1 >/dev/null 2>&1; then
        send_telegram "❌ WAN connectivity lost!"
    fi
fi
```

**Setup Telegram Bot:**

```bash
# 1. Message @BotFather on Telegram
#    Send: /newbot
#    Follow prompts to create bot
#    Save the token

# 2. Get your chat ID
#    Start chat with your bot
#    Send any message
#    Visit: https://api.telegram.org/bot<TOKEN>/getUpdates
#    Find your chat_id in response
```

**Pros:**

- ✅ Instant push notifications
- ✅ Free (Telegram)
- ✅ Works from anywhere
- ✅ Simple webhook integration

**Cons:**

- ❌ Requires external service
- ❌ Token stored on node

---

### Implementation Option C: External Monitoring (Most Robust)

**Best for:** Users who want centralized monitoring dashboard.

Run monitoring on external device (Raspberry Pi, NAS, server):

**Option C1: Simple Ping Monitor + Webhook**

```bash
#!/bin/bash
###############################################################################
# External Mesh Monitor (Run on external server/Pi)
# Pings nodes and sends alerts if unreachable
###############################################################################

NODES=("10.11.12.1" "10.11.12.2" "10.11.12.3")
NODE_NAMES=("mesh-node1" "mesh-node2" "mesh-node3")
TELEGRAM_BOT_TOKEN="your-token"
TELEGRAM_CHAT_ID="your-chat-id"
STATE_FILE="/tmp/mesh-monitor-state.txt"

send_alert() {
    local message="$1"
    curl -s -X POST \
        "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=${message}" \
        -d "parse_mode=Markdown" >/dev/null
}

# Create state file if not exists
touch "$STATE_FILE"

for i in "${!NODES[@]}"; do
    node_ip="${NODES[$i]}"
    node_name="${NODE_NAMES[$i]}"

    if ping -c 3 -W 5 "$node_ip" >/dev/null 2>&1; then
        # Node is up
        if grep -q "${node_name}:down" "$STATE_FILE"; then
            # Node recovered
            sed -i "/${node_name}:down/d" "$STATE_FILE"
            send_alert "✅ *${node_name}* is back online!"
        fi
    else
        # Node is down
        if ! grep -q "${node_name}:down" "$STATE_FILE"; then
            # New failure
            echo "${node_name}:down:$(date +%s)" >> "$STATE_FILE"
            send_alert "❌ *${node_name}* is offline! (${node_ip})"
        fi
    fi
done

# Add to cron on external server: */5 * * * * /path/to/mesh-monitor.sh
```

**Option C2: Uptime Kuma (Web Dashboard + Alerts)**

Popular open-source monitoring tool with web UI:

```bash
# Install on Raspberry Pi / NAS / Server
docker run -d --restart=always \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  --name uptime-kuma \
  louislam/uptime-kuma:1

# Access: http://your-server:3001
# Add monitors for:
# - Ping: 10.11.12.1, 10.11.12.2, 10.11.12.3
# - HTTP: http://10.11.12.1 (LuCI)
# - Port: 22 (SSH)

# Configure notifications:
# - Telegram
# - Discord
# - Email
# - Pushover
# - Slack
```

**Features:**

- ✅ Beautiful web dashboard
- ✅ Multi-channel alerts
- ✅ Uptime statistics
- ✅ Status page
- ✅ Historical data

**Cons:**

- ❌ Requires external server
- ❌ More complex setup

---

## Tier 2: Enhanced Monitoring (Optional) 📊

**Goal:** Better visibility, trending, and analysis.

### Daily/Weekly Reports

Add reporting script to send summaries:

```bash
#!/bin/sh
###############################################################################
# Daily Mesh Report
###############################################################################

TELEGRAM_BOT_TOKEN="your-token"
TELEGRAM_CHAT_ID="your-chat-id"
HOSTNAME=$(uci -q get system.@system[0].hostname || hostname)

# Gather stats
UPTIME=$(uptime | awk -F'up ' '{print $2}' | cut -d',' -f1)
LOAD=$(uptime | awk -F'load average:' '{print $2}')
MEM_FREE=$(free | awk '/Mem:/ {printf "%.1f", $4/$2*100}')
DISK_USAGE=$(df /x00 | tail -1 | awk '{print $5}')
NEIGHBOR_COUNT=$(batctl o | grep -v "No" | grep -c "^[0-9a-f]" || echo "0")

# WAN stats (gateway only)
if batctl gw | grep -q "server"; then
    WAN_STATUS=$(ping -c 3 -W 5 1.1.1.1 >/dev/null 2>&1 && echo "✅ Online" || echo "❌ Offline")
else
    WAN_STATUS="N/A (client)"
fi

# Bandwidth stats
BW_TODAY=$(vnstat -i bat0 -d | grep "today" | awk '{print $2" "$3}')

# Build report
REPORT="📊 *Daily Report - ${HOSTNAME}*

⏱ Uptime: ${UPTIME}
📈 Load: ${LOAD}
💾 Memory Free: ${MEM_FREE}%
💿 Disk Usage: ${DISK_USAGE}
🔗 Mesh Neighbors: ${NEIGHBOR_COUNT}
🌐 WAN: ${WAN_STATUS}
📡 Bandwidth (today): ${BW_TODAY}

_Generated: $(date)_"

# Send report
curl -s -X POST \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${REPORT}" \
    -d "parse_mode=Markdown" >/dev/null

# Add to cron: 0 8 * * * /usr/bin/daily-report.sh (8 AM daily)
```

### Log Analysis Alerts

Monitor logs for specific patterns:

```bash
#!/bin/sh
###############################################################################
# Log Analysis Alerting
###############################################################################

LOG_DIR="/x00/logs"
HOSTNAME=$(uci -q get system.@system[0].hostname || hostname)
TODAY=$(date +%Y-%m-%d)
LOG_FILE="${LOG_DIR}/${HOSTNAME}-${TODAY}.log"

# Check for errors in last capture
if [ -f "$LOG_FILE" ]; then
    # Count critical errors since last check (15 min)
    ERROR_COUNT=$(tail -100 "$LOG_FILE" | grep -cE "err|fail|crit" || echo "0")

    if [ "$ERROR_COUNT" -gt 10 ]; then
        # Extract error samples
        ERRORS=$(tail -100 "$LOG_FILE" | grep -E "err|fail|crit" | head -5)

        send_telegram "⚠️ *High Error Rate*

${ERROR_COUNT} errors in last 15 minutes

Sample errors:
\`\`\`
${ERRORS}
\`\`\`"
    fi

    # Check for specific critical events
    if tail -100 "$LOG_FILE" | grep -qi "out of memory"; then
        send_telegram "🚨 *OOM Event Detected!*

System is out of memory - possible crash imminent!"
    fi

    if tail -100 "$LOG_FILE" | grep -qi "batman.*disconnected"; then
        send_telegram "⚠️ *Mesh Topology Change*

Batman-adv reported disconnection event"
    fi
fi
```

---

## Tier 3: Advanced Monitoring (For Power Users) 🚀

**Goal:** Professional monitoring stack with dashboards and alerting.

### Option 1: Prometheus + Grafana

**Architecture:**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ OpenWrt     │────▶│ Prometheus  │────▶│  Grafana    │
│ Nodes (3x)  │     │ (on Pi/NAS) │     │ (Dashboard) │
│             │     │             │     │             │
│ collectd    │     │ Scrapes     │     │ Visualizes  │
│ + exporter  │     │ metrics     │     │ + Alerts    │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Setup:**

1. Install collectd-mod-prometheus on nodes (exports metrics)
2. Run Prometheus on external server to scrape nodes
3. Grafana for dashboards and alerting

**Pros:**

- ✅ Industry-standard monitoring
- ✅ Beautiful dashboards
- ✅ Powerful alerting
- ✅ Historical data retention

**Cons:**

- ❌ Complex setup
- ❌ Requires external infrastructure
- ❌ Overkill for 3-node mesh

### Option 2: LibreNMS

Full network monitoring system:

```bash
# Install on Ubuntu server/VM
curl https://raw.githubusercontent.com/librenms/librenms/master/install.sh | bash
```

**Features:**

- Auto-discovery of devices
- SNMP monitoring
- Alerting (email, Slack, webhook)
- Network maps
- Historical graphs

**Cons:**

- Heavy (requires server)
- Complex setup
- Way more than needed for 3 nodes

---

## My Recommended Setup (Best Balance) ✅

Based on your 3-node home mesh, here's what I recommend:

### **Tier 1: Essential Alerts (IMPLEMENT THIS)**

1. **On Each Node:**
   - Run alerting script (Telegram or email) every 15 minutes
   - Alert on: Disk full, no neighbors, low memory, high CPU

2. **On External Device (Optional but Recommended):**
   - Simple ping monitor (checks if nodes are reachable)
   - Sends alert if node offline for 5+ minutes

3. **Keep Existing Monitoring:**
   - ✅ Collectd + LuCI graphs (for viewing metrics)
   - ✅ Distributed syslog (for troubleshooting)
   - ✅ mesh-monitor.sh (for health checks)

### **Tier 2: Weekly Summary (Nice to Have)**

- Daily or weekly report via Telegram/email
- Shows uptime, bandwidth, neighbors, disk usage
- Runs at 8 AM daily via cron

### **Skip Tier 3 Unless:**

- You're managing 10+ nodes
- You need professional dashboards
- You have compliance requirements
- You enjoy complex monitoring setups

---

## Implementation Priority

### Week 1: Critical Alerts

```bash
1. Set up Telegram bot (5 minutes)
2. Deploy alert script to nodes (use playbook)
3. Test alerts (fill disk, stop batman, etc.)
4. Verify notifications working
```

### Week 2: External Monitoring

```bash
1. Set up ping monitor on Raspberry Pi/NAS
2. Add to cron (*/5 * * * *)
3. Test offline detection
```

### Week 3: Reports

```bash
1. Add daily report script
2. Schedule for 8 AM daily
3. Review first report
```

---

## Alert Tuning Guidelines

### Good Alerts (Actionable)

✅ **Disk > 95%** - Need to clean up logs
✅ **No neighbors for 10+ min** - Mesh broken, check hardware
✅ **Memory < 5MB** - System about to crash
✅ **Node offline 5+ min** - Hardware/network issue

### Bad Alerts (Noise)

❌ **CPU > 50%** - Normal during updates
❌ **Any error in logs** - Too sensitive
❌ **Neighbor count changed** - Normal mesh behavior
❌ **Bandwidth spike** - Expected during backups

### Alert Fatigue Prevention

1. **Use cooldown periods** (1 hour between duplicate alerts)
2. **Alert on sustained issues** (not momentary spikes)
3. **Combine related alerts** (one "node unhealthy" vs separate CPU/memory/disk)
4. **Test alert thresholds** (adjust based on false positives)

---

## Monitoring Checklist

Daily (Automated):

- [ ] All nodes pingable
- [ ] Mesh neighbors present
- [ ] Disk usage < 95%
- [ ] Memory free > 5MB

Weekly (Manual):

- [ ] Review graphs in LuCI
- [ ] Check bandwidth usage
- [ ] Review syslog for errors
- [ ] Verify backups working

Monthly (Manual):

- [ ] Update firmware if available
- [ ] Review long-term trends
- [ ] Clean old logs/data
- [ ] Test failover scenarios

---

## Cost Comparison

| Solution | Setup Time | Monthly Cost | Complexity |
|----------|------------|--------------|------------|
| **Telegram Alerts** | 30 min | $0 | Low |
| **Email Alerts** | 15 min | $0 | Low |
| **Uptime Kuma** | 2 hours | $0 (self-hosted) | Medium |
| **Prometheus + Grafana** | 8+ hours | $0 (self-hosted) | High |
| **Commercial (DataDog)** | 1 hour | $15+/month | Low |

**Recommendation:** Start with Telegram alerts ($0, 30 minutes setup)

---

## Next Steps

1. **Read this guide** ✅
2. **Choose alerting method** (Telegram, email, or webhook)
3. **Review implementation section** for your choice
4. **Set up test alerts** (manually trigger conditions)
5. **Deploy to production** (add to playbooks)
6. **Tune thresholds** (adjust based on false positives)
7. **Add external ping monitor** (optional but recommended)
8. **Schedule weekly reports** (optional)

---

## Support & Resources

- **Telegram Bot Guide:** https://core.telegram.org/bots
- **Pushover:** https://pushover.net/
- **Uptime Kuma:** https://github.com/louislam/uptime-kuma
- **Discord Webhooks:** https://support.discord.com/hc/en-us/articles/228383668
- **Prometheus on OpenWrt:** https://openwrt.org/docs/guide-user/perf_and_log/monitoring

---

## Summary

**For your 3-node mesh, implement:**

1. ✅ **Telegram bot alerts** (critical issues only)
   - Disk full, no neighbors, low memory, node offline
   - 15-minute checks, 1-hour cooldown

2. ✅ **External ping monitor** (optional but recommended)
   - Simple script on Raspberry Pi/NAS
   - Alerts if any node offline 5+ minutes

3. ✅ **Weekly summary reports** (nice to have)
   - Bandwidth, uptime, neighbors, disk usage
   - Sent every Monday at 8 AM

4. ✅ **Keep existing monitoring**
   - LuCI graphs for detailed analysis
   - Distributed syslog for troubleshooting
   - mesh-monitor.sh for health checks

**Skip:** Prometheus, Grafana, LibreNMS (overkill for 3 nodes)

**Result:** Professional monitoring without complexity!
