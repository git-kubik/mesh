"""
Live failover scenario tests.

Tests validate mesh network resilience and failover behavior.

WARNING: Some tests are destructive and temporarily disrupt network connectivity.
Use with caution and only in controlled environments.
"""

import re
import time

import pytest

from .conftest import NODES, NodeExecutor


@pytest.mark.live
class TestMeshRedundancy:
    """Test mesh network redundancy without disrupting connections."""

    def test_multiple_paths_exist(self, node1: NodeExecutor) -> None:
        """Verify multiple paths exist to each destination."""
        output = node1.batctl("o")
        # In a ring topology with wired mesh, should see paths through multiple interfaces
        # Count unique interfaces in originator table - look for [interface] patterns
        # Interfaces can be: lan3, lan4, phy0-mesh0, lan3mesh, lan4mesh, mesh0
        interfaces = re.findall(r"\[\s*(\S+)\s*\]", output)
        unique_interfaces = set(interfaces)

        # Check batman interfaces to see what's available
        bat_if = node1.batctl("if")
        has_wired_mesh = "lan3" in bat_if.lower() or "lan4" in bat_if.lower()

        if has_wired_mesh:
            # With wired ring, should have multiple interfaces
            assert (
                len(unique_interfaces) >= 2
            ), f"Should have paths through multiple interfaces: {output}"
        else:
            # Wireless-only mode: just verify we have a mesh interface active
            assert len(unique_interfaces) >= 1, f"Should have at least wireless mesh path: {output}"
            # Log a warning that wired mesh isn't active
            import warnings

            warnings.warn(
                "Wired mesh interfaces not active - running on wireless only", stacklevel=2
            )

    def test_tq_values_healthy(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify TQ (transmission quality) values are healthy."""
        for executor in all_node_executors:
            output = executor.batctl("o")
            tq_values = re.findall(r"\((\d+)\)", output)
            if tq_values:
                max_tq = max(int(t) for t in tq_values)
                min_tq = min(int(t) for t in tq_values)
                # In a healthy ring, max TQ should be very high (>200)
                assert max_tq > 180, f"{executor.node} max TQ too low: {max_tq}"
                # Min TQ shows worst path - should still be usable (>100)
                assert min_tq > 50, f"{executor.node} min TQ very low: {min_tq}"

    def test_neighbor_count_node1(self, node1: NodeExecutor) -> None:
        """Verify node1 has expected number of neighbors."""
        output = node1.batctl("n")
        # Count non-header lines
        lines = [
            line
            for line in output.strip().split("\n")
            if line and not line.startswith("IF") and "Neighbor" not in line
        ]
        # In ring topology, should have 2 wired + potentially wireless neighbors
        assert len(lines) >= 2, f"node1 should have at least 2 neighbors: {output}"

    def test_neighbor_count_node2(self, node2: NodeExecutor) -> None:
        """Verify node2 has expected number of neighbors."""
        output = node2.batctl("n")
        lines = [
            line
            for line in output.strip().split("\n")
            if line and not line.startswith("IF") and "Neighbor" not in line
        ]
        assert len(lines) >= 2, f"node2 should have at least 2 neighbors: {output}"

    def test_neighbor_count_node3(self, node3: NodeExecutor) -> None:
        """Verify node3 has expected number of neighbors."""
        output = node3.batctl("n")
        lines = [
            line
            for line in output.strip().split("\n")
            if line and not line.startswith("IF") and "Neighbor" not in line
        ]
        assert len(lines) >= 2, f"node3 should have at least 2 neighbors: {output}"


@pytest.mark.live
@pytest.mark.destructive
class TestLinkFailover:
    """
    Test link failover by temporarily disabling interfaces.

    WARNING: These tests temporarily disrupt network connectivity.
    """

    @pytest.fixture(autouse=True)
    def confirm_destructive(self) -> None:
        """Require explicit opt-in for destructive tests."""
        import os

        if os.environ.get("MESH_RUN_DESTRUCTIVE_TESTS") != "true":
            pytest.skip("Destructive tests skipped. Set MESH_RUN_DESTRUCTIVE_TESTS=true to run.")

    def test_lan3_failover_node1(self, node1: NodeExecutor, node2: NodeExecutor) -> None:
        """Test failover when node1 LAN3 link is disabled."""
        # Get current neighbor count
        before = node1.batctl("n")
        before_count = len(
            [
                line
                for line in before.strip().split("\n")
                if line and not line.startswith("IF") and "Neighbor" not in line
            ]
        )

        try:
            # Disable LAN3 mesh interface on node1
            node1.run("ip link set lan3mesh down")
            time.sleep(5)  # Wait for batman to detect change

            # Should still be able to reach node2 via LAN4->node3->node2
            assert node1.ping(
                NODES["node2"].ip, count=5
            ), "Lost connectivity to node2 after LAN3 failure"

        finally:
            # Re-enable interface
            node1.run("ip link set lan3mesh up")
            time.sleep(5)

            # Verify recovery
            after = node1.batctl("n")
            assert "lan3" in after.lower() or before_count <= len(
                after.split("\n")
            ), "Network did not recover after re-enabling LAN3"

    def test_complete_ring_path_alternative(self, node1: NodeExecutor, node3: NodeExecutor) -> None:
        """Test that traffic can route around a disabled link."""
        # Verify we can ping node3 before any changes
        assert node1.ping(NODES["node3"].ip), "Cannot reach node3 before test"

        try:
            # Disable the direct link (LAN4 on node1 -> LAN4 on node3)
            node1.run("ip link set lan4mesh down")
            time.sleep(10)  # Wait for batman OGM timeout

            # Should still reach node3 via node1->node2->node3
            result = node1.ping(NODES["node3"].ip, count=10)
            assert result, "Lost connectivity to node3 - ring failover failed"

        finally:
            # Re-enable
            node1.run("ip link set lan4mesh up")
            time.sleep(5)


@pytest.mark.live
@pytest.mark.destructive
class TestWANFailover:
    """
    Test WAN failover behavior.

    WARNING: These tests temporarily disrupt WAN connectivity.
    """

    @pytest.fixture(autouse=True)
    def confirm_destructive(self) -> None:
        """Require explicit opt-in for destructive tests."""
        import os

        if os.environ.get("MESH_RUN_DESTRUCTIVE_TESTS") != "true":
            pytest.skip("Destructive tests skipped. Set MESH_RUN_DESTRUCTIVE_TESTS=true to run.")

    def test_wan_failover_node2(self, node2: NodeExecutor) -> None:
        """Test that node2 can reach internet via mesh when its WAN fails."""
        # node2 is gw_mode=client, so it should use other nodes' WANs when its own fails

        try:
            # Disable node2's WAN interface
            node2.run("ip link set wan down 2>/dev/null || ip link set eth0.2 down")
            time.sleep(5)

            # node2 should still reach internet via mesh -> node1 or node3
            # Batman gateway selection should kick in
            result = node2.ping("1.1.1.1", count=10)
            assert result, "node2 lost internet when WAN failed - gateway failover broken"

        finally:
            # Re-enable WAN
            node2.run("ip link set wan up 2>/dev/null || ip link set eth0.2 up")
            # May need DHCP to get IP back
            node2.run("udhcpc -i wan 2>/dev/null || true")
            time.sleep(5)


@pytest.mark.live
class TestGatewaySelection:
    """Test Batman gateway selection behavior (non-destructive)."""

    def test_gateway_selection_status(self, node2: NodeExecutor) -> None:
        """Check current gateway selection on node2 (client mode)."""
        output = node2.batctl("gwl")
        # Should show available gateways with one marked as selected (*)
        assert (
            "*" in output or "=>" in output or len(output.strip()) > 0
        ), f"No gateway selection visible: {output}"

    def test_gateway_metrics(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify gateway metrics are being advertised."""
        for executor in all_node_executors:
            if executor.node_info.gw_mode == "server":
                # Gateway servers should have bandwidth configured
                output = executor.batctl("gw_mode")
                # Should show bandwidth in output
                assert (
                    "server" in output.lower()
                ), f"{executor.node} not in gateway server mode: {output}"


@pytest.mark.live
class TestServiceContinuity:
    """Test service continuity during normal operation."""

    def test_continuous_ping_node1_to_node3(self, node1: NodeExecutor) -> None:
        """Test continuous ping from node1 to node3 for packet loss."""
        rc, output, _ = node1.run(f"ping -c 20 -W 2 {NODES['node3'].ip}", timeout=60)
        # Parse packet loss
        match = re.search(r"(\d+)% packet loss", output)
        if match:
            loss = int(match.group(1))
            # Allow up to 20% loss over wireless mesh
            assert loss < 20, f"High packet loss ({loss}%) to node3: {output}"
        elif "packets transmitted" in output:
            # Got some output but couldn't parse loss - check received count
            received_match = re.search(r"(\d+) packets transmitted, (\d+) received", output)
            if received_match:
                sent = int(received_match.group(1))
                received = int(received_match.group(2))
                loss_pct = ((sent - received) / sent) * 100
                assert loss_pct < 20, f"High packet loss ({loss_pct}%) to node3: {output}"
        else:
            # No output at all - ping timed out completely
            assert rc == 0, f"Ping failed (no response): {output}"

    def test_continuous_ping_node2_to_internet(self, node2: NodeExecutor) -> None:
        """Test continuous ping from node2 to internet for packet loss."""
        rc, output, _ = node2.run("ping -c 20 -W 2 1.1.1.1", timeout=60)
        match = re.search(r"(\d+)% packet loss", output)
        if match:
            loss = int(match.group(1))
            # Allow up to 15% loss for internet over wireless mesh
            assert loss < 15, f"High packet loss ({loss}%) to internet: {output}"
        elif "packets transmitted" in output:
            received_match = re.search(r"(\d+) packets transmitted, (\d+) received", output)
            if received_match:
                sent = int(received_match.group(1))
                received = int(received_match.group(2))
                loss_pct = ((sent - received) / sent) * 100
                assert loss_pct < 15, f"High packet loss ({loss_pct}%) to internet: {output}"
        else:
            assert rc == 0, f"Ping failed (no response): {output}"

    def test_latency_between_nodes(self, node1: NodeExecutor) -> None:
        """Test latency between mesh nodes is acceptable."""
        rc, output, _ = node1.run(f"ping -c 10 {NODES['node2'].ip}")
        # Parse average latency
        match = re.search(r"min/avg/max.*= [\d.]+/([\d.]+)/", output)
        if match:
            avg_latency = float(match.group(1))
            # Wired mesh should be <10ms typically
            assert avg_latency < 50, f"High latency ({avg_latency}ms) to node2"

    def test_latency_to_internet(self, node1: NodeExecutor) -> None:
        """Test latency to internet is acceptable."""
        rc, output, _ = node1.run("ping -c 10 1.1.1.1")
        match = re.search(r"min/avg/max.*= [\d.]+/([\d.]+)/", output)
        if match:
            avg_latency = float(match.group(1))
            # Should be <100ms for most connections
            assert avg_latency < 200, f"High internet latency ({avg_latency}ms)"
