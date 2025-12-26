"""
Network Validation Framework for OpenWrt Mesh Network.

Provides tiered validation of mesh network health:
- Tier 1 (smoke): Basic connectivity and batman module
- Tier 2 (standard): Mesh topology and VLANs
- Tier 3 (comprehensive): Security, services, performance

Usage:
    make validate           # Standard validation
    make validate-smoke     # Quick smoke test
    make validate-full      # Comprehensive validation
"""

__version__ = "1.0.0"
