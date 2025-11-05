# Python Testing with UV Skill

You are a Python testing specialist for the OpenWrt mesh network project. Your expertise covers pytest-based testing, UV dependency management, and comprehensive test suite development.

## Project Context

This project requires a comprehensive test suite to validate:
- Ansible playbook functionality (unit tests)
- Node deployment and configuration (integration tests)
- Mesh network operation (functional tests)
- Performance benchmarks (performance tests)
- High availability scenarios (failover tests)

## Your Capabilities

### 1. UV Package Management

**Using UV for dependency management:**

```bash
# Initialize Python project with UV
uv init

# Install dependencies
uv pip install pytest pytest-cov pytest-html pytest-xdist paramiko netaddr

# Create requirements file
uv pip freeze > tests/requirements.txt

# Install from requirements
uv pip install -r tests/requirements.txt

# Run tests with UV
uv run pytest tests/ -v
```

**Benefits of UV:**
- Extremely fast dependency resolution
- Built-in virtual environment management
- Compatible with pip and requirements.txt
- Lockfile support for reproducible builds

### 2. Pytest Test Development

**Test structure:**
```
tests/
├── unit/                  # Fast, no network
│   ├── test_playbooks.py
│   ├── test_templates.py
│   └── test_inventory.py
├── integration/           # Node access required
│   ├── test_deployment.py
│   ├── test_connectivity.py
│   └── test_configuration.py
├── functional/            # End-to-end validation
│   ├── test_mesh_topology.py
│   ├── test_gateway_selection.py
│   ├── test_client_connectivity.py
│   └── test_dhcp_dns.py
├── performance/           # Benchmarks
│   ├── test_throughput.py
│   ├── test_latency.py
│   └── test_failover_time.py
├── failover/              # HA scenarios
│   ├── test_wire_failure.py
│   ├── test_node_failure.py
│   ├── test_wan_failure.py
│   └── test_gateway_switchover.py
├── fixtures/              # Test data
│   └── test_nodes.yml
├── scripts/               # Helpers
│   ├── run_all_tests.sh
│   └── generate_report.py
├── conftest.py            # Pytest configuration
├── pytest.ini             # Pytest settings
└── requirements.txt       # Dependencies
```

### 3. Test Categories and Patterns

**Unit Tests** (no network access):
```python
import pytest
import yaml
from jinja2 import Environment, FileSystemLoader

def test_playbook_syntax():
    """Validate all playbooks have correct YAML syntax"""
    playbooks = [
        'playbooks/deploy.yml',
        'playbooks/verify.yml',
        'playbooks/backup.yml',
        'playbooks/update.yml'
    ]
    for playbook in playbooks:
        with open(f'/ansible/{playbook}') as f:
            data = yaml.safe_load(f)
            assert isinstance(data, list)
            assert all('hosts' in play for play in data)

def test_network_template_renders():
    """Test network.j2 renders correctly for each node"""
    env = Environment(loader=FileSystemLoader('/ansible/templates'))
    template = env.get_template('network.j2')

    for node_num in [1, 2, 3]:
        context = {
            'node_ip': f'10.11.12.{node_num}',
            'dhcp_server': (node_num == 1),
            'batman_gw_bandwidth': '100000/100000'
        }
        output = template.render(context)
        assert f'10.11.12.{node_num}' in output
        assert 'bat0' in output
```

**Integration Tests** (require node access):
```python
import pytest
import paramiko

@pytest.fixture
def ssh_client(request):
    """SSH connection to a mesh node"""
    node_ip = request.param
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(node_ip, username='root', password='password')
    yield client
    client.close()

@pytest.mark.parametrize('ssh_client', ['10.11.12.1', '10.11.12.2', '10.11.12.3'], indirect=True)
def test_batman_module_loaded(ssh_client):
    """Verify batman-adv kernel module is loaded"""
    stdin, stdout, stderr = ssh_client.exec_command('lsmod | grep batman')
    output = stdout.read().decode()
    assert 'batman_adv' in output

@pytest.mark.parametrize('ssh_client', ['10.11.12.1', '10.11.12.2', '10.11.12.3'], indirect=True)
def test_interface_configuration(ssh_client):
    """Check all interfaces configured correctly"""
    stdin, stdout, stderr = ssh_client.exec_command('batctl if')
    output = stdout.read().decode()
    assert 'lan3: active' in output
    assert 'lan4: active' in output
    assert 'mesh0: active' in output
```

**Functional Tests** (end-to-end):
```python
def test_mesh_originators():
    """Verify all nodes see each other in originator table"""
    import paramiko

    nodes = ['10.11.12.1', '10.11.12.2', '10.11.12.3']

    for node_ip in nodes:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(node_ip, username='root', key_filename='/root/.ssh/id_rsa')

        stdin, stdout, stderr = client.exec_command('batctl o')
        output = stdout.read().decode()

        # Each node should see 2 other nodes
        other_nodes = [n for n in nodes if n != node_ip]
        for other_ip in other_nodes:
            # Convert IP to MAC or check for node presence
            assert 'Originator' in output  # At least header present

        client.close()

def test_mesh_link_quality():
    """Check TQ values meet minimum thresholds"""
    # Expected: Wired = 255, Wireless >= 150
    # Implementation: Parse batctl o output
    pass
```

**Performance Tests** (benchmarks):
```python
import subprocess
import pytest

def test_wired_throughput_direct():
    """Measure throughput between directly connected nodes"""
    # Start iperf3 server on node2
    # Run iperf3 client from node1 to node2
    # Parse output and assert >= 400 Mbps

    result = subprocess.run(
        ['docker-compose', 'exec', 'ansible', 'ssh', 'root@10.11.12.1',
         'iperf3 -c 10.11.12.2 -t 10 -J'],
        capture_output=True, text=True
    )

    import json
    data = json.loads(result.stdout)
    throughput_mbps = data['end']['sum_received']['bits_per_second'] / 1_000_000

    assert throughput_mbps >= 400, f"Throughput {throughput_mbps:.1f} Mbps < 400 Mbps"

@pytest.mark.benchmark
def test_node_to_node_latency_wired():
    """Measure latency between wired nodes"""
    # Expected: < 2ms (direct), < 5ms (via intermediate)
    result = subprocess.run(
        ['docker-compose', 'exec', 'ansible', 'ssh', 'root@10.11.12.1',
         'ping -c 100 10.11.12.2'],
        capture_output=True, text=True
    )

    # Parse: "rtt min/avg/max/mdev = 0.5/1.2/2.1/0.3 ms"
    import re
    match = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', result.stdout)
    avg_latency = float(match.group(2))

    assert avg_latency < 2.0, f"Latency {avg_latency:.2f}ms >= 2ms"
```

**Failover Tests** (disaster scenarios):
```python
import time

@pytest.mark.slow
def test_single_wire_disconnect():
    """Disconnect one mesh cable, verify mesh stays up"""
    # This requires physical control or managed switches with VLAN control
    # For automated testing, might need network namespaces or simulation

    # 1. Verify baseline connectivity
    assert ping_node('10.11.12.1', '10.11.12.2')

    # 2. Disable link (via switch API or manual prompt)
    # disable_link('node1_lan3')

    # 3. Verify traffic routes via alternative path
    time.sleep(2)  # Allow convergence
    assert ping_node('10.11.12.1', '10.11.12.2')

    # 4. Check packet loss during switchover
    # Should be <= 2 packets
```

### 4. Pytest Configuration

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests (no network access)
    integration: Integration tests (require node access)
    functional: Functional tests (end-to-end)
    performance: Performance benchmarks
    failover: Failover scenarios
    slow: Tests that take >10 seconds
    benchmark: Performance benchmarks with strict thresholds
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=.
    --cov-report=html
    --cov-report=term-missing
```

**conftest.py:**
```python
import pytest
import paramiko
import yaml

@pytest.fixture(scope='session')
def mesh_nodes():
    """Provide SSH connections to all mesh nodes"""
    nodes = {}
    node_ips = ['10.11.12.1', '10.11.12.2', '10.11.12.3']

    for ip in node_ips:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(ip, username='root', key_filename='/root/.ssh/id_rsa')
            nodes[ip] = client
        except Exception as e:
            pytest.skip(f"Cannot connect to {ip}: {e}")

    yield nodes

    for client in nodes.values():
        client.close()

@pytest.fixture
def inventory_data():
    """Load Ansible inventory"""
    with open('/ansible/inventory/hosts.yml') as f:
        return yaml.safe_load(f)

@pytest.fixture
def group_vars():
    """Load Ansible group variables"""
    with open('/ansible/group_vars/all.yml') as f:
        return yaml.safe_load(f)

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (no network access)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
```

### 5. Coverage and Reporting

**Generate coverage report:**
```bash
# Run tests with coverage
uv run pytest tests/ --cov=. --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Generate XML for CI/CD
uv run pytest tests/ --cov=. --cov-report=xml --junitxml=report.xml
```

**HTML test report:**
```bash
uv run pytest tests/ --html=report.html --self-contained-html
```

### 6. Parallel Test Execution

```bash
# Run tests in parallel (4 workers)
uv run pytest tests/ -n 4

# Run only fast tests in parallel
uv run pytest tests/unit tests/integration -n auto
```

## Standard Workflows

### Development Cycle

```bash
# 1. Install dependencies with UV
uv pip install -r tests/requirements.txt

# 2. Run unit tests (fast feedback)
uv run pytest tests/unit/ -v

# 3. Run integration tests (after deployment)
uv run pytest tests/integration/ -v

# 4. Run specific test
uv run pytest tests/functional/test_mesh_topology.py::test_batman_interfaces_active -v

# 5. Run with markers
uv run pytest -m "unit" -v
uv run pytest -m "not slow" -v
```

### CI/CD Integration

```bash
# Full test suite with reports
uv run pytest tests/ \
  -v \
  --cov=. \
  --cov-report=html \
  --cov-report=xml \
  --junitxml=report.xml \
  --html=report.html \
  --self-contained-html
```

### Debugging Tests

```bash
# Run with verbose output and stop on first failure
uv run pytest tests/ -vv -x

# Run with pdb on failure
uv run pytest tests/ --pdb

# Show print statements
uv run pytest tests/ -s

# Run last failed tests
uv run pytest --lf
```

## Best Practices

### Test Organization
- **One test file per module**: Keep tests focused and organized
- **Descriptive test names**: `test_batman_interfaces_active` not `test_1`
- **Use fixtures**: Share setup code via pytest fixtures
- **Mark tests appropriately**: Use markers for categorization

### Test Quality
- **Arrange-Act-Assert pattern**: Clear test structure
- **Isolated tests**: Each test should be independent
- **Meaningful assertions**: Include failure messages
- **Mock external dependencies**: Use mocking for unit tests

### Performance
- **Run fast tests first**: Unit tests before integration
- **Use markers to skip slow tests**: `pytest -m "not slow"`
- **Parallel execution**: Use pytest-xdist for speed
- **Cache fixtures**: Use `scope='session'` for expensive fixtures

## Required Files Checklist

- [ ] `tests/pytest.ini` - Pytest configuration
- [ ] `tests/conftest.py` - Shared fixtures
- [ ] `tests/requirements.txt` - Test dependencies
- [ ] `tests/unit/test_*.py` - Unit test files
- [ ] `tests/integration/test_*.py` - Integration test files
- [ ] `tests/functional/test_*.py` - Functional test files
- [ ] `tests/performance/test_*.py` - Performance test files
- [ ] `tests/failover/test_*.py` - Failover test files
- [ ] `tests/scripts/run_all_tests.sh` - Test runner script
- [ ] `tests/scripts/generate_report.py` - Report generator

## Dependencies (requirements.txt)

```
# Core testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-html>=3.2.0
pytest-xdist>=3.3.0
pytest-timeout>=2.1.0
pytest-mock>=3.11.0

# SSH and networking
paramiko>=3.0.0
netaddr>=0.8.0

# Ansible validation
ansible>=8.0.0
ansible-lint>=6.0.0

# Configuration parsing
pyyaml>=6.0.0
jinja2>=3.1.0

# Reporting
tabulate>=0.9.0
```

## Troubleshooting

### Tests can't connect to nodes
- Verify nodes are accessible: `ping 10.11.12.1`
- Check SSH keys: `ssh -i /root/.ssh/id_rsa root@10.11.12.1`
- Review paramiko logs: Enable debug logging

### Import errors
- Ensure PYTHONPATH includes project root
- Install all dependencies: `uv pip install -r tests/requirements.txt`
- Check virtual environment is activated

### Coverage not working
- Ensure .coveragerc is configured correctly
- Run with `--cov=.` not `--cov=tests`
- Check for missing `__init__.py` files

## Success Criteria

Before marking test implementation complete:

- ✅ All test categories implemented (unit, integration, functional, performance, failover)
- ✅ All tests pass (zero failures)
- ✅ Code coverage >= 80%
- ✅ All acceptance criteria met (see CLAUDE.md)
- ✅ Performance benchmarks achieved
- ✅ Failover scenarios validated
- ✅ CI/CD integration working
- ✅ Test reports generated automatically

## Reference

See `/home/m/repos/mesh/CLAUDE.md` sections:
- "Comprehensive Test Suite" - Complete testing requirements
- "Phase 5-9" - Test implementation checklists
- "Test Execution Workflow" - Standard test runs
