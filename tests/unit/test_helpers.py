"""
Unit tests for test helper functions.

Tests validate helper utilities used across the test suite.
"""

import pytest


@pytest.mark.unit
def test_mesh_network_config_fixture(mesh_network_config: dict) -> None:
    """
    Test that mesh_network_config fixture provides valid data.

    Args:
        mesh_network_config: Mesh network configuration from fixture.
    """
    assert "network" in mesh_network_config, "Config should include network"
    assert "nodes" in mesh_network_config, "Config should include nodes list"
    assert len(mesh_network_config["nodes"]) == 3, "Should have 3 nodes"


@pytest.mark.unit
def test_node_ips_fixture(node_ips: list) -> None:
    """
    Test that node_ips fixture provides valid IP addresses.

    Args:
        node_ips: List of node IPs from fixture.
    """
    assert len(node_ips) == 3, "Should have 3 node IPs"

    for ip in node_ips:
        assert ip.startswith("10.11.12."), f"IP {ip} should be in mesh network"


@pytest.mark.unit
def test_batman_config_fixture(batman_config: dict) -> None:
    """
    Test that batman_config fixture provides valid configuration.

    Args:
        batman_config: Batman-adv configuration from fixture.
    """
    required_keys = ["routing_algo", "gw_bandwidth", "orig_interval", "hop_penalty"]

    for key in required_keys:
        assert key in batman_config, f"Batman config should include {key}"


@pytest.mark.unit
def test_cleanup_fixture(cleanup_test_files: list) -> None:
    """
    Test that cleanup fixture provides a mutable list.

    Args:
        cleanup_test_files: List for tracking files to cleanup from fixture.
    """
    assert isinstance(cleanup_test_files, list), "Cleanup fixture should be a list"

    # Test we can append to it
    cleanup_test_files.append("test_file.tmp")
    assert "test_file.tmp" in cleanup_test_files, "Should be able to add to cleanup list"
