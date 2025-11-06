"""
Shared pytest fixtures for all test modules.

This module provides common fixtures for testing the mesh network deployment:
- Node connection fixtures
- SSH client fixtures
- Configuration fixtures
- Cleanup fixtures
"""

import os
from typing import Any, Dict, Generator, List

import pytest


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
        "mesh_id": "ha-mesh-net",
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
        "ssid": "HA-Network-5G",
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
