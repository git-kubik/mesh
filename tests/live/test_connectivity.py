"""
Live connectivity tests for mesh network.

Tests basic connectivity between all nodes and to external services.
"""

import re

import pytest

from .conftest import NODES, NodeExecutor, run_local


def parse_ping_stats(stdout: str) -> tuple[int, int, float]:
    """Parse ping output to extract transmitted, received, and loss percentage.

    Returns:
        Tuple of (transmitted, received, loss_percent)
    """
    match = re.search(r"(\d+) packets transmitted, (\d+) received", stdout)
    if match:
        transmitted = int(match.group(1))
        received = int(match.group(2))
        loss = ((transmitted - received) / transmitted) * 100 if transmitted > 0 else 100.0
        return transmitted, received, loss
    return 0, 0, 100.0


@pytest.mark.live
class TestNodeReachability:
    """Test that all nodes are reachable from the test machine."""

    def test_ping_node1(self) -> None:
        """Test ping to node1 - allows up to 50% packet loss."""
        rc, stdout, _ = run_local(f"ping -c 3 -W 2 {NODES['node1'].ip}")
        transmitted, received, loss = parse_ping_stats(stdout)
        assert received >= 1, f"Cannot ping node1 at {NODES['node1'].ip} (0/{transmitted} received)"
        assert loss <= 50, f"High packet loss to node1: {loss:.1f}%"

    def test_ping_node2(self) -> None:
        """Test ping to node2 - allows up to 50% packet loss."""
        rc, stdout, _ = run_local(f"ping -c 3 -W 2 {NODES['node2'].ip}")
        transmitted, received, loss = parse_ping_stats(stdout)
        assert received >= 1, f"Cannot ping node2 at {NODES['node2'].ip} (0/{transmitted} received)"
        assert loss <= 50, f"High packet loss to node2: {loss:.1f}%"

    def test_ping_node3(self) -> None:
        """Test ping to node3 - allows up to 50% packet loss."""
        rc, stdout, _ = run_local(f"ping -c 3 -W 2 {NODES['node3'].ip}")
        transmitted, received, loss = parse_ping_stats(stdout)
        assert received >= 1, f"Cannot ping node3 at {NODES['node3'].ip} (0/{transmitted} received)"
        assert loss <= 50, f"High packet loss to node3: {loss:.1f}%"


@pytest.mark.live
class TestSSHAccess:
    """Test SSH access to all nodes."""

    def test_ssh_node1(self, node1: NodeExecutor) -> None:
        """Test SSH access to node1."""
        output = node1.run_ok("echo 'SSH OK'")
        assert "SSH OK" in output

    def test_ssh_node2(self, node2: NodeExecutor) -> None:
        """Test SSH access to node2."""
        output = node2.run_ok("echo 'SSH OK'")
        assert "SSH OK" in output

    def test_ssh_node3(self, node3: NodeExecutor) -> None:
        """Test SSH access to node3."""
        output = node3.run_ok("echo 'SSH OK'")
        assert "SSH OK" in output

    def test_hostname_node1(self, node1: NodeExecutor) -> None:
        """Verify node1 hostname is correct."""
        hostname = node1.run_ok("uci get system.@system[0].hostname").strip()
        assert hostname == "mesh-node1"

    def test_hostname_node2(self, node2: NodeExecutor) -> None:
        """Verify node2 hostname is correct."""
        hostname = node2.run_ok("uci get system.@system[0].hostname").strip()
        assert hostname == "mesh-node2"

    def test_hostname_node3(self, node3: NodeExecutor) -> None:
        """Verify node3 hostname is correct."""
        hostname = node3.run_ok("uci get system.@system[0].hostname").strip()
        assert hostname == "mesh-node3"


@pytest.mark.live
class TestInterNodeConnectivity:
    """Test connectivity between mesh nodes."""

    def test_node1_can_ping_node2(self, node1: NodeExecutor) -> None:
        """Test node1 can ping node2."""
        assert node1.ping(NODES["node2"].ip), "node1 cannot ping node2"

    def test_node1_can_ping_node3(self, node1: NodeExecutor) -> None:
        """Test node1 can ping node3."""
        assert node1.ping(NODES["node3"].ip), "node1 cannot ping node3"

    def test_node2_can_ping_node1(self, node2: NodeExecutor) -> None:
        """Test node2 can ping node1."""
        assert node2.ping(NODES["node1"].ip), "node2 cannot ping node1"

    def test_node2_can_ping_node3(self, node2: NodeExecutor) -> None:
        """Test node2 can ping node3."""
        assert node2.ping(NODES["node3"].ip), "node2 cannot ping node3"

    def test_node3_can_ping_node1(self, node3: NodeExecutor) -> None:
        """Test node3 can ping node1."""
        assert node3.ping(NODES["node1"].ip), "node3 cannot ping node1"

    def test_node3_can_ping_node2(self, node3: NodeExecutor) -> None:
        """Test node3 can ping node2."""
        assert node3.ping(NODES["node2"].ip), "node3 cannot ping node2"

    def test_full_mesh_connectivity(self, all_node_executors: list[NodeExecutor]) -> None:
        """Test all nodes can reach all other nodes."""
        for executor in all_node_executors:
            for node_name, node_info in NODES.items():
                if node_info.ip != executor.node_info.ip:
                    assert executor.ping(node_info.ip), f"{executor.node} cannot ping {node_name}"


@pytest.mark.live
class TestInternetConnectivity:
    """Test internet connectivity from all nodes."""

    def test_node1_internet_ping(self, node1: NodeExecutor) -> None:
        """Test node1 can reach internet (ping 1.1.1.1)."""
        assert node1.ping("1.1.1.1"), "node1 cannot reach internet"

    def test_node2_internet_ping(self, node2: NodeExecutor) -> None:
        """Test node2 can reach internet (ping 1.1.1.1)."""
        assert node2.ping("1.1.1.1"), "node2 cannot reach internet"

    def test_node3_internet_ping(self, node3: NodeExecutor) -> None:
        """Test node3 can reach internet (ping 1.1.1.1)."""
        assert node3.ping("1.1.1.1"), "node3 cannot reach internet"

    def test_node1_dns_resolution(self, node1: NodeExecutor) -> None:
        """Test node1 can resolve DNS."""
        rc, stdout, _ = node1.run("nslookup google.com")
        assert rc == 0, "node1 DNS resolution failed"
        assert "Address" in stdout

    def test_node2_dns_resolution(self, node2: NodeExecutor) -> None:
        """Test node2 can resolve DNS."""
        rc, stdout, _ = node2.run("nslookup google.com")
        assert rc == 0, "node2 DNS resolution failed"
        assert "Address" in stdout

    def test_node3_dns_resolution(self, node3: NodeExecutor) -> None:
        """Test node3 can resolve DNS."""
        rc, stdout, _ = node3.run("nslookup google.com")
        assert rc == 0, "node3 DNS resolution failed"
        assert "Address" in stdout
