# GitHub Actions Workflows

This directory contains CI/CD workflows that enforce project standards and automate testing/deployment.

## Workflows

### 1. Pre-commit Checks (`pre-commit.yml`)

**Triggers**: Push/PR to `main` or `develop` branches

**Purpose**: Enforce code quality, security, and documentation standards

**Jobs**:

- **pre-commit**: Runs all pre-commit hooks (Black, isort, flake8, mypy, ansible-lint, etc.)
- **code-quality**: Additional code quality checks and linting
- **security**: Secrets scanning, vulnerability checks, permission audits
- **documentation**: Builds MkDocs documentation, checks for broken links
- **summary**: Generates job status summary

**Status**: 🔴 Blocking - Must pass for PR approval

**Local equivalent**:

```bash
pre-commit run --all-files
```

---

### 2. Tests (`tests.yml`)

**Triggers**: Push/PR to `main` or `develop` branches

**Purpose**: Run test suite and verify code coverage

**Jobs**:

- **unit-tests**: Run unit tests with coverage reporting (minimum 80%)
- **integration-tests**: Run integration tests (requires test environment)
- **docker-build**: Verify Docker images build successfully
- **test-summary**: Aggregate test results

**Status**: 🔴 Blocking - Unit tests must pass for PR approval

**Local equivalent**:

```bash
pytest tests/unit/ --cov=. --cov-report=term
cd docker && docker-compose build
```

---

### 3. Deploy Documentation (`deploy-docs.yml`)

**Triggers**:

- Push to `main` branch (only when docs/ or mkdocs.yml changes)
- Manual trigger via workflow_dispatch

**Purpose**: Build and deploy documentation to GitHub Pages

**Jobs**:

- **deploy**: Build MkDocs site and deploy to gh-pages branch

**Status**: ⚪ Non-blocking - Doesn't affect PR approval

**Deployment URL**: `https://git-kubik.github.io/mesh/`

**Local equivalent**:

```bash
mkdocs build --strict
mkdocs gh-deploy
```

---

## Workflow Status

Check workflow status:

- **GitHub UI**: Actions tab → Select workflow
- **README badge**: Add status badges to README.md
- **Git branch protection**: Require status checks to pass

## Adding Status Badges

Add to `README.md`:

```markdown
![Pre-commit Checks](https://github.com/git-kubik/mesh/workflows/Pre-commit%20Checks/badge.svg)
![Tests](https://github.com/git-kubik/mesh/workflows/Tests/badge.svg)
![Deploy Documentation](https://github.com/git-kubik/mesh/workflows/Deploy%20Documentation/badge.svg)
```

## Branch Protection Rules

Recommended settings for `main` branch:

1. **Require pull request reviews**: 1 approval minimum
2. **Require status checks**:
   - `pre-commit / Run pre-commit hooks`
   - `pre-commit / Code Quality Checks`
   - `tests / Unit Tests`
   - `tests / Docker Build Test`
3. **Require branches to be up to date**: Yes
4. **Require signed commits**: Recommended
5. **Include administrators**: Yes

Configure at: `Settings → Branches → Branch protection rules`

## Caching

Workflows use caching to speed up builds:

- **Pre-commit**: `~/.cache/pre-commit` (pre-commit environments)
- **Python**: `~/.cache/pip` (pip packages)
- **Docker**: Layer caching via buildx

Caches expire after 7 days of inactivity.

## Secrets and Variables

Required secrets (configure in repo settings):

- `CODECOV_TOKEN` (optional): For uploading coverage to Codecov
- SSH keys (if needed for deployment to external servers)

Repository variables:

- None required currently

## Manual Workflow Triggers

Some workflows support manual triggers:

```bash
# Via GitHub CLI
gh workflow run deploy-docs.yml

# Via GitHub UI
Actions tab → Select workflow → Run workflow
```

## Debugging Workflows

**View logs**:

- GitHub UI: Actions tab → Select run → Select job

**Re-run failed jobs**:

- GitHub UI: Actions tab → Select run → Re-run failed jobs

**Download artifacts**:

- GitHub UI: Actions tab → Select run → Artifacts section
- Or: `gh run download <run-id>`

**Test locally with act** (advanced):

```bash
# Install act: https://github.com/nektos/act
brew install act  # macOS

# Run workflow locally
act push
act pull_request
```

## Workflow Notifications

Configure notifications:

- **Email**: Settings → Notifications → Actions
- **Slack**: Use GitHub Actions integration
- **Discord**: Use webhook actions

## Troubleshooting

### Pre-commit checks fail

**Local fix**:

```bash
# Run pre-commit to see what failed
pre-commit run --all-files

# Auto-fix formatting issues
black .
isort .

# Commit fixes
git add .
git commit -m "fix: auto-format code"
```

### Tests fail

**Local fix**:

```bash
# Run failing tests locally
pytest tests/unit/ -v --tb=short

# Check coverage
pytest tests/unit/ --cov=. --cov-report=term
```

### Docker build fails

**Local fix**:

```bash
cd docker
docker-compose build --no-cache
docker-compose up -d
docker-compose logs
```

### Documentation build fails

**Local fix**:

```bash
# Check for errors
mkdocs build --strict --verbose

# Common issues:
# - Broken internal links
# - Missing files in nav
# - Invalid YAML in mkdocs.yml
```

## Performance Optimization

**Reduce workflow run time**:

- Use caching (already configured)
- Run jobs in parallel (already configured)
- Use matrix builds for multiple Python versions (if needed)
- Skip redundant jobs (e.g., docs on code-only changes)

**Current performance**:

- Pre-commit: ~3-5 minutes
- Tests: ~2-4 minutes
- Documentation: ~1-2 minutes

## Costs

GitHub Actions is free for public repositories with limits:

- **Free tier**: 2,000 minutes/month for private repos
- **Public repos**: Unlimited

Monitor usage: `Settings → Billing → Actions`

## Best Practices

1. **Always test workflows locally** with pre-commit before pushing
2. **Use caching** to speed up builds (already configured)
3. **Fail fast**: Run fastest checks first (linting before tests)
4. **Provide clear error messages** in workflow steps
5. **Keep workflows DRY**: Use reusable workflows for common patterns
6. **Version pin actions**: Use specific versions (v4, not @latest)

## Further Reading

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
