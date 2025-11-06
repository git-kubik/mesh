"""
Integration tests for Ansible facts gathering.

Tests validate that Ansible can gather facts from mesh nodes.
"""

import pytest


@pytest.mark.integration
@pytest.mark.requires_nodes
def test_gather_facts_from_node1() -> None:
    """
    Test gathering Ansible facts from node1.

    Validates that ansible.builtin.setup module works.
    """
    pytest.skip("Requires Ansible access to nodes")


@pytest.mark.integration
@pytest.mark.requires_nodes
def test_gather_facts_from_all_nodes() -> None:
    """
    Test gathering Ansible facts from all mesh nodes.

    Validates facts collection across the entire mesh.
    """
    pytest.skip("Requires Ansible access to all nodes")


@pytest.mark.integration
@pytest.mark.requires_nodes
def test_node_hostname_facts() -> None:
    """
    Test that node hostnames are correctly reported in facts.

    Expected hostnames: mesh-node-1, mesh-node-2, mesh-node-3
    """
    pytest.skip("Requires Ansible facts from nodes")


@pytest.mark.integration
@pytest.mark.requires_nodes
def test_node_network_facts() -> None:
    """
    Test that network facts are correctly reported.

    Validates IP addresses, network interfaces, and routing information.
    """
    pytest.skip("Requires Ansible facts from nodes")


@pytest.mark.integration
@pytest.mark.requires_nodes
def test_node_openwrt_version() -> None:
    """
    Test that OpenWrt version is reported in facts.

    Validates that nodes are running OpenWrt.
    """
    pytest.skip("Requires Ansible facts from nodes")


@pytest.mark.integration
@pytest.mark.requires_nodes
def test_batman_interface_in_facts() -> None:
    """
    Test that batman-adv interfaces appear in network facts.

    Expected interfaces: bat0, bat0-wired, bat0-wireless
    """
    pytest.skip("Requires Ansible facts and batman-adv configuration")
