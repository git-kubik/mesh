"""
Wireless validation checks.

Tier 4 (Certification):
- check_mesh_wireless: 802.11s mesh active
- check_roaming: 802.11r fast roaming configured
- check_bla: Bridge Loop Avoidance enabled
"""

from validate.config import NODES
from validate.core.executor import NodeExecutor
from validate.core.results import CheckResult, CheckStatus


def check_mesh_wireless() -> CheckResult:  # noqa: C901
    """
    Check wireless mesh configuration (802.11s or adhoc backup).

    Checks for:
    1. 802.11s mesh0 interface (primary wireless mesh)
    2. Or mesh-enabled wireless interface in batman-adv
    3. Wired-only mesh is valid (many deployments use wired backbone)

    Returns:
        CheckResult with wireless mesh status.
    """
    result = CheckResult(
        category="wireless.mesh",
        status=CheckStatus.PASS,
        message="",
    )

    wireless_mesh_count = 0

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Check if mesh0 interface exists (802.11s)
        rc, stdout, stderr = executor.run("iw dev mesh0 info 2>/dev/null")

        if rc == 0:
            # Parse mesh info
            mesh_id = None
            channel = None
            for line in stdout.strip().split("\n"):
                line = line.strip()
                if "ssid" in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        mesh_id = parts[1]
                elif "channel" in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        channel = parts[1]

            wireless_mesh_count += 1
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message=f"mesh0 active (SSID: {mesh_id}, ch: {channel})",
                data={"mesh_id": mesh_id, "channel": channel, "type": "802.11s"},
            )
            continue

        # Check for any wireless interface in batman mesh
        rc2, stdout2, _ = executor.run("batctl if 2>/dev/null | grep -E 'wlan|phy|radio' | head -1")

        if rc2 == 0 and stdout2.strip():
            wireless_mesh_count += 1
            iface = stdout2.strip().split()[0] if stdout2.strip() else "unknown"
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message=f"Wireless in batman: {iface}",
                data={"interface": iface, "type": "batman-wireless"},
            )
            continue

        # No wireless mesh found - check if wired mesh is working
        rc3, stdout3, _ = executor.run("batctl if 2>/dev/null | wc -l")
        try:
            iface_count = int(stdout3.strip()) if rc3 == 0 else 0
        except ValueError:
            iface_count = 0

        if iface_count >= 2:
            # Wired mesh is working, wireless is optional
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message=f"Wired mesh active ({iface_count} interfaces)",
                data={"interface_count": iface_count, "type": "wired-only"},
            )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.WARN,
                message="No wireless mesh, limited wired interfaces",
                data={"interface_count": iface_count},
            )

    result.aggregate_status()

    if wireless_mesh_count == len(NODES):
        result.message = "Wireless mesh active on all nodes"
    elif wireless_mesh_count > 0:
        result.message = f"Wireless mesh on {wireless_mesh_count}/{len(NODES)} nodes"
    elif result.passed:
        result.message = "Wired mesh active (wireless backup not configured)"
    else:
        result.message = "Mesh configuration incomplete"

    return result


def check_roaming() -> CheckResult:  # noqa: C901
    """
    Check that 802.11r fast roaming is configured.

    Verifies that the client AP (5GHz) has 802.11r/FT enabled
    for seamless client handoff between nodes.

    Returns:
        CheckResult with roaming configuration status.
    """
    result = CheckResult(
        category="wireless.roaming",
        status=CheckStatus.PASS,
        message="",
    )

    ft_configured = 0

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Check for 802.11r configuration in wireless config
        # Look for ieee80211r option in client AP configuration
        rc, stdout, stderr = executor.run(
            "uci show wireless 2>/dev/null | grep -E 'ieee80211r|ft_over_ds|ft_psk_generate'"
        )

        if rc == 0 and stdout.strip():
            # Parse the output to check if 802.11r is enabled
            has_11r = "ieee80211r='1'" in stdout or "ieee80211r=1" in stdout

            if has_11r:
                ft_configured += 1
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.PASS,
                    message="802.11r enabled",
                    data={"ieee80211r": True},
                )
            else:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.WARN,
                    message="802.11r config found but not enabled",
                    data={"ieee80211r": False},
                )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.WARN,
                message="No 802.11r configuration found",
                data={"ieee80211r": False},
            )

    result.aggregate_status()

    if ft_configured == len(NODES):
        result.status = CheckStatus.PASS
        result.message = f"802.11r configured on all {ft_configured} nodes"
    elif ft_configured > 0:
        result.status = CheckStatus.WARN
        result.message = f"802.11r only on {ft_configured}/{len(NODES)} nodes"
    else:
        result.status = CheckStatus.WARN
        result.message = "802.11r not configured (optional feature)"

    return result


def check_bla() -> CheckResult:
    """
    Check that Bridge Loop Avoidance is enabled.

    BLA prevents broadcast loops when batman-adv bridges
    multiple interfaces.

    Returns:
        CheckResult with BLA status.
    """
    result = CheckResult(
        category="wireless.bla",
        status=CheckStatus.PASS,
        message="",
    )

    all_have_bla = True

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Check BLA status
        rc, stdout, stderr = executor.run(
            "batctl meshif bat0 bla 2>/dev/null || batctl bla 2>/dev/null"
        )

        if rc != 0:
            # Try alternate method - check sysfs
            rc2, stdout2, _ = executor.run(
                "cat /sys/class/net/bat0/mesh/bridge_loop_avoidance 2>/dev/null"
            )
            if rc2 == 0:
                stdout = stdout2
                rc = 0

        if rc == 0:
            status_line = stdout.strip().lower()
            if "enabled" in status_line or status_line == "1":
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.PASS,
                    message="BLA enabled",
                    data={"bla_enabled": True},
                )
            elif "disabled" in status_line or status_line == "0":
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.WARN,
                    message="BLA disabled",
                    data={"bla_enabled": False},
                )
                all_have_bla = False
            else:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.WARN,
                    message=f"BLA status unclear: {status_line}",
                )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.WARN,
                message="Could not check BLA status",
            )
            all_have_bla = False

    result.aggregate_status()

    if all_have_bla and result.passed:
        result.message = "Bridge Loop Avoidance enabled on all nodes"
    else:
        result.message = "BLA not enabled on some nodes (optional)"

    return result
