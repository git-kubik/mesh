# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

Infrastructure-as-code for deploying a 3-node OpenWrt mesh network using Ansible in Docker.

**Stack**: OpenWrt + Batman-adv + Ansible + Docker + pytest
**Hardware**: D-Link DIR-1960 A1 (3 nodes)
**Network**: 10.11.12.0/24 (Node1: .1, Node2: .2, Node3: .3)
**Topology**: Full ring (LAN3/LAN4 wired) + 2.4GHz wireless backup + multi-WAN failover

## Specialized Skills

Invoke these skills for detailed technical guidance:

- **`docker-dev`** - Docker containers, Compose, web interface (Semaphore/AWX)
- **`ansible-dev`** - Playbooks, templates, inventory, Vault
- **`python-test`** - pytest testing with UV package manager
- **`openwrt-config`** - UCI configuration, opkg, system administration
- **`batman-mesh`** - Mesh routing, batctl, topology, gateway selection
- **`tech-docs`** - Technical documentation and MkDocs Material
- **`mesh-test`** - Network testing, benchmarking, failover validation
- **`project-standards`** - Code quality, testing, security standards
- **`mesh-pm`** - Project management and progress tracking

See `.claude/skills/README.md` for details.

## Repository Structure

```
mesh/
├── openwrt-mesh-ansible/       # Ansible project (inventory, playbooks, templates)
├── docker/                     # Docker containerization (to be created)
├── tests/                      # Test suite (to be created)
├── docs/                       # Documentation
├── .claude/skills/             # Specialized skills
├── .github/workflows/          # CI/CD pipelines
└── scripts/                    # Utility scripts
```

## Quick Start

```bash
# Setup development environment
./scripts/setup-dev-environment.sh

# Start Docker environment (once created)
cd docker && docker-compose up -d

# Deploy to nodes (via web UI or CLI)
docker-compose exec ansible ansible-playbook -i /ansible/inventory/hosts.yml \
  /ansible/playbooks/deploy.yml

# Run tests
docker-compose exec ansible pytest tests/ -v

# Check project status
# Use mesh-pm skill commands: status, next, validate, blockers, report
```

## Standards Enforcement

All code must pass automated checks before commit:

```bash
# Install pre-commit hooks (automatic in setup script)
pre-commit install

# Run all checks manually
pre-commit run --all-files

# Format code
black . --line-length 100
isort . --profile black

# Run linters
flake8 .
mypy tests/
ansible-lint openwrt-mesh-ansible/
```

**Requirements:**

- Python: PEP 8, Black formatting, type hints, 80% coverage minimum
- YAML: 2-space indent, ansible-lint compliance
- Bash: Shellcheck validation
- All commits: Conventional Commits format
- Security: Never commit secrets, use Ansible Vault

See `project-standards` skill and `CONTRIBUTING.md` for complete details.

## Implementation Phases

The project follows a 12-phase plan:

**Phases 1-4**: Docker Infrastructure & Web Interface (use `docker-dev`)
**Phases 5-9**: Test Suite Implementation (use `python-test`, `mesh-test`)
**Phase 10**: Test Automation & CI/CD
**Phase 11**: Continuous Monitoring (optional)
**Phase 12**: Documentation (use `tech-docs`)

Use `mesh-pm` skill for detailed phase tracking and status.

## Key Configuration

All settings in `openwrt-mesh-ansible/group_vars/all.yml`

**MUST CHANGE before deployment:**

- `mesh_password` - 2.4GHz mesh password
- `client_password` - 5GHz AP password
- `batman_gw_bandwidth` - WAN speeds

## Documentation

- **Technical guide**: `docs/openwrt-batman-mesh-setup.md`
- **Quick start**: `docs/ANSIBLE-QUICKSTART.md`
- **Pre-commit hooks**: `docs/PRE-COMMIT-HOOKS.md`
- **Contributing**: `CONTRIBUTING.md`
- **Standards**: `project-standards` skill
- **Testing**: `docs/TESTING.md` (to be created)

## Essential Commands

```bash
# Format and lint
black . && isort . && flake8 . && mypy tests/

# Run pre-commit checks
pre-commit run --all-files

# Deploy (once Docker ready)
docker-compose exec ansible ansible-playbook playbooks/deploy.yml

# Verify deployment
docker-compose exec ansible ansible-playbook playbooks/verify.yml

# Check mesh status
docker-compose exec ansible ansible mesh_nodes -a "batctl o"
docker-compose exec ansible ansible mesh_nodes -a "batctl gwl"

# Run tests
pytest tests/ -v --cov
```

## Getting Help

**For technical details**: Invoke appropriate skill (see list above)
**For procedures**: Check `docs/` or `CONTRIBUTING.md`
**For standards**: Use `project-standards` skill
**For progress**: Use `mesh-pm` skill

## Critical Notes

- Docker deployment is **mandatory** (not optional)
- Comprehensive testing is **required** for production readiness
- Pre-commit hooks **block commits** if checks fail (by design)
- Secrets management via Ansible Vault **only** (never commit plaintext)
- Sequential deployment: Configure nodes one at a time initially

---

**For detailed guidance on any topic, invoke the appropriate specialized skill.**
