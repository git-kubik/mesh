# Development

This section covers contributing to the project, code quality standards, testing, and CI/CD integration.

## Overview

The project uses modern development practices:

- **Python** for test suite (pytest)
- **Ansible** for deployment automation
- **Pre-commit** for code quality
- **GitHub Actions** for CI/CD

## Section Contents

| Document | Description |
|----------|-------------|
| [Testing Guide](testing.md) | Comprehensive test suite documentation |
| [Contributing](contributing.md) | How to contribute to the project |
| [Pre-commit Hooks](pre-commit.md) | Code quality automation |
| [Docker Setup](docker.md) | Containerized development environment |
| [Docker MCP](docker-mcp.md) | Docker MCP setup for Claude Code |
| [Tests README](tests-readme.md) | Quick test reference |

## Quick Start for Contributors

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR-USERNAME/mesh.git
cd mesh
```

### 2. Set Up Development Environment

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### 3. Make Changes

```bash
# Create a feature branch
git checkout -b feature/my-improvement

# Make your changes
# ...

# Run pre-commit checks
uv run pre-commit run --all-files

# Run tests
uv run pytest tests/unit -v
```

### 4. Submit Pull Request

```bash
git add .
git commit -m "feat: add my improvement"
git push origin feature/my-improvement
# Open PR on GitHub
```

## Code Standards

| Category | Tool | Standard |
|----------|------|----------|
| Python Formatting | Black | 100 char line length |
| Python Imports | isort | Black-compatible profile |
| Python Linting | flake8 | Max complexity 10 |
| Python Types | mypy | Strict mode |
| YAML | yamllint | 2-space indent |
| Ansible | ansible-lint | Production profile |
| Secrets | detect-secrets | Baseline checked |

## Test Categories

| Category | Purpose | Command |
|----------|---------|---------|
| Unit | Config validation, templates | `uv run pytest tests/unit/` |
| Integration | Ansible playbook syntax | `uv run pytest tests/integration/` |
| Live | Real node deployment | `uv run pytest tests/live/` |

See [Testing Guide](testing.md) for complete details.

## Project Structure

```
mesh/
├── openwrt-mesh-ansible/     # Ansible playbooks and roles
│   ├── playbooks/            # Deployment playbooks
│   ├── roles/                # Reusable Ansible roles
│   ├── templates/            # Jinja2 templates
│   └── group_vars/           # Configuration variables
├── tests/                    # Test suite
│   ├── unit/                 # Fast, no network needed
│   ├── integration/          # Requires connectivity
│   └── live/                 # Requires running nodes
├── docs/                     # Documentation (you are here)
└── .github/workflows/        # CI/CD pipelines
```

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:

```
feat(mesh): add wireless mesh failover support
fix(ansible): correct DHCP pool overlap
docs(readme): update deployment instructions
test(unit): add template rendering tests
```

## Related Documentation

- [Philosophy](../philosophy.md) - Design decisions and rationale
- [Reference](../reference/index.md) - Command and API reference
- [Troubleshooting](../troubleshooting/index.md) - Debugging guide
