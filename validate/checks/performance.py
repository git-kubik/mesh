"""
Performance validation checks.

Tier 3 (Comprehensive):
- check_latency: Inter-node latency within thresholds

Tier 4 (Certification):
- check_stress_ping: Extended ping test with packet loss measurement
"""

import re

from validate.config import MESH_SOURCE_INTERFACE, NODES, THRESHOLDS
from validate.core.executor import run_local
from validate.core.results import CheckResult, CheckStatus


def check_latency() -> CheckResult:  # noqa: C901
    """
    Check inter-node latency is within acceptable thresholds.

    Pings each node and verifies latency is under the configured max.

    Returns:
        CheckResult with latency measurements.
    """
    result = CheckResult(
        category="performance.latency",
        status=CheckStatus.PASS,
        message="",
    )

    max_latency = THRESHOLDS.get("max_latency_ms", 50)
    latencies = []

    # Build ping options
    ping_opts = "-c 5 -W 2"
    if MESH_SOURCE_INTERFACE:
        ping_opts += f" -I {MESH_SOURCE_INTERFACE}"

    for node_name, node_info in NODES.items():
        rc, stdout, stderr = run_local(f"ping {ping_opts} {node_info.ip}")

        if rc == 0:
            # Parse average latency
            avg_ms = None
            for line in stdout.split("\n"):
                if "avg" in line and "/" in line:
                    parts = line.split("=")[-1].split("/")
                    if len(parts) >= 2:
                        try:
                            avg_ms = float(parts[1])
                            latencies.append(avg_ms)
                        except ValueError:
                            pass
                    break

            if avg_ms is not None:
                if avg_ms <= max_latency:
                    result.add_node_result(
                        node=node_name,
                        status=CheckStatus.PASS,
                        message=f"{avg_ms:.1f}ms (max: {max_latency}ms)",
                        data={"latency_ms": avg_ms},
                    )
                else:
                    result.add_node_result(
                        node=node_name,
                        status=CheckStatus.WARN,
                        message=f"{avg_ms:.1f}ms exceeds {max_latency}ms threshold",
                        data={"latency_ms": avg_ms},
                    )
            else:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.WARN,
                    message="Could not parse latency",
                )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message="Ping failed",
            )

    result.aggregate_status()

    if latencies:
        avg = sum(latencies) / len(latencies)
        max_observed = max(latencies)
        if result.passed:
            result.message = f"Latency OK: avg {avg:.1f}ms, max {max_observed:.1f}ms"
        else:
            result.message = f"Latency issues: avg {avg:.1f}ms, max {max_observed:.1f}ms"
    else:
        result.message = "Could not measure latency"

    return result


def check_stress_ping() -> CheckResult:  # noqa: C901
    """
    Run extended ping test to measure packet loss under stress.

    Sends 100 pings to each node and measures packet loss percentage.
    Fails if loss exceeds the configured threshold (default 5%).

    Returns:
        CheckResult with packet loss measurements.
    """
    result = CheckResult(
        category="performance.stress",
        status=CheckStatus.PASS,
        message="",
    )

    max_loss = THRESHOLDS.get("max_packet_loss_pct", 5)
    ping_count = 100

    # Build ping options - flood-like but controlled
    ping_opts = f"-c {ping_count} -i 0.1 -W 2"
    if MESH_SOURCE_INTERFACE:
        ping_opts += f" -I {MESH_SOURCE_INTERFACE}"

    total_sent = 0
    total_received = 0

    for node_name, node_info in NODES.items():
        rc, stdout, stderr = run_local(f"ping {ping_opts} {node_info.ip}")

        # Parse packet loss from output
        # Example: "100 packets transmitted, 98 received, 2% packet loss"
        loss_pct = None
        received = None
        transmitted = None

        for line in stdout.split("\n"):
            if "packet loss" in line.lower():
                # Try to extract loss percentage
                match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*packet loss", line, re.IGNORECASE)
                if match:
                    loss_pct = float(match.group(1))

                # Also extract transmitted/received counts
                match2 = re.search(
                    r"(\d+)\s+packets transmitted.*?(\d+)\s+received", line, re.IGNORECASE
                )
                if match2:
                    transmitted = int(match2.group(1))
                    received = int(match2.group(2))
                break

        if loss_pct is not None:
            total_sent += transmitted or ping_count
            total_received += received or int(ping_count * (100 - loss_pct) / 100)

            if loss_pct <= max_loss:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.PASS,
                    message=f"{loss_pct:.1f}% loss ({ping_count} pings)",
                    data={"packet_loss_pct": loss_pct, "ping_count": ping_count},
                )
            else:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.FAIL,
                    message=f"{loss_pct:.1f}% loss exceeds {max_loss}% threshold",
                    data={"packet_loss_pct": loss_pct, "ping_count": ping_count},
                )
        else:
            if rc == 0:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.PASS,
                    message=f"{ping_count} pings OK",
                    data={"ping_count": ping_count},
                )
                total_sent += ping_count
                total_received += ping_count
            else:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.FAIL,
                    message="Ping test failed",
                )

    result.aggregate_status()

    # Calculate overall stats
    if total_sent > 0:
        overall_loss = ((total_sent - total_received) / total_sent) * 100
        if result.passed:
            result.message = f"Stress test passed: {overall_loss:.1f}% overall loss"
        else:
            result.message = (
                f"Stress test failed: {overall_loss:.1f}% overall loss (max: {max_loss}%)"
            )
    else:
        result.message = "Stress test could not complete"

    return result
