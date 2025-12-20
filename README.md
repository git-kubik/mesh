# OpenWrt Multi-Gateway Batman-adv Mesh Network

[![Pre-commit Checks](https://github.com/git-kubik/mesh/workflows/Pre-commit%20Checks/badge.svg)](https://github.com/git-kubik/mesh/actions)
[![Tests](https://github.com/git-kubik/mesh/workflows/Tests/badge.svg)](https://github.com/git-kubik/mesh/actions)
[![codecov](https://codecov.io/gh/git-kubik/mesh/branch/main/graph/badge.svg)](https://codecov.io/gh/git-kubik/mesh)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://git-kubik.github.io/mesh/)

High-availability OpenWrt mesh network with Batman-adv routing, multi-gateway failover, VLAN segmentation, and comprehensive automated testing.

## Features

- **Full Ring Topology**: 3 wired connections via managed switches forming a redundant ring
- **Wireless Backup**: 2.4GHz 802.11s mesh for automatic failover
- **Multi-Gateway**: 3 independent WAN connections with automatic failover
- **VLAN Segmentation**: Management (10), Guest (20), IoT (30), Mesh backbone (100), Client (200)
- **Unified WiFi**: 5GHz client AP with 802.11r seamless roaming
- **Batman-adv V**: Layer 2 mesh routing with Bridge Loop Avoidance (BLA)
- **Switch Integration**: TP-Link TL-SG108E managed switches for VLAN trunking
- **Docker Deployment**: Self-contained Ansible environment with Semaphore web interface
- **Comprehensive Testing**: 39 test files across unit, integration, functional, performance, and failover categories
- **Documentation**: Professional documentation site with MkDocs Material

## Deployment Options

This project provides **three ways** to deploy your mesh network, supporting different skill levels and preferences:

### 1. Makefile Automation (Recommended)

Run Ansible playbooks via Makefile for full automation control:

```bash
cd openwrt-mesh-ansible
make deploy-node NODE=1  # Deploy to a single node
make deploy              # Deploy to all nodes
make verify              # Verify mesh status
```

**Benefits**: Direct CLI access, scriptable, auto-detects node state
**Documentation**: [Makefile Reference](docs/reference/makefile.md) | [Quick Start](docs/getting-started/quickstart.md)

### 2. Docker Web Interface

Use Semaphore web UI for point-and-click deployment:

1. Start containers: `cd docker && docker-compose up -d`
2. Access <http://localhost:3000>
3. Login with configured credentials
4. Run deployment templates

**Benefits**: Visual feedback, job history, scheduling
**Documentation**: [Docker Setup](docs/development/docker.md)

### 3. Manual Configuration (Learning Path)

Complete step-by-step guide for understanding the configuration. Perfect for:

- Understanding how mesh networking works
- Learning OpenWrt and Batman-adv concepts
- Customizing beyond automation capabilities

**Documentation**: [Architecture Overview](docs/architecture/overview.md)

---

**All paths produce identical network configurations.** Choose based on your comfort level and use case.

## Quick Start

### Prerequisites

- **Hardware**: 3x D-Link DIR-1960 A1 routers with OpenWrt 24.10.4
- **Switches**: 2x TP-Link TL-SG108E managed switches (for VLAN trunking)
- **Software**: Python 3.11+, Ansible 8+, Docker (optional for web UI)
- **Network**: Ethernet cables for ring topology

### Quick Setup

1. **Clone and prepare:**

   ```bash
   git clone https://github.com/git-kubik/mesh.git
   cd mesh
   cp .env.example .env  # Configure credentials
   ```

2. **Deploy nodes one at a time:**

   ```bash
   cd openwrt-mesh-ansible

   # Deploy each node (auto-detects initial vs production state)
   make deploy-node NODE=1
   make deploy-node NODE=2
   make deploy-node NODE=3
   ```

3. **Verify the mesh:**

   ```bash
   make check-all       # Connectivity check
   make batman-status   # Mesh topology
   make verify          # Full verification
   ```

For detailed instructions, see the [Quick Start Guide](docs/getting-started/quickstart.md).

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │           INTERNET                  │
                    └─────────────┬───────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
   ┌─────────┐              ┌─────────┐              ┌─────────┐
   │  WAN 1  │              │  WAN 2  │              │  WAN 3  │
   │ Node 1  │              │ Node 2  │              │ Node 3  │
   │10.11.12.1              │10.11.12.2              │10.11.12.3
   └────┬────┘              └────┬────┘              └────┬────┘
        │                        │                        │
   LAN3 │ LAN4              LAN3 │ LAN4              LAN3 │ LAN4
        │                        │                        │
   ┌────┴────────────────────────┴────────────────────────┴────┐
   │                    Switch A (All VLANs)                    │
   │                    Switch C (Mesh VLAN only)               │
   │                    + 2.4GHz Wireless Backup                │
   └────────────────────────────────────────────────────────────┘
```

**Network Segments:**

| Network | VLAN | Subnet | WiFi SSID |
|---------|------|--------|-----------|
| Client (LAN) | 200 | 10.11.12.0/24 | HA-Client (5GHz) |
| Management | 10 | 10.11.10.0/24 | HA-Management (2.4GHz) |
| Guest | 20 | 10.11.20.0/24 | HA-Guest (5GHz) |
| IoT | 30 | 10.11.30.0/24 | HA-IoT (2.4GHz) |
| Mesh Backbone | 100 | - | HA-Mesh (2.4GHz, hidden) |

**Key Features:**

- **Bridge Loop Avoidance (BLA)**: Prevents L2 loops across mesh + switch
- **Multi-Gateway**: All 3 nodes with independent WAN (auto failover)
- **802.11r Fast Roaming**: Seamless handoff on client WiFi
- **Per-Node DHCP**: Pools 100-149, 150-199, 200-249 for redundancy

## Development

### Quick Setup

```bash
# Clone and setup
git clone https://github.com/git-kubik/mesh.git
cd mesh

# Automated development environment setup
./scripts/setup-dev-environment.sh
```

This installs:

- Python development tools (Black, isort, flake8, mypy, pylint)
- Pre-commit hooks (automatically enforce code standards)
- Testing framework (pytest with coverage)
- Documentation tools (MkDocs Material)

### Pre-commit Hooks

**This project enforces code quality standards using GitHub pre-commit hooks.**

Pre-commit hooks automatically run before each commit and check:

- ✅ Code formatting (Black, isort)
- ✅ Linting (flake8, pylint)
- ✅ Type checking (mypy)
- ✅ Ansible linting (ansible-lint)
- ✅ YAML validation (yamllint)
- ✅ Markdown linting (markdownlint)
- ✅ Secrets detection (detect-secrets)
- ✅ Trailing whitespace, end-of-file, merge conflicts

**Installation** (automatic with setup script):

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

**Usage**:

```bash
# Hooks run automatically on git commit
git commit -m "feat: add new feature"

# Run manually on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks (NOT RECOMMENDED - CI will fail)
git commit --no-verify
```

**What happens when you commit:**

1. Pre-commit hooks run automatically
2. Code is auto-formatted (Black, isort)
3. All linters check your code
4. Secrets scanner checks for leaked credentials
5. If any check fails, commit is blocked
6. Fix issues and try again

### Code Standards

This project adheres to high-quality standards:

**Python**:

- Style: PEP 8 with Black formatting (100 char lines)
- Type hints required on all functions
- Docstrings required (Google style)
- Minimum 80% test coverage

**YAML/Ansible**:

- 2-space indentation
- ansible-lint compliance
- Idempotent playbooks only
- Handlers for service restarts

**Testing**:

- pytest with markers (unit, integration, functional, performance, failover)
- Minimum 80% coverage (90% for new code)
- All tests must have docstrings

**Documentation**:

- MkDocs Material for site generation
- Markdown with 100 char line length
- Must build without errors/warnings

**Security**:

- Never commit secrets (enforced by detect-secrets)
- Ansible Vault for sensitive data
- 20+ character passwords
- ED25519 or RSA 4096 SSH keys

For complete standards, see [project-standards skill](.claude/skills/project-standards.md).

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific category
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/functional/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html

# Specific test
pytest tests/unit/test_playbooks.py::test_playbook_syntax -v
```

### Documentation

```bash
# Serve documentation locally
mkdocs serve
# Access at http://127.0.0.1:8000

# Build documentation
mkdocs build --strict

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Project Structure

```
mesh/
├── openwrt-mesh-ansible/       # Ansible project root
│   ├── inventory/              # Node definitions
│   │   ├── hosts.yml           # Production inventory (10.11.12.x)
│   │   └── hosts-initial.yml   # Initial setup inventory (192.168.0.1)
│   ├── group_vars/all.yml      # Configuration variables
│   ├── roles/                  # Ansible roles with Jinja2 templates
│   │   ├── network_config/     # Network, VLANs, Batman-adv, BLA
│   │   ├── wireless_config/    # WiFi, 802.11r, mesh backbone
│   │   ├── firewall_config/    # Zone-based firewall rules
│   │   ├── dhcp_config/        # Per-node DHCP pools
│   │   ├── system_config/      # System settings, SSH, packages
│   │   └── ...                 # Additional roles
│   ├── playbooks/              # Deployment playbooks
│   └── Makefile                # Automation commands
├── docker/                     # Docker containerization
│   ├── Dockerfile              # Alpine Python 3.11 + Ansible
│   ├── docker-compose.yml      # PostgreSQL + Semaphore UI
│   └── requirements.txt        # Python dependencies
├── tests/                      # Comprehensive test suite (39 files)
│   ├── unit/                   # Unit tests (syntax, templates)
│   ├── integration/            # Integration tests (cross-role)
│   ├── functional/             # Functional tests (UCI output)
│   ├── performance/            # Performance benchmarks
│   ├── failover/               # Failover scenarios
│   └── conftest.py             # 19 pytest fixtures
├── docs/                       # MkDocs Material documentation
│   ├── architecture/           # Architecture guides
│   ├── getting-started/        # Quick start guides
│   └── reference/              # Makefile, CLI reference
├── .github/workflows/          # GitHub Actions CI/CD
├── .claude/                    # Claude Code skills and commands
├── scripts/                    # Utility scripts
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── pyproject.toml              # Python project configuration
└── CONTRIBUTING.md             # Contribution guidelines
```

## Documentation

- **Quick Start**: [Getting Started](docs/getting-started/quickstart.md)
- **Architecture**: [Overview](docs/architecture/overview.md) | [VLANs](docs/architecture/vlan-architecture.md) | [Switch Integration](docs/architecture/switch-integration.md)
- **Reference**: [Makefile Commands](docs/reference/makefile.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Full Documentation**: <https://git-kubik.github.io/mesh/>

## CI/CD

**GitHub Actions workflows:**

- **Pre-commit Checks**: Runs all linters, formatters, and security scans
- **Tests**: Executes test suite with coverage reporting
- **Deploy Documentation**: Builds and deploys MkDocs site to GitHub Pages

**Status checks required for PR approval:**

- ✅ Pre-commit hooks pass
- ✅ Code quality checks pass
- ✅ Unit tests pass (minimum 80% coverage)
- ✅ Docker build succeeds

## Performance Benchmarks

Expected performance metrics:

| Metric | Threshold | Notes |
|--------|-----------|-------|
| Wired throughput (direct) | ≥ 400 Mbps | Node1 ↔ Node2 |
| Wired throughput (2-hop) | ≥ 200 Mbps | Node1 ↔ Node3 via Node2 |
| Wireless throughput | ≥ 50 Mbps | Via 2.4GHz mesh |
| Wired latency (direct) | < 2ms | Average RTT |
| Wired latency (2-hop) | < 5ms | Average RTT |
| Wireless latency | < 20ms | Average RTT |
| Wire failover time | < 1 second | Packet loss ≤ 2 |
| Gateway switchover | < 30 seconds | Internet interruption |

## Failover Capabilities

- **Single wire failure**: Mesh stays operational, ≤2 packets lost
- **All wires fail**: Automatic fallback to wireless mesh
- **Node failure**: Remaining nodes continue operating
- **WAN failure**: Automatic gateway switchover
- **Node recovery**: Automatic rejoin within 60 seconds

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick contribution workflow:**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run `./scripts/setup-dev-environment.sh` to set up pre-commit hooks
4. Make your changes (pre-commit hooks will run on commit)
5. Add tests for new functionality
6. Ensure all tests pass (`pytest tests/ -v`)
7. Push to your fork and create a Pull Request
8. All CI/CD checks must pass for approval

**Pre-commit hooks are mandatory** - they ensure code quality and prevent common issues.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **OpenWrt Project**: For the excellent embedded Linux distribution
- **Batman-adv**: For the robust mesh routing protocol
- **Ansible Community**: For automation tooling
- **MkDocs Material**: For beautiful documentation

## Support

- **Documentation**: <https://git-kubik.github.io/mesh/>
- **Issues**: [GitHub Issues](https://github.com/git-kubik/mesh/issues)
- **Discussions**: [GitHub Discussions](https://github.com/git-kubik/mesh/discussions)

## Roadmap

- [x] Basic mesh network with Batman-adv
- [x] Multi-gateway failover
- [x] Docker containerization
- [x] Comprehensive test suite (39 test files)
- [x] MkDocs documentation
- [x] Pre-commit hooks and CI/CD
- [x] VLAN segmentation (Management, Guest, IoT, Client, Mesh)
- [x] Switch integration (TP-Link TL-SG108E)
- [x] Bridge Loop Avoidance (BLA)
- [x] 802.11r fast roaming
- [ ] Monitoring dashboard (Prometheus/Grafana)
- [ ] Automated backup to cloud storage
- [ ] IPv6 support

---

**Built with ❤️ using OpenWrt, Batman-adv, Ansible, and Docker**
