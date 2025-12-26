"""
Batman-adv validation checks.

Tier 1 (Smoke):
- check_module: batman-adv kernel module loaded

Tier 2 (Standard):
- check_interfaces: bat0 interface exists and is UP
- check_neighbors: 2+ neighbors per node
- check_originators: All nodes visible in mesh
- check_gateways: All gateways advertising
"""

from validate.config import NODES, THRESHOLDS
from validate.core.executor import NodeExecutor
from validate.core.results import CheckResult, CheckStatus


def check_module() -> CheckResult:
    """
    Check that batman-adv kernel module is loaded on all nodes.

    Returns:
        CheckResult with per-node module status.
    """
    result = CheckResult(
        category="batman.module",
        status=CheckStatus.PASS,
        message="",
    )

    for node_name in NODES:
        executor = NodeExecutor(node_name)
        rc, stdout, stderr = executor.run("lsmod | grep -q batman_adv")

        if rc == 0:
            # Get batman version
            rc2, version, _ = executor.run("cat /sys/module/batman_adv/version 2>/dev/null")
            version_str = version.strip() if rc2 == 0 else "unknown"

            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message=f"v{version_str}",
                data={"version": version_str},
            )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message="batman-adv not loaded",
            )

    result.aggregate_status()

    if result.passed:
        result.message = "batman-adv loaded on all nodes"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"batman-adv not loaded: {', '.join(failed)}"

    return result


def check_interfaces() -> CheckResult:
    """
    Check that bat0 interface exists and is UP on all nodes.

    Returns:
        CheckResult with per-node interface status.
    """
    result = CheckResult(
        category="batman.interfaces",
        status=CheckStatus.PASS,
        message="",
    )

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Check bat0 exists and has UP flag (look for <...UP...> in flags)
        rc, stdout, stderr = executor.run("ip link show bat0 2>/dev/null")

        if rc == 0 and "<" in stdout and "UP" in stdout.split("<")[1].split(">")[0]:
            # Get bat0 MAC
            rc2, mac_out, _ = executor.run(
                "ip link show bat0 | grep -o 'link/ether [^ ]*' | cut -d' ' -f2"
            )
            mac = mac_out.strip() if rc2 == 0 else ""

            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message="bat0 UP",
                data={"mac": mac} if mac else {},
            )
        elif rc == 0:
            # bat0 exists but not UP
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message="bat0 exists but DOWN",
            )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message="bat0 not found",
            )

    result.aggregate_status()

    if result.passed:
        result.message = "bat0 UP on all nodes"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"bat0 issues: {', '.join(failed)}"

    return result


def check_neighbors() -> CheckResult:
    """
    Check that each node has sufficient batman neighbors.

    Returns:
        CheckResult with per-node neighbor count.
    """
    result = CheckResult(
        category="batman.neighbors",
        status=CheckStatus.PASS,
        message="",
    )

    min_neighbors = THRESHOLDS.get("min_neighbors", 2)
    total_neighbors = 0

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Count neighbors (exclude header line)
        rc, stdout, stderr = executor.run("batctl n 2>/dev/null | tail -n +3 | wc -l")

        if rc != 0:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message=f"batctl failed: {stderr.strip()}",
            )
            continue

        try:
            count = int(stdout.strip())
            total_neighbors += count

            if count >= min_neighbors:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.PASS,
                    message=f"{count} neighbors",
                    data={"neighbor_count": count},
                )
            else:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.FAIL,
                    message=f"Only {count} neighbors (need {min_neighbors}+)",
                    data={"neighbor_count": count},
                )
        except ValueError:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message=f"Invalid output: {stdout.strip()}",
            )

    result.aggregate_status()

    if result.passed:
        counts = [r.data.get("neighbor_count", 0) for r in result.nodes.values()]
        count_strs = [str(c) if i < len(counts) else "?" for i, c in enumerate(counts)]
        result.message = f"{min_neighbors}+ neighbors ({'/'.join(count_strs)})"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"Insufficient neighbors: {', '.join(failed)}"

    return result


def check_originators() -> CheckResult:
    """
    Check that all nodes are visible in the mesh originator table.

    A node sees other nodes but not itself in the originator table.
    With N nodes, each should see N-1 originators.

    Returns:
        CheckResult with per-node visibility status.
    """
    result = CheckResult(
        category="batman.originators",
        status=CheckStatus.PASS,
        message="",
    )

    # Each node sees others, not itself
    min_originators = len(NODES) - 1

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Get originators and count unique MACs (first column)
        # Lines with * are selected routes, others are alternate routes
        rc, stdout, stderr = executor.run("batctl o 2>/dev/null")

        if rc != 0:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message=f"batctl failed: {stderr.strip()}",
            )
            continue

        # Count unique originator MACs (lines starting with * or MAC address)
        # Format: "   mac:addr  time  (throughput) next-hop [iface]" or "* mac..."
        originators = set()
        for line in stdout.strip().split("\n"):
            line = line.strip()
            # Skip header lines
            if not line or "MainIF" in line or "B.A.T.M.A.N" in line or "Originator" in line:
                continue
            # Extract first MAC from line (starts with * or MAC)
            if line.startswith("*"):
                parts = line[1:].strip().split()
            else:
                parts = line.split()
            if parts and ":" in parts[0]:
                originators.add(parts[0])

        count = len(originators)

        if count >= min_originators:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message=f"{count} originators",
                data={"originator_count": count},
            )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message=f"Only {count} originators (need {min_originators}+)",
                data={"originator_count": count},
            )

    result.aggregate_status()

    if result.passed:
        result.message = f"All {len(NODES)} nodes visible ({min_originators}+ each)"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"Originator issues: {', '.join(failed)}"

    return result


def check_gateways() -> CheckResult:
    """
    Check that all expected gateways are advertising.

    A node sees other gateways but not itself in the gateway list.
    With 3 gateway nodes, each should see 2 other gateways.

    Returns:
        CheckResult with gateway status.
    """
    result = CheckResult(
        category="batman.gateways",
        status=CheckStatus.PASS,
        message="",
    )

    # Count gateway nodes (gw_mode=server)
    gateway_nodes = [n for n, info in NODES.items() if info.gw_mode == "server"]
    expected_visible = len(gateway_nodes) - 1  # Each sees others, not itself

    # Check from first node
    executor = NodeExecutor("node1")
    rc, stdout, stderr = executor.run("batctl gwl 2>/dev/null")

    if rc != 0:
        result.status = CheckStatus.FAIL
        result.message = f"batctl gwl failed: {stderr.strip()}"
        return result

    # Parse gateway list
    # Format: "  Router  ( throughput) Next Hop [outgoingIf]: Bandwidth"
    gateways = []
    for line in stdout.strip().split("\n"):
        line = line.strip()
        # Skip header lines
        if not line or "MainIF" in line or "B.A.T.M.A.N" in line or "Router" in line:
            continue
        # Gateway lines have MAC addresses and bandwidth info
        if ":" in line and ("MBit" in line or "/" in line):
            gateways.append(line)

    gateway_count = len(gateways)
    total_gateways = gateway_count + 1  # Plus self
    result.data = {"gateway_count": gateway_count, "total": total_gateways, "gateways": gateways}

    if gateway_count >= expected_visible:
        result.status = CheckStatus.PASS
        result.message = f"{total_gateways} gateways ({gateway_count} visible + self)"
    else:
        result.status = CheckStatus.FAIL
        result.message = f"Only {gateway_count} visible gateways (need {expected_visible}+)"

    return result
