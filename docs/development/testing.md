# Testing Guide

This document provides comprehensive guidance on the project's test suite, including how to run tests, write new tests, and understand the testing infrastructure.

## Overview

The project uses **pytest** as the testing framework with a multi-layered approach:

```
tests/
├── unit/           # Fast tests, no network required
├── integration/    # Require SSH connectivity to nodes
├── live/           # Require running mesh network
├── failover/       # Destructive tests (break things to verify recovery)
├── functional/     # End-to-end scenarios
└── performance/    # Throughput and latency benchmarks
```

## Quick Start

### Run Unit Tests (No Network Required)

```bash
# Run all unit tests
uv run pytest tests/unit -v

# Run with coverage
uv run pytest tests/unit -v --cov=tests --cov-report=html
```

### Run Live Tests (Requires Running Nodes)

```bash
# Quick connectivity tests
make test-quick

# Full live test suite
make test

# Complete suite with HTML report
make test-full
```

### Run Destructive Tests (Warning: Impacts Network!)

```bash
# Failover tests - temporarily breaks network
make test-destructive
```

## Test Categories

### Unit Tests (`tests/unit/`)

Fast tests that validate configuration without requiring network access.

| File | Purpose |
|------|---------|
| `test_config.py` | Validates `group_vars/all.yml` structure |
| `test_templates.py` | Renders Jinja2 templates with sample data |
| `test_roles.py` | Checks role structure (tasks/main.yml exists) |
| `test_playbook_syntax.py` | YAML syntax validation |
| `test_inventory.py` | Inventory file validation |
| `test_variables.py` | Variable parsing and types |
| `test_handlers.py` | Handler existence and references |
| `test_template_rendering.py` | Template rendering with real config |

**When to run**: Before every commit, in CI/CD

```bash
uv run pytest tests/unit -v
```

### Integration Tests (`tests/integration/`)

Tests that verify connectivity and Ansible facts.

| File | Purpose |
|------|---------|
| `test_ssh_connectivity.py` | SSH connection to nodes |
| `test_ansible_facts.py` | Gather and validate Ansible facts |
| `test_node_reachability.py` | Ping and basic connectivity |

**When to run**: After network changes, during development

```bash
uv run pytest tests/integration -v
```

### Live Tests (`tests/live/`)

Tests that validate the running mesh network.

| File | Purpose |
|------|---------|
| `test_connectivity.py` | Node-to-node communication |
| `test_batman_mesh.py` | Batman-adv topology and neighbors |
| `test_wireless.py` | WiFi configuration and clients |
| `test_vlans.py` | VLAN interfaces and isolation |
| `test_wan.py` | WAN connectivity and NAT |
| `test_failover.py` | Basic failover scenarios |

**When to run**: After deployments, regular health checks

```bash
uv run pytest tests/live -v --tb=short
```

### Failover Tests (`tests/failover/`)

Destructive tests that simulate failures.

!!! warning "These tests temporarily break your network!"

| File | Purpose |
|------|---------|
| `test_wired_failover.py` | Simulate cable disconnection |
| `test_wireless_failover.py` | Disable wireless mesh |
| `test_gateway_failover.py` | Remove gateway from mesh |
| `test_node_failure.py` | Reboot/shutdown node |

**When to run**: Quarterly, before production deployment

```bash
# Requires confirmation
make test-destructive
```

### Performance Tests (`tests/performance/`)

Benchmarks for throughput and latency.

| File | Purpose |
|------|---------|
| `test_throughput.py` | iperf3 bandwidth tests |
| `test_latency.py` | Ping latency statistics |
| `test_bandwidth.py` | Sustained bandwidth tests |

**When to run**: After topology changes, performance tuning

## Test Markers

Pytest markers allow selective test execution:

```python
@pytest.mark.unit         # No network required
@pytest.mark.integration  # Requires node connectivity
@pytest.mark.live         # Requires running mesh
@pytest.mark.failover     # Destructive tests
@pytest.mark.slow         # Takes > 30 seconds
@pytest.mark.wlan2        # Requires local wlan2 adapter
@pytest.mark.destructive  # Modifies network state
```

### Running by Marker

```bash
# Only unit tests
uv run pytest -m unit

# Only live tests (skip slow)
uv run pytest -m "live and not slow"

# Everything except destructive
uv run pytest -m "not destructive"
```

## Test Fixtures

### Shared Fixtures (`conftest.py`)

```python
# Available to all tests
@pytest.fixture
def ansible_root() -> Path:
    """Path to openwrt-mesh-ansible directory."""
    return Path(__file__).parent.parent / "openwrt-mesh-ansible"

@pytest.fixture
def mesh_network_config() -> dict:
    """Network configuration from group_vars."""
    return {
        "network": "10.11.12.0",
        "cidr": 24,
        "nodes": {
            1: "10.11.12.1",
            2: "10.11.12.2",
            3: "10.11.12.3",
        }
    }
```

### Live Test Fixtures (`tests/live/conftest.py`)

```python
@pytest.fixture
def node1() -> NodeExecutor:
    """SSH executor for node1 (10.11.12.1)."""
    return NodeExecutor("node1", "10.11.12.1")

@pytest.fixture
def all_node_executors() -> list[NodeExecutor]:
    """SSH executors for all nodes."""
    return [
        NodeExecutor("node1", "10.11.12.1"),
        NodeExecutor("node2", "10.11.12.2"),
        NodeExecutor("node3", "10.11.12.3"),
    ]
```

### Using NodeExecutor

```python
def test_batman_neighbors(node1: NodeExecutor):
    """Test that node1 sees neighbors."""
    output = node1.run_ok("batctl n")
    assert "bat0" in output.lower()

def test_ping_between_nodes(node1: NodeExecutor, node2: NodeExecutor):
    """Test node1 can ping node2."""
    assert node1.ping("10.11.12.2"), "node1 cannot reach node2"
```

## Writing New Tests

### Unit Test Example

```python
# tests/unit/test_my_feature.py

import pytest
from pathlib import Path

@pytest.mark.unit
class TestMyFeature:
    """Tests for my new feature."""

    def test_config_exists(self, ansible_root: Path) -> None:
        """Verify config file exists."""
        config_path = ansible_root / "group_vars" / "all.yml"
        assert config_path.exists()

    def test_required_variables(self, mesh_network_config: dict) -> None:
        """Verify required variables are set."""
        assert mesh_network_config["network"] == "10.11.12.0"
        assert len(mesh_network_config["nodes"]) == 3
```

### Live Test Example

```python
# tests/live/test_my_feature.py

import pytest
from .conftest import NodeExecutor

@pytest.mark.live
class TestMyFeature:
    """Live tests for my feature."""

    def test_service_running(self, all_node_executors: list[NodeExecutor]) -> None:
        """Verify my service is running on all nodes."""
        for executor in all_node_executors:
            output = executor.run_ok("pgrep my_service || echo 'not running'")
            assert "not running" not in output, f"{executor.node}: service not running"

    @pytest.mark.slow
    def test_performance_threshold(self, node1: NodeExecutor) -> None:
        """Test that latency is acceptable."""
        latency = node1.measure_latency("10.11.12.2")
        assert latency < 5, f"Latency too high: {latency}ms"
```

### Failover Test Example

```python
# tests/failover/test_my_failover.py

import pytest
import time
from tests.live.conftest import NodeExecutor

@pytest.mark.failover
@pytest.mark.destructive
class TestMyFailover:
    """Failover tests for my feature."""

    def test_recover_from_restart(self, node1: NodeExecutor, node2: NodeExecutor) -> None:
        """Test mesh recovers after node restart."""
        # Verify mesh is healthy
        assert node1.ping("10.11.12.2")

        # Trigger failure
        node2.run("reboot &")

        # Wait for reboot
        time.sleep(60)

        # Verify recovery
        retries = 10
        for _ in range(retries):
            if node1.ping("10.11.12.2"):
                return
            time.sleep(5)

        pytest.fail("Node2 did not recover after restart")
```

## CI/CD Integration

### GitHub Actions Workflow

Tests run automatically on:

- Push to any branch
- Pull request to main

```yaml
# .github/workflows/tests.yml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: |
          pip install uv
          uv sync
          uv run pytest tests/unit -v --cov
```

### Test Coverage

Minimum coverage requirements:

| Category | Required |
|----------|----------|
| Overall | 80% |
| New code | 90% |

View coverage report:

```bash
uv run pytest tests/unit --cov --cov-report=html
open htmlcov/index.html
```

## Makefile Targets

```bash
# Standard test suite
make test

# Quick connectivity only
make test-quick

# Full suite with HTML report
make test-full

# Failover tests (destructive!)
make test-destructive

# Run specific test file
make test TEST=test_batman_mesh.py

# Run with verbose output
make test VERBOSE=1
```

## Troubleshooting Tests

### Tests Can't Connect to Nodes

```bash
# Verify SSH connectivity
ssh root@10.11.12.1 "echo ok"

# Check SSH key
ssh-add -l

# Run with debug
uv run pytest tests/live -v --capture=no
```

### Tests Timeout

```bash
# Increase timeout
uv run pytest tests/live --timeout=300
```

### Flaky Tests

```bash
# Run multiple times to detect flakiness
uv run pytest tests/live --count=5

# Run with reruns on failure
uv run pytest tests/live --reruns=3
```

## Best Practices

1. **Keep unit tests fast**: < 1 second each
2. **Use appropriate markers**: Help others run the right tests
3. **Clean up after destructive tests**: Restore network state
4. **Document assumptions**: What state does the test expect?
5. **Use descriptive names**: `test_batman_neighbors_visible` not `test_1`
6. **Assert one thing**: Each test validates one behavior
7. **Use fixtures**: Don't repeat setup code
