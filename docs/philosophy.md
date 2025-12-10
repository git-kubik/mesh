# Philosophy & Design Decisions

This document explains the "why" behind the technical decisions in this project. Understanding these rationales will help you make informed decisions when customizing or extending the mesh network.

## Project Goals

### What Problem Are We Solving?

Home and small office networks typically suffer from:

- **Single Point of Failure**: One router goes down, everything stops
- **Dead Zones**: WiFi coverage gaps that expensive extenders only partially fix
- **Vendor Lock-in**: Proprietary mesh systems that lock you into ecosystems
- **Limited Control**: Consumer routers hide configuration behind simplified UIs
- **Poor Observability**: No way to see what's happening in your network

### Our Solution

A **high-availability mesh network** that provides:

- **Redundancy**: No single point of failure (wired ring + wireless backup)
- **Coverage**: Multiple APs with seamless roaming
- **Open Source**: Full control, no vendor lock-in
- **Automation**: Repeatable deployments via Infrastructure as Code
- **Observability**: Comprehensive monitoring and logging

## Why Batman-adv?

We chose **Batman-adv** (Better Approach To Mobile Adhoc Networking - advanced) over other mesh routing protocols for several compelling reasons.

### Comparison with Alternatives

| Feature | Batman-adv | OLSR | Babel | 802.11s-only |
|---------|------------|------|-------|--------------|
| Layer | 2 (Ethernet) | 3 (IP) | 3 (IP) | 2 (WiFi only) |
| Multi-interface | Yes | Yes | Yes | No |
| Wired + Wireless | Yes | Yes | Yes | **No** |
| Protocol agnostic | Yes | No (IP only) | No (IP only) | No |
| Gateway selection | Built-in | External | External | None |
| Production proven | Freifunk, government | Limited | Academic | Limited |

### Key Advantages of Batman-adv

#### 1. Layer 2 Transparency

Batman-adv operates at Layer 2 (Ethernet), which means:

- **Any protocol works**: IPv4, IPv6, ARP, DHCP, mDNS - all work without changes
- **VLAN support**: Easy network segmentation
- **Bridge integration**: Works seamlessly with Linux bridges
- **No IP conflicts**: Nodes don't need IP addresses to route

#### 2. Multi-Interface Support

```
bat0 (Batman interface)
 ├── lan3.100 (wired to Switch A)
 ├── lan4.100 (wired to Switch B)
 └── mesh0   (802.11s wireless)
```

All interfaces contribute to the mesh simultaneously. If one fails, traffic automatically routes through others.

#### 3. Built-in Gateway Selection

Batman-adv includes intelligent gateway selection based on:

- **Declared bandwidth**: Nodes advertise their WAN speed
- **Link quality**: Measured throughput to gateway
- **Hop count**: Fewer hops = lower latency

No external scripts or routing daemons required.

#### 4. Production Proven

- **Freifunk**: 45,000+ nodes across German community networks
- **Government networks**: Used in critical infrastructure
- **10+ years**: Mature codebase with active development
- **Linux mainline**: In the kernel since 2011

### Why Not OLSR?

OLSR (Optimized Link State Routing) is Layer 3:

- Requires IP addresses assigned before routing works
- DHCP becomes complex (chicken-and-egg problem)
- VLANs require separate routing instances
- More complex to debug

### Why Not Babel?

Babel is modern and efficient, but:

- Layer 3 only (same issues as OLSR)
- Less tooling and documentation
- Smaller community
- No built-in gateway selection

### Why Not Pure 802.11s?

802.11s is WiFi-only:

- **No wired backup**: Single failure domain
- **Distance limited**: Wireless range only
- **Bandwidth limited**: Shared wireless medium
- **Half the throughput**: Same radio for mesh and clients

We **do use 802.11s** for the wireless backup link, but layer it under Batman-adv for unified routing.

## Why BATMAN_V Algorithm?

Batman-adv offers two routing algorithms: BATMAN_IV (legacy) and BATMAN_V (current). We use BATMAN_V.

### BATMAN_IV vs BATMAN_V

| Aspect | BATMAN_IV | BATMAN_V |
|--------|-----------|----------|
| Metric | TQ (Transmission Quality) | Throughput |
| Optimization | Packet loss | Bandwidth |
| Mixed interfaces | Same weight | Interface-aware |
| Resource usage | Lower | Slightly higher |

### Why BATMAN_V is Better for Our Use Case

1. **Throughput-based metric**: Prefers Gigabit wired links over 802.11s
2. **Interface-aware**: Knows that wired > wireless
3. **Better for mixed networks**: Our topology has both wired and wireless

```
With BATMAN_IV:
  Node1 → (wireless, TQ=200) → Node2 ✓ (might choose this!)
  Node1 → (wired, TQ=255) → Node2

With BATMAN_V:
  Node1 → (wireless, 100 Mbps) → Node2
  Node1 → (wired, 1000 Mbps) → Node2 ✓ (always chooses this)
```

## Why Ansible?

We use **Ansible** for configuration management instead of alternatives.

### Comparison with Alternatives

| Feature | Ansible | Salt | Puppet | Shell Scripts |
|---------|---------|------|--------|---------------|
| Agentless | Yes | No | No | Yes |
| Idempotent | Yes | Yes | Yes | No (manual) |
| Language | YAML | YAML/Jinja | Ruby DSL | Bash |
| Learning curve | Low | Medium | High | Low |
| OpenWrt support | Excellent | Poor | Poor | Manual |

### Key Advantages of Ansible

#### 1. Agentless Design

```
Control Machine → SSH → OpenWrt Node
```

No daemon running on routers means:

- **No memory overhead** on resource-constrained devices
- **No security surface** from running agents
- **No version conflicts** between agent and server
- **Works immediately** after SSH is configured

#### 2. Idempotent Operations

Running the same playbook twice produces the same result:

```yaml
# This is safe to run repeatedly
- name: Configure network
  template:
    src: network.j2
    dest: /etc/config/network
```

Benefits:

- **Safe to re-run**: Fix failed deploys by re-running
- **Drift correction**: Playbook restores expected state
- **Self-documenting**: Playbooks describe desired state

#### 3. Human-Readable YAML

```yaml
# Easy to read and review
- name: Install mesh packages
  opkg:
    name: "{{ item }}"
    state: present
  loop:
    - batman-adv
    - batctl
    - wpad-mesh-mbedtls
```

Compared to shell scripts:

```bash
# Harder to read, not idempotent
opkg install batman-adv batctl wpad-mesh-mbedtls
```

## Why Docker?

Deployment uses Docker containers for consistency and ease of use.

### Benefits of Containerization

#### 1. Reproducible Environment

```dockerfile
FROM python:3.11-alpine
RUN pip install ansible==8.0.0 paramiko==3.0.0
```

Everyone runs the exact same versions, regardless of their host OS.

#### 2. Semaphore Web UI

Docker enables Semaphore, a web interface for Ansible:

- **Non-technical users**: No command line required
- **Team collaboration**: Shared job history
- **Audit trail**: Who ran what, when
- **Scheduling**: Automated maintenance jobs

#### 3. Isolation from Host

- **No Python version conflicts**: Container has its own Python
- **No dependency pollution**: Host system unchanged
- **Easy cleanup**: Remove container, everything's gone

#### 4. Cross-Platform

Works identically on:

- Linux (native)
- macOS (Docker Desktop)
- Windows (Docker Desktop, WSL2)

## Design Principles

### 1. Idempotent

Every operation should be safe to re-run:

```bash
# Running twice produces same result
make deploy-node NODE=1
make deploy-node NODE=1  # No changes
```

### 2. Declarative

Define **what** you want, not **how** to get there:

```yaml
# Declarative (good)
wireless:
  channel: 6
  ssid: my-network

# Imperative (avoided)
# uci set wireless.radio0.channel=6
# uci set wireless.default_radio0.ssid=my-network
# uci commit wireless
# wifi reload
```

### 3. Environment-Driven

All configuration via `.env` file:

```bash
# Single source of truth
MESH_PASSWORD=SecurePassword123!
CLIENT_SSID=HA-Client
BATMAN_GW_BANDWIDTH=100000/100000
```

Benefits:

- **No secrets in code**: `.env` is gitignored
- **Easy customization**: Edit one file
- **Same playbooks for everyone**: Only `.env` differs

### 4. Testable

Comprehensive test suite validates:

- **Unit tests**: Template rendering, config parsing
- **Integration tests**: SSH connectivity, Ansible facts
- **Live tests**: Mesh topology, client connectivity
- **Failover tests**: Recovery from failures

```bash
make test          # Standard tests
make test-full     # Complete suite
make test-destructive  # Failover scenarios
```

## Security Model

### SSH Key Authentication

Password authentication disabled after initial setup:

```yaml
# Only SSH keys accepted
PermitRootLogin prohibit-password
PasswordAuthentication no
```

### WPA3 (SAE) for Mesh

The 2.4GHz mesh backbone uses WPA3-SAE:

- **No pre-shared key exchange**: Resistant to offline attacks
- **Forward secrecy**: Past traffic protected if key compromised
- **Protected management frames**: Prevents deauth attacks

### Network Segmentation

VLANs isolate traffic:

| VLAN | Network | Access |
|------|---------|--------|
| 100 | Mesh backbone | Nodes only |
| 200 | Clients | Internet, local services |
| 300 | IoT | Internet only, isolated |
| 10 | Management | Switches, node admin |

### No Secrets in Git

Sensitive data never committed:

```gitignore
# .gitignore
.env
*.pem
*.key
```

Use Ansible Vault for any secrets that must be version-controlled.

## Hardware Choice: D-Link DIR-1960 A1

### Why This Router?

| Feature | DIR-1960 A1 | Typical Consumer |
|---------|-------------|------------------|
| CPU | Qualcomm IPQ4019 | MediaTek MT7621 |
| RAM | 256 MB | 64-128 MB |
| Flash | 128 MB | 8-16 MB |
| Ethernet | 4x Gigabit | 4x 100M or Gig |
| WiFi | AC1900 (2.4+5GHz) | AC1200 |
| OpenWrt support | Excellent | Variable |
| Price | ~$50-80 used | $20-40 |

### Key Selection Criteria

1. **Qualcomm ath10k WiFi**: Best OpenWrt wireless driver
2. **256MB RAM**: Room for batman-adv, monitoring
3. **128MB Flash**: Space for packages, logs
4. **4 Gigabit ports**: 2 for mesh, 2 for clients
5. **Proven OpenWrt support**: No surprises

### Alternatives Considered

| Device | Pros | Cons |
|--------|------|------|
| GL.iNet B1300 | Compact, OpenWrt preinstalled | 2 ports only |
| Linksys EA8300 | Tri-band | More expensive |
| TP-Link Archer C7 | Cheap, proven | Only 100MB RAM |
| Ubiquiti UniFi | Enterprise features | Proprietary firmware |

## Summary

This project makes specific technical choices:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Mesh protocol | Batman-adv | Layer 2, multi-interface, proven |
| Routing algorithm | BATMAN_V | Throughput-based for mixed networks |
| Configuration management | Ansible | Agentless, idempotent, readable |
| Containerization | Docker | Reproducible, cross-platform |
| Hardware | DIR-1960 A1 | Balanced performance and cost |

These choices optimize for:

- **Reliability**: Redundancy at every layer
- **Simplicity**: Easy to understand and maintain
- **Flexibility**: Customizable for your needs
- **Openness**: No vendor lock-in

## Further Reading

- [Batman-adv Documentation](https://www.open-mesh.org/projects/batman-adv/wiki)
- [OpenWrt Project](https://openwrt.org/)
- [Ansible Documentation](https://docs.ansible.com/)
- [Freifunk Network](https://freifunk.net/en/)
