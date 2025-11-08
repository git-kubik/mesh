"""
Unit tests for configuration validation.

Tests validate group_vars configuration including network settings,
Batman-adv configuration, wireless settings, and DHCP configuration.
"""

import pytest
import yaml


@pytest.mark.unit
def test_group_vars_file_exists(group_vars_path: str) -> None:
    """
    Test that group_vars/all.yml file exists.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    import os

    assert os.path.exists(group_vars_path), f"Group vars file not found: {group_vars_path}"


@pytest.mark.unit
def test_group_vars_valid_yaml(group_vars_path: str) -> None:
    """
    Test that group_vars/all.yml is valid YAML.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        try:
            yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in group_vars: {e}")


@pytest.mark.unit
def test_mesh_network_configuration(group_vars_path: str) -> None:
    """
    Test that mesh network configuration is properly defined.

    Validates network address, netmask, CIDR, and gateway settings.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    assert "mesh_network" in config, "mesh_network not defined"
    assert "mesh_netmask" in config, "mesh_netmask not defined"
    assert "mesh_cidr" in config, "mesh_cidr not defined"
    assert "mesh_gateway" in config, "mesh_gateway not defined"

    # Validate values
    assert config["mesh_network"] == "10.11.12.0", "Unexpected mesh network"
    assert config["mesh_cidr"] == 24, "Unexpected CIDR notation"


@pytest.mark.unit
def test_batman_configuration(group_vars_path: str) -> None:
    """
    Test that Batman-adv configuration is properly defined.

    Validates routing algorithm, gateway bandwidth, intervals, and penalties.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    required_keys = [
        "batman_routing_algo",
        "batman_gw_bandwidth",
        "batman_orig_interval",
        "batman_hop_penalty",
    ]

    for key in required_keys:
        assert key in config, f"Batman config missing: {key}"

    # Validate algorithm
    assert config["batman_routing_algo"] in [
        "BATMAN_IV",
        "BATMAN_V",
    ], "Invalid routing algorithm"


@pytest.mark.unit
def test_wireless_mesh_configuration(group_vars_path: str) -> None:
    """
    Test that wireless mesh (2.4GHz) configuration is properly defined.

    Validates mesh ID, encryption, channel, and multicast rate settings.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    required_keys = [
        "mesh_id",
        "mesh_encryption",
        "mesh_password",
        "mesh_channel",
        "mesh_htmode",
        "mesh_mcast_rate",
    ]

    for key in required_keys:
        assert key in config, f"Mesh wireless config missing: {key}"

    # Validate channel is in 2.4GHz range
    assert 1 <= config["mesh_channel"] <= 14, "Invalid 2.4GHz channel"


@pytest.mark.unit
def test_client_wireless_configuration(group_vars_path: str) -> None:
    """
    Test that client wireless (5GHz AP) configuration is properly defined.

    Validates SSID, encryption, channel, and HT mode settings.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    required_keys = [
        "client_ssid",
        "client_encryption",
        "client_password",
        "client_channel",
        "client_htmode",
        "client_country",
    ]

    for key in required_keys:
        assert key in config, f"Client wireless config missing: {key}"

    # Validate 5GHz channel
    assert config["client_channel"] >= 36, "Client channel should be in 5GHz range"


@pytest.mark.unit
def test_dhcp_configuration(group_vars_path: str) -> None:
    """
    Test that DHCP configuration is properly defined.

    Validates DHCP start, limit, and lease time settings.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    # Check for new redundant DHCP configuration
    required_keys = ["dhcp_pools", "dhcp_leasetime"]

    for key in required_keys:
        assert key in config, f"DHCP config missing: {key}"

    # Validate DHCP pools structure
    assert isinstance(config["dhcp_pools"], dict), "dhcp_pools must be dictionary"
    required_nodes = ["node1", "node2", "node3"]

    for node in required_nodes:
        assert node in config["dhcp_pools"], f"DHCP pool missing for {node}"
        pool = config["dhcp_pools"][node]
        assert "start" in pool, f"start missing in {node} DHCP pool"
        assert "limit" in pool, f"limit missing in {node} DHCP pool"
        assert isinstance(pool["start"], int), f"{node} start must be integer"
        assert isinstance(pool["limit"], int), f"{node} limit must be integer"
        assert pool["start"] > 0, f"{node} start must be positive"
        assert pool["limit"] > 0, f"{node} limit must be positive"


@pytest.mark.unit
def test_dns_servers_defined(group_vars_path: str) -> None:
    """
    Test that DNS servers are properly defined.

    Validates that at least one DNS server is configured.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    assert "dns_servers" in config, "dns_servers not defined"
    assert isinstance(config["dns_servers"], list), "dns_servers must be a list"
    assert len(config["dns_servers"]) > 0, "At least one DNS server required"


@pytest.mark.unit
def test_required_packages_defined(group_vars_path: str) -> None:
    """
    Test that required packages are properly defined.

    Validates that essential packages like batman-adv and batctl are listed.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    assert "required_packages" in config, "required_packages not defined"
    packages = config["required_packages"]

    # Check for essential packages
    essential = ["kmod-batman-adv", "batctl"]
    for pkg in essential:
        assert pkg in packages, f"Essential package missing: {pkg}"
