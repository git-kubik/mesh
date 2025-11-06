"""
Performance tests for network throughput.

Tests measure throughput using iperf3 across different mesh paths.
"""

import pytest


@pytest.mark.performance
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_wired_throughput_node1_to_node2() -> None:
    """
    Test wired throughput between node1 and node2.

    Target: >= 400 Mbps over wired mesh link.
    Uses iperf3 for measurement.
    """
    pytest.skip("Requires iperf3 on nodes and performance testing setup")


@pytest.mark.performance
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_wired_throughput_node2_to_node3() -> None:
    """
    Test wired throughput between node2 and node3.

    Target: >= 400 Mbps over wired mesh link.
    """
    pytest.skip("Requires iperf3 on nodes")


@pytest.mark.performance
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_wired_throughput_node3_to_node1() -> None:
    """
    Test wired throughput between node3 and node1.

    Target: >= 400 Mbps over wired mesh link.
    """
    pytest.skip("Requires iperf3 on nodes")


@pytest.mark.performance
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_wireless_mesh_throughput() -> None:
    """
    Test throughput over wireless mesh (2.4GHz) backup link.

    Target: >= 50 Mbps over wireless mesh.
    Tested with wired links disabled.
    """
    pytest.skip("Requires iperf3 and wireless-only configuration")


@pytest.mark.performance
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_bidirectional_throughput() -> None:
    """
    Test bidirectional throughput simultaneously.

    Validates full-duplex performance over mesh links.
    """
    pytest.skip("Requires iperf3 bidirectional testing")


@pytest.mark.performance
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_throughput_under_load() -> None:
    """
    Test throughput with multiple concurrent streams.

    Validates performance degradation under load.
    """
    pytest.skip("Requires iperf3 with multiple parallel streams")


@pytest.mark.performance
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_client_to_internet_throughput() -> None:
    """
    Test client throughput to internet through mesh.

    Measures end-to-end performance for client devices.
    """
    pytest.skip("Requires client device and internet speed test")


@pytest.mark.performance
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_throughput_across_ring() -> None:
    """
    Test throughput across the full ring topology.

    Measures performance of multi-hop paths.
    """
    pytest.skip("Requires iperf3 and routing through ring")
