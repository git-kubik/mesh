"""
Service validation checks.

Tier 3 (Comprehensive):
- check_dhcp: dnsmasq running and configured
- check_firewall: Firewall zones configured and running
"""

from validate.config import NODES
from validate.core.executor import NodeExecutor
from validate.core.results import CheckResult, CheckStatus


def check_dhcp() -> CheckResult:
    """
    Check that DHCP (dnsmasq) is running and configured.

    Returns:
        CheckResult with DHCP status.
    """
    result = CheckResult(
        category="services.dhcp",
        status=CheckStatus.PASS,
        message="",
    )

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Check dnsmasq is running
        rc, stdout, _ = executor.run("pgrep -x dnsmasq")

        if rc != 0:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message="dnsmasq not running",
            )
            continue

        # Check DHCP pools are configured
        rc2, pools, _ = executor.run("uci show dhcp | grep -c 'dhcp\\.'")

        try:
            pool_count = int(pools.strip()) if pools.strip() else 0
        except ValueError:
            pool_count = 0

        if pool_count > 0:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message=f"dnsmasq running, {pool_count} config entries",
                data={"config_entries": pool_count},
            )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message="dnsmasq running but no DHCP config",
            )

    result.aggregate_status()

    if result.passed:
        result.message = "DHCP (dnsmasq) running on all nodes"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"DHCP issues: {', '.join(failed)}"

    return result


def check_firewall() -> CheckResult:
    """
    Check that firewall is running with zones configured.

    Returns:
        CheckResult with firewall status.
    """
    result = CheckResult(
        category="services.firewall",
        status=CheckStatus.PASS,
        message="",
    )

    # Core zones: lan (clients), wan (internet), iot (devices), management (admin)
    expected_zones = ["lan", "wan", "iot", "management"]

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Check firewall is running (fw4 for OpenWrt 22.03+)
        rc, stdout, _ = executor.run("pgrep -f 'fw4\\|firewall' || /etc/init.d/firewall status")

        if rc != 0:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message="Firewall not running",
            )
            continue

        # Check zones exist
        rc2, zones_out, _ = executor.run("uci show firewall | grep '\\.name=' | cut -d= -f2")
        zones = [z.strip().strip("'\"") for z in zones_out.split("\n") if z.strip()]

        missing = [z for z in expected_zones if z not in zones]

        if not missing:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message=f"Firewall running, {len(zones)} zones",
                data={"zones": zones},
            )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message=f"Missing zones: {', '.join(missing)}",
                data={"zones": zones, "missing": missing},
            )

    result.aggregate_status()

    if result.passed:
        result.message = "Firewall running with all zones"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"Firewall issues: {', '.join(failed)}"

    return result
