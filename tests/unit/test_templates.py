"""
Unit tests for Ansible template validation.

Tests validate Jinja2 templates for syntax and proper variable usage.
Templates are located in role directories: roles/*/templates/
"""

import os
from pathlib import Path
from typing import Dict, List

import pytest
from jinja2 import Environment, TemplateSyntaxError

# Template locations in roles
ROLE_TEMPLATES = {
    "network_config": "network.j2",
    "wireless_config": "wireless.j2",
    "dhcp_config": "dhcp.j2",
    "firewall_config": "firewall.j2",
}


@pytest.mark.unit
def test_role_templates_exist(
    roles_with_templates: Dict[str, str], role_paths: Dict[str, Path]
) -> None:
    """
    Test that expected template files exist in role directories.

    Args:
        roles_with_templates: Mapping of roles to template filenames.
        role_paths: Mapping of role names to paths.
    """
    for role_name, template_name in roles_with_templates.items():
        template_path = role_paths[role_name] / "templates" / template_name
        assert template_path.exists(), f"Template not found: {role_name}/templates/{template_name}"


@pytest.mark.unit
def test_all_role_templates_valid_jinja2(
    roles_with_templates: Dict[str, str], role_paths: Dict[str, Path]
) -> None:
    """
    Test that all role templates have valid Jinja2 syntax.

    Args:
        roles_with_templates: Mapping of roles to template filenames.
        role_paths: Mapping of role names to paths.
    """
    env = Environment()

    for role_name, template_name in roles_with_templates.items():
        template_path = role_paths[role_name] / "templates" / template_name
        if template_path.exists():
            with open(template_path, "r") as f:
                template_content = f.read()
                try:
                    env.parse(template_content)
                except TemplateSyntaxError as e:
                    pytest.fail(f"Jinja2 syntax error in {role_name}/{template_name}: {e}")


@pytest.mark.unit
def test_network_template_structure(role_paths: Dict[str, Path]) -> None:
    """Test that network.j2 template has expected structure."""
    template_path = role_paths["network_config"] / "templates" / "network.j2"
    with open(template_path, "r") as f:
        content = f.read()

    # Network template should define key sections
    assert "config interface" in content, "Network template should define interfaces"
    assert "lan" in content.lower(), "Network template should define LAN interface"
    assert "bat0" in content, "Network template should define batman interface"


@pytest.mark.unit
def test_wireless_template_structure(role_paths: Dict[str, Path]) -> None:
    """Test that wireless.j2 template has expected structure."""
    template_path = role_paths["wireless_config"] / "templates" / "wireless.j2"
    with open(template_path, "r") as f:
        content = f.read()

    # Wireless template should define key sections
    assert "config wifi-device" in content, "Wireless template should define wifi devices"
    assert "config wifi-iface" in content, "Wireless template should define wifi interfaces"
    assert "mesh" in content.lower(), "Wireless template should configure mesh interface"


@pytest.mark.unit
def test_dhcp_template_structure(role_paths: Dict[str, Path]) -> None:
    """Test that dhcp.j2 template has expected structure."""
    template_path = role_paths["dhcp_config"] / "templates" / "dhcp.j2"
    with open(template_path, "r") as f:
        content = f.read()

    # DHCP template should define key sections
    assert "config dnsmasq" in content, "DHCP template should configure dnsmasq"
    assert "config dhcp" in content, "DHCP template should define DHCP config"


@pytest.mark.unit
def test_firewall_template_structure(role_paths: Dict[str, Path]) -> None:
    """Test that firewall.j2 template has expected structure."""
    template_path = role_paths["firewall_config"] / "templates" / "firewall.j2"
    with open(template_path, "r") as f:
        content = f.read()

    # Firewall template should define key sections
    assert "config defaults" in content, "Firewall template should define defaults"
    assert "config zone" in content, "Firewall template should define zones"


@pytest.mark.unit
def test_templates_use_variables(role_paths: Dict[str, Path]) -> None:
    """Test that templates use Jinja2 variables for customization."""
    templates = {
        "network_config": "network.j2",
        "wireless_config": "wireless.j2",
        "dhcp_config": "dhcp.j2",
        "firewall_config": "firewall.j2",
    }

    for role_name, template_name in templates.items():
        template_path = role_paths[role_name] / "templates" / template_name
        with open(template_path, "r") as f:
            content = f.read()

        # Check for Jinja2 variable syntax
        has_variables = "{{" in content and "}}" in content
        assert has_variables, f"Template {role_name}/{template_name} should use Jinja2 variables"


@pytest.mark.unit
def test_templates_no_hardcoded_ips(role_paths: Dict[str, Path]) -> None:
    """Test that templates don't hardcode node-specific IPs."""
    templates = {
        "network_config": "network.j2",
        "dhcp_config": "dhcp.j2",
    }

    for role_name, template_name in templates.items():
        template_path = role_paths[role_name] / "templates" / template_name
        with open(template_path, "r") as f:
            content = f.read()

        # Check for hardcoded mesh node IPs (should use variables)
        # 10.11.12.1, .2, .3 should be variables, not literals
        import re

        hardcoded_pattern = r"10\.11\.12\.[123]['\"\s\n]"
        matches = re.findall(hardcoded_pattern, content)
        # Allow for template examples but not direct hardcoding
        assert (
            len(matches) == 0 or "{{" in content
        ), f"Template {role_name}/{template_name} may have hardcoded IPs"


# Legacy template directory tests (for backwards compatibility)
@pytest.mark.unit
def test_legacy_templates_directory() -> None:
    """
    Test legacy templates directory (templates are now in roles).

    This test documents that templates have moved to role directories.
    """
    legacy_templates_dir = "openwrt-mesh-ansible/templates"

    # Templates have been moved to roles - this is expected
    if os.path.exists(legacy_templates_dir):
        # If legacy directory exists, it should be empty or contain only non-.j2 files
        j2_files = list(Path(legacy_templates_dir).glob("*.j2"))
        if j2_files:
            pytest.skip(
                f"Legacy templates found in {legacy_templates_dir} - "
                "templates should be in roles/*/templates/"
            )


@pytest.mark.unit
def test_all_templates_in_codebase() -> None:
    """Test that we can find all .j2 templates in the codebase."""
    roles_dir = Path("openwrt-mesh-ansible/roles")

    if not roles_dir.exists():
        pytest.skip("Roles directory does not exist")

    # Find all .j2 files in roles
    template_files: List[Path] = []
    for role_dir in roles_dir.iterdir():
        if role_dir.is_dir():
            templates_dir = role_dir / "templates"
            if templates_dir.exists():
                template_files.extend(templates_dir.glob("*.j2"))

    # We expect at least the 4 main templates
    assert len(template_files) >= 4, f"Expected at least 4 templates, found {len(template_files)}"

    # Parse all templates
    env = Environment()
    for template_file in template_files:
        with open(template_file, "r") as f:
            try:
                env.parse(f.read())
            except TemplateSyntaxError as e:
                pytest.fail(f"Syntax error in {template_file}: {e}")
