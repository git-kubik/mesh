# OpenWrt Multi-Gateway Batman-adv Mesh Network

[![Pre-commit Checks](https://github.com/yourusername/mesh/workflows/Pre-commit%20Checks/badge.svg)](https://github.com/yourusername/mesh/actions)
[![Tests](https://github.com/yourusername/mesh/workflows/Tests/badge.svg)](https://github.com/yourusername/mesh/actions)
[![codecov](https://codecov.io/gh/yourusername/mesh/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/mesh)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://yourusername.github.io/mesh/)

High-availability OpenWrt mesh network with Batman-adv routing, multi-gateway failover, and comprehensive automated testing.

## Features

- **🔄 Full Ring Topology**: 3 wired connections (LAN3/LAN4 ports) forming a complete ring
- **📡 Wireless Backup**: 2.4GHz 802.11s mesh for automatic failover
- **🌐 Multi-Gateway**: 3 independent WAN connections with automatic failover
- **📱 Unified WiFi**: 5GHz client AP with 802.11r seamless roaming
- **🐧 Batman-adv V**: Layer 2 mesh routing with automatic path selection
- **🐳 Docker Deployment**: Self-contained Ansible environment with web interface
- **✅ Comprehensive Testing**: Unit, integration, functional, performance, and failover tests
- **📚 Documentation**: Professional documentation site with MkDocs Material

## Deployment Options

This project provides **three ways** to deploy your mesh network, supporting different skill levels and preferences:

### 1. 🔧 Manual Deployment (Learning Path)

Complete step-by-step guide for manual configuration. Perfect for:

- Understanding how mesh networking works
- Learning OpenWrt and Batman-adv concepts
- Customizing beyond automation capabilities

**Documentation**: [Manual Setup Guide](openwrt-batman-mesh-setup.md) | [Initial Node Setup](INITIAL-NODE-SETUP.md)

### 2. 🐳 Docker CLI Automation (Developer Path)

Run Ansible playbooks via Docker exec for full automation control:

```bash
cd docker
docker-compose up -d
docker-compose exec ansible ansible-playbook -i /ansible/inventory/hosts.yml /ansible/playbooks/deploy.yml
```

**Benefits**: Direct CLI access, scriptable, version controlled
**Documentation**: [Docker README](docker-README.md) | [Ansible Quick Start](ANSIBLE-QUICKSTART.md)

### 3. 🌐 Web Interface Automation (User-Friendly Path)

Use Semaphore web UI for point-and-click deployment:

1. Access <http://localhost:3000> (after `docker-compose up -d`)
2. Login with default credentials
3. Click "Run" on the deployment template
4. Monitor progress in real-time

**Benefits**: Visual feedback, job history, scheduling, notifications
**Documentation**: [Docker README](docker-README.md)

---

**All three paths produce identical network configurations.** Choose based on your comfort level and use case.

## Quick Start

### Choose Your Path

Select a deployment method from the [Deployment Options](#deployment-options) above, then follow the appropriate guide:

- **Manual**: [Initial Node Setup](INITIAL-NODE-SETUP.md) → [Manual Setup Guide](openwrt-batman-mesh-setup.md)
- **Docker CLI**: [Docker README](docker-README.md) → [Ansible Quick Start](ANSIBLE-QUICKSTART.md)
- **Web Interface**: [Docker README](docker-README.md)

### Prerequisites (Automation Paths)

- **Hardware**: 3x D-Link DIR-1960 A1 routers with OpenWrt 24.10.4
- **Software**: Docker Desktop 20.10+ (or Docker Engine + docker-compose)
- **Network**: Ethernet cables for ring topology

### Quick Setup (Automation Paths)

1. **Clone and prepare:**

   ```bash
   git clone https://github.com/yourusername/mesh.git
   cd mesh

   # Prepare initial node (manual step required)
   # Follow: INITIAL-NODE-SETUP.md for first node
   ```

2. **Start automation environment:**

   ```bash
   cd docker
   docker-compose up -d
   ```

3. **Deploy via Web Interface OR CLI:**

   **Option A: Web Interface**
   - Open <http://localhost:3000>
   - Login: admin / changeme
   - Run deployment template

   **Option B: Docker CLI**

   ```bash
   docker-compose exec ansible ansible-playbook -i /ansible/inventory/hosts.yml /ansible/playbooks/deploy.yml
   ```

For detailed instructions, see the deployment path documentation above.

## Architecture

```
Node1 (10.11.12.1) ←lan3→ Node2 (10.11.12.2)
  ↑ lan4                      ↓ lan4
  └──────────← Node3 (10.11.12.3)

  + 2.4GHz wireless mesh backup
  + 5GHz unified client AP (802.11r roaming)
```

**Network Details:**

- **LAN**: 10.11.12.0/24
- **DHCP**: Split pools across all nodes for redundancy
  - Node1: 10.11.12.100-149
  - Node2: 10.11.12.150-199
  - Node3: 10.11.12.200-249
- **DNS**: All 3 nodes provide caching DNS (redundant)
- **Gateways**: All 3 nodes (automatic failover)
- **Client AP**: HA-Network-5G (5GHz, WPA2/WPA3)

## Development

### Quick Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/mesh.git
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

For complete standards, see [project-standards skill](https://github.com/git-kubik/mesh/blob/main/.claude/skills/project-standards.md).

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
├── openwrt-mesh-ansible/       # Ansible playbooks and templates
│   ├── inventory/hosts.yml     # Node definitions
│   ├── group_vars/all.yml      # Configuration variables
│   ├── templates/              # Jinja2 templates for OpenWrt configs
│   └── playbooks/              # Deployment playbooks
├── docker/                     # Docker containerization
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── tests/                      # Comprehensive test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── functional/             # Functional tests
│   ├── performance/            # Performance benchmarks
│   └── failover/               # Failover scenarios
├── docs/                       # MkDocs documentation
├── .github/                    # GitHub Actions workflows
│   └── workflows/
│       ├── pre-commit.yml      # Code quality enforcement
│       ├── tests.yml           # Test automation
│       └── deploy-docs.yml     # Documentation deployment
├── .claude/                    # Claude Code skills and commands
│   ├── skills/                 # Specialized development skills
│   └── commands/               # Slash commands
├── scripts/                    # Utility scripts
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── pyproject.toml              # Python project configuration
├── CLAUDE.md                   # AI assistant instructions
├── CONTRIBUTING.md             # Contribution guidelines
└── README.md                   # This file
```

## Documentation

- **Quick Start**: [ANSIBLE-QUICKSTART.md](ANSIBLE-QUICKSTART.md)
- **Technical Guide**: [openwrt-batman-mesh-setup.md](openwrt-batman-mesh-setup.md)
- **Testing Guide**: [tests-README.md](tests-README.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Full Documentation**: <https://yourusername.github.io/mesh/>

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

This project is licensed under the MIT License - see the [LICENSE](https://github.com/git-kubik/mesh/blob/main/LICENSE) file for details.

## Acknowledgments

- **OpenWrt Project**: For the excellent embedded Linux distribution
- **Batman-adv**: For the robust mesh routing protocol
- **Ansible Community**: For automation tooling
- **MkDocs Material**: For beautiful documentation

## Support

- **Documentation**: <https://yourusername.github.io/mesh/>
- **Issues**: [GitHub Issues](https://github.com/yourusername/mesh/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mesh/discussions)

## Roadmap

- [x] Basic mesh network with Batman-adv
- [x] Multi-gateway failover
- [x] Docker containerization
- [x] Comprehensive test suite
- [x] MkDocs documentation
- [x] Pre-commit hooks and CI/CD
- [ ] VLAN support for guest networks
- [ ] Monitoring dashboard
- [ ] Automated backup to cloud storage
- [ ] IPv6 support

---

**Built with ❤️ using OpenWrt, Batman-adv, Ansible, and Docker**
