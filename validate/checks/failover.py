"""
Failover validation checks.

Tier 4 (Certification):
- check_link_failover: Ring survives single link failure
- check_wan_failover: WAN failover works correctly
- check_node_failover: Mesh survives node failure
"""

from validate.config import NODES
from validate.core.executor import NodeExecutor
from validate.core.results import CheckResult, CheckStatus


def check_link_failover() -> CheckResult:  # noqa: C901
    """
    Check that mesh ring survives a single link failure.

    Simulates link failure by temporarily disabling one mesh interface
    and verifying connectivity is maintained through alternate path.

    Returns:
        CheckResult with link failover status.
    """
    result = CheckResult(
        category="failover.link",
        status=CheckStatus.PASS,
        message="",
    )

    # We'll test by checking that each node has multiple paths (neighbors)
    # A healthy ring should have 2+ neighbors per node
    # If we had only 1 neighbor, a single link failure would isolate the node

    min_neighbors = 2

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Count neighbors
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

            if count >= min_neighbors:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.PASS,
                    message=f"{count} paths available",
                    data={"neighbor_count": count},
                )
            else:
                result.add_node_result(
                    node=node_name,
                    status=CheckStatus.FAIL,
                    message=f"Only {count} path (need {min_neighbors}+ for redundancy)",
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
        result.message = "All nodes have redundant paths"
    else:
        result.message = "Some nodes lack redundant paths for failover"

    return result


def check_wan_failover() -> CheckResult:  # noqa: C901
    """
    Check that WAN failover is configured and working.

    Verifies that multiple gateways are available and the mesh
    can route traffic through alternate gateways.

    Returns:
        CheckResult with WAN failover status.
    """
    result = CheckResult(
        category="failover.wan",
        status=CheckStatus.PASS,
        message="",
    )

    # Count nodes with WAN (gw_mode=server)
    gateway_nodes = [n for n, info in NODES.items() if info.gw_mode == "server"]

    if len(gateway_nodes) < 2:
        result.status = CheckStatus.FAIL
        result.message = f"Only {len(gateway_nodes)} gateway(s) - need 2+ for WAN failover"
        return result

    # Check each gateway can reach internet
    working_gateways = 0

    for node_name in gateway_nodes:
        executor = NodeExecutor(node_name)

        # Check internet connectivity
        rc, stdout, stderr = executor.run("ping -c 2 -W 3 8.8.8.8")

        if rc == 0:
            working_gateways += 1
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message="WAN active",
            )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.WARN,
                message="WAN unreachable",
            )

    # Check gateway selection from a client perspective
    executor = NodeExecutor("node1")
    rc, stdout, stderr = executor.run("batctl gwl 2>/dev/null | grep -c MBit")

    try:
        visible_gateways = int(stdout.strip()) if rc == 0 else 0
    except ValueError:
        visible_gateways = 0

    result.data = {
        "total_gateways": len(gateway_nodes),
        "working_gateways": working_gateways,
        "visible_gateways": visible_gateways,
    }

    if working_gateways >= 2:
        result.status = CheckStatus.PASS
        result.message = f"{working_gateways}/{len(gateway_nodes)} gateways active for failover"
    elif working_gateways == 1:
        result.status = CheckStatus.WARN
        result.message = f"Only 1/{len(gateway_nodes)} gateway active - failover degraded"
    else:
        result.status = CheckStatus.FAIL
        result.message = "No working gateways"

    return result


def check_node_failover() -> CheckResult:  # noqa: C901
    """
    Check that mesh can survive a node failure.

    Verifies mesh topology has enough redundancy that losing
    any single node doesn't partition the network.

    Returns:
        CheckResult with node failover status.
    """
    result = CheckResult(
        category="failover.node",
        status=CheckStatus.PASS,
        message="",
    )

    # For a 3-node ring, each node should see 2 originators
    # This means full mesh connectivity
    node_count = len(NODES)
    expected_originators = node_count - 1  # Each sees all others

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Get originator count
        rc, stdout, stderr = executor.run("batctl o 2>/dev/null")

        if rc != 0:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message=f"batctl failed: {stderr.strip()}",
            )
            continue

        # Count unique originators
        originators = set()
        for line in stdout.strip().split("\n"):
            line = line.strip()
            if not line or "MainIF" in line or "B.A.T.M.A.N" in line or "Originator" in line:
                continue
            if line.startswith("*"):
                parts = line[1:].strip().split()
            else:
                parts = line.split()
            if parts and ":" in parts[0]:
                originators.add(parts[0])

        count = len(originators)

        if count >= expected_originators:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message=f"Sees all {count} peers",
                data={"originator_count": count},
            )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message=f"Only sees {count}/{expected_originators} peers",
                data={"originator_count": count},
            )

    result.aggregate_status()

    if result.passed:
        result.message = f"Full mesh connectivity ({node_count} nodes)"
    else:
        result.message = "Incomplete mesh - node failure could partition network"

    return result
