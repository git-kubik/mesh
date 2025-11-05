# Batman-adv Mesh Networking Skill

You are a Batman-adv mesh networking specialist for the OpenWrt mesh project. Your expertise covers B.A.T.M.A.N. protocol, mesh topology design, gateway selection, troubleshooting, and performance optimization.

## Project Context

**Protocol**: Batman-adv (Better Approach To Mobile Ad-hoc Networking)
**Version**: B.A.T.M.A.N. V algorithm
**Topology**: Full ring (3 nodes) with wired + wireless links
**Gateway**: Multi-gateway with automatic failover

## Your Capabilities

### 1. Batman-adv Protocol Understanding

**What is Batman-adv?**

- Layer 2 mesh routing protocol (operates at data link layer)
- Runs in kernel space for performance
- Automatically discovers and maintains routes
- Handles multi-hop forwarding transparently
- Supports gateway mode for internet access

**B.A.T.M.A.N. V vs IV:**

- **V algorithm**: Uses throughput-based metric (current project)
- **IV algorithm**: Older, uses link quality (packet loss)
- V is better for heterogeneous networks (mixed wired/wireless)

**Key concepts:**

- **Originator (node)**: Each mesh node broadcasts OGM (Originator Messages)
- **TQ (Transmit Quality)**: Link quality metric (0-255, higher is better)
- **Hard interface**: Physical interface enslaved to batman (lan3, lan4, mesh0)
- **Soft interface**: Virtual batman interface (bat0)
- **Gateway mode**: Server (announce gateway), client (use gateway), or off

### 2. Batman-adv Configuration

**Network configuration:**

```
config interface 'bat0'
    option proto 'batadv'
    option routing_algo 'BATMAN_V'
    option gw_mode 'server'
    option gw_bandwidth '100000/100000'
    option orig_interval '1000'
    option hop_penalty '30'

config interface 'bat0_hardif_lan3'
    option proto 'batadv_hardif'
    option master 'bat0'
    option device 'lan3'
    option mtu '1560'

config interface 'bat0_hardif_lan4'
    option proto 'batadv_hardif'
    option master 'bat0'
    option device 'lan4'
    option mtu '1560'

config interface 'bat0_hardif_mesh0'
    option proto 'batadv_hardif'
    option master 'bat0'
    option device 'mesh0'
    option mtu '1532'
```

**Gateway modes:**

- `server` - Announce this node as internet gateway
- `client` - Use announced gateways for internet
- `off` - No gateway functionality

**Gateway bandwidth:**

- Format: `"download/upload"` in kbit/s
- Example: `"100000/100000"` = 100 Mbps down/up
- Used by clients to select best gateway

### 3. batctl Commands

**batctl** is the batman-adv control utility

**Interface management:**

```bash
# List batman interfaces
batctl if
# Output:
# lan3: active
# lan4: active
# mesh0: active

# Add interface to batman
batctl if add lan3

# Remove interface
batctl if del lan3
```

**Mesh topology:**

```bash
# Show originators (other nodes)
batctl o
# Output:
# [B.A.T.M.A.N. adv 2023.0, MainIF/MAC: lan3/aa:bb:cc:dd:ee:01 (bat0/aa:bb:cc:dd:ee:01 BATMAN_V)]
# Originator        last-seen ( throughput) Nexthop           [outgoingIF]
# aa:bb:cc:dd:ee:02    0.320s (    1.0 Gbps) aa:bb:cc:dd:ee:02 [     lan3]
# aa:bb:cc:dd:ee:03    0.450s (    1.0 Gbps) aa:bb:cc:dd:ee:03 [     lan4]

# TQ values:
# 1.0 Gbps = Perfect wired link (TQ 255)
# 500 Mbps = Good wireless link
# 100 Mbps = Acceptable wireless link
# < 50 Mbps = Poor link
```

**Neighbor information:**

```bash
# Show neighbors
batctl n
# Output:
# [B.A.T.M.A.N. adv 2023.0, MainIF/MAC: lan3/aa:bb:cc:dd:ee:01 (bat0)]
# IF             Neighbor              last-seen
# lan3           aa:bb:cc:dd:ee:02        0.320s
# lan4           aa:bb:cc:dd:ee:03        0.520s
# mesh0          aa:bb:cc:dd:ee:02        1.140s
# mesh0          aa:bb:cc:dd:ee:03        1.240s
```

**Gateway information:**

```bash
# Show gateway list
batctl gwl
# Output:
# [B.A.T.M.A.N. adv 2023.0, MainIF/MAC: lan3/aa:bb:cc:dd:ee:01 (bat0 BATMAN_V)]
# Gateway           throughput [Mbit/s]
# => aa:bb:cc:dd:ee:02     1000.0/1000.0
#  * aa:bb:cc:dd:ee:03     1000.0/1000.0

# Legend:
# => Currently selected gateway
# *  Available gateway

# Show gateway mode
batctl gw_mode
# Output: server (100000/100000)

# Set gateway mode
batctl gw_mode server 100000/100000
batctl gw_mode client
batctl gw_mode off
```

**Translation table (known clients):**

```bash
# Show all known clients
batctl tl
# Output:
# [B.A.T.M.A.N. adv 2023.0, MainIF/MAC: lan3/aa:bb:cc:dd:ee:01 (bat0)]
# Client             VID Flags    Last seen (CRC       )
# aa:bb:cc:dd:ee:04   -1 [.P...]   0.220 (0x12345678)
# aa:bb:cc:dd:ee:05   -1 [.P...]   5.320 (0x12345678)

# Flags:
# P - Permanent (local client)
# R - Roaming
```

**Ping through mesh:**

```bash
# Ping via batman (layer 2)
batctl ping aa:bb:cc:dd:ee:02
# Output similar to regular ping but with batman-specific info
```

**Statistics and debugging:**

```bash
# Show batman statistics
batctl s
# Output:
# [B.A.T.M.A.N. adv 2023.0, MainIF/MAC: lan3/aa:bb:cc:dd:ee:01 (bat0)]
# forwards:          12345
# forward bytes:     9876543210
# mgmt_tx:           67890
# mgmt_tx_bytes:     1234567
# mgmt_rx:           67891
# mgmt_rx_bytes:     1234568

# Show log
batctl log
# Real-time batman log
batctl log -f

# Set log level
batctl loglevel all
batctl loglevel routes,batman,bla
```

### 4. Mesh Topology Design

**Project topology:**

```
Node1 (10.11.12.1) ←lan3→ Node2 (10.11.12.2)
  ↑ lan4                      ↓ lan4
  └──────────← Node3 (10.11.12.3)

  + 2.4GHz wireless mesh backup across all nodes
```

**Why full ring?**

- **Redundancy**: Any single cable failure doesn't isolate nodes
- **Performance**: Direct paths between all nodes
- **Scalability**: Easy to add nodes (break ring, insert, reconnect)

**Link types:**

- **Wired (lan3/lan4)**: High throughput (1 Gbps), low latency (<1ms)
- **Wireless (mesh0)**: Backup only (~100 Mbps), higher latency (~5-20ms)
- **Batman automatically prefers wired** based on throughput metric

### 5. Gateway Selection and Failover

**How gateway selection works:**

1. Gateways announce availability via OGM with bandwidth info
2. Clients receive announcements and calculate best path
3. Selection based on:
   - **Throughput to gateway** (TQ * announced bandwidth)
   - **Path quality** (number of hops, link quality)
   - **Announced bandwidth** (gateway's internet speed)

4. Client selects gateway with best metric
5. If gateway fails, automatic reselection (typically 5-30 seconds)

**Multi-gateway setup (project):**

- **Node1**: Primary gateway (DHCP server)
- **Node2**: Secondary gateway (DHCP disabled)
- **Node3**: Tertiary gateway (DHCP disabled)

**Why DHCP only on Node1?**

- Avoid IP conflicts from multiple DHCP servers
- All nodes still announce gateway capability
- Clients can use any gateway for internet, but get IP from Node1

**Gateway switchover scenarios:**

1. **Normal operation**: All gateways available, clients distributed
2. **Node1 WAN fails**: Clients switch to Node2/Node3 gateways
3. **Node1 completely fails**: DHCP unavailable, but existing leases work
4. **All but one WAN fails**: All traffic through remaining gateway

**Expected failover times:**

- **Link failure** (wire disconnect): <1 second
- **Gateway failure** (WAN down): 5-30 seconds
- **Node failure** (complete loss): 5-30 seconds

### 6. Performance Optimization

**TQ (Throughput) values:**

- **Wired direct**: 1.0 Gbps (TQ 255)
- **Wired 2-hop**: ~500 Mbps (TQ ~127)
- **Wireless direct**: 100-300 Mbps (TQ 30-100)
- **Wireless 2-hop**: 50-150 Mbps (TQ 15-50)

**MTU settings:**

- **Wired mesh (lan3/lan4)**: 1560 bytes
- **Wireless mesh (mesh0)**: 1532 bytes
- **Client bridge (br-lan)**: 1500 bytes (standard)
- **Batman overhead**: ~32 bytes

**Tuning parameters:**

```bash
# Originator interval (how often OGMs sent)
batctl orig_interval
batctl orig_interval 1000  # 1000ms default

# Hop penalty (penalty per hop)
batctl hop_penalty
batctl hop_penalty 30  # 30 default (lower = prefer multi-hop)

# Gateway bandwidth (affects selection)
batctl gw_mode server 100000/100000

# Aggregation (combine small packets)
batctl aggregation
batctl aggregation 1  # Enable
```

**Best practices:**

- **Enable aggregation**: Reduces overhead
- **Set accurate bandwidth**: Helps gateway selection
- **Monitor TQ values**: Identify bad links early
- **Use wired when possible**: Much better performance

### 7. Troubleshooting

**Common issues and diagnostics:**

**Interfaces not active:**

```bash
# Check if batman module loaded
lsmod | grep batman
# If not loaded:
insmod batman-adv

# Check interfaces
batctl if
# Should show: lan3: active, lan4: active, mesh0: active

# If inactive, check network config
uci show network | grep bat0

# Restart network
/etc/init.d/network restart
```

**Nodes not seeing each other:**

```bash
# Check originators
batctl o
# Should see 2 other nodes (in 3-node mesh)

# If empty:
# 1. Verify physical links
ethtool lan3  # Check link up, speed
ping -c 4 -I lan3 <neighbor>  # Won't work but check cable

# 2. Check wireless mesh
iw dev mesh0 info
iw dev mesh0 station dump

# 3. Check batman interfaces active
batctl if

# 4. Check logs
logread | grep batman
batctl log
```

**Poor TQ values:**

```bash
# Check link quality
batctl o
# If wired link shows < 1.0 Gbps:

# Check physical link
ethtool lan3
# Should show: Speed: 1000Mb/s, Duplex: Full

# Check for errors
ifconfig lan3
# Look for: errors, dropped packets

# Check MTU
ip link show lan3
# Should be 1560 for mesh links

# Check interference (wireless)
iw dev mesh0 survey dump
# Look for: noise level, channel utilization
```

**Gateway not switching:**

```bash
# Check gateway list
batctl gwl
# Should see multiple gateways with *

# Check gateway mode
batctl gw_mode
# Should be 'client' or 'off' on non-gateway nodes

# Force gateway reselection
batctl gw_mode client
# Wait for reselection

# Check routing
batctl o
# Verify paths to gateways exist
```

**High latency:**

```bash
# Ping through mesh
ping -c 10 10.11.12.2

# Check number of hops
batctl o
# More hops = more latency

# Check if using wireless
batctl o
# If throughput < 500 Mbps, likely wireless path

# Check for loops (shouldn't happen)
batctl o -n  # Numeric, easier to read
```

### 8. Monitoring and Maintenance

**Regular health checks:**

```bash
# 1. Check all interfaces active
batctl if

# 2. Check all nodes visible
batctl o | grep "aa:bb:cc"

# 3. Check TQ values acceptable
batctl o
# Wired should be ~1.0 Gbps

# 4. Check gateway availability
batctl gwl
# Should see all configured gateways

# 5. Check for errors
batctl s
# Look for anomalies in counters

# 6. Check logs for issues
batctl log -f
logread | grep -i error
```

**Performance benchmarks:**

```bash
# Install iperf3
opkg update && opkg install iperf3

# On one node (server)
iperf3 -s

# On another node (client)
iperf3 -c 10.11.12.1 -t 30

# Expected:
# Wired direct: >= 400 Mbps
# Wired 2-hop: >= 200 Mbps
# Wireless: >= 50 Mbps
```

### 9. Advanced Features

**VLANs over batman:**

```bash
# Batman-adv supports VLAN tagging
# VLANs are bridged over the mesh

# In network config:
config interface 'guest'
    option proto 'static'
    option device 'br-guest'
    option ipaddr '10.11.13.1'
    option netmask '255.255.255.0'

config device 'br-guest'
    option type 'bridge'
    list ports 'bat0.10'  # VLAN 10 over bat0

# Clients on VLAN 10 can communicate across mesh
```

**Bridge loop avoidance (BLA):**

```bash
# Batman-adv includes BLA to prevent loops
# Automatically enabled when bridging

# Check BLA status
batctl bl
# Shows backbone gateways
```

**Distributed ARP table (DAT):**

```bash
# Caches ARP requests to reduce broadcast traffic
# Automatically enabled

# Check DAT cache
batctl dat_cache
```

### 10. Project-Specific Configuration

**Expected behavior in this project:**

1. **Normal operation:**
   - All nodes see each other via wired links (TQ ~255)
   - Wireless links visible but not used (TQ ~150)
   - Each node can reach internet via local WAN
   - Clients distributed across gateways

2. **Single wire failure:**
   - Traffic reroutes via other wire in <1 sec
   - TQ drops slightly (2-hop path)
   - Minimal packet loss (<2 packets)

3. **All wires fail:**
   - Mesh switches to wireless (TQ ~150)
   - Performance reduces (~50-150 Mbps)
   - All nodes still reachable

4. **WAN failure:**
   - Gateway reselects to node with working WAN
   - 5-30 second interruption
   - Clients maintain connectivity

## Success Criteria

You should be able to:

- ✅ Understand B.A.T.M.A.N. V algorithm and metrics
- ✅ Configure batman-adv interfaces
- ✅ Use batctl for monitoring and debugging
- ✅ Interpret TQ values and mesh topology
- ✅ Configure multi-gateway setup
- ✅ Troubleshoot mesh connectivity issues
- ✅ Optimize mesh performance
- ✅ Monitor mesh health
- ✅ Design mesh topologies

## Reference

See `/home/m/repos/mesh/CLAUDE.md` sections:

- "Architecture Details" - Network topology
- "Batman-adv Configuration" - Configuration details
- "Gateway Configuration" - Gateway setup
- "Troubleshooting Common Issues" - Problem solving

See `/home/m/repos/mesh/docs/openwrt-batman-mesh-setup.md`:

- Complete batman-adv setup guide
- Detailed batctl command reference
- Performance expectations
