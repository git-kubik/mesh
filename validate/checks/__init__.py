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
"""

from validate.checks import batman, connectivity

__all__ = [
    "connectivity",
    "batman",
]
