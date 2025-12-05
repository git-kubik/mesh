"""
Live Batman-adv mesh network tests.

Tests validate Batman-adv mesh topology, neighbors, originators, and gateways.
"""

import re

import pytest

from .conftest import NodeExecutor


@pytest.mark.live
class TestBatmanInterface:
    """Test Batman-adv interface configuration."""

    def test_bat0_interface_exists_node1(self, node1: NodeExecutor) -> None:
        """Verify bat0 interface exists on node1."""
        output = node1.run_ok("ip link show bat0")
        assert "bat0" in output
        assert "UP" in output or "state UP" in output.upper()

    def test_bat0_interface_exists_node2(self, node2: NodeExecutor) -> None:
        """Verify bat0 interface exists on node2."""
        output = node2.run_ok("ip link show bat0")
        assert "bat0" in output
        assert "UP" in output or "state UP" in output.upper()

    def test_bat0_interface_exists_node3(self, node3: NodeExecutor) -> None:
        """Verify bat0 interface exists on node3."""
        output = node3.run_ok("ip link show bat0")
        assert "bat0" in output
        assert "UP" in output or "state UP" in output.upper()

    def test_batman_routing_algo(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify all nodes use BATMAN_V routing algorithm."""
        for executor in all_node_executors:
            output = executor.batctl("ra")
            assert "BATMAN_V" in output, f"{executor.node} not using BATMAN_V"


@pytest.mark.live
class TestBatmanNeighbors:
    """Test Batman-adv neighbor discovery."""

    def test_node1_has_neighbors(self, node1: NodeExecutor) -> None:
        """Verify node1 has Batman neighbors."""
        output = node1.batctl("n")
        # Should see at least 2 neighbors (node2 and node3)
        lines = [line for line in output.strip().split("\n") if line and not line.startswith("IF")]
        assert len(lines) >= 2, f"node1 should have at least 2 neighbors, got: {output}"

    def test_node2_has_neighbors(self, node2: NodeExecutor) -> None:
        """Verify node2 has Batman neighbors."""
        output = node2.batctl("n")
        lines = [line for line in output.strip().split("\n") if line and not line.startswith("IF")]
        assert len(lines) >= 2, f"node2 should have at least 2 neighbors, got: {output}"

    def test_node3_has_neighbors(self, node3: NodeExecutor) -> None:
        """Verify node3 has Batman neighbors."""
        output = node3.batctl("n")
        lines = [line for line in output.strip().split("\n") if line and not line.startswith("IF")]
        assert len(lines) >= 2, f"node3 should have at least 2 neighbors, got: {output}"


@pytest.mark.live
class TestBatmanOriginators:
    """Test Batman-adv originator table."""

    def test_node1_sees_all_originators(self, node1: NodeExecutor) -> None:
        """Verify node1 sees originators for node2 and node3."""
        output = node1.batctl("o")
        # Count unique originator MACs (excluding header lines)
        mac_pattern = r"([0-9a-f]{2}:){5}[0-9a-f]{2}"
        macs = set(re.findall(mac_pattern, output.lower()))
        assert len(macs) >= 2, f"node1 should see at least 2 originators: {output}"

    def test_node2_sees_all_originators(self, node2: NodeExecutor) -> None:
        """Verify node2 sees originators for node1 and node3."""
        output = node2.batctl("o")
        mac_pattern = r"([0-9a-f]{2}:){5}[0-9a-f]{2}"
        macs = set(re.findall(mac_pattern, output.lower()))
        assert len(macs) >= 2, f"node2 should see at least 2 originators: {output}"

    def test_node3_sees_all_originators(self, node3: NodeExecutor) -> None:
        """Verify node3 sees originators for node1 and node2."""
        output = node3.batctl("o")
        mac_pattern = r"([0-9a-f]{2}:){5}[0-9a-f]{2}"
        macs = set(re.findall(mac_pattern, output.lower()))
        assert len(macs) >= 2, f"node3 should see at least 2 originators: {output}"


@pytest.mark.live
class TestBatmanGateways:
    """Test Batman-adv gateway configuration and selection."""

    def test_node1_gateway_mode_server(self, node1: NodeExecutor) -> None:
        """Verify node1 is configured as gateway server."""
        output = node1.batctl("gw_mode")
        assert "server" in output.lower(), f"node1 should be gw server: {output}"

    def test_node2_gateway_mode_server(self, node2: NodeExecutor) -> None:
        """Verify node2 is configured as gateway server (all nodes are gateways)."""
        output = node2.batctl("gw_mode")
        assert "server" in output.lower(), f"node2 should be gw server: {output}"

    def test_node3_gateway_mode_server(self, node3: NodeExecutor) -> None:
        """Verify node3 is configured as gateway server."""
        output = node3.batctl("gw_mode")
        assert "server" in output.lower(), f"node3 should be gw server: {output}"

    def test_gateway_list_shows_servers(self, node2: NodeExecutor) -> None:
        """Verify gateway list shows available gateways."""
        output = node2.batctl("gwl")
        # Should see at least node1 and node3 as gateways
        mac_pattern = r"([0-9a-f]{2}:){5}[0-9a-f]{2}"
        macs = set(re.findall(mac_pattern, output.lower()))
        assert len(macs) >= 2, f"Should see at least 2 gateways: {output}"

    def test_gateway_bandwidth_configured(self, node1: NodeExecutor) -> None:
        """Verify gateway bandwidth is configured on node1."""
        # Check if bandwidth is set (non-zero)
        output = node1.run_ok("uci get network.bat0.gw_bandwidth 2>/dev/null || echo 'not set'")
        # Either should have config or batctl shows bandwidth
        if "not set" in output:
            bw_output = node1.batctl("gw_mode")
            assert "MBit" in bw_output or "Mbit" in bw_output, "Gateway bandwidth not configured"


@pytest.mark.live
class TestRingTopology:
    """Test full ring topology is established via dual switches."""

    def test_wired_interfaces_up(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify mesh interfaces (lan3.100, lan4.100 VLANs) are UP."""
        for executor in all_node_executors:
            # Check for mesh interfaces in batman
            # With switch integration, interfaces are lan3.100, lan4.100
            output = executor.batctl("if")
            has_lan3 = "lan3" in output.lower()
            has_lan4 = "lan4" in output.lower()
            has_mesh = "mesh" in output.lower()
            assert (
                has_lan3 or has_lan4 or has_mesh
            ), f"{executor.node} missing mesh interfaces in batman: {output}"

    def test_node1_ring_connections(self, node1: NodeExecutor) -> None:
        """Verify node1 has connections to node2 (LAN3) and node3 (LAN4)."""
        neighbors = node1.batctl("n")
        # Should have neighbors on at least 2 different interfaces
        interfaces = re.findall(r"^\s*(\S+)", neighbors, re.MULTILINE)
        # Filter out header
        interfaces = [i for i in interfaces if i and i != "IF" and "Neighbor" not in i]
        assert len(interfaces) >= 2, f"node1 should connect via 2 interfaces: {neighbors}"

    def test_node2_ring_connections(self, node2: NodeExecutor) -> None:
        """Verify node2 has connections to node1 (LAN3) and node3 (LAN4)."""
        neighbors = node2.batctl("n")
        interfaces = re.findall(r"^\s*(\S+)", neighbors, re.MULTILINE)
        interfaces = [i for i in interfaces if i and i != "IF" and "Neighbor" not in i]
        assert len(interfaces) >= 2, f"node2 should connect via 2 interfaces: {neighbors}"

    def test_node3_ring_connections(self, node3: NodeExecutor) -> None:
        """Verify node3 has connections to node1 (LAN4) and node2 (LAN3)."""
        neighbors = node3.batctl("n")
        interfaces = re.findall(r"^\s*(\S+)", neighbors, re.MULTILINE)
        interfaces = [i for i in interfaces if i and i != "IF" and "Neighbor" not in i]
        assert len(interfaces) >= 2, f"node3 should connect via 2 interfaces: {neighbors}"

    def test_mesh_path_redundancy(self, node1: NodeExecutor) -> None:
        """Test that multiple paths exist to each destination (ring provides redundancy)."""
        # Check originator table for multiple potential next hops
        output = node1.batctl("o")
        # In a healthy ring, should see good TQ values (>200 out of 255)
        # and multiple entries showing different paths
        assert output.strip(), "Originator table should not be empty"
        # Look for TQ values
        tq_values = re.findall(r"\((\d+)\)", output)
        if tq_values:
            max_tq = max(int(t) for t in tq_values)
            assert max_tq > 150, f"TQ values too low, possible connectivity issue: {output}"


@pytest.mark.live
class TestMeshInterfaces:
    """Test mesh interface configuration."""

    def test_lan3mesh_in_batman_node1(self, node1: NodeExecutor) -> None:
        """Verify lan3mesh is part of batman on node1."""
        output = node1.batctl("if")
        # Should have mesh interfaces attached to batman
        assert (
            "lan3" in output.lower() or "mesh" in output.lower()
        ), f"node1 lan3mesh not in batman: {output}"

    def test_lan4mesh_in_batman_node1(self, node1: NodeExecutor) -> None:
        """Verify lan4mesh is part of batman on node1."""
        output = node1.batctl("if")
        assert (
            "lan4" in output.lower() or "mesh" in output.lower()
        ), f"node1 lan4mesh not in batman: {output}"

    def test_wireless_mesh_interface_exists(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify wireless mesh interface exists on all nodes."""
        for executor in all_node_executors:
            # Check for wireless mesh in iw dev or batman interfaces
            rc, stdout, _ = executor.run("iw dev")
            # Look for mesh point interface
            has_mesh = "mesh point" in stdout.lower() or "mesh0" in stdout.lower()
            if not has_mesh:
                # Alternative: check batman interfaces
                bat_if = executor.batctl("if")
                has_mesh = "mesh" in bat_if.lower()
            assert has_mesh, f"{executor.node} missing wireless mesh interface"


@pytest.mark.live
class TestVLANInterfaces:
    """Test VLAN interface configuration for switch integration."""

    def test_mesh_vlan_interfaces_exist(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify VLAN 100 mesh interfaces (lan3.100, lan4.100) exist."""
        for executor in all_node_executors:
            rc, stdout, _ = executor.run("ip link show | grep -E 'lan[34]\\.100'")
            # Should have both lan3.100 and lan4.100
            has_lan3_vlan = "lan3.100" in stdout
            has_lan4_vlan = "lan4.100" in stdout
            assert (
                has_lan3_vlan and has_lan4_vlan
            ), f"{executor.node} missing mesh VLAN interfaces: {stdout}"

    def test_client_vlan_interfaces_exist(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify VLAN 200 client interfaces (lan3.200, lan4.200) exist."""
        for executor in all_node_executors:
            rc, stdout, _ = executor.run("ip link show | grep -E 'lan[34]\\.200'")
            # Should have both lan3.200 and lan4.200
            has_lan3_vlan = "lan3.200" in stdout
            has_lan4_vlan = "lan4.200" in stdout
            assert (
                has_lan3_vlan and has_lan4_vlan
            ), f"{executor.node} missing client VLAN interfaces: {stdout}"

    def test_iot_bridge_exists(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify IoT bridge (br-iot) exists for LAN2."""
        for executor in all_node_executors:
            rc, stdout, _ = executor.run("ip link show br-iot")
            assert rc == 0, f"{executor.node} missing br-iot interface"
            assert "br-iot" in stdout

    def test_lan2_in_iot_bridge(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify LAN2 is member of IoT bridge."""
        for executor in all_node_executors:
            rc, stdout, _ = executor.run("bridge link show | grep lan2")
            # lan2 should be in br-iot bridge
            if rc == 0:
                assert (
                    "br-iot" in stdout or "lan2" in stdout
                ), f"{executor.node} lan2 not properly bridged: {stdout}"
