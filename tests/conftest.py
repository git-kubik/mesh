"""
Shared pytest fixtures for all test modules.

This module provides common fixtures for testing the mesh network deployment:
- Node connection fixtures
- SSH client fixtures
- Configuration fixtures
- Role fixtures
- Cleanup fixtures
"""

import os
from pathlib import Path
from typing import Any, Dict, Generator, List

import pytest

# Base paths
ANSIBLE_ROOT = Path("openwrt-mesh-ansible")
ROLES_ROOT = ANSIBLE_ROOT / "roles"
HANDLERS_ROOT = ANSIBLE_ROOT / "handlers"


@pytest.fixture
def ansible_root() -> Path:
    """
    Provide path to Ansible project root.

    Returns:
        Path to openwrt-mesh-ansible directory.
    """
    return ANSIBLE_ROOT


@pytest.fixture
def roles_root() -> Path:
    """
    Provide path to roles directory.

    Returns:
        Path to roles directory.
    """
    return ROLES_ROOT


@pytest.fixture
def all_role_names() -> List[str]:
    """
    Provide list of all role names.

    Returns:
        List of all role directory names.
    """
    return [
        "backup",
        "package_management",
        "ssh_transition",
        "system_config",
        "network_config",
        "wireless_config",
        "dhcp_config",
        "firewall_config",
        "usb_storage",
    ]


@pytest.fixture
def role_paths(all_role_names: List[str]) -> Dict[str, Path]:
    """
    Provide paths to all role directories.

    Args:
        all_role_names: List of role names from fixture.

    Returns:
        Dictionary mapping role names to their directory paths.
    """
    return {name: ROLES_ROOT / name for name in all_role_names}


@pytest.fixture
def roles_with_templates() -> Dict[str, str]:
    """
    Provide mapping of roles to their template files.

    Returns:
        Dictionary mapping role names to template filenames.
    """
    return {
        "network_config": "network.j2",
        "wireless_config": "wireless.j2",
        "dhcp_config": "dhcp.j2",
        "firewall_config": "firewall.j2",
    }


@pytest.fixture
def ssh_transition_subtasks() -> List[str]:
    """
    Provide list of ssh_transition role subtask files.

    Returns:
        List of subtask filenames for ssh_transition role.
    """
    return [
        "move_dropbear.yml",
        "generate_keys.yml",
        "deploy_keys.yml",
        "configure_openssh.yml",
        "start_openssh.yml",
        "cleanup_dropbear.yml",
    ]


@pytest.fixture
def usb_storage_subtasks() -> List[str]:
    """
    Provide list of usb_storage role subtask files.

    Returns:
        List of subtask filenames for usb_storage role.
    """
    return [
        "detect.yml",
        "partition.yml",
        "format.yml",
        "mount.yml",
        "configure_persistent.yml",
    ]


@pytest.fixture
def handlers_path() -> Path:
    """
    Provide path to centralized handlers.

    Returns:
        Path to handlers directory.
    """
    return HANDLERS_ROOT


@pytest.fixture
def mesh_network_config() -> Dict[str, Any]:
    """
    Provide mesh network configuration.

    Returns:
        Dictionary containing mesh network settings including IPs, network, and gateway.
    """
    return {
        "network": "10.11.12.0",
        "netmask": "255.255.255.0",
        "cidr": 24,
        "gateway": "10.11.12.1",
        "nodes": ["10.11.12.1", "10.11.12.2", "10.11.12.3"],
    }


@pytest.fixture
def node_ips() -> List[str]:
    """
    Provide list of node IP addresses.

    Returns:
        List of IP addresses for all mesh nodes.
    """
    return ["10.11.12.1", "10.11.12.2", "10.11.12.3"]


@pytest.fixture
def inventory_path() -> str:
    """
    Provide path to Ansible inventory file.

    Returns:
        Absolute path to hosts.yml inventory file.
    """
    return os.path.abspath("openwrt-mesh-ansible/inventory/hosts.yml")


@pytest.fixture
def group_vars_path() -> str:
    """
    Provide path to Ansible group_vars file.

    Returns:
        Absolute path to all.yml group variables file.
    """
    return os.path.abspath("openwrt-mesh-ansible/group_vars/all.yml")


@pytest.fixture
def playbook_paths() -> Dict[str, str]:
    """
    Provide paths to all Ansible playbooks.

    Returns:
        Dictionary mapping playbook names to their absolute file paths.
    """
    return {
        "deploy": os.path.abspath("openwrt-mesh-ansible/playbooks/deploy.yml"),
        "verify": os.path.abspath("openwrt-mesh-ansible/playbooks/verify.yml"),
        "backup": os.path.abspath("openwrt-mesh-ansible/playbooks/backup.yml"),
        "update": os.path.abspath("openwrt-mesh-ansible/playbooks/update.yml"),
    }


@pytest.fixture
def batman_config() -> Dict[str, Any]:
    """
    Provide Batman-adv configuration.

    Returns:
        Dictionary containing Batman-adv routing settings.
    """
    return {
        "routing_algo": "BATMAN_V",
        "gw_bandwidth": "100000/100000",
        "orig_interval": 1000,
        "hop_penalty": 15,
    }


@pytest.fixture
def mesh_wireless_config() -> Dict[str, Any]:
    """
    Provide mesh wireless configuration (2.4GHz).

    Returns:
        Dictionary containing mesh wireless settings.
    """
    return {
        "mesh_id": "HA-Mesh",
        "encryption": "sae",
        "channel": 6,
        "htmode": "HT40",
        "mcast_rate": 24000,
    }


@pytest.fixture
def client_wireless_config() -> Dict[str, Any]:
    """
    Provide client wireless configuration (5GHz AP).

    Returns:
        Dictionary containing client AP wireless settings.
    """
    return {
        "ssid": "HA-Client",
        "encryption": "psk2+ccmp",
        "channel": 36,
        "htmode": "VHT80",
        "country": "AU",
    }


@pytest.fixture(scope="session")
def ssh_client() -> Generator[Any, None, None]:
    """
    Provide SSH client for node connections (requires paramiko).

    This fixture is session-scoped to reuse connections across tests.
    Yields SSH client that can connect to mesh nodes.

    Yields:
        SSH client object (paramiko.SSHClient when available).
    """
    pytest.skip("SSH client requires paramiko and node access", allow_module_level=False)
    yield None


@pytest.fixture
def cleanup_test_files() -> Generator[List[str], None, None]:
    """
    Track and cleanup test files created during tests.

    Yields a list that tests can append file paths to for cleanup.

    Yields:
        List of file paths to be cleaned up after test execution.
    """
    files_to_cleanup: List[str] = []
    yield files_to_cleanup

    # Cleanup after test
    import os

    for filepath in files_to_cleanup:
        if os.path.exists(filepath):
            os.remove(filepath)


# Pytest markers
def pytest_configure(config: Any) -> None:
    """
    Register custom pytest markers.

    Args:
        config: Pytest configuration object.
    """
    config.addinivalue_line("markers", "unit: Unit tests (no node access required)")
    config.addinivalue_line("markers", "integration: Integration tests (requires node access)")
    config.addinivalue_line("markers", "functional: Functional end-to-end tests")
    config.addinivalue_line("markers", "performance: Performance benchmark tests")
    config.addinivalue_line("markers", "failover: Failover scenario tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line("markers", "requires_nodes: Tests requiring physical nodes")
