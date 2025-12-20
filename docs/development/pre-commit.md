# Pre-commit Hooks Guide

This guide explains the pre-commit hooks used in this project and how to work with them effectively.

## Overview

Pre-commit hooks are automated checks that run before each commit to ensure code quality, consistency, and security. They prevent common issues from being committed to the repository.

**Benefits:**

- ✅ Automatic code formatting
- ✅ Early error detection
- ✅ Consistent code style
- ✅ Security scanning
- ✅ Prevents broken commits
- ✅ Saves time in code review

## Quick Start

### Installation

```bash
# Automated setup (recommended)
./scripts/setup-dev-environment.sh

# Or manual installation
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

### Basic Usage

```bash
# Hooks run automatically on commit
git add .
git commit -m "feat: add new feature"
# Pre-commit hooks run here automatically

# Run manually on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run black
pre-commit run flake8
```

## Hooks Explained

### 1. Code Formatting

#### Black (Python Formatter)

**What it does**: Automatically formats Python code to PEP 8 style
**Config**: 100 character line length
**Auto-fix**: Yes

```bash
# Run manually
black . --line-length 100

# Check without modifying
black --check .
```

**Common issues**:

- Long lines: Split into multiple lines
- Inconsistent quotes: Uses double quotes by default
- Trailing commas: Adds where appropriate

#### isort (Import Sorter)

**What it does**: Sorts and organizes Python imports
**Config**: Black-compatible profile
**Auto-fix**: Yes

```bash
# Run manually
isort . --profile black

# Check without modifying
isort --check-only .
```

**Import order**:

1. Standard library imports
2. Third-party imports
3. Local application imports

### 2. Linting

#### flake8 (Python Linter)

**What it does**: Checks Python code for style and potential errors
**Config**: 100 char lines, ignores E203/W503
**Auto-fix**: No (manual fixes required)

```bash
# Run manually
flake8 . --max-line-length 100
```

**Common issues**:

- Unused imports: Remove or use them
- Undefined names: Fix typos or import missing modules
- Line too long: Refactor or split line
- Complexity too high: Simplify function logic

#### mypy (Type Checker)

**What it does**: Checks Python type hints for correctness
**Config**: Strict mode enabled
**Auto-fix**: No

```bash
# Run manually
mypy tests/ --strict
```

**Common issues**:

- Missing type hints: Add type annotations
- Type mismatches: Fix incorrect types
- Incompatible types: Correct function signatures

**Example fixes**:

```python
# ❌ Missing type hints
def calculate(x, y):
    return x + y

# ✅ With type hints
def calculate(x: int, y: int) -> int:
    return x + y
```

#### ansible-lint (Ansible Linter)

**What it does**: Checks Ansible playbooks for best practices
**Config**: Production profile
**Auto-fix**: Partial (some rules auto-fixable)

```bash
# Run manually
ansible-lint openwrt-mesh-ansible/
```

**Common issues**:

- Tasks without names: Add descriptive names
- Using command instead of module: Use specific modules
- No handlers for services: Use handlers for restarts
- Bare variables in conditionals: Quote variables

#### yamllint (YAML Linter)

**What it does**: Validates YAML syntax and style
**Config**: 120 char lines, 2-space indentation
**Auto-fix**: No

```bash
# Run manually
yamllint -c .yamllint.yaml .
```

#### markdownlint (Markdown Linter)

**What it does**: Enforces Markdown style consistency
**Config**: Default rules with fixes enabled
**Auto-fix**: Yes

```bash
# Run manually
markdownlint '**/*.md' --fix
```

### 3. Security

#### detect-secrets

**What it does**: Scans for accidentally committed secrets
**Config**: Uses .secrets.baseline
**Auto-fix**: No (manual review required)

```bash
# Run manually
detect-secrets scan --baseline .secrets.baseline

# Audit secrets
detect-secrets audit .secrets.baseline
```

**What it detects**:

- API keys
- Private keys
- Passwords
- AWS credentials
- JWT tokens
- High entropy strings

**If secrets detected**:

1. **Remove secret from code**
2. **Use Ansible Vault** for sensitive data
3. **Update .secrets.baseline** if false positive
4. **Rotate the secret** if already committed

#### shellcheck (Shell Script Checker)

**What it does**: Checks bash scripts for common issues
**Auto-fix**: No

```bash
# Run manually
shellcheck scripts/*.sh
```

### 4. General File Checks

#### trailing-whitespace

**What it does**: Removes trailing whitespace from lines
**Auto-fix**: Yes

#### end-of-file-fixer

**What it does**: Ensures files end with a newline
**Auto-fix**: Yes

#### check-yaml

**What it does**: Validates YAML files are parseable
**Auto-fix**: No

#### check-merge-conflict

**What it does**: Detects merge conflict markers
**Auto-fix**: No

#### check-added-large-files

**What it does**: Prevents committing large files (>1MB)
**Auto-fix**: No

#### detect-private-key

**What it does**: Prevents committing private SSH keys
**Auto-fix**: No

## Common Workflows

### First-Time Setup

```bash
# 1. Clone repository
git clone https://github.com/git-kubik/mesh.git
cd mesh

# 2. Run automated setup
./scripts/setup-dev-environment.sh

# 3. Verify installation
pre-commit run --all-files

# 4. Make a test commit
git commit --allow-empty -m "test: verify pre-commit setup"
```

### Daily Development

```bash
# 1. Make changes
vim tests/test_something.py

# 2. Add files
git add tests/test_something.py

# 3. Commit (hooks run automatically)
git commit -m "feat(tests): add new test"

# If hooks fail:
# - Review the errors
# - Fix issues (many auto-fixed)
# - Try committing again

# 4. Push to remote
git push origin feature/my-feature
```

### Fixing Hook Failures

```bash
# Scenario 1: Formatting issues (auto-fixed)
git add .
git commit -m "feat: add feature"
# Black and isort auto-fix files
# Files modified by this hook:
#   tests/test_example.py
# Review changes and stage them:
git add tests/test_example.py
git commit -m "feat: add feature"

# Scenario 2: Linting errors (manual fix required)
git commit -m "feat: add feature"
# flake8 reports:
#   tests/test_example.py:10:80: E501 line too long
# Fix the issue:
vim tests/test_example.py  # Split long line
git add tests/test_example.py
git commit -m "feat: add feature"

# Scenario 3: Type errors (manual fix required)
git commit -m "feat: add feature"
# mypy reports:
#   tests/test_example.py:15: error: Missing type hint
# Fix the issue:
vim tests/test_example.py  # Add type hints
git add tests/test_example.py
git commit -m "feat: add feature"
```

### Updating Hooks

```bash
# Update to latest hook versions
pre-commit autoupdate

# Review changes
git diff .pre-commit-config.yaml

# Test new versions
pre-commit run --all-files

# Commit updates
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"
```

### Skipping Hooks (Not Recommended)

```bash
# Skip all hooks for one commit
git commit --no-verify -m "feat: something"

# Skip specific hook
SKIP=flake8 git commit -m "feat: something"

# Skip multiple hooks
SKIP=flake8,mypy git commit -m "feat: something"
```

**⚠️ Warning**: Skipping hooks locally doesn't skip CI/CD checks. If hooks fail locally, they'll fail in CI.

## Troubleshooting

### Hooks Not Running

**Problem**: Hooks don't run on commit

**Solution**:

```bash
# Check if hooks installed
ls -la .git/hooks/pre-commit

# Reinstall hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Verify installation
pre-commit run --help
```

### Slow Hook Execution

**Problem**: Hooks take too long to run

**Solutions**:

```bash
# Use pre-commit's caching (already configured)
# Caches stored in ~/.cache/pre-commit/

# Run only on changed files (default behavior)
git commit  # Only checks staged files

# Skip slow hooks during development
SKIP=mypy git commit -m "wip: working"
# Remember to run full checks before pushing:
pre-commit run --all-files
```

### Hook Failures on CI/CD

**Problem**: Hooks pass locally but fail in CI

**Common causes**:

1. Different Python version
2. Cached results locally
3. Missing dependencies

**Solution**:

```bash
# Clear pre-commit cache
pre-commit clean

# Run with same environment as CI
docker run --rm -v $(pwd):/app -w /app python:3.11 bash -c "
  pip install pre-commit
  pre-commit run --all-files
"

# Or use GitHub Actions locally
brew install act  # Install act
act pull_request  # Run PR workflow
```

### Updating .secrets.baseline

**Problem**: Legitimate string flagged as secret

**Solution**:

```bash
# Update baseline to include new "secret"
detect-secrets scan --baseline .secrets.baseline

# Audit to mark as false positive
detect-secrets audit .secrets.baseline
# Press 'n' to mark as not a secret

# Commit updated baseline
git add .secrets.baseline
git commit -m "chore: update secrets baseline"
```

## Best Practices

### Do's

✅ **Run hooks before pushing**:

```bash
pre-commit run --all-files
git push
```

✅ **Fix issues immediately**: Don't accumulate hook failures

✅ **Keep hooks updated**: Run `pre-commit autoupdate` monthly

✅ **Add tests for new hooks**: Ensure they work correctly

✅ **Document exceptions**: If skipping hooks, explain why

### Don'ts

❌ **Don't use --no-verify habitually**: Defeats the purpose

❌ **Don't commit half-fixed code**: Complete fixes before committing

❌ **Don't ignore security warnings**: Always investigate secret detections

❌ **Don't disable hooks globally**: Use SKIP for rare exceptions

## Configuration Files

### .pre-commit-config.yaml

Main configuration file for pre-commit hooks.

**Key sections**:

- `repos`: List of hook repositories
- `hooks`: Specific hooks to run
- `args`: Arguments passed to hooks

**Example**:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        args: [--line-length=100]
```

### pyproject.toml

Python tool configurations (Black, isort, mypy, pytest).

**Example**:

```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100
```

### .yamllint.yaml

YAML linting configuration.

### .secrets.baseline

Baseline file for detect-secrets.

## Integration with GitHub Actions

Pre-commit hooks also run in CI/CD:

**Workflow**: `.github/workflows/pre-commit.yml`

**Runs**:

- On every push to main/develop
- On every pull request
- All the same hooks as local

**Status**: Required for PR approval

**View results**: GitHub Actions tab

## Advanced Usage

### Custom Hooks

Add project-specific hooks to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: check-ansible-vault
        name: Check Ansible Vault files
        entry: bash -c 'grep -r "ANSIBLE_VAULT" group_vars/'
        language: system
        pass_filenames: false
```

### Hook Ordering

Hooks run in order defined in config. Optimize for:

1. Fast auto-fixers first (Black, isort)
2. Fast checkers (flake8)
3. Slow checkers last (mypy)

### Per-Directory Hooks

Run hooks only on specific directories:

```yaml
- id: flake8
  files: ^tests/.*\.py$  # Only test files
  exclude: ^tests/fixtures/  # Except fixtures
```

## Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Pre-commit Hooks](https://github.com/pre-commit/pre-commit-hooks)
- [Black Documentation](https://black.readthedocs.io/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [ansible-lint Documentation](https://ansible-lint.readthedocs.io/)

## Getting Help

**Issues with pre-commit**:

1. Check this guide first
2. Review [Contributing Guide](contributing.md)
3. Check [GitHub Issues](https://github.com/git-kubik/mesh/issues)
4. Ask in [GitHub Discussions](https://github.com/git-kubik/mesh/discussions)

**Reporting problems**:

```bash
# Include this information when reporting issues
pre-commit --version
python --version
git --version
pre-commit run --all-files --verbose
```

---

**Remember**: Pre-commit hooks are here to help, not hinder. They catch issues early, maintain code quality, and make code review faster!
