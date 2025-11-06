"""
Failover tests for gateway failover scenarios.

Tests validate multi-WAN gateway failover functionality.
"""

import pytest


@pytest.mark.failover
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_primary_gateway_wan_failure() -> None:
    """
    Test failover when primary gateway (node1) WAN fails.

    Validates automatic switch to secondary gateway.
    Target: < 5 seconds for gateway failover.
    """
    pytest.skip("Requires WAN failure simulation")


@pytest.mark.failover
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_secondary_gateway_promotion() -> None:
    """
    Test secondary gateway promotion to primary.

    Validates node2 or node3 becomes active gateway.
    """
    pytest.skip("Requires gateway promotion monitoring")


@pytest.mark.failover
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_gateway_wan_recovery() -> None:
    """
    Test recovery when primary gateway WAN is restored.

    Validates automatic return to primary gateway.
    """
    pytest.skip("Requires WAN recovery simulation")


@pytest.mark.failover
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_client_internet_during_gateway_failover() -> None:
    """
    Test client internet access during gateway failover.

    Validates minimal interruption to client connections.
    """
    pytest.skip("Requires client device and failover simulation")


@pytest.mark.failover
@pytest.mark.requires_nodes
def test_batman_gateway_announcement() -> None:
    """
    Test Batman gateway announcements during failover.

    Validates batctl gwl updates correctly.
    """
    pytest.skip("Requires batctl gateway monitoring")


@pytest.mark.failover
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_active_connections_during_gateway_failover() -> None:
    """
    Test impact on active connections during gateway failover.

    Measures connection drops and recovery time.
    """
    pytest.skip("Requires active connection monitoring")


@pytest.mark.failover
@pytest.mark.requires_nodes
@pytest.mark.slow
def test_dns_during_gateway_failover() -> None:
    """
    Test DNS resolution during gateway failover.

    Validates DNS queries continue to work.
    """
    pytest.skip("Requires DNS query testing during failover")
