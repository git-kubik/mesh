---
name: commit
description: Properly commit changes with pre-commit checks and workflow validation
---

# Git Commit Protocol

Execute a proper git commit with all checks and validations.

## Steps to Follow

### 1. Pre-commit Checks and Corrections

First, run pre-commit hooks to catch and fix any issues:

```bash
# Run pre-commit checks on all changed files
uv run pre-commit run --all-files

# If there are failures, review and fix them:
# - Formatting issues: Let pre-commit auto-fix when possible
# - Linting issues: Fix manually
# - Security issues: Review and resolve

# After fixes, run again to verify:
uv run pre-commit run --all-files
```

### 2. Review Changes

```bash
# Check what files will be committed
git status

# Review the actual changes
git diff --staged

# If unstaged changes exist after pre-commit fixes:
git add -A
```

### 3. Create Detailed Commit Message

Write a commit message following Conventional Commits format:

```bash
git commit -m "<type>: <description>

<detailed explanation of what changed and why>

- List specific changes
- Explain the reasoning
- Reference any related issues"
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring without changing functionality
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `chore`: Maintenance tasks
- `style`: Code style/formatting changes

### 4. Push and Check Workflows

```bash
# Push the changes
git push

# Check GitHub Actions status (if available)
# Use GitHub MCP tools to check workflow runs:
# mcp__github__list_workflow_runs
```

### 5. Monitor and Fix Workflow Issues

If workflows fail:

1. **Check workflow logs**:
   - Use `mcp__github__get_job_logs` with `failed_only: true`
   - Identify the specific failure

2. **Common fixes**:
   - **Shellcheck failures**: Fix shell script issues
   - **Secret detection**: Review and mark false positives in `.secrets.baseline`
   - **YAML linting**: Fix formatting issues in YAML files
   - **Python linting**: Fix flake8/mypy issues

3. **Fix and amend if needed**:

   ```bash
   # Make fixes
   # ...

   # Amend the commit (only if not pushed to protected branch)
   git add -A
   git commit --amend
   git push --force-with-lease
   ```

## Example Execution

```bash
# 1. Pre-commit checks
uv run pre-commit run --all-files

# 2. Stage all changes
git add -A

# 3. Commit with detailed message
git commit -m "feat: improve logging with descriptive filenames

- Add node number and action type to log filenames
- Format: ACTION_nodeN_TIMESTAMP.log
- Makes debugging easier by clearly identifying logs
- Helps track deployment history per node"

# 4. Push changes
git push

# 5. Verify workflows pass
# Check GitHub Actions status
```

## Important Notes

- **Always ask user permission** before committing (per user instructions)
- **Never skip pre-commit checks** - they prevent issues
- **Write meaningful commit messages** - they document history
- **Monitor CI/CD** - ensure changes don't break builds
- **Fix failures immediately** - don't leave broken commits

## Troubleshooting

### Pre-commit keeps failing

- Check if you need to update baseline: `~/.cache/pre-commit/*/detect-secrets/bin/detect-secrets scan --baseline .secrets.baseline`
- Run specific hook: `uv run pre-commit run <hook-id>`

### Workflows fail on GitHub

- Check the specific job that failed
- Look for error messages in logs
- Common issues: permissions, missing dependencies, syntax errors
- Fix locally and push again

### Secrets detected

- If false positive: Update `.secrets.baseline`
- If real secret: Remove it, rotate it, use environment variables

Remember: The goal is clean, well-documented commits that pass all checks!
