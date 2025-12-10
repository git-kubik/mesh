# Debugging Guide

This guide covers advanced debugging techniques for diagnosing mesh network issues.

## Batman-adv Debugging

### batctl Command Reference

The `batctl` utility is your primary tool for debugging the mesh.

#### View Mesh Participants

```bash
# Originators - all nodes in the mesh
batctl o
```

Output explanation:

```
   Originator        last-seen (#/255) Nexthop           [outgoingIF]
 * aa:bb:cc:dd:ee:01    0.040s   (255) aa:bb:cc:dd:ee:01 [  lan3.100]
   aa:bb:cc:dd:ee:02    0.500s   (220) aa:bb:cc:dd:ee:01 [  lan3.100]
```

- `*` = best path selected
- `(255)` = TQ (transmission quality) - higher is better
- `Nexthop` = next hop MAC for this destination

#### View Direct Neighbors

```bash
# Neighbors - directly connected nodes
batctl n
```

Output:

```
IF             Neighbor              last-seen
lan3.100       aa:bb:cc:dd:ee:01     0.040s
lan4.100       aa:bb:cc:dd:ee:03     0.120s
mesh0          aa:bb:cc:dd:ee:02     0.500s
```

#### View Gateways

```bash
# Gateway list
batctl gwl
```

Output:

```
  Router            ( TQ) Next Hop          [outgoingIF]  Bandwidth
* aa:bb:cc:dd:ee:01 (255) aa:bb:cc:dd:ee:01 [  lan3.100]: 100.0/100.0 MBit
  aa:bb:cc:dd:ee:02 (220) aa:bb:cc:dd:ee:01 [  lan3.100]:  50.0/50.0 MBit
```

#### Check Gateway Mode

```bash
# This node's gateway mode
batctl gw_mode
# Output: server (or client, or off)
```

#### View Mesh Interfaces

```bash
# Interfaces attached to batman
batctl if
```

Output:

```
lan3.100: active
lan4.100: active
mesh0: active
```

#### Ping Through Mesh

```bash
# Ping by MAC address (layer 2)
batctl ping aa:bb:cc:dd:ee:01
```

#### Trace Route Through Mesh

```bash
# Trace path to MAC
batctl traceroute aa:bb:cc:dd:ee:01
```

#### View Translation Table

```bash
# Local clients
batctl tl

# Global clients (across mesh)
batctl tg
```

#### View Mesh Statistics

```bash
# Statistics
batctl s
```

### Interpreting TQ Values

| TQ Value | Quality | Action |
|----------|---------|--------|
| 255 | Perfect | No action needed |
| 200-254 | Good | Normal operation |
| 150-199 | Fair | Check for interference |
| 100-149 | Poor | Investigate link |
| < 100 | Bad | Fix immediately |

### Common Batman-adv Issues

#### No Originators Visible

```bash
batctl o
# Empty output
```

**Causes**:

1. No interfaces attached: `batctl if` shows nothing
2. Physical connectivity issue
3. VLAN mismatch

**Debug**:

```bash
# Check interfaces
batctl if
ip link show | grep -E "(lan3|lan4|mesh)"

# Check for batman traffic
tcpdump -i lan3.100 ether proto 0x4305
```

#### Flapping TQ Values

**Causes**:

1. Wireless interference
2. Loose cable
3. Overloaded link

**Debug**:

```bash
# Watch TQ changes
watch -n 1 'batctl o'

# Check interface errors
ip -s link show lan3.100
```

## Network Debugging

### Interface Status

```bash
# All interfaces with statistics
ip -s link show

# Specific interface
ip -s link show lan3.100
```

Look for:

- `RX errors` - receiving problems
- `TX errors` - sending problems
- `dropped` - packets dropped

### IP Addressing

```bash
# All IP addresses
ip addr show

# Routing table
ip route show

# Default route
ip route show default
```

### ARP Table

```bash
# View ARP cache
ip neigh show

# Clear ARP cache
ip neigh flush all
```

### Bridge Status

```bash
# Bridge members
brctl show

# Bridge MAC table
brctl showmacs br-lan

# Bridge STP status
brctl showstp br-lan
```

### Packet Capture

```bash
# Capture on interface
tcpdump -i lan3.100 -n

# Capture specific protocol
tcpdump -i bat0 icmp

# Capture with VLAN tags visible
tcpdump -i lan3 -e

# Save to file for analysis
tcpdump -i bat0 -w /tmp/capture.pcap
```

### Connectivity Testing

```bash
# Basic ping
ping -c 5 10.11.12.2

# Ping with source interface
ping -I bat0 10.11.12.2

# Traceroute
traceroute -n 10.11.12.2

# MTU testing
ping -M do -s 1472 10.11.12.2
```

## Wireless Debugging

### Radio Information

```bash
# List wireless devices
iw dev

# Radio capabilities
iw phy phy0 info

# Current channel info
iw dev wlan0 info
```

### Scan for Networks

```bash
# Scan (may disrupt connections briefly)
iw dev wlan0 scan | grep -E "(SSID|signal|freq)"
```

### Connected Clients

```bash
# Station list (AP mode)
iw dev wlan1 station dump

# Mesh peers (802.11s)
iw dev mesh0 station dump
```

### Signal Quality

```bash
# Survey data (noise, busy time)
iw dev wlan0 survey dump
```

### Wireless Logs

```bash
# hostapd logs
logread | grep hostapd

# wpa_supplicant logs
logread | grep wpa
```

## UCI Debugging

### View Configuration

```bash
# Show all of a config file
uci show network

# Show specific value
uci get network.bat0.gw_mode

# Show uncommitted changes
uci changes
```

### Debug Configuration Issues

```bash
# Validate config syntax
uci show 2>&1 | grep -i error

# Compare running vs saved config
uci show network > /tmp/saved.txt
uci show network | diff /tmp/saved.txt -
```

### Reset to Defaults

```bash
# Reset specific config
uci revert network

# Full factory reset (DANGER!)
firstboot && reboot
```

## Log Analysis

### System Log

```bash
# Recent entries
logread | tail -50

# Filter by service
logread | grep batman
logread | grep dnsmasq
logread | grep hostapd

# Follow live
logread -f
```

### Kernel Log

```bash
# Kernel messages
dmesg | tail -50

# Filter errors
dmesg | grep -i error
```

### Log Timestamps

```bash
# With timestamps
logread -e
```

## Performance Debugging

### CPU Usage

```bash
# Top processes
top -b -n 1

# CPU by process
ps aux | sort -k3 -r | head
```

### Memory Usage

```bash
# Memory overview
free

# Detailed memory
cat /proc/meminfo
```

### Network Throughput

```bash
# Install iperf3 if not present
opkg install iperf3

# Server mode
iperf3 -s

# Client mode (from another node)
iperf3 -c 10.11.12.1

# Test both directions
iperf3 -c 10.11.12.1 --bidir
```

### Interface Statistics

```bash
# Real-time stats
watch -n 1 'ip -s link show bat0'

# Traffic on all interfaces
cat /proc/net/dev
```

## Firewall Debugging

### View Rules

```bash
# nftables (newer)
nft list ruleset

# iptables (legacy)
iptables -L -v -n
iptables -t nat -L -v -n
```

### Trace Packets

```bash
# Enable tracing
iptables -t raw -A PREROUTING -p icmp -j TRACE
iptables -t raw -A OUTPUT -p icmp -j TRACE

# View trace in logs
logread | grep TRACE

# Disable tracing
iptables -t raw -F
```

### Test Connectivity

```bash
# Test specific port
nc -zv 10.11.12.2 22

# Test through specific interface
curl --interface bat0 http://1.1.1.1
```

## Diagnostic Script

Create a comprehensive diagnostic script:

```bash
#!/bin/sh
# Save as /tmp/debug.sh and run

echo "=== System Info ==="
cat /etc/openwrt_release
uptime
free

echo -e "\n=== Network Interfaces ==="
ip link show

echo -e "\n=== IP Addresses ==="
ip addr show

echo -e "\n=== Routes ==="
ip route show

echo -e "\n=== Batman Interfaces ==="
batctl if

echo -e "\n=== Batman Neighbors ==="
batctl n

echo -e "\n=== Batman Originators ==="
batctl o

echo -e "\n=== Gateway List ==="
batctl gwl

echo -e "\n=== Bridge Status ==="
brctl show

echo -e "\n=== Wireless ==="
iw dev

echo -e "\n=== Recent Errors ==="
logread | grep -i error | tail -20
```

Run with:

```bash
sh /tmp/debug.sh > /tmp/debug-output.txt 2>&1
```

## Getting Help

When opening an issue, include:

1. **Output of debug script** (above)
2. **Specific error messages**
3. **Steps to reproduce**
4. **What you've already tried**
5. **Network diagram** if relevant
