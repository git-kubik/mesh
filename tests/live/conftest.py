"""
Fixtures for live network testing.

Provides SSH connections, node execution helpers, and network configuration.
"""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest


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
NODES = {
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
        gw_mode="server",  # All nodes are gateways in this deployment
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
    "guest_network": "10.11.30.0/24",
    "dns_servers": ["1.1.1.1", "8.8.8.8"],
    "mesh_ssid": "ha-mesh-net",
    "client_ssid": "HA-Network-5G",
    "management_ssid": "HA-Management",
    "guest_ssid": "HA-Guest",
}


def get_ssh_key_path() -> str:
    """Get the SSH key path from environment or default."""
    return os.environ.get("SSH_KEY_PATH", os.path.expanduser("~/.ssh/openwrt_mesh_rsa"))


def ssh_command(node_ip: str, command: str, timeout: int = 30) -> Tuple[int, str, str]:
    """
    Execute a command on a node via SSH.

    Args:
        node_ip: IP address of the node.
        command: Command to execute.
        timeout: Command timeout in seconds.

    Returns:
        Tuple of (return_code, stdout, stderr).
    """
    ssh_key = get_ssh_key_path()
    ssh_opts = [
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "BatchMode=yes",
        "-i",
        ssh_key,
    ]

    cmd = ["ssh", *ssh_opts, f"root@{node_ip}", command]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


def run_on_node(node: str, command: str, timeout: int = 30) -> Tuple[int, str, str]:
    """
    Execute a command on a named node.

    Args:
        node: Node name (node1, node2, node3).
        command: Command to execute.
        timeout: Command timeout in seconds.

    Returns:
        Tuple of (return_code, stdout, stderr).
    """
    node_info = NODES.get(node)
    if not node_info:
        return -1, "", f"Unknown node: {node}"
    return ssh_command(node_info.ip, command, timeout)


def run_local(command: str, timeout: int = 30) -> Tuple[int, str, str]:
    """
    Execute a command locally.

    Args:
        command: Command to execute (as shell string).
        timeout: Command timeout in seconds.

    Returns:
        Tuple of (return_code, stdout, stderr).
    """
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


@pytest.fixture(scope="session")
def nodes() -> Dict[str, NodeInfo]:
    """Provide node information dictionary."""
    return NODES


@pytest.fixture(scope="session")
def network_config() -> Dict[str, Any]:
    """Provide network configuration."""
    return NETWORK_CONFIG


@pytest.fixture(scope="session")
def node_ips() -> List[str]:
    """Provide list of node IP addresses."""
    return [NODES["node1"].ip, NODES["node2"].ip, NODES["node3"].ip]


@pytest.fixture(scope="session")
def ssh_key_path() -> str:
    """Provide SSH key path."""
    return get_ssh_key_path()


@pytest.fixture(scope="session")
def check_nodes_reachable(node_ips: List[str]) -> None:
    """
    Verify all nodes are reachable before running tests.

    Raises pytest.skip if any node is unreachable.
    """
    unreachable = []
    for ip in node_ips:
        rc, _, _ = run_local(f"ping -c 1 -W 2 {ip}")
        if rc != 0:
            unreachable.append(ip)

    if unreachable:
        pytest.skip(f"Nodes unreachable: {', '.join(unreachable)}")


@pytest.fixture(scope="session")
def check_ssh_access(node_ips: List[str], ssh_key_path: str) -> None:
    """
    Verify SSH access to all nodes before running tests.

    Raises pytest.skip if SSH access fails.
    """
    if not Path(ssh_key_path).exists():
        pytest.skip(f"SSH key not found: {ssh_key_path}")

    for ip in node_ips:
        rc, _, stderr = ssh_command(ip, "echo ok", timeout=10)
        if rc != 0:
            pytest.skip(f"SSH access failed to {ip}: {stderr}")


@pytest.fixture
def wlan2_interface() -> Optional[str]:
    """
    Get wlan2 interface name if available.

    Returns interface name or None if not available.
    """
    rc, stdout, _ = run_local("ip link show wlan2 2>/dev/null")
    if rc == 0 and "wlan2" in stdout:
        return "wlan2"
    return None


@pytest.fixture
def can_use_wlan2(wlan2_interface: Optional[str]) -> bool:
    """Check if wlan2 is available for testing."""
    return wlan2_interface is not None


# Helper class for test assertions
class NodeExecutor:
    """Helper class for executing commands on nodes."""

    def __init__(self, node: str):
        """Initialize with node name."""
        self.node = node
        self.node_info = NODES[node]

    def run(self, command: str, timeout: int = 30) -> Tuple[int, str, str]:
        """Execute command on this node."""
        return run_on_node(self.node, command, timeout)

    def run_ok(self, command: str, timeout: int = 30) -> str:
        """Execute command and assert success, return stdout."""
        rc, stdout, stderr = self.run(command, timeout)
        assert rc == 0, f"Command failed on {self.node}: {command}\nstderr: {stderr}"
        return stdout

    def batctl(self, args: str, timeout: int = 30) -> str:
        """Execute batctl command and return output."""
        return self.run_ok(f"batctl {args}", timeout)

    def uci_get(self, key: str) -> str:
        """Get UCI configuration value."""
        return self.run_ok(f"uci get {key}").strip()

    def ping(self, target: str, count: int = 3) -> bool:
        """Ping a target from this node."""
        rc, _, _ = self.run(f"ping -c {count} -W 2 {target}")
        return rc == 0


@pytest.fixture
def node1() -> NodeExecutor:
    """Provide executor for node1."""
    return NodeExecutor("node1")


@pytest.fixture
def node2() -> NodeExecutor:
    """Provide executor for node2."""
    return NodeExecutor("node2")


@pytest.fixture
def node3() -> NodeExecutor:
    """Provide executor for node3."""
    return NodeExecutor("node3")


@pytest.fixture
def all_node_executors() -> List[NodeExecutor]:
    """Provide executors for all nodes."""
    return [NodeExecutor("node1"), NodeExecutor("node2"), NodeExecutor("node3")]
