"""
Live infrastructure connectivity tests.

Tests connectivity to switches and infrastructure devices on the management network.
These tests verify that network infrastructure is reachable from mesh nodes.
"""

import pytest

from .conftest import NodeExecutor, run_local

# Infrastructure device configuration
# Management network: 10.11.10.0/24
SWITCHES = {
    "switch_a": {
        "name": "Switch A",
        "ip": "10.11.10.11",
        "description": "Primary mesh switch (Node1-Node2 wired link)",
    },
    "switch_b": {
        "name": "Switch B",
        "ip": "10.11.10.12",
        "description": "Secondary mesh switch (Node2-Node3 and Node3-Node1 wired links)",
    },
    "switch_c": {
        "name": "Switch C",
        "ip": "10.11.10.13",
        "description": "Infrastructure switch (IoT devices, Proxmox cluster)",
    },
}

INFRASTRUCTURE_DEVICES = {
    "rpi_qdevice": {
        "name": "RPi QDevice",
        "ip": "10.11.10.20",
        "description": "Raspberry Pi - Proxmox cluster quorum device",
    },
    "proxmox1": {
        "name": "Proxmox Node 1",
        "ip": "10.11.10.21",
        "description": "Proxmox virtualization host 1",
    },
    "proxmox2": {
        "name": "Proxmox Node 2",
        "ip": "10.11.10.22",
        "description": "Proxmox virtualization host 2",
    },
}


def parse_ping_stats(stdout: str) -> tuple[int, int, float]:
    """Parse ping output to extract transmitted, received, and loss percentage.

    Returns:
        Tuple of (transmitted, received, loss_percent)
    """
    import re

    match = re.search(r"(\d+) packets transmitted, (\d+) received", stdout)
    if match:
        transmitted = int(match.group(1))
        received = int(match.group(2))
        loss = ((transmitted - received) / transmitted) * 100 if transmitted > 0 else 100.0
        return transmitted, received, loss
    return 0, 0, 100.0


@pytest.mark.live
@pytest.mark.infrastructure
class TestSwitchConnectivity:
    """Test connectivity to all network switches.

    Switches are on the management VLAN (10) at 10.11.10.x.
    Tests ping from local machine (must be on management network or have route).
    """

    def test_ping_switch_a(self) -> None:
        """Test ping to Switch A (10.11.10.11)."""
        switch = SWITCHES["switch_a"]
        rc, stdout, _ = run_local(f"ping -c 3 -W 2 {switch['ip']}")
        transmitted, received, loss = parse_ping_stats(stdout)
        assert received >= 1, f"Cannot ping {switch['name']} at {switch['ip']}"
        assert loss <= 50, f"High packet loss to {switch['name']}: {loss:.1f}%"

    def test_ping_switch_b(self) -> None:
        """Test ping to Switch B (10.11.10.12)."""
        switch = SWITCHES["switch_b"]
        rc, stdout, _ = run_local(f"ping -c 3 -W 2 {switch['ip']}")
        transmitted, received, loss = parse_ping_stats(stdout)
        assert received >= 1, f"Cannot ping {switch['name']} at {switch['ip']}"
        assert loss <= 50, f"High packet loss to {switch['name']}: {loss:.1f}%"

    def test_ping_switch_c(self) -> None:
        """Test ping to Switch C (10.11.10.13)."""
        switch = SWITCHES["switch_c"]
        rc, stdout, _ = run_local(f"ping -c 3 -W 2 {switch['ip']}")
        transmitted, received, loss = parse_ping_stats(stdout)
        assert received >= 1, f"Cannot ping {switch['name']} at {switch['ip']}"
        assert loss <= 50, f"High packet loss to {switch['name']}: {loss:.1f}%"

    def test_all_switches_reachable(self) -> None:
        """Test that all switches are reachable."""
        unreachable = []
        for switch in SWITCHES.values():
            rc, _, _ = run_local(f"ping -c 1 -W 2 {switch['ip']}")
            if rc != 0:
                unreachable.append(f"{switch['name']} ({switch['ip']})")

        assert not unreachable, f"Unreachable switches: {', '.join(unreachable)}"


@pytest.mark.live
@pytest.mark.infrastructure
class TestSwitchConnectivityFromNodes:
    """Test that mesh nodes can reach all switches.

    Nodes should be able to ping switches via the management bridge interface.
    """

    def test_node1_can_ping_all_switches(self, node1: NodeExecutor) -> None:
        """Test node1 can ping all switches."""
        for switch in SWITCHES.values():
            assert node1.ping(switch["ip"]), f"node1 cannot ping {switch['name']}"

    def test_node2_can_ping_all_switches(self, node2: NodeExecutor) -> None:
        """Test node2 can ping all switches."""
        for switch in SWITCHES.values():
            assert node2.ping(switch["ip"]), f"node2 cannot ping {switch['name']}"

    def test_node3_can_ping_all_switches(self, node3: NodeExecutor) -> None:
        """Test node3 can ping all switches."""
        for switch in SWITCHES.values():
            assert node3.ping(switch["ip"]), f"node3 cannot ping {switch['name']}"


@pytest.mark.live
@pytest.mark.infrastructure
class TestInfrastructureConnectivity:
    """Test connectivity to infrastructure devices (RPi, Proxmox nodes).

    Infrastructure devices are on management VLAN 10.
    These tests may be skipped if devices are not yet deployed.
    """

    def test_ping_rpi_qdevice(self) -> None:
        """Test ping to Raspberry Pi QDevice (10.11.10.20)."""
        device = INFRASTRUCTURE_DEVICES["rpi_qdevice"]
        rc, stdout, _ = run_local(f"ping -c 3 -W 2 {device['ip']}")
        if rc != 0:
            pytest.skip(f"{device['name']} not deployed yet")
        transmitted, received, loss = parse_ping_stats(stdout)
        assert received >= 1, f"Cannot ping {device['name']} at {device['ip']}"

    def test_ping_proxmox1(self) -> None:
        """Test ping to Proxmox Node 1 (10.11.10.21)."""
        device = INFRASTRUCTURE_DEVICES["proxmox1"]
        rc, stdout, _ = run_local(f"ping -c 3 -W 2 {device['ip']}")
        if rc != 0:
            pytest.skip(f"{device['name']} not deployed yet")
        transmitted, received, loss = parse_ping_stats(stdout)
        assert received >= 1, f"Cannot ping {device['name']} at {device['ip']}"

    def test_ping_proxmox2(self) -> None:
        """Test ping to Proxmox Node 2 (10.11.10.22)."""
        device = INFRASTRUCTURE_DEVICES["proxmox2"]
        rc, stdout, _ = run_local(f"ping -c 3 -W 2 {device['ip']}")
        if rc != 0:
            pytest.skip(f"{device['name']} not deployed yet")
        transmitted, received, loss = parse_ping_stats(stdout)
        assert received >= 1, f"Cannot ping {device['name']} at {device['ip']}"


@pytest.mark.live
@pytest.mark.infrastructure
class TestInfrastructureConnectivityFromNodes:
    """Test that mesh nodes can reach infrastructure devices."""

    def test_node1_can_ping_infrastructure(self, node1: NodeExecutor) -> None:
        """Test node1 can ping all infrastructure devices."""
        for device in INFRASTRUCTURE_DEVICES.values():
            # Skip if device not responding (not deployed yet)
            rc, _, _ = run_local(f"ping -c 1 -W 1 {device['ip']}")
            if rc != 0:
                continue
            assert node1.ping(device["ip"]), f"node1 cannot ping {device['name']}"

    def test_node2_can_ping_infrastructure(self, node2: NodeExecutor) -> None:
        """Test node2 can ping all infrastructure devices."""
        for device in INFRASTRUCTURE_DEVICES.values():
            rc, _, _ = run_local(f"ping -c 1 -W 1 {device['ip']}")
            if rc != 0:
                continue
            assert node2.ping(device["ip"]), f"node2 cannot ping {device['name']}"

    def test_node3_can_ping_infrastructure(self, node3: NodeExecutor) -> None:
        """Test node3 can ping all infrastructure devices."""
        for device in INFRASTRUCTURE_DEVICES.values():
            rc, _, _ = run_local(f"ping -c 1 -W 1 {device['ip']}")
            if rc != 0:
                continue
            assert node3.ping(device["ip"]), f"node3 cannot ping {device['name']}"


@pytest.mark.live
@pytest.mark.infrastructure
class TestManagementNetworkRouting:
    """Test that management network (10.11.10.0/24) is properly routed."""

    def test_node1_has_management_interface(self, node1: NodeExecutor) -> None:
        """Verify node1 has management bridge configured."""
        output = node1.run_ok("ip addr show br-management_bridge 2>/dev/null || echo 'not found'")
        if "not found" in output:
            pytest.skip("Management bridge not configured on node1")
        assert "10.11.10.1" in output, "node1 missing management IP 10.11.10.1"

    def test_node2_has_management_interface(self, node2: NodeExecutor) -> None:
        """Verify node2 has management bridge configured."""
        output = node2.run_ok("ip addr show br-management_bridge 2>/dev/null || echo 'not found'")
        if "not found" in output:
            pytest.skip("Management bridge not configured on node2")
        assert "10.11.10.2" in output, "node2 missing management IP 10.11.10.2"

    def test_node3_has_management_interface(self, node3: NodeExecutor) -> None:
        """Verify node3 has management bridge configured."""
        output = node3.run_ok("ip addr show br-management_bridge 2>/dev/null || echo 'not found'")
        if "not found" in output:
            pytest.skip("Management bridge not configured on node3")
        assert "10.11.10.3" in output, "node3 missing management IP 10.11.10.3"
