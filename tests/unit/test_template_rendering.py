"""
Unit tests for Ansible template rendering with mock variables.

Tests validate that templates render correctly with sample variable values.
"""

from pathlib import Path
from typing import Any, Dict

import pytest
from jinja2 import Environment, FileSystemLoader


@pytest.fixture
def mock_node_variables() -> Dict[str, Any]:
    """
    Provide mock variables for template rendering.

    Returns:
        Dictionary of variables simulating Ansible node context.
    """
    return {
        # Node identity
        "inventory_hostname": "node1",
        "node_ip": "10.11.12.1",
        "node_number": 1,
        # Network settings
        "mesh_bridge_ip": "10.11.12.1",
        "mesh_netmask": "255.255.255.0",
        "mesh_network": "10.11.12.0",
        "batman_gateway_mode": "server",
        "batman_gw_bandwidth": "100000/100000",
        # VLAN settings
        "switch_mesh_vlan": 100,
        "switch_client_vlan": 200,
        "iot_vlan": 30,
        "iot_network": "10.11.30.0",
        "enable_vlans": True,
        "vlans": {
            "management": {
                "vid": 10,
                "network": "10.11.10.0/24",
                "gateway_ip": "10.11.10.1",
                "netmask": "255.255.255.0",
                "dhcp_start": 100,
                "dhcp_limit": 50,
            },
            "guest": {
                "vid": 20,
                "network": "10.11.20.0/24",
                "gateway_ip": "10.11.20.1",
                "netmask": "255.255.255.0",
                "dhcp_start": 100,
                "dhcp_limit": 50,
            },
        },
        # Wireless settings
        "mesh_id": "HA-Mesh",
        "mesh_password": "test-mesh-password",
        "mesh_channel": 6,
        "client_ssid": "HA-Client",
        "client_password": "test-client-password",
        "client_channel": 36,
        "country_code": "AU",
        # DHCP settings
        "dhcp_pools": {
            "node1": {"start": 100, "limit": 50},
            "node2": {"start": 150, "limit": 50},
            "node3": {"start": 200, "limit": 50},
        },
        # Firewall settings
        "wan_interface": "wan",
        "lan_interface": "lan",
    }


@pytest.fixture
def jinja_env(role_paths: Dict[str, Path]) -> Environment:
    """
    Create Jinja2 environment with template search paths.

    Args:
        role_paths: Mapping of role names to paths.

    Returns:
        Jinja2 Environment configured with template paths.
    """
    # Collect all template directories
    template_dirs = []
    for _role_name, role_path in role_paths.items():
        templates_dir = role_path / "templates"
        if templates_dir.exists():
            template_dirs.append(str(templates_dir))

    return Environment(loader=FileSystemLoader(template_dirs))


@pytest.mark.unit
class TestNetworkTemplateRendering:
    """Tests for network.j2 template rendering."""

    def test_network_template_renders(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that network.j2 template renders without errors."""
        template_path = role_paths["network_config"] / "templates" / "network.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("network.j2")

        # Should not raise
        result = template.render(**mock_node_variables)
        assert len(result) > 0, "Rendered template should not be empty"

    def test_network_template_contains_node_ip(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that rendered network template contains node IP."""
        template_path = role_paths["network_config"] / "templates" / "network.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("network.j2")

        result = template.render(**mock_node_variables)
        assert mock_node_variables["node_ip"] in result, "Network template should contain node IP"

    def test_network_template_defines_loopback(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that rendered network template defines loopback interface."""
        template_path = role_paths["network_config"] / "templates" / "network.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("network.j2")

        result = template.render(**mock_node_variables)
        assert "loopback" in result.lower(), "Network template should define loopback"

    def test_network_template_defines_batman(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that rendered network template defines batman interface."""
        template_path = role_paths["network_config"] / "templates" / "network.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("network.j2")

        result = template.render(**mock_node_variables)
        assert "bat0" in result, "Network template should define bat0 interface"


@pytest.mark.unit
class TestWirelessTemplateRendering:
    """Tests for wireless.j2 template rendering."""

    def test_wireless_template_renders(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that wireless.j2 template renders without errors."""
        template_path = role_paths["wireless_config"] / "templates" / "wireless.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("wireless.j2")

        result = template.render(**mock_node_variables)
        assert len(result) > 0, "Rendered template should not be empty"

    def test_wireless_template_contains_mesh_settings(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that rendered wireless template contains mesh settings."""
        template_path = role_paths["wireless_config"] / "templates" / "wireless.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("wireless.j2")

        result = template.render(**mock_node_variables)
        assert mock_node_variables["mesh_id"] in result, "Should contain mesh_id"

    def test_wireless_template_contains_client_ssid(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that rendered wireless template contains client SSID."""
        template_path = role_paths["wireless_config"] / "templates" / "wireless.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("wireless.j2")

        result = template.render(**mock_node_variables)
        assert mock_node_variables["client_ssid"] in result, "Should contain client_ssid"

    def test_wireless_template_defines_wifi_devices(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that rendered wireless template defines wifi devices."""
        template_path = role_paths["wireless_config"] / "templates" / "wireless.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("wireless.j2")

        result = template.render(**mock_node_variables)
        assert "config wifi-device" in result, "Should define wifi devices"


@pytest.mark.unit
class TestDHCPTemplateRendering:
    """Tests for dhcp.j2 template rendering."""

    def test_dhcp_template_renders(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that dhcp.j2 template renders without errors."""
        template_path = role_paths["dhcp_config"] / "templates" / "dhcp.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("dhcp.j2")

        result = template.render(**mock_node_variables)
        assert len(result) > 0, "Rendered template should not be empty"

    def test_dhcp_template_defines_dnsmasq(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that rendered DHCP template defines dnsmasq settings."""
        template_path = role_paths["dhcp_config"] / "templates" / "dhcp.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("dhcp.j2")

        result = template.render(**mock_node_variables)
        assert "dnsmasq" in result.lower(), "DHCP template should define dnsmasq"

    def test_dhcp_template_contains_pool_settings(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that rendered DHCP template contains pool settings."""
        template_path = role_paths["dhcp_config"] / "templates" / "dhcp.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("dhcp.j2")

        result = template.render(**mock_node_variables)
        # Should contain DHCP pool configuration
        assert "start" in result or "limit" in result, "DHCP template should define pool"


@pytest.mark.unit
class TestFirewallTemplateRendering:
    """Tests for firewall.j2 template rendering."""

    def test_firewall_template_renders(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that firewall.j2 template renders without errors."""
        template_path = role_paths["firewall_config"] / "templates" / "firewall.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("firewall.j2")

        result = template.render(**mock_node_variables)
        assert len(result) > 0, "Rendered template should not be empty"

    def test_firewall_template_defines_zones(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that rendered firewall template defines zones."""
        template_path = role_paths["firewall_config"] / "templates" / "firewall.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("firewall.j2")

        result = template.render(**mock_node_variables)
        assert "config zone" in result, "Firewall template should define zones"

    def test_firewall_template_defines_defaults(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that rendered firewall template defines defaults."""
        template_path = role_paths["firewall_config"] / "templates" / "firewall.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("firewall.j2")

        result = template.render(**mock_node_variables)
        assert "config defaults" in result, "Firewall template should define defaults"


@pytest.mark.unit
class TestTemplateVariableSubstitution:
    """Tests for proper variable substitution in templates."""

    def test_different_nodes_produce_different_output(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that different node variables produce different output."""
        template_path = role_paths["network_config"] / "templates" / "network.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("network.j2")

        # Render for node1
        node1_vars = mock_node_variables.copy()
        node1_result = template.render(**node1_vars)

        # Render for node2
        node2_vars = mock_node_variables.copy()
        node2_vars["inventory_hostname"] = "node2"
        node2_vars["node_ip"] = "10.11.12.2"
        node2_vars["node_number"] = 2
        node2_result = template.render(**node2_vars)

        # Results should be different
        assert node1_result != node2_result, "Different nodes should produce different configs"
        assert "10.11.12.1" in node1_result, "Node1 config should have node1 IP"
        assert "10.11.12.2" in node2_result, "Node2 config should have node2 IP"

    def test_no_undefined_variables_in_output(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that rendered templates don't contain undefined variable markers."""
        templates = {
            "network_config": "network.j2",
            "wireless_config": "wireless.j2",
            "dhcp_config": "dhcp.j2",
            "firewall_config": "firewall.j2",
        }

        for role_name, template_name in templates.items():
            template_path = role_paths[role_name] / "templates" / template_name
            env = Environment(loader=FileSystemLoader(str(template_path.parent)))
            template = env.get_template(template_name)

            result = template.render(**mock_node_variables)

            # Check for Jinja2 undefined markers
            assert "{{" not in result, f"{template_name} has unrendered variables"
            assert "}}" not in result, f"{template_name} has unrendered variables"
            assert "undefined" not in result.lower(), f"{template_name} has undefined references"


@pytest.mark.unit
class TestTemplateOutputFormat:
    """Tests for template output format (UCI format)."""

    def test_network_template_uci_format(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that network template produces valid UCI format."""
        template_path = role_paths["network_config"] / "templates" / "network.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("network.j2")

        result = template.render(**mock_node_variables)

        # UCI format checks - templates may have header comments
        # Find first non-comment, non-empty line
        first_config_found = False
        lines = result.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                if stripped.startswith("config "):
                    first_config_found = True
                    break
                # Skip empty lines before first config
                if stripped:
                    break

        assert first_config_found, "UCI file should contain config sections"

        # Check for proper option format
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                # Should be config, option, list, or empty tab-indented
                valid_starts = ("config ", "option ", "list ", "\t")
                assert (
                    any(
                        stripped.startswith(start) or line.startswith("\t")
                        for start in valid_starts
                    )
                    or stripped == ""
                ), f"Invalid UCI line: {line}"

    def test_wireless_template_uci_format(
        self, role_paths: Dict[str, Path], mock_node_variables: Dict[str, Any]
    ) -> None:
        """Test that wireless template produces valid UCI format."""
        template_path = role_paths["wireless_config"] / "templates" / "wireless.j2"
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template("wireless.j2")

        result = template.render(**mock_node_variables)

        # UCI format checks
        assert "config wifi-device" in result, "Should have wifi-device config sections"
        assert "config wifi-iface" in result, "Should have wifi-iface config sections"
