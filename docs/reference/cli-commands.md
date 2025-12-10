# CLI Commands Reference

This document provides a comprehensive reference for command-line tools used in OpenWrt mesh network administration.

## Batman-adv Commands (batctl)

The `batctl` utility is the primary tool for managing and debugging batman-adv mesh networks.

### Viewing Mesh Status

#### Originators (Routing Table)

```bash
batctl o
```

Shows all nodes in the mesh and their routing metrics:

```
   Originator        last-seen (#/255) Nexthop           [outgoingIF]
 * aa:bb:cc:dd:ee:01    0.040s   (255) aa:bb:cc:dd:ee:01 [  lan3.100]
   aa:bb:cc:dd:ee:02    0.500s   (220) aa:bb:cc:dd:ee:01 [  lan3.100]
```

| Column | Description |
|--------|-------------|
| `*` | Best route selected |
| `Originator` | MAC address of mesh node |
| `last-seen` | Time since last OGM received |
| `(#/255)` | TQ value (transmission quality) |
| `Nexthop` | Next hop MAC address |
| `[outgoingIF]` | Interface to use |

#### Neighbors

```bash
batctl n
```

Shows directly connected neighbors:

```
IF             Neighbor              last-seen
lan3.100       aa:bb:cc:dd:ee:01     0.040s
mesh0          aa:bb:cc:dd:ee:02     0.500s
```

#### Interfaces

```bash
batctl if
```

Shows interfaces attached to batman-adv:

```
lan3.100: active
lan4.100: active
mesh0: active
```

#### Gateway List

```bash
batctl gwl
```

Shows available gateways and their bandwidth:

```
  Router            ( TQ) Next Hop          [outgoingIF]  Bandwidth
* aa:bb:cc:dd:ee:01 (255) aa:bb:cc:dd:ee:01 [  lan3.100]: 100.0/100.0 MBit
```

#### Gateway Mode

```bash
batctl gw_mode
```

Shows current gateway mode: `server`, `client`, or `off`.

### Translation Tables

#### Local Clients

```bash
batctl tl
```

Shows clients connected to this node.

#### Global Clients

```bash
batctl tg
```

Shows all clients across the mesh.

### Debugging

#### Ping (Layer 2)

```bash
batctl ping <MAC-address>
```

Ping by MAC address through the mesh.

#### Traceroute

```bash
batctl traceroute <MAC-address>
```

Trace route to destination through mesh.

#### Statistics

```bash
batctl s
```

Shows batman-adv statistics.

### TQ Value Reference

| TQ Value | Quality | Action |
|----------|---------|--------|
| 255 | Perfect | No action needed |
| 200-254 | Good | Normal operation |
| 150-199 | Fair | Check for interference |
| 100-149 | Poor | Investigate link |
| < 100 | Bad | Fix immediately |

---

## UCI Configuration Commands

UCI (Unified Configuration Interface) is OpenWrt's configuration system.

### Viewing Configuration

```bash
# Show all of a config file
uci show network

# Show specific value
uci get network.lan.ipaddr

# Show in export format
uci export network

# Show uncommitted changes
uci changes
```

### Modifying Configuration

```bash
# Set a value
uci set network.lan.ipaddr='10.11.12.1'

# Add to a list
uci add_list dhcp.lan.dhcp_option='6,10.11.12.1'

# Delete a setting
uci delete network.wan

# Commit changes
uci commit network
```

### Common UCI Commands

| Command | Description |
|---------|-------------|
| `uci show <config>` | Display config in dot notation |
| `uci export <config>` | Display config in UCI format |
| `uci get <config>.<section>.<option>` | Get specific value |
| `uci set <config>.<section>.<option>=<value>` | Set value |
| `uci delete <config>.<section>` | Delete section |
| `uci add <config> <type>` | Add new section |
| `uci commit <config>` | Save changes |
| `uci revert <config>` | Discard changes |
| `uci changes` | Show pending changes |

### Configuration Files

| File | Purpose |
|------|---------|
| `/etc/config/network` | Network interfaces, VLANs |
| `/etc/config/wireless` | WiFi configuration |
| `/etc/config/dhcp` | DHCP server settings |
| `/etc/config/firewall` | Firewall zones and rules |
| `/etc/config/system` | Hostname, timezone |
| `/etc/config/dropbear` | Dropbear SSH settings |
| `/etc/config/luci` | LuCI web interface |

---

## Network Commands

### Interface Information

```bash
# List all interfaces (brief)
ip -br link show

# Show IP addresses
ip -br addr show

# Show specific interface
ip addr show bat0

# Interface statistics
ip -s link show bat0
```

### Routing

```bash
# Show routing table
ip route show

# Show default route
ip route show default

# Add static route
ip route add 192.168.100.0/24 via 10.11.12.1

# Show routing rules
ip rule show
```

### ARP/Neighbors

```bash
# Show ARP cache
ip neigh show

# Clear ARP cache
ip neigh flush all
```

### Bridge Commands

```bash
# Show bridge members
brctl show

# Show bridge MAC table
brctl showmacs br-lan

# Show STP status
brctl showstp br-lan
```

### Testing Connectivity

```bash
# Basic ping
ping -c 5 10.11.12.2

# Ping with specific interface
ping -I bat0 10.11.12.2

# MTU testing
ping -M do -s 1472 10.11.12.2

# Traceroute
traceroute -n 10.11.12.2

# Test specific port
nc -zv 10.11.12.2 22
```

---

## Wireless Commands (iw)

### Device Information

```bash
# List wireless devices
iw dev

# Radio information
iw phy phy0 info

# Current channel
iw dev wlan0 info
```

### Scanning

```bash
# Scan for networks (may briefly disrupt connections)
iw dev wlan0 scan | grep -E "(SSID|signal|freq)"
```

### Station Information

```bash
# Connected stations (AP mode)
iw dev wlan1 station dump

# Mesh peers (802.11s)
iw dev mesh0 station dump

# Survey data (noise, busy time)
iw dev wlan0 survey dump
```

### Signal Quality

```bash
# Check signal strength for a station
iw dev wlan1 station dump | grep signal
```

---

## Package Management (opkg)

### Querying Packages

```bash
# List installed packages
opkg list-installed

# Search for packages
opkg list | grep batman

# Show package info
opkg info batctl-full

# Check for upgrades
opkg list-upgradable
```

### Installing/Removing

```bash
# Update package lists
opkg update

# Install package
opkg install batctl-full

# Remove package
opkg remove batctl-full

# Install from URL
opkg install http://example.com/package.ipk
```

### Common Packages

| Package | Description |
|---------|-------------|
| `batctl-full` | Batman-adv control tool |
| `kmod-batman-adv` | Batman-adv kernel module |
| `wpad-mesh-mbedtls` | WiFi daemon with mesh support |
| `openssh-server` | OpenSSH server |
| `collectd` | Metrics collection |
| `vnstat` | Bandwidth monitoring |

---

## Service Management

### Init Scripts

```bash
# Start service
/etc/init.d/network start

# Stop service
/etc/init.d/network stop

# Restart service
/etc/init.d/network restart

# Reload configuration
/etc/init.d/network reload

# Enable at boot
/etc/init.d/network enable

# Disable at boot
/etc/init.d/network disable

# Check status
/etc/init.d/network status
```

### Common Services

| Service | Description |
|---------|-------------|
| `network` | Network interfaces |
| `wireless` | WiFi (via `wifi` command) |
| `firewall` | Firewall rules |
| `dnsmasq` | DHCP/DNS server |
| `sshd` | OpenSSH server |
| `dropbear` | Dropbear SSH server |
| `collectd` | Metrics collection |
| `vnstat` | Bandwidth tracking |
| `cron` | Scheduled tasks |

### WiFi Commands

```bash
# Reload wireless config
wifi reload

# Bring up all radios
wifi up

# Bring down all radios
wifi down

# Show wireless status
wifi status
```

---

## System Commands

### System Information

```bash
# OpenWrt version
cat /etc/openwrt_release

# Kernel version
uname -a

# System uptime
uptime

# Memory usage
free -m

# Disk usage
df -h

# CPU info
cat /proc/cpuinfo
```

### Logging

```bash
# View system log
logread

# Follow log (live)
logread -f

# Filter by service
logread | grep batman

# Kernel messages
dmesg

# Filter kernel errors
dmesg | grep -i error
```

### Process Management

```bash
# List processes
ps

# Top processes by CPU
top -b -n 1

# Find process by name
pgrep dnsmasq

# Kill process
kill <pid>
```

### Backup and Restore

```bash
# Create backup
sysupgrade -b /tmp/backup.tar.gz

# Restore backup
sysupgrade -r /tmp/backup.tar.gz

# Flash firmware (keep settings)
sysupgrade /tmp/firmware.bin

# Flash firmware (wipe settings)
sysupgrade -n /tmp/firmware.bin

# Factory reset
firstboot && reboot
```

---

## Firewall Commands

### nftables (Modern)

```bash
# List all rules
nft list ruleset

# List specific table
nft list table inet fw4

# Flush all rules (careful!)
nft flush ruleset
```

### iptables (Legacy)

```bash
# List filter rules
iptables -L -v -n

# List NAT rules
iptables -t nat -L -v -n

# Enable packet tracing
iptables -t raw -A PREROUTING -p icmp -j TRACE
```

---

## Diagnostic Script

Create a comprehensive diagnostic script:

```bash
#!/bin/sh
# Save as /tmp/diag.sh

echo "=== System ==="
cat /etc/openwrt_release | grep DISTRIB_DESCRIPTION
uptime
free -m | head -2

echo -e "\n=== Network ==="
ip -br addr show | grep -E "(bat0|br-lan)"
ip route show default

echo -e "\n=== Batman Mesh ==="
batctl if
echo "Neighbors: $(batctl n | wc -l)"
batctl gwl

echo -e "\n=== Wireless ==="
iw dev | grep -E "(Interface|ssid|channel)"

echo -e "\n=== Services ==="
for svc in network firewall dnsmasq sshd collectd; do
  /etc/init.d/$svc status 2>/dev/null || echo "$svc: not running"
done

echo -e "\n=== Recent Errors ==="
logread | grep -i error | tail -5
```

Run with:

```bash
sh /tmp/diag.sh
```

---

## Quick Reference Card

### Most Common Commands

| Task | Command |
|------|---------|
| View mesh nodes | `batctl o` |
| View neighbors | `batctl n` |
| View gateways | `batctl gwl` |
| View interfaces | `ip -br addr` |
| View routes | `ip route` |
| View logs | `logread` |
| Restart network | `/etc/init.d/network restart` |
| Reload wireless | `wifi reload` |
| Update packages | `opkg update` |
| System backup | `sysupgrade -b /tmp/backup.tar.gz` |

### Emergency Commands

| Situation | Command |
|-----------|---------|
| Network broken | `/etc/init.d/network restart` |
| Can't SSH | Serial console: 115200 8N1 |
| Factory reset | `firstboot && reboot` |
| Rollback config | `uci revert; /etc/init.d/network restart` |
