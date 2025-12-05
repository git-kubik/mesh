"""
Live WAN and internet connectivity tests.

Tests validate WAN interface configuration, NAT, and multi-WAN setup.
"""

import re

import pytest

from .conftest import NodeExecutor


@pytest.mark.live
class TestWANInterfaces:
    """Test WAN interface configuration."""

    def test_wan_interface_exists_node1(self, node1: NodeExecutor) -> None:
        """Verify WAN interface exists and is UP on node1."""
        output = node1.run_ok("ip link show wan 2>/dev/null || ip link show eth0.2")
        assert "UP" in output or "state UP" in output.upper(), f"node1 WAN not UP: {output}"

    def test_wan_interface_exists_node2(self, node2: NodeExecutor) -> None:
        """Verify WAN interface exists and is UP on node2."""
        output = node2.run_ok("ip link show wan 2>/dev/null || ip link show eth0.2")
        assert "UP" in output or "state UP" in output.upper(), f"node2 WAN not UP: {output}"

    def test_wan_interface_exists_node3(self, node3: NodeExecutor) -> None:
        """Verify WAN interface exists and is UP on node3."""
        output = node3.run_ok("ip link show wan 2>/dev/null || ip link show eth0.2")
        assert "UP" in output or "state UP" in output.upper(), f"node3 WAN not UP: {output}"

    def test_wan_has_ip_node1(self, node1: NodeExecutor) -> None:
        """Verify node1 WAN has an IP address."""
        rc, output, _ = node1.run("ip addr show wan 2>/dev/null || ip addr show eth0.2")
        # Should have an inet address
        assert "inet " in output, f"node1 WAN missing IP: {output}"

    def test_wan_has_ip_node2(self, node2: NodeExecutor) -> None:
        """Verify node2 WAN has an IP address."""
        rc, output, _ = node2.run("ip addr show wan 2>/dev/null || ip addr show eth0.2")
        assert "inet " in output, f"node2 WAN missing IP: {output}"

    def test_wan_has_ip_node3(self, node3: NodeExecutor) -> None:
        """Verify node3 WAN has an IP address."""
        rc, output, _ = node3.run("ip addr show wan 2>/dev/null || ip addr show eth0.2")
        assert "inet " in output, f"node3 WAN missing IP: {output}"


@pytest.mark.live
class TestDefaultRoutes:
    """Test default route configuration."""

    def test_default_route_exists_node1(self, node1: NodeExecutor) -> None:
        """Verify node1 has a default route."""
        output = node1.run_ok("ip route show default")
        assert "default" in output, f"node1 missing default route: {output}"

    def test_default_route_exists_node2(self, node2: NodeExecutor) -> None:
        """Verify node2 has a default route."""
        output = node2.run_ok("ip route show default")
        assert "default" in output, f"node2 missing default route: {output}"

    def test_default_route_exists_node3(self, node3: NodeExecutor) -> None:
        """Verify node3 has a default route."""
        output = node3.run_ok("ip route show default")
        assert "default" in output, f"node3 missing default route: {output}"


@pytest.mark.live
class TestNATMasquerade:
    """Test NAT/masquerade configuration."""

    def test_nat_rules_exist_node1(self, node1: NodeExecutor) -> None:
        """Verify NAT rules exist on node1."""
        # Check nftables or iptables for masquerade rules
        rc, output, _ = node1.run("nft list ruleset 2>/dev/null | grep -i masq")
        if rc != 0:
            # Try iptables
            rc, output, _ = node1.run("iptables -t nat -L -n | grep -i masq")
        assert rc == 0 or "MASQ" in output.upper(), "node1 missing NAT rules"

    def test_nat_rules_exist_node2(self, node2: NodeExecutor) -> None:
        """Verify NAT rules exist on node2."""
        rc, output, _ = node2.run("nft list ruleset 2>/dev/null | grep -i masq")
        if rc != 0:
            rc, output, _ = node2.run("iptables -t nat -L -n | grep -i masq")
        assert rc == 0 or "MASQ" in output.upper(), "node2 missing NAT rules"

    def test_nat_rules_exist_node3(self, node3: NodeExecutor) -> None:
        """Verify NAT rules exist on node3."""
        rc, output, _ = node3.run("nft list ruleset 2>/dev/null | grep -i masq")
        if rc != 0:
            rc, output, _ = node3.run("iptables -t nat -L -n | grep -i masq")
        assert rc == 0 or "MASQ" in output.upper(), "node3 missing NAT rules"


@pytest.mark.live
class TestInternetConnectivity:
    """Test actual internet connectivity from each node."""

    def test_ping_cloudflare_node1(self, node1: NodeExecutor) -> None:
        """Test node1 can ping Cloudflare DNS (1.1.1.1)."""
        assert node1.ping("1.1.1.1", count=3), "node1 cannot reach 1.1.1.1"

    def test_ping_cloudflare_node2(self, node2: NodeExecutor) -> None:
        """Test node2 can ping Cloudflare DNS (1.1.1.1)."""
        assert node2.ping("1.1.1.1", count=3), "node2 cannot reach 1.1.1.1"

    def test_ping_cloudflare_node3(self, node3: NodeExecutor) -> None:
        """Test node3 can ping Cloudflare DNS (1.1.1.1)."""
        assert node3.ping("1.1.1.1", count=3), "node3 cannot reach 1.1.1.1"

    def test_ping_google_node1(self, node1: NodeExecutor) -> None:
        """Test node1 can ping Google DNS (8.8.8.8)."""
        assert node1.ping("8.8.8.8", count=3), "node1 cannot reach 8.8.8.8"

    def test_ping_google_node2(self, node2: NodeExecutor) -> None:
        """Test node2 can ping Google DNS (8.8.8.8)."""
        assert node2.ping("8.8.8.8", count=3), "node2 cannot reach 8.8.8.8"

    def test_ping_google_node3(self, node3: NodeExecutor) -> None:
        """Test node3 can ping Google DNS (8.8.8.8)."""
        assert node3.ping("8.8.8.8", count=3), "node3 cannot reach 8.8.8.8"


@pytest.mark.live
class TestDNSResolution:
    """Test DNS resolution from each node."""

    def test_dns_resolution_node1(self, node1: NodeExecutor) -> None:
        """Test node1 can resolve DNS names."""
        rc, output, _ = node1.run("nslookup google.com 2>/dev/null || host google.com")
        assert rc == 0, f"node1 DNS resolution failed: {output}"

    def test_dns_resolution_node2(self, node2: NodeExecutor) -> None:
        """Test node2 can resolve DNS names."""
        rc, output, _ = node2.run("nslookup google.com 2>/dev/null || host google.com")
        assert rc == 0, f"node2 DNS resolution failed: {output}"

    def test_dns_resolution_node3(self, node3: NodeExecutor) -> None:
        """Test node3 can resolve DNS names."""
        rc, output, _ = node3.run("nslookup google.com 2>/dev/null || host google.com")
        assert rc == 0, f"node3 DNS resolution failed: {output}"


@pytest.mark.live
class TestHTTPConnectivity:
    """Test HTTP/HTTPS connectivity."""

    def test_http_connectivity_node1(self, node1: NodeExecutor) -> None:
        """Test node1 can make HTTP requests."""
        # Check if curl is available first
        rc, _, _ = node1.run("which curl")
        if rc != 0:
            pytest.skip("curl not installed on node1")
        curl_cmd = "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10"
        rc, output, _ = node1.run(f"{curl_cmd} http://detectportal.firefox.com/success.txt")
        assert rc == 0 and "200" in output, f"node1 HTTP failed: {output}"

    def test_http_connectivity_node2(self, node2: NodeExecutor) -> None:
        """Test node2 can make HTTP requests."""
        rc, _, _ = node2.run("which curl")
        if rc != 0:
            pytest.skip("curl not installed on node2")
        curl_cmd = "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10"
        rc, output, _ = node2.run(f"{curl_cmd} http://detectportal.firefox.com/success.txt")
        assert rc == 0 and "200" in output, f"node2 HTTP failed: {output}"

    def test_http_connectivity_node3(self, node3: NodeExecutor) -> None:
        """Test node3 can make HTTP requests."""
        rc, _, _ = node3.run("which curl")
        if rc != 0:
            pytest.skip("curl not installed on node3")
        curl_cmd = "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10"
        rc, output, _ = node3.run(f"{curl_cmd} http://detectportal.firefox.com/success.txt")
        assert rc == 0 and "200" in output, f"node3 HTTP failed: {output}"

    def test_https_connectivity_node1(self, node1: NodeExecutor) -> None:
        """Test node1 can make HTTPS requests."""
        rc, _, _ = node1.run("which curl")
        if rc != 0:
            pytest.skip("curl not installed on node1")
        rc, output, _ = node1.run(
            "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 https://www.google.com"
        )
        assert rc == 0 and (
            "200" in output or "301" in output or "302" in output
        ), f"node1 HTTPS failed: {output}"


@pytest.mark.live
class TestMultiWAN:
    """Test multi-WAN configuration (all 3 nodes have independent WAN)."""

    def test_all_nodes_have_independent_wan(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify each node has its own WAN connection."""
        wan_gateways = []
        for executor in all_node_executors:
            output = executor.run_ok("ip route show default")
            # Extract gateway IP
            match = re.search(r"via (\d+\.\d+\.\d+\.\d+)", output)
            if match:
                wan_gateways.append((executor.node, match.group(1)))

        # All nodes should have a gateway
        assert len(wan_gateways) == 3, f"Not all nodes have WAN gateway: {wan_gateways}"

    def test_wan_traceroute_node1(self, node1: NodeExecutor) -> None:
        """Verify node1 routes directly via its own WAN."""
        rc, output, _ = node1.run("traceroute -n -m 3 1.1.1.1 2>/dev/null | head -4")
        if rc == 0:
            # First hop should be node1's WAN gateway, not another mesh node
            first_hop = output.split("\n")[1] if len(output.split("\n")) > 1 else ""
            # Should not see 10.11.12.x as first hop (that would mean going through mesh)
            assert (
                "10.11.12" not in first_hop
            ), f"node1 routing through mesh instead of own WAN: {output}"

    def test_wan_traceroute_node2(self, node2: NodeExecutor) -> None:
        """Verify node2 routes directly via its own WAN."""
        rc, output, _ = node2.run("traceroute -n -m 3 1.1.1.1 2>/dev/null | head -4")
        if rc == 0:
            first_hop = output.split("\n")[1] if len(output.split("\n")) > 1 else ""
            assert (
                "10.11.12" not in first_hop
            ), f"node2 routing through mesh instead of own WAN: {output}"

    def test_wan_traceroute_node3(self, node3: NodeExecutor) -> None:
        """Verify node3 routes directly via its own WAN."""
        rc, output, _ = node3.run("traceroute -n -m 3 1.1.1.1 2>/dev/null | head -4")
        if rc == 0:
            first_hop = output.split("\n")[1] if len(output.split("\n")) > 1 else ""
            assert (
                "10.11.12" not in first_hop
            ), f"node3 routing through mesh instead of own WAN: {output}"
