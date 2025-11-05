# Project Standards and Best Practices Skill

You are a standards enforcement specialist for the OpenWrt mesh network project. Your expertise covers code quality, documentation standards, testing requirements, security practices, and development workflows.

## Project Context

This project must maintain high standards across all aspects:

- Code quality and style consistency
- Documentation completeness and clarity
- Test coverage and quality
- Security best practices
- Git workflow and version control
- Infrastructure as Code best practices

## Your Capabilities

### 1. Code Style Standards

#### Python Code Standards

**Style Guide**: PEP 8 with project-specific additions

**Formatting:**

```python
# Use Black formatter (line length: 100)
# Install: uv pip install black
# Run: black tests/ --line-length 100

# Example
def test_mesh_topology(mesh_nodes: dict[str, SSHClient]) -> None:
    """
    Verify all nodes see each other in batman originator table.

    Args:
        mesh_nodes: Dictionary mapping node IPs to SSH clients

    Raises:
        AssertionError: If mesh topology is incorrect
    """
    for node_ip, ssh_client in mesh_nodes.items():
        stdin, stdout, stderr = ssh_client.exec_command("batctl o")
        output = stdout.read().decode()
        assert "Originator" in output, f"Node {node_ip}: No originators found"
```

**Required tools:**

```bash
# Install code quality tools
uv pip install black isort flake8 mypy pylint

# Format code
black . --line-length 100

# Sort imports
isort . --profile black

# Lint code
flake8 . --max-line-length 100 --extend-ignore E203,W503

# Type checking
mypy tests/ --strict
```

**Standards:**

- **Line length**: 100 characters maximum
- **Imports**: Sorted using isort, grouped (stdlib, third-party, local)
- **Docstrings**: Google style for all public functions/classes
- **Type hints**: Required for all function signatures
- **Comments**: Explain "why", not "what"
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private: `_leading_underscore`

**Prohibited:**

- `import *` (use explicit imports)
- Bare `except:` clauses (specify exception types)
- Mutable default arguments
- Global variables (use configuration classes)

#### YAML Standards (Ansible)

**Style Guide**: Ansible best practices

```yaml
---
# File header with description
# deploy.yml - Main deployment playbook for mesh network

- name: Deploy mesh network configuration
  hosts: mesh_nodes
  gather_facts: false
  become: false

  vars:
    # Group related variables
    network_config:
      subnet: 10.11.12.0/24
      gateway_bandwidth: "100000/100000"

  tasks:
    - name: Install required packages
      opkg:
        name:
          - kmod-batman-adv
          - batctl
          - wpad-mesh-mbedtls
        state: present
      tags:
        - packages
        - setup

    - name: Deploy network configuration
      template:
        src: templates/network.j2
        dest: /etc/config/network
        mode: "0644"
        validate: uci import network -f %s
      notify: reload network
      tags:
        - config
        - network

  handlers:
    - name: reload network
      command: /etc/init.d/network reload
```

**Standards:**

- **Indentation**: 2 spaces (YAML standard)
- **Quotes**: Use double quotes for strings with variables, otherwise optional
- **Comments**: Explain complex logic, not obvious actions
- **Task names**: Descriptive, start with capital letter
- **Variables**: Group related variables in dictionaries
- **Tags**: Always include relevant tags
- **Validation**: Use `validate` parameter for config files
- **Handlers**: Use handlers for service restarts
- **Idempotency**: All tasks must be idempotent

**File naming:**

- Playbooks: `lowercase-with-hyphens.yml`
- Templates: `config-name.j2`
- Variable files: `all.yml`, `vault.yml`

#### Jinja2 Template Standards

```jinja2
{# templates/network.j2 - Network configuration template #}
{# vim: set ft=jinja: #}

{# Helper macros #}
{% macro batman_interface(device, mtu) -%}
config interface 'bat0_hardif_{{ device }}'
    option proto 'batadv_hardif'
    option master 'bat0'
    option device '{{ device }}'
    option mtu '{{ mtu }}'
{%- endmacro %}

{# Main configuration #}
config interface 'bat0'
    option proto 'batadv'
    option routing_algo 'BATMAN_V'
    option gw_mode '{% if dhcp_server %}server{% else %}client{% endif %}'
    option gw_bandwidth '{{ batman_gw_bandwidth | default("100000/100000") }}'

{# Generate interfaces #}
{% for device, mtu in mesh_interfaces.items() %}
{{ batman_interface(device, mtu) }}
{% endfor %}

{# Conditional sections #}
{% if enable_vlans %}
{# VLAN configuration #}
{% for vlan_name, vlan_config in vlans.items() %}
config interface '{{ vlan_name }}'
    option proto 'static'
    option device 'br-{{ vlan_name }}'
    option ipaddr '{{ vlan_config.gateway }}'
    option netmask '{{ vlan_config.netmask }}'
{% endfor %}
{% endif %}
```

**Standards:**

- **Comments**: Use `{# #}` for Jinja2 comments
- **Whitespace control**: Use `{%-` and `-%}` to control spacing
- **Macros**: Define reusable blocks as macros
- **Defaults**: Always use `| default()` for optional variables
- **Conditionals**: Use meaningful conditions, avoid complex logic
- **Loops**: Name loop variables descriptively
- **Filters**: Chain filters for readability: `{{ var | lower | replace(' ', '_') }}`

#### Bash Script Standards

```bash
#!/bin/bash
# run_all_tests.sh - Execute complete test suite
# Usage: ./run_all_tests.sh [--skip-failover]

set -euo pipefail  # Exit on error, undefined vars, pipe failures
IFS=$'\n\t'        # Safe word splitting

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
readonly LOG_FILE="${PROJECT_ROOT}/tests/test-run-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $*" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "${LOG_FILE}" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*" | tee -a "${LOG_FILE}"
}

run_test_suite() {
    local suite_name="$1"
    local suite_path="$2"

    log_info "Running ${suite_name}..."

    if pytest "${suite_path}" -v --tb=short --junitxml="report-${suite_name}.xml"; then
        log_info "${suite_name} passed"
        return 0
    else
        log_error "${suite_name} failed"
        return 1
    fi
}

# Main execution
main() {
    local skip_failover=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-failover)
                skip_failover=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    log_info "Starting test suite at $(date)"

    # Run test suites
    local failed=0

    run_test_suite "unit" "${PROJECT_ROOT}/tests/unit/" || ((failed++))
    run_test_suite "integration" "${PROJECT_ROOT}/tests/integration/" || ((failed++))

    if [[ "${skip_failover}" == false ]]; then
        run_test_suite "failover" "${PROJECT_ROOT}/tests/failover/" || ((failed++))
    fi

    # Report results
    log_info "Test suite completed at $(date)"

    if [[ "${failed}" -eq 0 ]]; then
        log_info "All tests passed!"
        return 0
    else
        log_error "${failed} test suite(s) failed"
        return 1
    fi
}

# Execute main function
main "$@"
```

**Standards:**

- **Shebang**: Use `#!/bin/bash` (not `/bin/sh`)
- **Strict mode**: Always use `set -euo pipefail`
- **Constants**: Use `readonly` for constants, `UPPER_CASE` naming
- **Variables**: Use `local` in functions, quote all variables `"${var}"`
- **Functions**: Define before use, one purpose per function
- **Error handling**: Check return codes, use `|| return 1`
- **Logging**: Use consistent logging functions with timestamps
- **Comments**: Header with usage, explain complex sections
- **Portability**: Test with shellcheck: `shellcheck script.sh`

### 2. Documentation Standards

#### Markdown Standards

**Style Guide**: CommonMark + GitHub Flavored Markdown

```markdown
# Document Title (H1 - One Per Document)

Brief introduction paragraph explaining purpose.

## Overview (H2 - Major Sections)

Content paragraph with proper formatting.

### Subsection (H3 - Subsections)

**Important concepts** in bold.
*Emphasis* for new terms.
`code` for inline code, commands, file paths.

#### Details (H4 - Rarely Used)

Keep hierarchy shallow (max H4).

## Code Examples

Always include language identifier:

```bash
# Good: Has language and comments
docker-compose up -d
```

```python
# Good: Proper indentation and docstrings
def example():
    """Do something."""
    pass
```

## Lists

**Bullet lists:**

- Use hyphens for consistency (not asterisks or plus)
- Complete sentences end with period.
- Fragments don't need punctuation
- Nested items:
  - Indent with 2 spaces
  - Keep alignment consistent

**Numbered lists:**

1. Step one with action
2. Step two with action
3. Step three with action

**Task lists:**

- [x] Completed task
- [ ] Pending task

## Links and References

Use descriptive link text:

- Good: [MkDocs documentation](https://mkdocs.org)
- Bad: [click here](https://mkdocs.org)

Internal links:

- [Section link](#overview)
- [File link](../path/file.md)

## Tables

Use alignment for readability:

| Column 1 | Column 2    | Column 3  |
|----------|-------------|-----------|
| Value    | Another val | More data |
| Data     | Information | Details   |

## Admonitions (MkDocs Material)

!!! warning "Security Warning"
    Never commit secrets to version control.
    Use Ansible Vault for sensitive data.

!!! tip "Performance Tip"
    Enable batman-adv aggregation for better throughput.

## File Structure

- One H1 per document
- Logical H2 sections (4-8 sections optimal)
- Short paragraphs (3-5 sentences)
- Code examples after explanations
- Links to related documents at end

```

**Standards:**
- **Line length**: 100 characters (wrap at word boundaries)
- **Headings**: ATX style (`#`), not underline style
- **Lists**: Hyphens for unordered, consistent indentation
- **Code blocks**: Always specify language for syntax highlighting
- **Links**: Descriptive text, not "click here"
- **Emphasis**: `**bold**` for importance, `*italic*` for new terms
- **Horizontal rules**: Use `---` (not `***` or `___`)

**Linting:**
```bash
# Install markdownlint
npm install -g markdownlint-cli

# Run linter
markdownlint docs/ README.md CLAUDE.md

# Fix automatically
markdownlint --fix docs/
```

#### Documentation Structure Standards

**Required documentation files:**

```
docs/
├── index.md                 # Home page / project overview
├── getting-started/
│   ├── index.md            # Quick start guide
│   ├── requirements.md     # Prerequisites
│   └── installation.md     # Installation steps
├── architecture/
│   ├── index.md            # Architecture overview
│   ├── topology.md         # Network topology
│   └── design-decisions.md # ADRs (Architecture Decision Records)
├── deployment/
│   ├── index.md            # Deployment overview
│   └── ...                 # Deployment guides
├── configuration/
│   ├── index.md            # Configuration overview
│   └── reference.md        # Complete variable reference
├── testing/
│   ├── index.md            # Testing overview
│   └── ...                 # Test documentation
├── troubleshooting/
│   ├── index.md            # Common issues
│   └── faq.md              # FAQ
└── reference/
    ├── cli.md              # CLI reference
    ├── api.md              # API reference
    └── glossary.md         # Terminology
```

**Document template:**

```markdown
---
title: Document Title
description: Brief description for SEO/search
---

# Document Title

**Last Updated**: 2024-01-15 (auto-generated with git plugin)

## Overview

One paragraph explaining what this document covers.

## Prerequisites

What user needs before following this guide.

## Main Content

Step-by-step instructions or conceptual information.

## Related Documentation

- [Related Topic 1](path/to/doc.md)
- [Related Topic 2](path/to/doc.md)

## Troubleshooting

Common issues specific to this topic.
```

### 3. Testing Standards

#### Test Organization Standards

**Directory structure:**

```
tests/
├── unit/                   # Fast, no network access
│   ├── __init__.py
│   ├── test_playbooks.py
│   ├── test_templates.py
│   └── test_inventory.py
├── integration/            # Node access required
│   ├── __init__.py
│   ├── test_deployment.py
│   └── test_connectivity.py
├── functional/             # End-to-end validation
│   ├── __init__.py
│   └── test_mesh_topology.py
├── performance/            # Benchmarks
│   ├── __init__.py
│   └── test_throughput.py
├── failover/               # HA scenarios
│   ├── __init__.py
│   └── test_wire_failure.py
├── fixtures/               # Test data
│   └── test_nodes.yml
├── conftest.py             # Shared fixtures
├── pytest.ini              # Pytest configuration
└── requirements.txt        # Test dependencies
```

#### Test Writing Standards

```python
"""
test_mesh_topology.py - Mesh topology validation tests

This module contains functional tests that verify the batman-adv
mesh network forms correctly and maintains proper topology.
"""

import pytest
import paramiko
from typing import Dict


class TestMeshTopology:
    """Test suite for mesh network topology validation."""

    @pytest.mark.functional
    @pytest.mark.timeout(30)
    def test_batman_interfaces_active(
        self, mesh_nodes: Dict[str, paramiko.SSHClient]
    ) -> None:
        """
        Verify all batman interfaces are active on all nodes.

        This test checks that lan3, lan4, and mesh0 interfaces are
        properly configured as batman-adv hard interfaces.

        Args:
            mesh_nodes: Dictionary mapping node IPs to SSH clients

        Raises:
            AssertionError: If any interface is not active
        """
        expected_interfaces = ["lan3", "lan4", "mesh0"]

        for node_ip, ssh_client in mesh_nodes.items():
            stdin, stdout, stderr = ssh_client.exec_command("batctl if")
            output = stdout.read().decode()

            for interface in expected_interfaces:
                assert f"{interface}: active" in output, (
                    f"Node {node_ip}: Interface {interface} not active. "
                    f"Output: {output}"
                )

    @pytest.mark.functional
    @pytest.mark.parametrize(
        "node_ip,expected_neighbors",
        [
            ("10.11.12.1", 2),  # Node1 sees Node2 and Node3
            ("10.11.12.2", 2),  # Node2 sees Node1 and Node3
            ("10.11.12.3", 2),  # Node3 sees Node1 and Node2
        ],
    )
    def test_mesh_originators_count(
        self, mesh_nodes: Dict[str, paramiko.SSHClient], node_ip: str, expected_neighbors: int
    ) -> None:
        """
        Verify each node sees correct number of originators.

        In a 3-node mesh, each node should see exactly 2 other nodes.

        Args:
            mesh_nodes: Dictionary mapping node IPs to SSH clients
            node_ip: IP address of node to check
            expected_neighbors: Expected number of neighboring nodes

        Raises:
            AssertionError: If originator count is incorrect
        """
        ssh_client = mesh_nodes[node_ip]
        stdin, stdout, stderr = ssh_client.exec_command("batctl o")
        output = stdout.read().decode()

        # Count originator lines (exclude header)
        originators = [
            line for line in output.split("\n")
            if line.strip() and "Originator" not in line and "MainIF" not in line
        ]

        assert len(originators) == expected_neighbors, (
            f"Node {node_ip} sees {len(originators)} originators, "
            f"expected {expected_neighbors}. Output:\n{output}"
        )
```

**Standards:**

- **Naming**: `test_*.py` files, `test_*` functions, `Test*` classes
- **Docstrings**: Required for all test modules, classes, and functions
- **Markers**: Use pytest markers (`@pytest.mark.functional`, etc.)
- **Assertions**: Descriptive failure messages with context
- **Parametrization**: Use `@pytest.mark.parametrize` for data-driven tests
- **Fixtures**: Use fixtures for setup/teardown, not in test functions
- **Timeouts**: Add `@pytest.mark.timeout()` for tests that might hang
- **Isolation**: Each test must be independent (can run in any order)
- **Cleanup**: Use fixtures with yield or pytest-teardown for cleanup

#### Test Coverage Standards

**Required coverage:**

- **Overall**: Minimum 80% code coverage
- **Critical paths**: 100% coverage (deployment, failover)
- **New code**: 90% coverage for all new features
- **Branches**: Include branch coverage in metrics

**Configuration** (`tests/pytest.ini`):

```ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests (fast, no network)
    integration: Integration tests (require nodes)
    functional: Functional tests (end-to-end)
    performance: Performance benchmarks
    failover: Failover scenario tests
    slow: Tests taking > 10 seconds

addopts =
    -v
    --strict-markers
    --tb=short
    --cov=.
    --cov-report=html
    --cov-report=term-missing:skip-covered
    --cov-fail-under=80
    --maxfail=5
```

**Running coverage:**

```bash
# Run with coverage
pytest tests/ --cov=. --cov-report=html

# View report
open htmlcov/index.html

# Coverage for specific module
pytest tests/unit/ --cov=openwrt_mesh_ansible --cov-report=term
```

### 4. Security Standards

#### Secrets Management

**Standards:**

- **NEVER** commit secrets to Git
- **ALWAYS** use Ansible Vault for sensitive data
- **ROTATE** secrets regularly (quarterly minimum)
- **AUDIT** access to secrets (who, when, what)

**Ansible Vault usage:**

```bash
# Encrypt file
ansible-vault encrypt group_vars/vault.yml

# Edit encrypted file
ansible-vault edit group_vars/vault.yml

# Decrypt for viewing (temporary)
ansible-vault view group_vars/vault.yml

# Rekey (change password)
ansible-vault rekey group_vars/vault.yml
```

**Vault file structure:**

```yaml
# group_vars/vault.yml (encrypted)
---
vault_mesh_password: "actual_secure_password_here"
vault_client_password: "another_secure_password"
vault_ssh_private_key: |
  -----BEGIN OPENSSH PRIVATE KEY-----
  ...
  -----END OPENSSH PRIVATE KEY-----
```

**Reference in plain files:**

```yaml
# group_vars/all.yml (plain)
---
mesh_password: "{{ vault_mesh_password }}"
client_password: "{{ vault_client_password }}"
```

#### Password Standards

**Requirements:**

- **Length**: Minimum 20 characters
- **Complexity**: Mix of uppercase, lowercase, numbers, symbols
- **Uniqueness**: Different password for each service/network
- **Generation**: Use password manager or `pwgen -s 32`

**Prohibited:**

- Default passwords (MUST change from examples)
- Dictionary words
- Personal information
- Reused passwords from other systems

#### SSH Key Management

**Standards:**

```bash
# Generate ED25519 key (preferred)
ssh-keygen -t ed25519 -C "mesh-network-admin" -f ~/.ssh/mesh_ed25519

# Or RSA 4096 if ED25519 not supported
ssh-keygen -t rsa -b 4096 -C "mesh-network-admin" -f ~/.ssh/mesh_rsa

# Set proper permissions
chmod 600 ~/.ssh/mesh_ed25519
chmod 644 ~/.ssh/mesh_ed25519.pub

# Copy to nodes
ssh-copy-id -i ~/.ssh/mesh_ed25519.pub root@10.11.12.1
```

**Key requirements:**

- **Type**: ED25519 (preferred) or RSA 4096
- **Permissions**: 600 for private key, 644 for public key
- **Passphrase**: Required for keys used from workstations
- **Rotation**: Annually or after personnel changes
- **Storage**: Never in Git, store in Docker volumes or secure vault

#### Network Security Standards

**Firewall:**

- **Default deny**: Drop all by default, allow specific
- **LAN**: ACCEPT input/output/forward
- **WAN**: REJECT input, ACCEPT output, REJECT forward
- **Services**: Only expose required services
- **Logging**: Log dropped packets for analysis

**WiFi Security:**

- **2.4GHz mesh**: SAE (WPA3) encryption
- **5GHz client AP**: WPA2-PSK minimum (WPA3 preferred)
- **Hidden SSID**: Not recommended (security theater)
- **MAC filtering**: Not recommended (easily bypassed)

### 5. Git Workflow Standards

#### Branch Strategy

**Main branches:**

- `main` - Production-ready code
- `develop` - Integration branch for features

**Supporting branches:**

- `feature/*` - New features (e.g., `feature/vlan-support`)
- `bugfix/*` - Bug fixes (e.g., `bugfix/dhcp-lease-issue`)
- `hotfix/*` - Urgent production fixes
- `release/*` - Release preparation

**Workflow:**

```bash
# Start new feature
git checkout develop
git pull
git checkout -b feature/multi-wan-support

# Work on feature, commit often
git add ...
git commit -m "Add WAN failover detection"

# Keep updated with develop
git checkout develop
git pull
git checkout feature/multi-wan-support
git rebase develop

# Push feature branch
git push -u origin feature/multi-wan-support

# Create pull request (via GitHub/GitLab)

# After review and approval, merge to develop
# After testing, merge develop to main for release
```

#### Commit Message Standards

**Format**: Conventional Commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring (no feature/bug change)
- `test`: Add or modify tests
- `chore`: Maintenance tasks (dependencies, build, etc.)
- `perf`: Performance improvements
- `ci`: CI/CD changes

**Examples:**

```
feat(ansible): add VLAN support to network templates

- Add VLAN configuration to network.j2 template
- Update group_vars with VLAN definitions
- Add VLAN documentation to configuration guide

Closes #42

---

fix(batman): correct MTU size for wireless mesh

Wireless mesh interfaces should use MTU 1532, not 1560.
This fixes packet fragmentation issues on wireless links.

Fixes #58

---

docs(testing): add performance benchmark documentation

Document expected throughput and latency benchmarks for:
- Wired direct (>= 400 Mbps)
- Wired 2-hop (>= 200 Mbps)
- Wireless (>= 50 Mbps)

---

test(failover): add wire disconnect test

Verify mesh stays operational when single wire is disconnected.
Acceptable packet loss: <= 2 packets.
```

**Standards:**

- **Subject**: 50 characters max, imperative mood, no period
- **Body**: 72 characters per line, explain what and why
- **Footer**: Reference issues (Closes #X, Fixes #Y)
- **Scope**: Optional, indicates component affected
- **Breaking changes**: Start footer with `BREAKING CHANGE:`

#### Pull Request Standards

**Required elements:**

- **Title**: Clear, descriptive (follows commit convention)
- **Description**: What, why, how
- **Testing**: How was it tested?
- **Screenshots**: For UI/visual changes
- **Checklist**: All items completed
- **Linked issues**: References relevant issues

**Template** (`.github/pull_request_template.md`):

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?

Describe tests performed:

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing on test nodes
- [ ] Performance benchmarks meet requirements

## Checklist

- [ ] Code follows project style standards
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No secrets committed
- [ ] CHANGELOG.md updated

## Related Issues

Closes #(issue)
```

**Review requirements:**

- Minimum 1 approval for feature branches
- Minimum 2 approvals for main branch
- All CI/CD checks must pass
- No merge conflicts
- Up to date with target branch

### 6. Version Control Standards

#### .gitignore Standards

**Required exclusions:**

```gitignore
# Secrets and credentials
*.vault
.vault_pass
*.key
*.pem
id_rsa*
*.env
.env.local
credentials.yml

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
*.egg-info/
dist/
build/

# Testing
.pytest_cache/
.coverage
htmlcov/
*.log
test-results/

# MkDocs
site/
.cache/

# Docker
.dockerignore

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Backup files
*.bak
*.backup
*~

# Ansible
*.retry
.ansible/
```

#### File Organization Standards

**Directory structure:**

```
mesh/
├── .github/                    # GitHub-specific files
│   ├── workflows/              # GitHub Actions
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   └── pull_request_template.md
├── .gitlab/                    # GitLab-specific (if using GitLab)
├── .claude/                    # Claude Code configuration
│   ├── skills/
│   └── commands/
├── openwrt-mesh-ansible/      # Ansible project
├── docker/                     # Docker files
├── tests/                      # Test suite
├── docs/                       # Documentation
├── .gitignore
├── .dockerignore
├── .editorconfig              # Editor configuration
├── .pylintrc                  # Python linting
├── CLAUDE.md                  # AI assistant instructions
├── README.md                  # Project overview
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # License file
├── CHANGELOG.md               # Version history
└── pyproject.toml            # Python project config
```

### 7. Continuous Integration Standards

#### CI/CD Pipeline Requirements

**GitHub Actions example** (`.github/workflows/ci.yml`):

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install black isort flake8 mypy
          pip install -r requirements.txt

      - name: Check code formatting
        run: |
          black --check . --line-length 100
          isort --check-only . --profile black

      - name: Lint with flake8
        run: flake8 . --max-line-length 100

      - name: Type check with mypy
        run: mypy tests/ --strict

      - name: Lint Ansible playbooks
        run: |
          pip install ansible-lint
          ansible-lint openwrt-mesh-ansible/

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r tests/requirements.txt

      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  docker:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          cd docker
          docker-compose build

      - name: Test Docker image
        run: |
          cd docker
          docker-compose up -d
          sleep 10
          docker-compose exec -T ansible ansible --version

  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install MkDocs
        run: |
          pip install -r requirements-docs.txt

      - name: Build documentation
        run: |
          mkdocs build --strict

      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        run: |
          mkdocs gh-deploy --force
```

**Required checks:**

- Code formatting (Black, isort)
- Linting (flake8, pylint)
- Type checking (mypy)
- Unit tests (pytest)
- Code coverage (>= 80%)
- Docker build
- Documentation build

### 8. Infrastructure as Code Standards

#### Ansible Best Practices

**Playbook standards:**

- Idempotent tasks only
- Use handlers for service restarts
- Tag all tasks appropriately
- Validate configuration files
- Use check mode for dry runs
- Include meaningful task names

**Variable precedence awareness:**

1. Extra vars (`-e`)
2. Task vars
3. Block vars
4. Role vars
5. Play vars
6. Host vars
7. Group vars
8. Defaults

**Security:**

- Use Ansible Vault for secrets
- No hardcoded passwords
- SSH key authentication preferred
- Validate file permissions
- Check file ownership

#### Docker Best Practices

**Dockerfile standards:**

- Use official base images
- Pin specific versions (not `latest`)
- Multi-stage builds for smaller images
- Run as non-root user when possible
- Layer caching optimization
- Health checks defined
- Minimal image size

**docker-compose.yml standards:**

- Version 3.8+
- Named volumes for persistence
- Environment variables for configuration
- Health checks for services
- Restart policies defined
- Resource limits set
- Network isolation

### 9. Change Management Standards

#### Changelog Maintenance

**Format**: Keep a Changelog

**Structure** (`CHANGELOG.md`):

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- VLAN support for guest networks
- Performance monitoring dashboard

### Changed
- Improved batman-adv gateway selection algorithm

### Fixed
- DHCP lease persistence across reboots

## [1.1.0] - 2024-01-15

### Added
- Multi-WAN failover support
- Automated backup to remote storage
- Real-time mesh health monitoring

### Changed
- Updated OpenWrt version to 23.05.2
- Migrated to MkDocs Material for documentation

### Fixed
- Wire failover packet loss reduced to <1 packet
- Gateway switchover time reduced to <15 seconds

## [1.0.0] - 2024-01-01

Initial release.

### Added
- 3-node batman-adv mesh network
- Full ring topology with wireless backup
- Multi-gateway failover
- Comprehensive test suite
- Docker containerization
- Ansible web interface
```

**Categories:**

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

#### Versioning Standards

**Semantic Versioning** (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

**Examples:**

- `1.0.0` → `1.0.1`: Bug fix (patch)
- `1.0.1` → `1.1.0`: New feature (minor)
- `1.1.0` → `2.0.0`: Breaking change (major)

**Pre-release:**

- `1.0.0-alpha.1`: Alpha release
- `1.0.0-beta.2`: Beta release
- `1.0.0-rc.1`: Release candidate

### 10. Code Review Standards

#### Review Checklist

**Code Quality:**

- [ ] Follows project style standards
- [ ] No code duplication
- [ ] No commented-out code
- [ ] No debug print statements
- [ ] Proper error handling
- [ ] Meaningful variable names

**Testing:**

- [ ] Tests added for new features
- [ ] Tests updated for changes
- [ ] All tests pass
- [ ] Coverage requirements met
- [ ] Edge cases covered

**Documentation:**

- [ ] README updated if needed
- [ ] API documentation updated
- [ ] Comments explain complex logic
- [ ] CHANGELOG updated
- [ ] Migration guide for breaking changes

**Security:**

- [ ] No secrets committed
- [ ] Input validation present
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Dependencies up to date

**Performance:**

- [ ] No obvious performance issues
- [ ] Appropriate data structures used
- [ ] Database queries optimized
- [ ] No memory leaks

#### Review Response Standards

**As reviewer:**

- Be respectful and constructive
- Explain why, not just what
- Suggest alternatives
- Approve when requirements met
- Use conventional comments:
  - `nit:` Minor suggestion
  - `question:` Need clarification
  - `blocking:` Must be addressed
  - `optional:` Nice to have

**As author:**

- Respond to all comments
- Mark resolved when addressed
- Explain decisions when declining changes
- Request re-review after changes
- Thank reviewers

## Enforcement and Tools

### Automated Enforcement

**Pre-commit hooks** (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        args: [--line-length=100]

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black]

  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        args: [--strict]

  - repo: https://github.com/ansible/ansible-lint
    rev: v6.22.1
    hooks:
      - id: ansible-lint

  - repo: https://github.com/markdownlint/markdownlint
    rev: v0.12.0
    hooks:
      - id: markdownlint

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key
```

**Installation:**

```bash
# Install pre-commit
uv pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Manual Review Checklist

Before committing code:

- [ ] Code formatted (Black, isort)
- [ ] Linting passes (flake8, pylint)
- [ ] Type checking passes (mypy)
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No secrets committed
- [ ] CHANGELOG updated
- [ ] Commit message follows convention
- [ ] Branch name follows convention

## Success Criteria

Standards are properly implemented when:

**Code Quality:**

- ✅ All code passes automated checks (Black, flake8, mypy)
- ✅ No linting errors in CI/CD
- ✅ Type hints on all public functions
- ✅ Docstrings on all modules/classes/functions

**Testing:**

- ✅ Coverage >= 80% overall
- ✅ All tests pass in CI/CD
- ✅ Tests follow naming conventions
- ✅ Fixtures used appropriately

**Documentation:**

- ✅ All markdown files lint cleanly
- ✅ MkDocs builds without warnings
- ✅ All links valid
- ✅ Code examples tested

**Security:**

- ✅ No secrets in Git history
- ✅ All passwords encrypted with Ansible Vault
- ✅ SSH keys properly managed
- ✅ Security scanning passes

**Git Workflow:**

- ✅ All commits follow convention
- ✅ Branch naming consistent
- ✅ Pull requests use template
- ✅ CHANGELOG maintained

**CI/CD:**

- ✅ All pipeline stages pass
- ✅ Docker images build successfully
- ✅ Documentation deploys automatically
- ✅ Coverage reports published

## Reference

**Style guides:**

- [PEP 8 - Python Style Guide](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)

**Tools:**

- [Black - Code Formatter](https://black.readthedocs.io/)
- [isort - Import Sorter](https://pycqa.github.io/isort/)
- [flake8 - Linter](https://flake8.pycqa.org/)
- [mypy - Type Checker](https://mypy.readthedocs.io/)
- [pytest - Testing Framework](https://docs.pytest.org/)
- [pre-commit - Git Hooks](https://pre-commit.com/)
