# GitHub Project Management Setup Guide

This guide explains how to complete the GitHub project management setup for the mesh network deployment project.

## What's Been Done

✅ **Repository created**: https://github.com/git-kubik/mesh
✅ **Code pushed**: All Ansible playbooks, documentation, and tooling
✅ **Labels created**: 30 labels (12 phase labels, 4 priority labels, 6 type/status labels)
✅ **Milestones created**: 7 milestones for all 12 implementation phases

## What You Need to Do

### 1. Create GitHub Project

GitHub Projects provide Kanban-style project management. Unfortunately, the GitHub MCP doesn't support creating projects yet, so you need to do this manually.

**Steps:**

1. Go to: https://github.com/git-kubik/mesh/projects
2. Click "New project"
3. Choose "Board" template
4. Name it: "Mesh Network Deployment"
5. Click "Create project"

**Or use the GitHub CLI:**

```bash
gh project create --owner @me --title "Mesh Network Deployment"
```

### 2. Configure Project Views

Once the project is created, set up these views:

**Board View (Default):**
- Columns: Backlog, To Do, In Progress, In Review, Done
- This is your main working view

**Table View:**
- Shows all issues in spreadsheet format
- Good for bulk editing and filtering

**Roadmap View:**
- Timeline visualization
- Shows milestones and due dates

### 3. Add Custom Fields (Optional but Recommended)

Custom fields help track additional metadata:

1. Click "⋯" menu → "Settings" → "Custom fields"
2. Add these fields:
   - **Phase** (Single select): Options 1-12
   - **Acceptance Criteria Met** (Single select): Yes/No/Partial
   - **Estimated Hours** (Number)
   - **Actual Hours** (Number)

### 4. Set Up Automation

Enable these automations:

1. **Auto-add items**: Automatically add new issues to project
   - Settings → Workflows → "Auto-add to project"
   - Enable for: "is:issue is:open"

2. **Auto-move items**: Move items based on status
   - When issue status changes to "In Progress" → Move to "In Progress" column
   - When PR is opened → Move to "In Review" column
   - When issue is closed → Move to "Done" column

### 5. Create Issue Templates

Create issue templates for consistent formatting:

Create `.github/ISSUE_TEMPLATE/phase-task.md`:

```markdown
---
name: Phase Task
about: Standard task for implementation phases
labels: type-feature
---

## Task: [Task Name]

**Phase**: [Phase Number]
**Priority**: [Critical/High/Medium/Low]
**Estimated Effort**: [X hours]

## Description
[What needs to be done]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Implementation Details
- **Files to create/modify**: `path/to/file`
- **Dependencies**: #123 (issue number)
- **References**: Related documentation

## Definition of Done
- [ ] Code implemented
- [ ] Tests passing
- [ ] Documentation updated
- [ ] PR reviewed and merged

## Related Issues
- Part of Milestone X: #milestone
- Blocked by: #123
- Blocks: #456
```

### 6. Create Issues for All Tasks

I've created a few sample Phase 1 issues to demonstrate the format. You can create the remaining issues using the same pattern.

**To create issues in bulk**, you can:

**Option 1: Use GitHub CLI**
```bash
gh issue create \
  --title "[Phase 1] Create Dockerfile for Ansible container" \
  --body "See template" \
  --label "phase-1-docker,priority-critical,type-infrastructure" \
  --milestone 1
```

**Option 2: Use the GitHub web interface**
- Go to: https://github.com/git-kubik/mesh/issues/new
- Use the issue template
- Fill in the details
- Add labels and milestone

**Option 3: Ask Claude to create them**
- Claude can create all issues using the GitHub MCP
- Just say "create all Phase 1 issues"

### 7. Add Issues to Project

After creating issues, add them to your project:

**Option 1: Automatic (if automation enabled)**
- Issues are automatically added to project

**Option 2: Manual**
- Open issue → Click "Projects" in sidebar → Select your project

**Option 3: Bulk add**
```bash
# Get project number from URL: github.com/users/USERNAME/projects/NUMBER
gh project item-add PROJECT_NUMBER --owner @me --url ISSUE_URL
```

## Current Setup Status

### Labels (30 total)

**Phase Labels:**
- phase-1-docker through phase-12-documentation

**Priority Labels:**
- priority-critical (blocker)
- priority-high (important)
- priority-medium (normal)
- priority-low (nice to have)

**Type Labels:**
- type-feature, type-bug, type-enhancement
- type-testing, type-infrastructure
- Plus default labels (documentation, etc.)

**Status Labels:**
- status-blocked, status-in-progress

### Milestones (7 total)

| Milestone | Phases | Tasks | Due Date |
|-----------|--------|-------|----------|
| 1. Docker Infrastructure | 1-4 | 23 | Nov 19, 2025 |
| 2. Unit & Integration Tests | 5-6 | 9 | Nov 26, 2025 |
| 3. Functional & Performance Tests | 7-8 | 7 | Dec 3, 2025 |
| 4. Failover Tests | 9 | 4 | Dec 10, 2025 |
| 5. Test Automation & CI/CD | 10 | 8 | Dec 17, 2025 |
| 6. Documentation | 12 | 6 | Dec 24, 2025 |
| 7. Continuous Monitoring (Optional) | 11 | 4 | TBD |

## Next Steps

1. **Create GitHub Project** (5 minutes)
   - Follow instructions above
   - Set up board columns and views

2. **Create issues** (30-60 minutes)
   - Start with Phase 1 (7 tasks)
   - Use issue template for consistency
   - Assign labels and milestone

3. **Start working!**
   - Move issues to "In Progress"
   - Create PRs and link to issues
   - Track progress on project board

## Useful GitHub Commands

```bash
# List all labels
gh label list --repo git-kubik/mesh

# List all milestones
gh api repos/git-kubik/mesh/milestones

# Create issue
gh issue create --title "Title" --body "Body" \
  --label "phase-1-docker,priority-high" --milestone 1

# List issues
gh issue list --milestone 1 --label "phase-1-docker"

# View issue
gh issue view 1

# Close issue
gh issue close 1

# Create PR
gh pr create --title "Title" --body "Description"

# Link PR to issue (in PR description)
# Use: "Closes #123" or "Fixes #123"
```

## Integration with Existing PM Tools

Your project already has excellent PM tools:

- **/pm-status** - Quick status overview
- **/pm-next** - Next priority tasks
- **/pm-validate** - Phase validation
- **/pm-blockers** - Identify blockers

**Workflow:**
1. Use `/pm-next` to identify next tasks
2. Create GitHub issues for those tasks
3. Work on issues, move through project board
4. Use `/pm-validate` to check phase completion

## Resources

- **GitHub Projects docs**: https://docs.github.com/en/issues/planning-and-tracking-with-projects
- **GitHub CLI docs**: https://cli.github.com/manual/
- **Project repository**: https://github.com/git-kubik/mesh
- **GitHub PM skill**: `.claude/skills/github-pm.md`

## Sample Phase 1 Issues

I've created a few sample issues to demonstrate the format. Check them out:

- Issue #1: Create Dockerfile for Ansible container
- Issue #2: Create docker-compose.yml
- Issue #3: Create requirements.txt

You can use these as templates for creating the remaining Phase 1 and subsequent phase issues.

---

**Need help?** Ask Claude to create issues, set up workflows, or explain any GitHub PM concepts!
