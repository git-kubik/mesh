"""
Connectivity validation checks.

Tier 1 (Smoke):
- check_ping: All nodes respond to ping
- check_ssh: SSH authentication works
"""

from pathlib import Path

from validate.config import MESH_SOURCE_INTERFACE, NODES, get_ssh_key_path
from validate.core.executor import run_local, ssh_command
from validate.core.results import CheckResult, CheckStatus


def check_ping() -> CheckResult:  # noqa: C901
    """
    Check that all nodes respond to ping.

    Returns:
        CheckResult with per-node ping status.
    """
    result = CheckResult(
        category="connectivity.ping",
        status=CheckStatus.PASS,
        message="",
    )

    # Build ping command with optional source interface
    ping_opts = "-c 3 -W 2"
    if MESH_SOURCE_INTERFACE:
        ping_opts += f" -I {MESH_SOURCE_INTERFACE}"

    latencies = []
    for node_name, node_info in NODES.items():
        rc, stdout, stderr = run_local(f"ping {ping_opts} {node_info.ip}")

        if rc == 0:
            # Parse average latency from ping output
            # Example: rtt min/avg/max/mdev = 0.123/0.456/0.789/0.111 ms
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

            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message=f"{avg_ms:.1f}ms" if avg_ms else "OK",
                data={"latency_ms": avg_ms} if avg_ms else {},
            )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message=f"Ping failed: {stderr.strip() or 'no response'}",
            )

    result.aggregate_status()

    if result.passed and latencies:
        avg = sum(latencies) / len(latencies)
        result.message = f"All {len(NODES)} nodes respond ({avg:.1f}ms avg)"
    elif result.passed:
        result.message = f"All {len(NODES)} nodes respond"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"Nodes unreachable: {', '.join(failed)}"

    return result


def check_ssh() -> CheckResult:
    """
    Check SSH access to all nodes.

    Returns:
        CheckResult with per-node SSH status.
    """
    result = CheckResult(
        category="connectivity.ssh",
        status=CheckStatus.PASS,
        message="",
    )

    # First check SSH key exists
    ssh_key = get_ssh_key_path()
    if not Path(ssh_key).exists():
        result.status = CheckStatus.FAIL
        result.message = f"SSH key not found: {ssh_key}"
        return result

    for node_name, node_info in NODES.items():
        rc, stdout, stderr = ssh_command(node_info.ip, "echo ok", timeout=10)

        if rc == 0 and "ok" in stdout:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message="SSH OK",
            )
        else:
            error = stderr.strip() if stderr else "Connection failed"
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message=f"SSH failed: {error}",
            )

    result.aggregate_status()

    if result.passed:
        result.message = f"SSH verified ({len(NODES)}/{len(NODES)} nodes)"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"SSH failed: {', '.join(failed)}"

    return result
