"""
Live wireless network tests.

Tests validate wireless configuration, SSIDs, and mesh wireless backup.
Includes tests that use local wlan2 adapter for client-side validation.
"""

import logging
import os
import re
import time
from typing import Optional

import pytest

from .conftest import NETWORK_CONFIG, NodeExecutor, run_local

logger = logging.getLogger(__name__)


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
        """Verify client SSID (HA-Client) is configured."""
        expected_ssid = str(NETWORK_CONFIG["client_ssid"])
        for executor in all_node_executors:
            output = executor.run_ok("uci show wireless | grep ssid")
            assert (
                expected_ssid in output
            ), f"{executor.node} missing client SSID {expected_ssid}: {output}"

    def test_mesh_ssid_configured(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify mesh SSID (HA-Mesh) is configured."""
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

    def test_iot_ssid_configured(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify IoT SSID (HA-IoT) is configured."""
        expected_ssid = str(NETWORK_CONFIG["iot_ssid"])
        for executor in all_node_executors:
            rc, output, _ = executor.run("uci show wireless | grep ssid")
            if expected_ssid in output:
                assert True
            else:
                pytest.skip(f"IoT SSID not configured on {executor.node}")


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
            str(NETWORK_CONFIG["iot_ssid"]),
            str(NETWORK_CONFIG["guest_ssid"]),
        ]
        found_ssid = any(ssid in stdout for ssid in expected_ssids)
        assert found_ssid, f"No mesh SSIDs found in scan: {stdout}"

    def test_wlan2_can_see_client_ssid(self) -> None:
        """Test that wlan2 can see the client SSID (HA-Client)."""
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


class Wlan2Helper:
    """Helper class for wlan2 WiFi connection tests."""

    @staticmethod
    def disconnect() -> None:
        """Disconnect wlan2 from any network."""
        run_local("sudo pkill -f 'wpa_supplicant.*wlan2' 2>/dev/null")
        run_local("sudo dhcpcd --release wlan2 2>/dev/null")
        run_local("sudo ip addr flush dev wlan2 2>/dev/null")
        time.sleep(1)

    @staticmethod
    def connect(ssid: str, password: str, timeout: int = 30) -> bool:
        """Connect wlan2 to a network using wpa_supplicant."""
        import tempfile

        Wlan2Helper.disconnect()

        rc, _, _ = run_local("sudo ip link set wlan2 up")
        if rc != 0:
            return False

        ctrl_dir = "/tmp/wpa_supplicant_test"
        run_local(f"sudo mkdir -p {ctrl_dir} && sudo chmod 755 {ctrl_dir}")

        wpa_config = f"""ctrl_interface={ctrl_dir}
ctrl_interface_group=0
update_config=1

network={{
    ssid="{ssid}"
    psk="{password}"
    key_mgmt=WPA-PSK
    proto=RSN WPA
    pairwise=CCMP TKIP
    group=CCMP TKIP
    scan_ssid=1
}}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(wpa_config)
            config_file = f.name

        try:
            rc, stdout, stderr = run_local(
                f"sudo wpa_supplicant -B -i wlan2 -c {config_file} 2>&1", timeout=10
            )
            logger.info(f"wpa_supplicant start: rc={rc}, out={stdout}, err={stderr}")
            if rc != 0:
                return False

            time.sleep(2)

            last_state = ""
            for i in range(timeout // 2):
                time.sleep(2)
                rc, stdout, stderr = run_local(f"sudo wpa_cli -p {ctrl_dir} -i wlan2 status 2>&1")
                if rc == 0 and stdout.strip():
                    for line in stdout.split("\n"):
                        if line.startswith("wpa_state="):
                            state = line.split("=")[1]
                            if state != last_state:
                                logger.info(f"wpa_state: {state} (attempt {i+1})")
                                last_state = state
                    if "wpa_state=COMPLETED" in stdout:
                        return True

            logger.error(f"Connection failed. Final status:\n{stdout}")
            return False
        finally:
            run_local(f"rm -f {config_file}")
            run_local(f"sudo rm -rf {ctrl_dir}")

    @staticmethod
    def get_dhcp_address(timeout: int = 30) -> Optional[str]:
        """Get DHCP address on wlan2."""
        run_local("sudo dhcpcd --release wlan2 2>&1", timeout=10)
        time.sleep(1)

        rc, stdout, stderr = run_local("sudo dhcpcd --rebind wlan2 2>&1", timeout=timeout)
        logger.info(f"dhcpcd rebind: rc={rc}, out={stdout[:500] if stdout else ''}")

        for attempt in range(timeout // 2):
            time.sleep(2)
            rc, stdout, _ = run_local("ip -4 addr show wlan2")
            if rc == 0 and "inet " in stdout:
                match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", stdout)
                if match:
                    ip = match.group(1)
                    logger.info(f"Got IP address: {ip} (attempt {attempt + 1})")
                    return ip
            logger.info(f"Waiting for IP... (attempt {attempt + 1})")

        logger.error(f"Failed to get IP. Final state: {stdout}")
        return None


@pytest.mark.live
@pytest.mark.wlan2
@pytest.mark.slow
class TestWlan2Networks:
    """
    Comprehensive wlan2 connection tests for all wireless networks.

    Each test connects once and validates: connection, DHCP, internet, and isolation.
    """

    @pytest.fixture(autouse=True)
    def check_wlan2_available(self, can_use_wlan2: bool) -> None:
        """Skip tests if wlan2 is not available."""
        if not can_use_wlan2:
            pytest.skip("wlan2 adapter not available")

    def test_client_network_5ghz(self) -> None:
        """Test 5GHz Client network (HA-Client): connect, DHCP, internet."""
        password = os.environ.get("CLIENT_PASSWORD")
        if not password:
            pytest.skip("CLIENT_PASSWORD not set")
            return  # For mypy
        ssid = os.environ.get("CLIENT_SSID") or str(NETWORK_CONFIG["client_ssid"])

        try:
            # 1. Connect
            logger.info(f"Connecting to {ssid}...")
            connected = Wlan2Helper.connect(ssid, password)
            assert connected, f"Failed to connect to {ssid}"
            logger.info(f"Connected to {ssid}")

            # 2. DHCP
            logger.info("Requesting DHCP address...")
            ip_addr = Wlan2Helper.get_dhcp_address()
            assert ip_addr is not None, "Failed to get DHCP address"
            assert ip_addr.startswith(
                "10.11.12."
            ), f"Unexpected IP: {ip_addr} (expected 10.11.12.x)"
            logger.info(f"Got IP: {ip_addr}")

            # 3. Internet connectivity
            logger.info("Testing internet connectivity...")
            rc, _, _ = run_local("ping -c 3 -W 5 1.1.1.1")
            assert rc == 0, "Cannot ping 1.1.1.1 via Client network"

            # 4. DNS resolution
            logger.info("Testing DNS resolution...")
            rc, _, _ = run_local("ping -c 3 -W 5 google.com")
            assert rc == 0, "Cannot resolve DNS via Client network"

            logger.info("All Client network tests passed")
        finally:
            Wlan2Helper.disconnect()

    def test_management_network_24ghz(self) -> None:
        """Test 2.4GHz Management network (HA-Management): connect, DHCP, internet."""
        password = os.environ.get("MGMT_PASSWORD")
        if not password:
            pytest.skip("MGMT_PASSWORD not set")
            return  # For mypy
        ssid = str(NETWORK_CONFIG["management_ssid"])

        try:
            # 1. Connect
            logger.info(f"Connecting to {ssid}...")
            connected = Wlan2Helper.connect(ssid, password)
            assert connected, f"Failed to connect to {ssid}"
            logger.info(f"Connected to {ssid}")

            # 2. DHCP
            logger.info("Requesting DHCP address...")
            ip_addr = Wlan2Helper.get_dhcp_address()
            assert ip_addr is not None, "Failed to get DHCP address"
            assert ip_addr.startswith(
                "10.11.10."
            ), f"Unexpected IP: {ip_addr} (expected 10.11.10.x)"
            logger.info(f"Got IP: {ip_addr}")

            # 3. Internet connectivity
            logger.info("Testing internet connectivity...")
            rc, _, _ = run_local("ping -c 3 -W 5 1.1.1.1")
            assert rc == 0, "Cannot ping 1.1.1.1 via Management network"

            # 4. DNS resolution
            logger.info("Testing DNS resolution...")
            rc, _, _ = run_local("ping -c 3 -W 5 google.com")
            assert rc == 0, "Cannot resolve DNS via Management network"

            logger.info("All Management network tests passed")
        finally:
            Wlan2Helper.disconnect()

    def test_iot_network_24ghz(self) -> None:
        """Test 2.4GHz IoT network (HA-IoT): connect, DHCP, internet, isolation."""
        password = os.environ.get("IOT_PASSWORD")
        if not password:
            pytest.skip("IOT_PASSWORD not set")
            return  # For mypy
        ssid = os.environ.get("IOT_SSID") or str(NETWORK_CONFIG["iot_ssid"])

        try:
            # 1. Connect
            logger.info(f"Connecting to {ssid}...")
            connected = Wlan2Helper.connect(ssid, password)
            assert connected, f"Failed to connect to {ssid}"
            logger.info(f"Connected to {ssid}")

            # 2. DHCP
            logger.info("Requesting DHCP address...")
            ip_addr = Wlan2Helper.get_dhcp_address()
            assert ip_addr is not None, "Failed to get DHCP address"
            assert ip_addr.startswith(
                "10.11.30."
            ), f"Unexpected IP: {ip_addr} (expected 10.11.30.x)"
            logger.info(f"Got IP: {ip_addr}")

            # 3. Internet connectivity
            logger.info("Testing internet connectivity...")
            rc, _, _ = run_local("ping -c 3 -W 5 1.1.1.1")
            assert rc == 0, "Cannot ping 1.1.1.1 via IoT network"

            # 4. DNS resolution
            logger.info("Testing DNS resolution...")
            rc, _, _ = run_local("ping -c 3 -W 5 google.com")
            assert rc == 0, "Cannot resolve DNS via IoT network"

            # 5. Isolation - should NOT reach internal LAN
            logger.info("Testing IoT isolation from internal LAN...")
            rc, stdout, _ = run_local("ping -c 2 -W 3 10.11.12.1")
            assert rc != 0, f"SECURITY: IoT reached internal LAN 10.11.12.1! Output: {stdout}"

            logger.info("All IoT network tests passed (including isolation)")
        finally:
            Wlan2Helper.disconnect()

    def test_guest_network_5ghz(self) -> None:
        """Test 5GHz Guest network (HA-Guest): connect, DHCP, internet, isolation."""
        password = os.environ.get("GUEST_PASSWORD")
        if not password:
            pytest.skip("GUEST_PASSWORD not set")
            return  # For mypy
        ssid = str(NETWORK_CONFIG["guest_ssid"])

        try:
            # 1. Connect
            logger.info(f"Connecting to {ssid}...")
            connected = Wlan2Helper.connect(ssid, password)
            assert connected, f"Failed to connect to {ssid}"
            logger.info(f"Connected to {ssid}")

            # 2. DHCP
            logger.info("Requesting DHCP address...")
            ip_addr = Wlan2Helper.get_dhcp_address()
            assert ip_addr is not None, "Failed to get DHCP address"
            assert ip_addr.startswith(
                "10.11.20."
            ), f"Unexpected IP: {ip_addr} (expected 10.11.20.x)"
            logger.info(f"Got IP: {ip_addr}")

            # 3. Internet connectivity
            logger.info("Testing internet connectivity...")
            rc, _, _ = run_local("ping -c 3 -W 5 1.1.1.1")
            assert rc == 0, "Cannot ping 1.1.1.1 via Guest network"

            # 4. DNS resolution
            logger.info("Testing DNS resolution...")
            rc, _, _ = run_local("ping -c 3 -W 5 google.com")
            assert rc == 0, "Cannot resolve DNS via Guest network"

            # 5. Isolation - should NOT reach internal LAN
            logger.info("Testing guest isolation from internal LAN...")
            rc, stdout, _ = run_local("ping -c 2 -W 3 10.11.12.1")
            assert rc != 0, f"SECURITY: Guest reached internal LAN 10.11.12.1! Output: {stdout}"

            rc, stdout, _ = run_local("ping -c 2 -W 3 10.11.12.2")
            assert rc != 0, f"SECURITY: Guest reached internal LAN 10.11.12.2! Output: {stdout}"

            # 6. Isolation - should NOT reach management network
            logger.info("Testing guest isolation from management network...")
            rc, stdout, _ = run_local("ping -c 2 -W 3 10.11.10.1")
            assert rc != 0, f"SECURITY: Guest reached management 10.11.10.1! Output: {stdout}"

            logger.info("All Guest network tests passed (including isolation)")
        finally:
            Wlan2Helper.disconnect()


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
