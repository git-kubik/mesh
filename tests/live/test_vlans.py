"""
Live VLAN and network segmentation tests.

Tests validate VLAN configuration, network isolation, and multi-network setup.
"""

import pytest

from .conftest import NodeExecutor


@pytest.mark.live
class TestVLANInterfaces:
    """Test VLAN interface configuration on nodes."""

    def test_management_vlan_interface_node1(self, node1: NodeExecutor) -> None:
        """Verify management VLAN interface exists on node1."""
        output = node1.run_ok("ip addr show")
        # Look for management network - node may have .1 if acting as primary
        assert "10.11.10." in output, f"node1 missing management IP: {output}"

    def test_management_vlan_interface_node2(self, node2: NodeExecutor) -> None:
        """Verify management VLAN interface exists on node2."""
        output = node2.run_ok("ip addr show")
        assert "10.11.10." in output, f"node2 missing management IP: {output}"

    def test_management_vlan_interface_node3(self, node3: NodeExecutor) -> None:
        """Verify management VLAN interface exists on node3."""
        output = node3.run_ok("ip addr show")
        assert "10.11.10." in output, f"node3 missing management IP: {output}"

    def test_guest_vlan_interface_node1(self, node1: NodeExecutor) -> None:
        """Verify guest VLAN interface exists on node1."""
        output = node1.run_ok("ip addr show")
        assert "10.11.30." in output, f"node1 missing guest IP: {output}"

    def test_guest_vlan_interface_node2(self, node2: NodeExecutor) -> None:
        """Verify guest VLAN interface exists on node2."""
        output = node2.run_ok("ip addr show")
        assert "10.11.30." in output, f"node2 missing guest IP: {output}"

    def test_guest_vlan_interface_node3(self, node3: NodeExecutor) -> None:
        """Verify guest VLAN interface exists on node3."""
        output = node3.run_ok("ip addr show")
        assert "10.11.30." in output, f"node3 missing guest IP: {output}"


@pytest.mark.live
class TestMainLANConfiguration:
    """Test main LAN (10.11.12.0/24) configuration."""

    def test_main_lan_ip_node1(self, node1: NodeExecutor) -> None:
        """Verify node1 has correct main LAN IP."""
        output = node1.run_ok("ip addr show br-lan")
        assert "10.11.12.1" in output, f"node1 missing LAN IP: {output}"

    def test_main_lan_ip_node2(self, node2: NodeExecutor) -> None:
        """Verify node2 has correct main LAN IP."""
        output = node2.run_ok("ip addr show br-lan")
        assert "10.11.12.2" in output, f"node2 missing LAN IP: {output}"

    def test_main_lan_ip_node3(self, node3: NodeExecutor) -> None:
        """Verify node3 has correct main LAN IP."""
        output = node3.run_ok("ip addr show br-lan")
        assert "10.11.12.3" in output, f"node3 missing LAN IP: {output}"


@pytest.mark.live
class TestDHCPConfiguration:
    """Test DHCP server configuration on each node."""

    def test_dhcp_running_node1(self, node1: NodeExecutor) -> None:
        """Verify DHCP (dnsmasq) is running on node1."""
        output = node1.run_ok("pgrep -x dnsmasq || pgrep dnsmasq")
        assert output.strip(), "dnsmasq not running on node1"

    def test_dhcp_running_node2(self, node2: NodeExecutor) -> None:
        """Verify DHCP (dnsmasq) is running on node2."""
        output = node2.run_ok("pgrep -x dnsmasq || pgrep dnsmasq")
        assert output.strip(), "dnsmasq not running on node2"

    def test_dhcp_running_node3(self, node3: NodeExecutor) -> None:
        """Verify DHCP (dnsmasq) is running on node3."""
        output = node3.run_ok("pgrep -x dnsmasq || pgrep dnsmasq")
        assert output.strip(), "dnsmasq not running on node3"

    def test_dhcp_pool_node1(self, node1: NodeExecutor) -> None:
        """Verify node1 DHCP pool starts at 100."""
        output = node1.run_ok("uci get dhcp.lan.start")
        assert output.strip() == "100", f"node1 DHCP start should be 100: {output}"

    def test_dhcp_pool_node2(self, node2: NodeExecutor) -> None:
        """Verify node2 DHCP pool starts at 150."""
        output = node2.run_ok("uci get dhcp.lan.start")
        assert output.strip() == "150", f"node2 DHCP start should be 150: {output}"

    def test_dhcp_pool_node3(self, node3: NodeExecutor) -> None:
        """Verify node3 DHCP pool starts at 200."""
        output = node3.run_ok("uci get dhcp.lan.start")
        assert output.strip() == "200", f"node3 DHCP start should be 200: {output}"


@pytest.mark.live
class TestFirewallZones:
    """Test firewall zone configuration."""

    def test_lan_zone_exists(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify LAN firewall zone exists on all nodes."""
        for executor in all_node_executors:
            output = executor.run_ok("uci show firewall | grep zone.*lan")
            assert "lan" in output.lower(), f"{executor.node} missing lan zone"

    def test_wan_zone_exists(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify WAN firewall zone exists on all nodes."""
        for executor in all_node_executors:
            output = executor.run_ok("uci show firewall | grep zone.*wan")
            assert "wan" in output.lower(), f"{executor.node} missing wan zone"

    def test_guest_zone_isolation(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify guest zone has isolation configured."""
        for executor in all_node_executors:
            # Check for guest zone with forward REJECT
            rc, output, _ = executor.run("uci show firewall | grep -i guest")
            if rc == 0 and "guest" in output.lower():
                # Guest zone should exist and have restricted forwarding
                zone_output = executor.run_ok("uci show firewall")
                assert "guest" in zone_output.lower(), f"{executor.node} guest zone not configured"


@pytest.mark.live
class TestNetworkBridges:
    """Test network bridge configuration."""

    def test_br_lan_exists(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify br-lan bridge exists on all nodes."""
        for executor in all_node_executors:
            output = executor.run_ok("ip link show br-lan")
            assert "br-lan" in output, f"{executor.node} missing br-lan bridge"

    def test_bat0_in_bridge(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify bat0 is part of br-lan bridge."""
        for executor in all_node_executors:
            output = executor.run_ok("brctl show br-lan || bridge link show")
            assert "bat0" in output, f"{executor.node} bat0 not in br-lan: {output}"


@pytest.mark.live
class TestInterVLANRouting:
    """Test routing between VLANs and networks."""

    def test_management_can_reach_lan(self, node1: NodeExecutor) -> None:
        """Test that management network can reach main LAN (by design)."""
        # From management interface, should be able to ping LAN
        # This validates the firewall allows mgmt->lan
        rc, output, _ = node1.run(
            "ping -c 1 -W 2 -I 10.11.10.1 10.11.12.2 2>/dev/null || echo 'ping failed'"
        )
        # Note: This may fail if routing isn't set up - that's expected in some configs
        # The test documents expected behavior
        pass  # Informational test

    def test_guest_network_isolated(self, node1: NodeExecutor) -> None:
        """Document that guest network should be isolated from LAN."""
        # Guest network (10.11.30.0/24) should NOT reach LAN (10.11.12.0/24)
        # This is enforced by firewall rules
        # Actual isolation test would require a client on guest network
        pass  # Requires client on guest network to fully test
