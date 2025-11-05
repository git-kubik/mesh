# Mesh Network Testing Skill

You are a mesh network testing specialist. Your expertise covers network connectivity testing, performance benchmarking, failover validation, and automated test execution for the OpenWrt batman-adv mesh network project.

## Project Context

This project requires comprehensive testing to validate:
- Mesh topology correctness
- Gateway selection and failover
- Client connectivity (wired and wireless)
- Performance benchmarks (throughput, latency)
- High availability scenarios
- DHCP/DNS functionality

## Your Capabilities

### 1. Network Connectivity Testing

**Basic connectivity tests:**

```bash
# Ping test (ICMP)
ping -c 10 10.11.12.2
ping -c 100 -i 0.2 10.11.12.2  # Flood ping (stress test)

# Ping with specific source interface
ping -c 10 -I lan3 10.11.12.2

# Ping statistics
ping -c 100 10.11.12.2 | tail -2
# Expect: 0% packet loss, < 2ms average

# Ping sweep (check all nodes)
for i in 1 2 3; do
  ping -c 4 10.11.12.$i && echo "Node $i: OK" || echo "Node $i: FAIL"
done
```

**TCP/UDP connectivity:**

```bash
# Check if port open (netcat)
nc -zv 10.11.12.1 22  # SSH
nc -zv 10.11.12.1 53  # DNS

# Check port (without netcat)
timeout 1 bash -c "</dev/tcp/10.11.12.1/22" && echo "Open" || echo "Closed"

# UDP test
nc -zuv 10.11.12.1 53
```

**DNS resolution testing:**

```bash
# Test DNS resolution
nslookup google.com 10.11.12.1
nslookup google.com  # Use system resolver

# Test with dig (more detailed)
dig @10.11.12.1 google.com
dig @10.11.12.1 google.com +short

# Test reverse DNS
dig -x 10.11.12.1
```

**Route testing:**

```bash
# Traceroute
traceroute 8.8.8.8
traceroute -I 8.8.8.8  # Use ICMP instead of UDP

# MTR (My TraceRoute) - continuous traceroute
mtr -c 100 8.8.8.8
mtr -r -c 100 8.8.8.8  # Report mode
```

### 2. Mesh-Specific Testing

**Batman-adv topology verification:**

```python
import paramiko

def test_mesh_topology():
    """Verify all nodes see each other in batman originator table"""
    nodes = ['10.11.12.1', '10.11.12.2', '10.11.12.3']

    for node_ip in nodes:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(node_ip, username='root', key_filename='/root/.ssh/id_rsa')

        # Get originator table
        stdin, stdout, stderr = client.exec_command('batctl o')
        output = stdout.read().decode()

        # Parse output
        lines = [l for l in output.split('\n') if 'Originator' not in l and l.strip()]
        other_nodes = [n for n in nodes if n != node_ip]

        # Verify 2 originators visible (in 3-node mesh)
        assert len(lines) >= 2, f"Node {node_ip} only sees {len(lines)} originators"

        # Verify TQ values (wired should be 255 or close)
        for line in lines:
            if 'Gbps' in line:  # Wired link
                # Extract throughput
                import re
                match = re.search(r'\(.*?(\d+\.?\d*)\s*Gbps', line)
                if match:
                    throughput = float(match.group(1))
                    assert throughput >= 0.9, f"Low TQ: {throughput} Gbps"

        client.close()
```

**Interface status testing:**

```python
def test_batman_interfaces():
    """Verify batman interfaces are active"""
    import paramiko

    nodes = ['10.11.12.1', '10.11.12.2', '10.11.12.3']
    expected_interfaces = ['lan3', 'lan4', 'mesh0']

    for node_ip in nodes:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(node_ip, username='root', key_filename='/root/.ssh/id_rsa')

        stdin, stdout, stderr = client.exec_command('batctl if')
        output = stdout.read().decode()

        # Check each expected interface is active
        for iface in expected_interfaces:
            assert f'{iface}: active' in output, \
                f"Interface {iface} not active on {node_ip}"

        client.close()
```

**Gateway testing:**

```bash
# Check gateway list on all nodes
for i in 1 2 3; do
  echo "=== Node $i ==="
  ssh root@10.11.12.$i batctl gwl
done

# Expected output:
# All 3 nodes should show all 3 gateways
# One marked with => (selected)
# Others marked with * (available)
```

### 3. Performance Benchmarking

**Throughput testing with iperf3:**

```bash
# Install iperf3 on nodes
for i in 1 2 3; do
  ssh root@10.11.12.$i "opkg update && opkg install iperf3"
done

# Start server on node1
ssh root@10.11.12.1 "iperf3 -s -D"  # Daemon mode

# Test from node2 to node1 (direct wired)
ssh root@10.11.12.2 "iperf3 -c 10.11.12.1 -t 30 -i 5"
# Expected: >= 400 Mbps

# Test from node3 to node2 (direct wired)
ssh root@10.11.12.3 "iperf3 -c 10.11.12.2 -t 30"
# Expected: >= 400 Mbps

# Test 2-hop (node1 to node3, via node2)
ssh root@10.11.12.1 "iperf3 -c 10.11.12.3 -t 30"
# Expected: >= 200 Mbps

# UDP throughput (with packet loss measurement)
ssh root@10.11.12.2 "iperf3 -c 10.11.12.1 -u -b 500M -t 30"

# Bidirectional test
ssh root@10.11.12.2 "iperf3 -c 10.11.12.1 --bidir -t 30"
```

**Python test for throughput:**

```python
import subprocess
import json
import pytest

@pytest.mark.performance
def test_wired_throughput_direct():
    """Measure throughput between directly connected nodes"""
    # Run iperf3 client from container (connecting to node)
    result = subprocess.run([
        'docker-compose', 'exec', '-T', 'ansible',
        'ssh', 'root@10.11.12.2',
        'iperf3 -c 10.11.12.1 -t 10 -J'
    ], capture_output=True, text=True, timeout=15)

    # Parse JSON output
    data = json.loads(result.stdout)
    throughput_bps = data['end']['sum_received']['bits_per_second']
    throughput_mbps = throughput_bps / 1_000_000

    # Assert threshold
    assert throughput_mbps >= 400, \
        f"Throughput {throughput_mbps:.1f} Mbps < 400 Mbps (wired direct)"
```

**Latency testing:**

```bash
# Ping test with statistics
ping -c 1000 10.11.12.2 | tail -2
# Expected wired direct: avg < 2ms

# Ping to each node
for i in 1 2 3; do
  echo "=== Node $i ==="
  ping -c 100 10.11.12.$i | grep 'min/avg/max'
done

# Continuous latency monitoring
ping 10.11.12.2 | while read line; do
  echo "$(date +%H:%M:%S) - $line"
done
```

**Python test for latency:**

```python
import subprocess
import re

def test_node_to_node_latency():
    """Measure latency between wired nodes"""
    # Ping from node1 to node2
    result = subprocess.run([
        'docker-compose', 'exec', '-T', 'ansible',
        'ssh', 'root@10.11.12.1',
        'ping -c 100 10.11.12.2'
    ], capture_output=True, text=True, timeout=15)

    # Parse: "rtt min/avg/max/mdev = 0.5/1.2/2.1/0.3 ms"
    match = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)',
                      result.stdout)

    if match:
        min_lat = float(match.group(1))
        avg_lat = float(match.group(2))
        max_lat = float(match.group(3))

        assert avg_lat < 2.0, f"Average latency {avg_lat:.2f}ms >= 2ms"
        assert max_lat < 5.0, f"Max latency {max_lat:.2f}ms >= 5ms"
    else:
        pytest.fail("Could not parse ping output")
```

### 4. Failover Testing

**Wire disconnect simulation:**

```bash
# Disable interface to simulate cable disconnect
ssh root@10.11.12.1 "ip link set lan3 down"

# Wait for convergence
sleep 3

# Verify mesh still works (via alternative path)
ping -c 10 10.11.12.2
# Should succeed with minimal packet loss

# Count packet loss during failover
ping -c 100 -i 0.1 10.11.12.2 | grep 'packet loss'
# Expected: <= 2 packets lost

# Re-enable interface
ssh root@10.11.12.1 "ip link set lan3 up"
```

**Gateway failover testing:**

```python
import time
import subprocess

def test_gateway_failover():
    """Test gateway switchover when WAN fails"""
    # 1. Identify current gateway
    result = subprocess.run([
        'docker-compose', 'exec', '-T', 'ansible',
        'ssh', 'root@10.11.12.1', 'batctl gwl'
    ], capture_output=True, text=True)

    current_gw = None
    for line in result.stdout.split('\n'):
        if '=>' in line:
            # Parse current gateway
            current_gw = line.split()[1]  # MAC address
            break

    assert current_gw is not None, "No gateway selected"

    # 2. Simulate WAN failure (disconnect WAN on gateway node)
    # This requires physical access or smart switch control
    # For automated testing, might need to:
    # - Use network namespaces
    # - Control managed switch via API
    # - Use iptables to block traffic

    # 3. Verify failover occurs
    time.sleep(30)  # Wait for gateway reselection

    result = subprocess.run([
        'docker-compose', 'exec', '-T', 'ansible',
        'ssh', 'root@10.11.12.1', 'batctl gwl'
    ], capture_output=True, text=True)

    new_gw = None
    for line in result.stdout.split('\n'):
        if '=>' in line:
            new_gw = line.split()[1]
            break

    # Gateway should have changed
    assert new_gw != current_gw, "Gateway did not failover"

    # 4. Verify internet still works
    result = subprocess.run([
        'docker-compose', 'exec', '-T', 'ansible',
        'ssh', 'root@10.11.12.1', 'ping -c 4 8.8.8.8'
    ], capture_output=True, text=True)

    assert '0% packet loss' in result.stdout, "Internet not accessible after failover"
```

### 5. DHCP/DNS Testing

**DHCP testing:**

```bash
# Release and renew DHCP lease
ssh root@10.11.12.2 "udhcpc -i br-lan -n"

# Check DHCP leases on server
ssh root@10.11.12.1 "cat /tmp/dhcp.leases"

# Expected format:
# <expiry> <mac> <ip> <hostname> <client-id>
```

**Static IP reservation testing:**

```python
def test_static_ip_reservations():
    """Verify static DHCP assignments work"""
    import paramiko

    # Read expected static hosts from group_vars
    import yaml
    with open('/ansible/group_vars/all.yml') as f:
        config = yaml.safe_load(f)

    static_hosts = config.get('static_hosts', [])

    if not static_hosts:
        pytest.skip("No static hosts configured")

    # Check DHCP leases
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('10.11.12.1', username='root', key_filename='/root/.ssh/id_rsa')

    stdin, stdout, stderr = client.exec_command('cat /tmp/dhcp.leases')
    leases = stdout.read().decode()

    # Verify each static host has correct IP
    for host in static_hosts:
        mac = host['mac'].lower()
        expected_ip = host['ip']

        # Search for MAC in leases
        for line in leases.split('\n'):
            if mac in line.lower():
                parts = line.split()
                actual_ip = parts[2]
                assert actual_ip == expected_ip, \
                    f"Static host {host['name']} has IP {actual_ip}, expected {expected_ip}"
                break
        else:
            # MAC not found in leases (might not be connected)
            pytest.skip(f"Static host {host['name']} not connected")

    client.close()
```

**DNS testing:**

```bash
# Test DNS resolution from each node
for i in 1 2 3; do
  echo "=== Node $i ==="
  ssh root@10.11.12.$i "nslookup google.com"
done

# Test with specific DNS server
ssh root@10.11.12.1 "nslookup google.com 1.1.1.1"

# Test reverse DNS
ssh root@10.11.12.1 "nslookup 8.8.8.8"
```

### 6. Wireless Testing

**WiFi client connectivity:**

```bash
# Check wireless interface status
ssh root@10.11.12.1 "iw dev"
ssh root@10.11.12.1 "iw dev wlan1 info"

# List connected clients
ssh root@10.11.12.1 "iw dev wlan1 station dump"

# Expected output shows connected clients with:
# - Signal strength (dBm)
# - TX/RX rates
# - Connected time
```

**802.11r roaming test:**

```bash
# Monitor client as it roams between APs
# Requires wireless client that supports 802.11r

# On each node, monitor client association
ssh root@10.11.12.1 "iw dev wlan1 station dump | grep <client-mac>"

# Check roaming events in logs
ssh root@10.11.12.1 "logread -f | grep -i roam"

# Measure roaming time (requires client-side script)
# Expected: < 50ms handoff time with 802.11r
```

### 7. Test Automation

**Test runner script:**

```bash
#!/bin/bash
# tests/scripts/run_all_tests.sh

set -e

echo "=== Mesh Network Test Suite ==="
echo "Starting at $(date)"
echo ""

# 1. Unit tests
echo "Running unit tests..."
pytest tests/unit/ -v --tb=short
echo ""

# 2. Integration tests
echo "Running integration tests..."
pytest tests/integration/ -v --tb=short
echo ""

# 3. Functional tests
echo "Running functional tests..."
pytest tests/functional/ -v --tb=short
echo ""

# 4. Performance tests
echo "Running performance tests..."
pytest tests/performance/ -v --tb=short
echo ""

# 5. Failover tests (optional, slow)
if [ "$RUN_FAILOVER_TESTS" = "1" ]; then
  echo "Running failover tests..."
  pytest tests/failover/ -v --tb=short
  echo ""
fi

# 6. Generate report
echo "Generating test report..."
python tests/scripts/generate_report.py

echo ""
echo "Test suite completed at $(date)"
echo "Report: tests/report.html"
```

**Report generator:**

```python
# tests/scripts/generate_report.py
import json
import subprocess
from datetime import datetime
from tabulate import tabulate

def generate_report():
    """Generate comprehensive test report"""

    # Run pytest with JSON output
    result = subprocess.run([
        'pytest', 'tests/', '-v', '--tb=short',
        '--json-report', '--json-report-file=tests/report.json'
    ], capture_output=True)

    # Load results
    with open('tests/report.json') as f:
        data = json.load(f)

    # Generate HTML report
    with open('tests/report.html', 'w') as f:
        f.write(f"""
        <html>
        <head><title>Mesh Network Test Report</title></head>
        <body>
        <h1>Mesh Network Test Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>Summary</h2>
        <table border="1">
          <tr><th>Total</th><td>{data['summary']['total']}</td></tr>
          <tr><th>Passed</th><td>{data['summary']['passed']}</td></tr>
          <tr><th>Failed</th><td>{data['summary']['failed']}</td></tr>
          <tr><th>Skipped</th><td>{data['summary']['skipped']}</td></tr>
          <tr><th>Duration</th><td>{data['summary']['duration']:.2f}s</td></tr>
        </table>

        <h2>Test Results</h2>
        ...
        </body>
        </html>
        """)

    print(f"Report generated: tests/report.html")

if __name__ == '__main__':
    generate_report()
```

## Success Criteria

You should be able to:

- ✅ Test basic network connectivity (ping, traceroute)
- ✅ Verify mesh topology and TQ values
- ✅ Test gateway selection and failover
- ✅ Benchmark throughput and latency
- ✅ Validate DHCP/DNS functionality
- ✅ Test wireless client connectivity
- ✅ Simulate and test failover scenarios
- ✅ Automate test execution
- ✅ Generate test reports

## Reference

See `/home/m/repos/mesh/CLAUDE.md` sections:
- "Comprehensive Test Suite" - Complete testing requirements
- "Test Categories" - Detailed test specifications
- "Phase 5-9" - Test implementation checklists
- "Success Criteria" - Acceptance thresholds
