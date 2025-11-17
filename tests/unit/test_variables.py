"""
Unit tests for Ansible variable validation.

Tests validate variable types, ranges, and interdependencies.
"""

import re
from typing import Any

import pytest
import yaml


def extract_default(value: Any) -> Any:
    """
    Extract default value from Jinja2 template string.

    Handles templates like:
    - "{{ lookup('env', 'VAR') | default('value', true) }}"
    - "{{ lookup('env', 'VAR') | default('value', true) | int }}"
    - "{{ lookup('env', 'VAR') | default('a,b,c', true) | split(',') }}"

    Args:
        value: Raw value from YAML (may be template or actual value)

    Returns:
        Extracted default value with proper type conversion
    """
    if not isinstance(value, str):
        return value

    # Check if it's a Jinja2 template
    if not value.startswith("{{") or not value.endswith("}}"):
        return value

    # Extract default value from | default('value', true)
    match = re.search(r"\|\s*default\('([^']+)',\s*true\)", value)
    if not match:
        return value

    default_val = match.group(1)

    # Check if there's a type filter (int, bool, split)
    if "| int" in value:
        return int(default_val)
    elif "| bool" in value:
        return default_val.lower() in ("true", "yes", "1")
    elif "| split(',')" in value:
        return [item.strip() for item in default_val.split(",")]

    return default_val


@pytest.mark.unit
def test_network_variables_consistency(group_vars_path: str) -> None:
    """
    Test that network variables are internally consistent.

    Validates that mesh_network, mesh_gateway, and CIDR are compatible.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    network = extract_default(config["mesh_network"])
    gateway = extract_default(config["mesh_gateway"])
    cidr = extract_default(config["mesh_cidr"])

    # Basic validation
    assert network.startswith("10.11.12"), "Network should be in 10.11.12.0/24 range"
    assert gateway.startswith("10.11.12"), "Gateway should be in same network"
    assert cidr == 24, "CIDR should be /24"


@pytest.mark.unit
def test_batman_bandwidth_format(group_vars_path: str) -> None:
    """
    Test that Batman gateway bandwidth is in correct format.

    Format should be download/upload in kbit/s.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    bandwidth = extract_default(config["batman_gw_bandwidth"])
    assert "/" in bandwidth, "Bandwidth should be in download/upload format"

    parts = bandwidth.split("/")
    assert len(parts) == 2, "Bandwidth should have exactly two parts"

    # Verify both parts are numeric
    for part in parts:
        assert part.isdigit(), f"Bandwidth part '{part}' should be numeric"


@pytest.mark.unit
def test_wireless_channel_validity(group_vars_path: str) -> None:
    """
    Test that wireless channels are valid for their bands.

    2.4GHz: channels 1-14
    5GHz: channels 36 and above

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    mesh_channel = extract_default(config["mesh_channel"])
    client_channel = extract_default(config["client_channel"])

    # Mesh is 2.4GHz
    assert 1 <= mesh_channel <= 14, "Mesh channel must be in 2.4GHz range (1-14)"

    # Client is 5GHz
    assert client_channel >= 36, "Client channel must be in 5GHz range (36+)"


@pytest.mark.unit
def test_mtu_settings_valid(group_vars_path: str) -> None:
    """
    Test that MTU settings are within valid ranges.

    Wireless MTU should be less than wired MTU due to overhead.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    if "mtu_wired_mesh" in config and "mtu_wireless_mesh" in config:
        wired_mtu = extract_default(config["mtu_wired_mesh"])
        wireless_mtu = extract_default(config["mtu_wireless_mesh"])

        assert 1280 <= wired_mtu <= 1600, "Wired MTU should be in reasonable range"
        assert 1280 <= wireless_mtu <= 1600, "Wireless MTU should be in reasonable range"
        assert wireless_mtu < wired_mtu, "Wireless MTU should be less than wired due to overhead"


@pytest.mark.unit
def test_password_variables_exist(group_vars_path: str) -> None:
    """
    Test that password variables are defined (not testing values).

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    password_vars = ["mesh_password", "client_password"]

    for var in password_vars:
        assert var in config, f"Password variable '{var}' not defined"
        assert isinstance(config[var], str), f"Password variable '{var}' should be string"
        assert len(config[var]) > 0, f"Password variable '{var}' should not be empty"


@pytest.mark.unit
def test_encryption_types_valid(group_vars_path: str) -> None:
    """
    Test that encryption types are valid for OpenWrt.

    Args:
        group_vars_path: Path to group_vars file from fixture.
    """
    with open(group_vars_path, "r") as f:
        config = yaml.safe_load(f)

    valid_mesh_encryption = ["none", "sae"]
    valid_client_encryption = ["none", "psk", "psk2", "psk+ccmp", "psk2+ccmp"]

    mesh_enc = extract_default(config["mesh_encryption"])
    client_enc = extract_default(config["client_encryption"])

    assert mesh_enc in valid_mesh_encryption, f"Invalid mesh encryption: {mesh_enc}"
    assert client_enc in valid_client_encryption, f"Invalid client encryption: {client_enc}"
