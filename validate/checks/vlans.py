"""
VLAN validation checks.

Tier 2 (Standard):
- check_mesh_vlan: VLAN 100 on lan3/lan4
- check_client_vlan: VLAN 200 configured

Tier 3 (Comprehensive):
- check_management_vlan: VLAN 10 (10.11.10.0/24)
- check_iot_vlan: VLAN 30 (10.11.30.0/24)
- check_guest_vlan: VLAN 20 (10.11.20.0/24)
"""

from validate.config import NODES, VLANS
from validate.core.executor import NodeExecutor
from validate.core.results import CheckResult, CheckStatus


def check_mesh_vlan() -> CheckResult:
    """
    Check that VLAN 100 is configured on lan3/lan4 interfaces.

    Returns:
        CheckResult with per-node VLAN status.
    """
    result = CheckResult(
        category="vlans.mesh",
        status=CheckStatus.PASS,
        message="",
    )

    vlan_id = VLANS.get("mesh", {}).get("id", 100)

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Check for VLAN interfaces
        rc, stdout, _ = executor.run(f"ip link show | grep -E 'lan[34]\\.{vlan_id}'")

        if rc == 0:
            # Count VLAN interfaces found
            interfaces = [
                line.split(":")[1].strip().split("@")[0]
                for line in stdout.strip().split("\n")
                if line.strip()
            ]

            if len(interfaces) >= 2:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.PASS,
                    message=f"VLAN {vlan_id} on {', '.join(interfaces)}",
                    data={"interfaces": interfaces},
                )
            else:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.FAIL,
                    message=f"Only {len(interfaces)} VLAN interfaces (need 2)",
                    data={"interfaces": interfaces},
                )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message=f"No VLAN {vlan_id} interfaces found",
            )

    result.aggregate_status()

    if result.passed:
        result.message = f"VLAN {vlan_id} on lan3/lan4"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"VLAN {vlan_id} issues: {', '.join(failed)}"

    return result


def check_client_vlan() -> CheckResult:
    """
    Check that client VLAN 200 is configured.

    Returns:
        CheckResult with client VLAN status.
    """
    result = CheckResult(
        category="vlans.client",
        status=CheckStatus.PASS,
        message="",
    )

    vlan_id = VLANS.get("client", {}).get("id", 200)
    expected_network = str(VLANS.get("client", {}).get("network", "10.11.12.0/24"))

    # Extract network prefix for grep pattern (e.g., "10.11.12" from "10.11.12.0/24")
    network_base = expected_network.split("/")[0].rsplit(".", 1)[0]

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Check for VLAN interface or bridge with client VLAN
        rc, stdout, _ = executor.run(f"ip addr show | grep -E '({network_base}|vlan.*{vlan_id})'")

        if rc == 0 and stdout.strip():
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message=f"Client VLAN {vlan_id} configured",
            )
        else:
            # Check UCI configuration
            rc2, uci_out, _ = executor.run(f"uci show network | grep -i vlan.*{vlan_id}")
            if rc2 == 0:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.PASS,
                    message=f"Client VLAN {vlan_id} in UCI",
                )
            else:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.FAIL,
                    message=f"Client VLAN {vlan_id} not found",
                )

    result.aggregate_status()

    if result.passed:
        result.message = f"VLAN {vlan_id} configured"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"Client VLAN issues: {', '.join(failed)}"

    return result


def _check_network_vlan(vlan_name: str, category: str) -> CheckResult:
    """
    Check a named VLAN configuration.

    Args:
        vlan_name: VLAN name from config (management, iot, guest).
        category: Check category name.

    Returns:
        CheckResult with VLAN status.
    """
    result = CheckResult(
        category=category,
        status=CheckStatus.PASS,
        message="",
    )

    vlan_config = VLANS.get(vlan_name, {})
    vlan_id = vlan_config.get("id", 0)
    expected_network = str(vlan_config.get("network", ""))

    if not vlan_id:
        result.status = CheckStatus.SKIP
        result.message = f"VLAN {vlan_name} not configured"
        return result

    network_base = expected_network.split("/")[0].rsplit(".", 1)[0] if expected_network else ""

    for node_name, node_info in NODES.items():
        executor = NodeExecutor(node_name)

        # Check for network interface with expected IP range
        if network_base:
            expected_ip = f"{network_base}.{node_info.node_num}"
            rc, stdout, _ = executor.run(f"ip addr show | grep '{expected_ip}/'")

            if rc == 0:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.PASS,
                    message=f"{expected_ip} configured",
                    data={"ip": expected_ip},
                )
                continue

        # Fallback: check UCI for VLAN
        rc2, uci_out, _ = executor.run(f"uci show network | grep -i '{vlan_name}'")
        if rc2 == 0:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message=f"VLAN {vlan_id} in UCI",
            )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message=f"VLAN {vlan_id} ({vlan_name}) not found",
            )

    result.aggregate_status()

    if result.passed:
        result.message = f"VLAN {vlan_id} ({vlan_name}) configured"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"VLAN {vlan_name} issues: {', '.join(failed)}"

    return result


def check_management_vlan() -> CheckResult:
    """Check management VLAN (10)."""
    return _check_network_vlan("management", "vlans.management")


def check_iot_vlan() -> CheckResult:
    """Check IoT VLAN (30)."""
    return _check_network_vlan("iot", "vlans.iot")


def check_guest_vlan() -> CheckResult:
    """Check Guest VLAN (20)."""
    return _check_network_vlan("guest", "vlans.guest")
