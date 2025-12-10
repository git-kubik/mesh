# Contributing to OpenWrt Mesh Network

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Standards and Guidelines](#standards-and-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Review Process](#review-process)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Docker Desktop 20.10+ or Docker Engine with docker-compose
- Git 2.40+
- Python 3.11+ (for local testing)
- (Optional) Access to OpenWrt routers for testing

### Development Environment Setup

**Quick Setup (Automated):**

```bash
# Clone the repository
git clone https://github.com/yourusername/mesh.git
cd mesh

# Run automated setup script
./scripts/setup-dev-environment.sh
```

The setup script will:

- Check prerequisites (Python 3.11+, Git, Docker)
- Install UV package manager (if not present)
- Install all development dependencies
- Install and configure pre-commit hooks
- Run initial pre-commit checks
- Verify test environment

**Manual Setup:**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/mesh.git
   cd mesh
   ```

2. **Install development tools:**

   ```bash
   # Using UV (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv pip install -r requirements-dev.txt

   # Or using pip
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks (REQUIRED):**

   ```bash
   # Install Git hooks
   pre-commit install

   # Install commit message hooks
   pre-commit install --hook-type commit-msg

   # Run on all files to verify
   pre-commit run --all-files
   ```

   **Important**: Pre-commit hooks are mandatory and enforce:
   - Code formatting (Black, isort)
   - Linting (flake8, pylint, ansible-lint)
   - Type checking (mypy)
   - Security (detect-secrets)
   - YAML/Markdown validation

4. **Create secrets baseline:**

   ```bash
   detect-secrets scan --baseline .secrets.baseline
   ```

5. **Start Docker environment:**

   ```bash
   cd docker
   docker-compose up -d
   ```

6. **Verify setup:**

   ```bash
   # Run unit tests
   pytest tests/unit/ -v

   # Check code style
   black --check .
   flake8 .
   mypy tests/

   # Run all pre-commit checks
   pre-commit run --all-files
   ```

### Project Structure

Understanding the project layout helps with contributions:

```
mesh/
├── openwrt-mesh-ansible/    # Ansible playbooks and templates
├── docker/                   # Docker containerization
├── tests/                    # Test suite
├── docs/                     # Documentation (MkDocs)
├── .claude/                  # Claude Code skills and commands
└── ...
```

For detailed structure, see the repository root.

## Development Workflow

### 1. Choose an Issue

- Browse [open issues](https://github.com/yourusername/mesh/issues)
- Look for issues tagged `good first issue` or `help wanted`
- Comment on the issue to claim it and prevent duplicate work
- If no issue exists for your work, create one first

### 2. Create a Branch

Follow the branch naming convention:

```bash
# For new features
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b bugfix/issue-description

# For documentation
git checkout -b docs/what-you-are-documenting

# For hotfixes
git checkout -b hotfix/critical-issue
```

### 3. Make Changes

Follow the project standards (see below). Key principles:

- Make focused, atomic commits
- Write clear commit messages
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Format code
black . --line-length 100
isort . --profile black

# Lint code
flake8 . --max-line-length 100
mypy tests/ --strict

# Run tests
pytest tests/unit/ -v
pytest tests/integration/ -v  # If you have test nodes

# Check documentation
mkdocs build --strict
```

### 5. Commit Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: <type>(<scope>): <subject>

git commit -m "feat(ansible): add VLAN support to network templates"
git commit -m "fix(batman): correct MTU size for wireless mesh"
git commit -m "docs(testing): add performance benchmark documentation"
git commit -m "test(failover): add wire disconnect test"
```

**Commit types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Formatting
- `chore`: Maintenance
- `perf`: Performance

### 6. Push and Create Pull Request

```bash
git push -u origin your-branch-name
```

Then create a pull request on GitHub following the PR template.

## Standards and Guidelines

This project maintains high standards. See the sections below for complete details.

### Code Style

**Python:**

- Style: PEP 8
- Formatter: Black (line length: 100)
- Import sorting: isort
- Linter: flake8
- Type checking: mypy
- All public functions must have type hints and docstrings

**YAML (Ansible):**

- Indentation: 2 spaces
- Task names: Descriptive, capitalized
- Use handlers for service restarts
- All playbooks must be idempotent
- Lint with ansible-lint

**Bash:**

- Always use `set -euo pipefail`
- Quote all variables: `"${var}"`
- Use `readonly` for constants
- Check with shellcheck

**Markdown:**

- Line length: 100 characters
- Headings: ATX style (`#`)
- Code blocks: Always specify language
- Lint with markdownlint

### Testing Requirements

- **Coverage**: Minimum 80% overall, 90% for new code
- **Test types**: Unit, integration, functional, performance, failover
- **Documentation**: All tests must have docstrings
- **Markers**: Use pytest markers (`@pytest.mark.unit`, etc.)
- **Isolation**: Tests must be independent

### Documentation Standards

- **Format**: Markdown with MkDocs Material
- **Structure**: Clear hierarchy (max H4)
- **Examples**: Include code examples
- **Links**: Use descriptive link text
- **Validation**: Must build without errors/warnings

### Security Standards

- **Never** commit secrets to Git
- Use Ansible Vault for sensitive data
- Minimum password length: 20 characters
- Use ED25519 SSH keys (or RSA 4096)
- Rotate secrets quarterly

## Testing

### Running Tests Locally

```bash
# All tests
pytest tests/ -v

# Specific category
pytest tests/unit/ -v
pytest tests/functional/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Parallel execution
pytest tests/ -n auto
```

### Writing Tests

Follow these guidelines:

```python
"""
test_example.py - Example test module

Clear description of what this module tests.
"""

import pytest


class TestFeature:
    """Test suite for specific feature."""

    @pytest.mark.unit
    def test_something_specific(self) -> None:
        """
        Test that specific thing works correctly.

        This docstring explains what the test does and why.
        """
        # Arrange
        expected = "value"

        # Act
        result = function_to_test()

        # Assert
        assert result == expected, "Descriptive failure message"
```

**Requirements:**

- Descriptive test names (`test_*`)
- Docstrings for all tests
- Arrange-Act-Assert pattern
- Meaningful assertions with failure messages
- Appropriate markers

### Test Data

Use fixtures for test data, not hardcoded values:

```python
@pytest.fixture
def mesh_config():
    """Provide test mesh configuration."""
    return {
        "network": "10.11.12.0/24",
        "nodes": ["10.11.12.1", "10.11.12.2", "10.11.12.3"]
    }
```

## Submitting Changes

### Before Submitting

**Pre-commit hooks automatically check most items**, but verify:

- [ ] Pre-commit hooks installed and passing (`pre-commit run --all-files`)
- [ ] Code formatted (Black, isort) - **auto-fixed by pre-commit**
- [ ] Linting passes (flake8, mypy, ansible-lint) - **checked by pre-commit**
- [ ] No secrets committed - **checked by detect-secrets**
- [ ] Tests written and passing (`pytest tests/ -v`)
- [ ] Test coverage >= 80% (`pytest --cov=. --cov-report=term`)
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow Conventional Commits format
- [ ] All CI/CD checks pass on GitHub

**Note**: Pre-commit hooks will prevent you from committing if checks fail. To see what failed:

```bash
# Run all checks manually
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run flake8 --all-files

# Skip hooks (NOT RECOMMENDED - CI will fail)
git commit --no-verify
```

### Pull Request Process

1. **Create PR** using the pull request template
2. **Fill out template** completely (don't skip sections)
3. **Link related issues** (Fixes #123, Closes #456)
4. **Request review** from maintainers
5. **Address feedback** promptly and professionally
6. **Update PR** as requested
7. **Wait for approval** before merging

### PR Review Criteria

Your PR will be reviewed for:

- **Code quality**: Follows standards, well-structured
- **Testing**: Adequate test coverage, tests pass
- **Documentation**: Updated and clear
- **Security**: No vulnerabilities or secrets
- **Performance**: No regressions
- **Backwards compatibility**: Breaking changes justified and documented

## Review Process

### As a Contributor

When receiving feedback:

- Respond to all comments (even if just acknowledging)
- Ask for clarification if needed
- Make requested changes or explain why you disagree
- Mark conversations as resolved when addressed
- Be patient and professional

### Comment Types

Reviewers may use these prefixes:

- `nit:` - Minor suggestion, not blocking
- `question:` - Need clarification
- `blocking:` - Must be addressed before approval
- `optional:` - Nice to have, not required
- `suggestion:` - Alternative approach to consider

## Additional Resources

### Documentation

- [Pre-commit Hooks](pre-commit.md) - Pre-commit configuration guide
- [Initial Node Setup](../getting-started/initial-setup.md) - Hardware setup guide
- [Architecture Overview](../architecture/overview.md) - Full deployment guide
- [Ansible Quick Start](../getting-started/ansible-basics.md) - Quick deployment guide

### External Resources

- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/mesh/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mesh/discussions)
- **Email**: <your.email@example.com>

### Project Skills

Use Claude Code skills for specialized help:

- `docker-dev` - Docker containerization
- `ansible-dev` - Ansible playbooks and templates
- `python-test` - pytest and testing
- `project-standards` - Code standards and best practices
- `mesh-pm` - Project management and progress tracking

## Recognition

Contributors will be recognized in:

- CHANGELOG.md (for significant contributions)
- README.md (contributors section)
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

**Questions?** Open an issue or discussion, and we'll be happy to help!

**Thank you for contributing!** 🎉
