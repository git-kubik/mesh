"""
Unit tests for Ansible inventory validation.

Tests validate inventory structure, node definitions, and host variables.
"""

import pytest
import yaml


@pytest.mark.unit
def test_inventory_file_exists(inventory_path: str) -> None:
    """
    Test that inventory file exists.

    Args:
        inventory_path: Path to inventory file from fixture.
    """
    import os

    assert os.path.exists(inventory_path), f"Inventory file not found: {inventory_path}"


@pytest.mark.unit
def test_inventory_valid_yaml(inventory_path: str) -> None:
    """
    Test that inventory file is valid YAML.

    Args:
        inventory_path: Path to inventory file from fixture.
    """
    with open(inventory_path, "r") as f:
        try:
            yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in inventory: {e}")


@pytest.mark.unit
def test_inventory_has_mesh_nodes_group(inventory_path: str) -> None:
    """
    Test that inventory defines mesh_nodes group.

    Args:
        inventory_path: Path to inventory file from fixture.
    """
    with open(inventory_path, "r") as f:
        inventory = yaml.safe_load(f)

    assert "all" in inventory, "Missing 'all' group"
    assert "children" in inventory["all"], "Missing 'children' in all group"
    assert "mesh_nodes" in inventory["all"]["children"], "Missing 'mesh_nodes' group"


@pytest.mark.unit
def test_inventory_has_three_nodes(inventory_path: str) -> None:
    """
    Test that inventory defines exactly three nodes.

    Args:
        inventory_path: Path to inventory file from fixture.
    """
    with open(inventory_path, "r") as f:
        inventory = yaml.safe_load(f)

    mesh_nodes = inventory["all"]["children"]["mesh_nodes"]["children"]

    # Count total hosts
    total_hosts = 0
    for group in mesh_nodes.values():
        if "hosts" in group:
            total_hosts += len(group["hosts"])

    assert total_hosts == 3, f"Expected 3 nodes, found {total_hosts}"


@pytest.mark.unit
def test_inventory_node_ips(inventory_path: str, node_ips: list) -> None:
    """
    Test that node IPs are correctly defined.

    Args:
        inventory_path: Path to inventory file from fixture.
        node_ips: Expected node IPs from fixture.
    """
    with open(inventory_path, "r") as f:
        inventory = yaml.safe_load(f)

    mesh_nodes = inventory["all"]["children"]["mesh_nodes"]["children"]

    found_ips = []
    for group in mesh_nodes.values():
        if "hosts" in group:
            for host in group["hosts"].values():
                found_ips.append(host["ansible_host"])

    assert sorted(found_ips) == sorted(node_ips), "Node IPs do not match expected values"


@pytest.mark.unit
def test_inventory_node_variables(inventory_path: str) -> None:
    """
    Test that nodes have required variables defined.

    Validates ansible_host, node_ip, node_id, and dhcp_server settings.

    Args:
        inventory_path: Path to inventory file from fixture.
    """
    with open(inventory_path, "r") as f:
        inventory = yaml.safe_load(f)

    mesh_nodes = inventory["all"]["children"]["mesh_nodes"]["children"]

    required_vars = ["ansible_host", "node_ip", "node_id", "dhcp_server"]

    for group in mesh_nodes.values():
        if "hosts" in group:
            for hostname, host_vars in group["hosts"].items():
                for var in required_vars:
                    assert (
                        var in host_vars
                    ), f"Missing required variable '{var}' for host {hostname}"


@pytest.mark.unit
def test_inventory_gateway_groups(inventory_path: str) -> None:
    """
    Test that gateway groups are properly defined.

    Validates gateway_primary and gateway_secondary groups exist.

    Args:
        inventory_path: Path to inventory file from fixture.
    """
    with open(inventory_path, "r") as f:
        inventory = yaml.safe_load(f)

    mesh_nodes = inventory["all"]["children"]["mesh_nodes"]["children"]

    assert "gateway_primary" in mesh_nodes, "Missing gateway_primary group"
    assert "gateway_secondary" in mesh_nodes, "Missing gateway_secondary group"


@pytest.mark.unit
def test_inventory_dhcp_server_configuration(inventory_path: str) -> None:
    """
    Test that exactly one node has DHCP server enabled.

    Args:
        inventory_path: Path to inventory file from fixture.
    """
    with open(inventory_path, "r") as f:
        inventory = yaml.safe_load(f)

    mesh_nodes = inventory["all"]["children"]["mesh_nodes"]["children"]

    dhcp_servers = []
    for group in mesh_nodes.values():
        if "hosts" in group:
            for hostname, host_vars in group["hosts"].items():
                if host_vars.get("dhcp_server", False):
                    dhcp_servers.append(hostname)

    assert len(dhcp_servers) == 1, f"Expected 1 DHCP server, found {len(dhcp_servers)}"


@pytest.mark.unit
def test_inventory_mesh_ports_defined(inventory_path: str) -> None:
    """
    Test that mesh ports are defined for all nodes.

    Args:
        inventory_path: Path to inventory file from fixture.
    """
    with open(inventory_path, "r") as f:
        inventory = yaml.safe_load(f)

    mesh_nodes = inventory["all"]["children"]["mesh_nodes"]["children"]

    for group in mesh_nodes.values():
        if "hosts" in group:
            for hostname, host_vars in group["hosts"].items():
                assert (
                    "mesh_ports" in host_vars
                ), f"Missing mesh_ports for host {hostname}"
                assert len(host_vars["mesh_ports"]) > 0, f"No mesh ports defined for {hostname}"
