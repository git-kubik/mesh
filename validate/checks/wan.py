"""
WAN and internet connectivity checks.

Tier 3 (Comprehensive):
- check_connectivity: Internet reachable via WAN
- check_dns: DNS resolution working
"""

from validate.config import NODES
from validate.core.executor import NodeExecutor
from validate.core.results import CheckResult, CheckStatus


def check_connectivity() -> CheckResult:  # noqa: C901
    """
    Check internet connectivity from mesh nodes.

    Tests connectivity to 8.8.8.8 (Google DNS).

    Returns:
        CheckResult with WAN connectivity status.
    """
    result = CheckResult(
        category="wan.connectivity",
        status=CheckStatus.PASS,
        message="",
    )

    test_targets = ["8.8.8.8", "1.1.1.1"]

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Try each target
        connected = False
        for target in test_targets:
            rc, stdout, _ = executor.run(f"ping -c 2 -W 3 {target}")
            if rc == 0:
                connected = True
                # Extract latency
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
                    node=node_name,
                    status=CheckStatus.PASS,
                    message=f"WAN OK ({latency:.1f}ms)" if latency else "WAN OK",
                    data={"target": target, "latency_ms": latency},
                )
                break

        if not connected:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message="No internet connectivity",
            )

    result.aggregate_status()

    if result.passed:
        result.message = "Internet reachable from all nodes"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"WAN connectivity issues: {', '.join(failed)}"

    return result


def check_dns() -> CheckResult:
    """
    Check DNS resolution is working.

    Tests resolution of google.com and cloudflare.com.

    Returns:
        CheckResult with DNS status.
    """
    result = CheckResult(
        category="wan.dns",
        status=CheckStatus.PASS,
        message="",
    )

    test_domains = ["google.com", "cloudflare.com"]

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Try to resolve domains
        resolved = False
        for domain in test_domains:
            # Use nslookup or host command
            rc, stdout, _ = executor.run(f"nslookup {domain} 2>/dev/null | grep -i address")

            if rc == 0 and stdout.strip():
                resolved = True
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.PASS,
                    message="DNS resolution OK",
                    data={"test_domain": domain},
                )
                break

        if not resolved:
            # Try with dig as fallback
            rc2, dig_out, _ = executor.run(f"dig +short {test_domains[0]} 2>/dev/null")
            if rc2 == 0 and dig_out.strip():
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.PASS,
                    message="DNS resolution OK",
                )
            else:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.FAIL,
                    message="DNS resolution failed",
                )

    result.aggregate_status()

    if result.passed:
        result.message = "DNS resolution working"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"DNS issues: {', '.join(failed)}"

    return result
