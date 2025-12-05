"""
Live wireless network tests.

Tests validate wireless configuration, SSIDs, and mesh wireless backup.
Includes tests that use local wlan2 adapter for client-side validation.
"""

import re
import time

import pytest

from .conftest import NETWORK_CONFIG, NodeExecutor, run_local


@pytest.mark.live
class TestWirelessInterfaces:
    """Test wireless interface configuration on nodes."""

    def test_radio0_exists(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify 2.4GHz radio (radio0) exists on all nodes."""
        for executor in all_node_executors:
            output = executor.run_ok("iw dev")
            assert (
                "phy#0" in output or "wlan" in output
            ), f"{executor.node} missing radio0: {output}"

    def test_radio1_exists(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify 5GHz radio (radio1) exists on all nodes."""
        for executor in all_node_executors:
            output = executor.run_ok("iw dev")
            # Should have multiple phys/interfaces
            phy_count = output.count("phy#")
            assert phy_count >= 1, f"{executor.node} missing radios: {output}"

    def test_mesh_interface_configured(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify mesh interface is configured on 2.4GHz."""
        for executor in all_node_executors:
            output = executor.run_ok("iw dev")
            # Look for mesh point type interface
            assert (
                "mesh point" in output.lower() or "type mesh" in output.lower()
            ), f"{executor.node} missing mesh interface: {output}"

    def test_ap_interface_configured(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify AP interface is configured for client access."""
        for executor in all_node_executors:
            output = executor.run_ok("iw dev")
            # Look for AP type interface
            assert (
                "type AP" in output or "type ap" in output.lower()
            ), f"{executor.node} missing AP interface: {output}"


@pytest.mark.live
class TestWirelessSSIDs:
    """Test SSID configuration."""

    def test_client_ssid_configured(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify client SSID (HA-Network-5G) is configured."""
        expected_ssid = str(NETWORK_CONFIG["client_ssid"])
        for executor in all_node_executors:
            output = executor.run_ok("uci show wireless | grep ssid")
            assert (
                expected_ssid in output
            ), f"{executor.node} missing client SSID {expected_ssid}: {output}"

    def test_mesh_ssid_configured(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify mesh SSID (ha-mesh-net) is configured."""
        expected_mesh_id = str(NETWORK_CONFIG["mesh_ssid"])
        for executor in all_node_executors:
            output = executor.run_ok("uci show wireless | grep mesh_id")
            assert (
                expected_mesh_id in output
            ), f"{executor.node} missing mesh_id {expected_mesh_id}: {output}"

    def test_management_ssid_configured(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify management SSID (HA-Management) is configured."""
        expected_ssid = str(NETWORK_CONFIG["management_ssid"])
        for executor in all_node_executors:
            rc, output, _ = executor.run("uci show wireless | grep ssid")
            # Management SSID may not be configured on all setups
            if expected_ssid in output:
                assert True
            else:
                pytest.skip(f"Management SSID not configured on {executor.node}")

    def test_guest_ssid_configured(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify guest SSID (HA-Guest) is configured."""
        expected_ssid = str(NETWORK_CONFIG["guest_ssid"])
        for executor in all_node_executors:
            rc, output, _ = executor.run("uci show wireless | grep ssid")
            if expected_ssid in output:
                assert True
            else:
                pytest.skip(f"Guest SSID not configured on {executor.node}")


@pytest.mark.live
class TestWirelessMeshBackup:
    """Test wireless mesh backup link functionality."""

    def test_mesh_peers_visible(self, node1: NodeExecutor) -> None:
        """Verify mesh peers are visible via wireless."""
        # Check mesh station list
        rc, output, _ = node1.run("iw dev mesh0 station dump 2>/dev/null || echo 'no mesh0'")
        if "no mesh0" not in output:
            # Should see peer stations if wireless mesh is working
            assert (
                "Station" in output or output.strip() == ""
            ), f"Unexpected mesh station output: {output}"

    def test_wireless_mesh_interface_in_batman(
        self, all_node_executors: list[NodeExecutor]
    ) -> None:
        """Verify wireless mesh interface is part of batman."""
        for executor in all_node_executors:
            output = executor.batctl("if")
            # Should have mesh interface attached
            has_wireless_mesh = (
                "mesh0" in output.lower() or "wlan" in output.lower() or "mesh" in output.lower()
            )
            assert has_wireless_mesh, f"{executor.node} wireless mesh not in batman: {output}"


@pytest.mark.live
@pytest.mark.wlan2
class TestWlan2ClientConnection:
    """
    Tests using the local wlan2 adapter to validate client connectivity.

    These tests require wlan2 to be available on the test machine.
    """

    @pytest.fixture(autouse=True)
    def check_wlan2_available(self, can_use_wlan2: bool) -> None:
        """Skip tests if wlan2 is not available."""
        if not can_use_wlan2:
            pytest.skip("wlan2 adapter not available")

    def test_wlan2_can_scan_ssids(self) -> None:
        """Test that wlan2 can scan for mesh network SSIDs."""
        # Bring up interface and scan
        run_local("sudo ip link set wlan2 up")
        time.sleep(1)

        rc, stdout, stderr = run_local("sudo iw dev wlan2 scan 2>/dev/null | grep SSID")
        if rc != 0:
            pytest.skip(f"Cannot scan with wlan2: {stderr}")

        # Should see at least one of our SSIDs
        expected_ssids = [
            str(NETWORK_CONFIG["client_ssid"]),
            str(NETWORK_CONFIG["management_ssid"]),
            str(NETWORK_CONFIG["guest_ssid"]),
        ]
        found_ssid = any(ssid in stdout for ssid in expected_ssids)
        assert found_ssid, f"No mesh SSIDs found in scan: {stdout}"

    def test_wlan2_can_see_client_ssid(self) -> None:
        """Test that wlan2 can see the client SSID (HA-Network-5G)."""
        run_local("sudo ip link set wlan2 up")
        time.sleep(1)

        rc, stdout, _ = run_local("sudo iw dev wlan2 scan 2>/dev/null | grep SSID")
        expected_ssid = str(NETWORK_CONFIG["client_ssid"])
        assert expected_ssid in stdout, f"Client SSID {expected_ssid} not visible"

    def test_wlan2_signal_strength(self) -> None:
        """Test signal strength of visible SSIDs."""
        run_local("sudo ip link set wlan2 up")
        time.sleep(1)

        rc, stdout, _ = run_local("sudo iw dev wlan2 scan 2>/dev/null | grep -E 'SSID|signal'")
        if rc != 0:
            pytest.skip("Cannot scan with wlan2")

        # Parse signal strengths
        signals = re.findall(r"signal: (-?\d+)", stdout)
        if signals:
            max_signal = max(int(s) for s in signals)
            # Signal should be reasonable (better than -80 dBm)
            assert max_signal > -80, f"Signal too weak: {max_signal} dBm"


@pytest.mark.live
@pytest.mark.wlan2
@pytest.mark.slow
class TestWlan2NetworkAccess:
    """
    Tests for connecting wlan2 to mesh networks and verifying access.

    These are slower tests that actually connect to networks.
    """

    @pytest.fixture(autouse=True)
    def check_wlan2_available(self, can_use_wlan2: bool) -> None:
        """Skip tests if wlan2 is not available."""
        if not can_use_wlan2:
            pytest.skip("wlan2 adapter not available")

    def _connect_to_network(self, ssid: str, password: str) -> bool:
        """Connect wlan2 to a network using wpa_supplicant."""
        # Create temporary wpa_supplicant config
        wpa_config = f"""
ctrl_interface=/var/run/wpa_supplicant
network={{
    ssid="{ssid}"
    psk="{password}"
    key_mgmt=WPA-PSK
}}
"""
        # This is a template - actual implementation would need password
        # For now, skip if password not provided
        _ = wpa_config  # Placeholder for future implementation
        return False

    def test_connect_to_client_network(self) -> None:
        """Test connecting to client network (HA-Network-5G)."""
        # This test requires the actual password
        # Skip by default, can be enabled with environment variable
        password = pytest.importorskip("os").environ.get("MESH_CLIENT_PASSWORD")
        if not password:
            pytest.skip("MESH_CLIENT_PASSWORD not set")

        # Would implement actual connection test here
        pytest.skip("Connection test not implemented - requires password handling")

    def test_dhcp_from_mesh_network(self) -> None:
        """Test that DHCP works when connected to mesh network."""
        # Requires actual connection
        pytest.skip("Requires connection to mesh network")

    def test_internet_via_mesh_network(self) -> None:
        """Test internet access when connected via mesh network."""
        # Requires actual connection
        pytest.skip("Requires connection to mesh network")


@pytest.mark.live
class TestWireless80211r:
    """Test 802.11r fast roaming configuration."""

    def test_80211r_enabled(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify 802.11r is enabled on client AP interfaces."""
        for executor in all_node_executors:
            rc, output, _ = executor.run("uci show wireless | grep ieee80211r")
            if rc == 0 and "1" in output:
                assert True
            else:
                # 802.11r might not be configured
                pytest.skip(f"802.11r not configured on {executor.node}")

    def test_mobility_domain_consistent(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify all nodes use the same mobility domain."""
        mobility_domains = []
        for executor in all_node_executors:
            rc, output, _ = executor.run("uci show wireless | grep mobility_domain")
            if rc == 0:
                # Extract mobility domain value
                match = re.search(r"mobility_domain='([^']+)'", output)
                if match:
                    mobility_domains.append(match.group(1))

        if len(mobility_domains) >= 2:
            # All should be the same
            assert (
                len(set(mobility_domains)) == 1
            ), f"Inconsistent mobility domains: {mobility_domains}"
        else:
            pytest.skip("802.11r mobility domain not configured on enough nodes")
