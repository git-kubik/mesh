# Security Hardening Guide

This document describes the security hardening measures implemented for the OpenWrt mesh network and how to use the security audit and validation tools.

## Overview

The security hardening implementation provides:

- **HTTPS/TLS**: Self-signed certificates for LuCI web interface
- **SSH Hardening**: Connection limits, timeouts, and security options
- **Rate Limiting**: Protection against brute force and flood attacks
- **Service Hardening**: Disable unnecessary services
- **Security Logging**: Local logging of security events
- **Validation**: Automated security posture checks

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Network Segmentation (VLANs, Zones)               │
│  Layer 2: Firewall Rules (Zone-based, Stateful)             │
│  Layer 3: Rate Limiting (SSH, ICMP, Connections)            │
│  Layer 4: Service Hardening (SSH, HTTP, Disabled Services)  │
│  Layer 5: Authentication (SSH Keys, Strong Passwords)       │
│  Layer 6: Encryption (WPA3/SAE Mesh, WPA2 Clients, HTTPS)   │
│  Layer 7: Monitoring & Validation (Logging, Audits)         │
└─────────────────────────────────────────────────────────────┘
```

### Current Security Posture

| Component | Status | Details |
|-----------|--------|---------|
| SSH Authentication | Strong | Key-only, no password auth |
| SSH Algorithms | Strong | Post-quantum support (sntrup761, mlkem768) |
| TLS/HTTPS | Strong | TLSv1.2/1.3, Grade A ciphers |
| Firewall | Strong | Zone-based with SYN flood protection |
| Wireless Mesh | Strong | WPA3-SAE encryption |
| Wireless Client | Good | WPA2-PSK with 802.11r |

## Configuration

### Environment Variables

All security settings can be configured via environment variables in `.env`:

```bash
# Master switch
SECURITY_HARDENING_ENABLED=true

# HTTPS/TLS
SECURITY_HTTPS_ENABLED=true
SECURITY_TLS_CERT_DAYS=3650
SECURITY_HTTP_REDIRECT_ENABLED=true

# SSH
SECURITY_SSH_MAX_AUTH_TRIES=3
SECURITY_SSH_LOGIN_GRACE_TIME=30
SECURITY_SSH_MAX_SESSIONS=5

# Rate Limiting
SECURITY_RATE_LIMIT_SSH=3          # per minute
SECURITY_RATE_LIMIT_ICMP=10        # per second

# Logging
SECURITY_SYSLOG_LOCAL_ENABLED=true
SECURITY_SYSLOG_REMOTE_ENABLED=false
SECURITY_SYSLOG_SERVER=            # IP:port for remote syslog
```

### Ansible Variables

Variables are defined in `group_vars/all.yml` under the "Security Hardening Configuration" section.

## Deployment

### Full Deployment

Security hardening is automatically applied during regular deployment:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml
```

### Security-Only Deployment

To apply only security hardening:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --tags security
```

### Skip Security Hardening

To skip security hardening:

```bash
SECURITY_HARDENING_ENABLED=false ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml
```

## Security Auditing

### Full Security Audit

Performs comprehensive security scanning of all nodes:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/security_audit.yml
```

Output includes:

- System information
- SSH configuration audit
- HTTPS/TLS configuration
- Firewall rules and zones
- Wireless security settings
- Running services
- Listening ports
- Network security (batman-adv BLA, ARP cache)

### Quick Security Check

Lightweight validation for regular use:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/security_check.yml
```

Checks:

- SSH security configuration
- Firewall running status
- HTTPS configuration
- Rate limiting
- Critical services
- Disabled services

### Single Node Audit

```bash
ansible-playbook -i inventory/hosts.yml playbooks/security_audit.yml --limit node1
```

## Security Components

### 1. HTTPS/TLS Configuration

Self-signed certificates are generated for each node:

- **Certificate Location**: `/etc/uhttpd.crt`, `/etc/uhttpd.key`
- **Validity**: 10 years (configurable)
- **Key Size**: 2048-bit RSA
- **HTTP Redirect**: Enabled by default

#### HTTP Security Headers Limitation

!!! warning "uhttpd Limitation"
    OpenWrt's built-in web server (uhttpd) does **not** support custom HTTP
    security headers. Headers like X-Frame-Options, Content-Security-Policy,
    and X-XSS-Protection cannot be added to responses.

**Why this matters:**

- **uhttpd** is a lightweight embedded web server designed for resource-constrained devices
- It lacks the extensibility of full-featured servers like nginx or Apache
- There is no supported mechanism to inject custom headers into responses

**Mitigation:**

The LuCI web interface is only accessible via:

1. **HTTPS** with TLS encryption (prevents eavesdropping)
2. **Management VLAN** (isolated from untrusted networks)
3. **Strong authentication** (password protection)

**Alternative (not implemented):**

For environments requiring HTTP security headers, you would need to:

1. Install nginx as a reverse proxy
2. Configure nginx to proxy requests to uhttpd
3. Add security headers in nginx configuration

This adds complexity and resource overhead not suitable for embedded devices.

### 2. SSH Hardening

Additional SSH security options beyond base configuration:

| Option | Value | Purpose |
|--------|-------|---------|
| LoginGraceTime | 30 | Disconnect after 30s if not authenticated |
| MaxAuthTries | 3 | Max authentication attempts |
| MaxSessions | 5 | Max concurrent sessions |
| ClientAliveInterval | 300 | Dead connection detection |
| ClientAliveCountMax | 2 | Disconnects after 2 missed keepalives |
| PermitEmptyPasswords | no | Block empty passwords |
| X11Forwarding | no | Disable X11 |
| AllowAgentForwarding | no | Disable agent forwarding |
| AllowTcpForwarding | no | Disable TCP forwarding |

### 3. Rate Limiting

iptables rules for attack prevention:

| Type | Limit | Purpose |
|------|-------|---------|
| SSH | 3/minute per IP | Brute force prevention |
| ICMP | 10/second | Ping flood prevention |

Rules are saved to `/etc/firewall.rate_limit` and included in firewall.

### 4. Service Hardening

Disabled services to reduce attack surface:

| Service | Reason |
|---------|--------|
| odhcpd | IPv6 DHCP not used |

Verified running services:

- sshd (OpenSSH)
- dnsmasq (DHCP/DNS)
- firewall

### 5. Security Logging

Local logging configuration:

- Log size: 128KB
- Buffer size: 64KB
- Firewall drop logging: Enabled (10/minute limit)
- Security monitor: `/usr/sbin/security-monitor.sh`

#### Future: Remote Syslog

Prepared for future remote syslog integration (Proxmox VM):

```bash
SECURITY_SYSLOG_REMOTE_ENABLED=true
SECURITY_SYSLOG_SERVER=10.11.10.50:514
```

## Troubleshooting

### Common Issues

#### Certificate Regeneration

To regenerate TLS certificates:

```bash
ssh root@10.11.12.1 "rm /etc/uhttpd.crt /etc/uhttpd.key"
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --tags security
```

#### Rate Limiting Issues

If legitimate connections are being blocked:

```bash
# Check current iptables rules
ssh root@10.11.12.1 "iptables -L INPUT -v -n"

# Temporarily disable rate limiting
ssh root@10.11.12.1 "iptables -F SSH_RATE_LIMIT"
```

#### SSH Lockout Recovery

If locked out due to SSH hardening:

1. Access via serial console
2. Edit `/etc/ssh/sshd_config` to revert settings
3. Restart sshd: `/etc/init.d/sshd restart`

### Security Report Location

Reports are saved to `/tmp/security-report-*.json` on each node.

## Maintenance

### Regular Security Checks

Schedule regular security checks using cron:

```bash
# Add to crontab
0 6 * * * cd /path/to/mesh && ansible-playbook -i inventory/hosts.yml playbooks/security_check.yml
```

### Package Updates

Check for security updates:

```bash
ssh root@10.11.12.1 "opkg update && opkg list-upgradable"
```

### Log Review

View security events:

```bash
ssh root@10.11.12.1 "logread | grep -E 'authpriv|dropbear|sshd|firewall'"
```

## Related Documentation

- [Network Architecture](../architecture/network-topology.md)
- [VLAN Architecture](../architecture/vlan-architecture.md)
- [SSH Keys Configuration](../deployment/ssh-keys.md)
- [Batman-adv Mesh](../architecture/batman-mesh.md)
