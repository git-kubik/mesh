"""
Validation checks organized by category.

Categories:
- connectivity: Ping, SSH access
- batman: Module, interfaces, neighbors, originators, gateways
- vlans: VLAN configuration validation
- services: DHCP, firewall
- security: SSH hardening, HTTPS
- wan: Internet connectivity, DNS
- infrastructure: Switch reachability
- failover: Link, WAN, node failover
- wireless: 802.11s mesh, 802.11r roaming, BLA
- performance: Latency, stress testing
"""

from validate.checks import batman, connectivity, failover, performance, wireless

__all__ = [
    "connectivity",
    "batman",
    "failover",
    "wireless",
    "performance",
]
