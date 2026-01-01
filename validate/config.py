"""
Network configuration constants for validation framework.

Ported from tests/live/conftest.py for standalone use.
"""

import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class NodeInfo:
    """Information about a mesh node."""

    name: str
    ip: str
    node_num: int
    gw_mode: str  # "server" or "client"
    lan3_peer: str  # Node connected to LAN3
    lan4_peer: str  # Node connected to LAN4


# Node configuration matching the actual deployment
NODES: Dict[str, NodeInfo] = {
    "node1": NodeInfo(
        name="mesh-node1",
        ip="10.11.12.1",
        node_num=1,
        gw_mode="server",
        lan3_peer="node2",
        lan4_peer="node3",
    ),
    "node2": NodeInfo(
        name="mesh-node2",
        ip="10.11.12.2",
        node_num=2,
        gw_mode="server",
        lan3_peer="node1",
        lan4_peer="node3",
    ),
    "node3": NodeInfo(
        name="mesh-node3",
        ip="10.11.12.3",
        node_num=3,
        gw_mode="server",
        lan3_peer="node2",
        lan4_peer="node1",
    ),
}

# Network configuration
NETWORK_CONFIG = {
    "mesh_network": "10.11.12.0/24",
    "mesh_gateway": "10.11.12.1",
    "management_network": "10.11.10.0/24",
    "iot_network": "10.11.30.0/24",
    "guest_network": "10.11.20.0/24",
    "dns_servers": ["1.1.1.1", "8.8.8.8"],
}

# Source interface for reaching mesh nodes (VLAN 200)
# Set to None to use default routing, or specify interface name
MESH_SOURCE_INTERFACE = os.environ.get("MESH_SOURCE_INTERFACE", "enp5s0.200")

# VLAN configuration
VLANS = {
    "mesh": {"id": 100, "interfaces": ["lan3.100", "lan4.100"]},
    "client": {"id": 200, "network": "10.11.12.0/24"},
    "management": {"id": 10, "network": "10.11.10.0/24"},
    "iot": {"id": 30, "network": "10.11.30.0/24"},
    "guest": {"id": 20, "network": "10.11.20.0/24"},
}

# Switch configuration (management network)
SWITCHES = {
    "switch_a": {"ip": "10.11.10.11", "description": "Primary mesh switch"},
    "switch_b": {"ip": "10.11.10.12", "description": "Secondary mesh switch"},
    "switch_c": {"ip": "10.11.10.13", "description": "Infrastructure switch"},
}

# Validation thresholds
THRESHOLDS = {
    "ping_timeout_ms": 1000,
    "ssh_timeout_sec": 10,
    "min_neighbors": 2,
    "min_originators": 3,
    "min_gateways": 3,
    "max_latency_ms": 50,
    "max_packet_loss_pct": 5,
    "switch_response_timeout_ms": 200,
}


def get_ssh_key_path() -> str:
    """Get the SSH key path from environment or default."""
    path = os.environ.get("SSH_KEY_PATH", "~/.ssh/openwrt_mesh_rsa")
    return os.path.expanduser(path)
