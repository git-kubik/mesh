"""
Infrastructure validation checks.

Tier 3 (Comprehensive):
- check_switches: All managed switches reachable
"""

import os

from validate.config import SWITCHES
from validate.core.executor import run_local
from validate.core.results import CheckResult, CheckStatus

# Source interface for switches (via untagged eth2 with host routes)
# Switches respond on untagged VLAN, not VLAN 10
SWITCH_SOURCE_INTERFACE = os.environ.get("SWITCH_SOURCE_INTERFACE", "eth2")


def check_switches() -> CheckResult:  # noqa: C901
    """
    Check that all managed switches are reachable.

    Pings each switch in the SWITCHES configuration.

    Returns:
        CheckResult with switch reachability status.
    """
    result = CheckResult(
        category="infrastructure.switches",
        status=CheckStatus.PASS,
        message="",
    )

    if not SWITCHES:
        result.status = CheckStatus.SKIP
        result.message = "No switches configured"
        return result

    reachable = 0
    total = len(SWITCHES)

    # Build ping options with source interface for switches
    ping_opts = "-c 2 -W 2"
    if SWITCH_SOURCE_INTERFACE:
        ping_opts += f" -I {SWITCH_SOURCE_INTERFACE}"

    for switch_name, switch_info in SWITCHES.items():
        ip = switch_info.get("ip", "")
        description = switch_info.get("description", switch_name)

        if not ip:
            result.add_node_result(
                node=switch_name,
                status=CheckStatus.SKIP,
                message="No IP configured",
            )
            continue

        # Ping the switch
        rc, stdout, _ = run_local(f"ping {ping_opts} {ip}")

        if rc == 0:
            reachable += 1
            # Parse latency
            latency = None
            for line in stdout.split("\n"):
                if "avg" in line and "/" in line:
                    parts = line.split("=")[-1].split("/")
                    if len(parts) >= 2:
                        try:
                            latency = float(parts[1])
                        except ValueError:
                            pass
                    break

            result.add_node_result(
                node=switch_name,
                status=CheckStatus.PASS,
                message=f"{description} ({ip}) - {latency:.1f}ms"
                if latency
                else f"{description} ({ip})",
                data={"ip": ip, "latency_ms": latency},
            )
        else:
            result.add_node_result(
                node=switch_name,
                status=CheckStatus.FAIL,
                message=f"{description} ({ip}) unreachable",
                data={"ip": ip},
            )

    result.aggregate_status()

    if result.passed:
        result.message = f"All {total} switches reachable"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"Switches unreachable: {', '.join(failed)}"

    return result
