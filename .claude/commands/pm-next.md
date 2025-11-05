---
description: Identify the next 3-5 priority tasks to work on
---

# Next Priority Tasks

You are the project manager. Based on the current state of the repository, identify the next priority tasks.

## Instructions

1. **Assess current state**:
   - Scan `docker/`, `tests/`, `docs/` directories
   - Check CLAUDE.md for phase requirements
   - Identify the current active phase

2. **Determine prerequisites**:
   - Verify previous phases are complete
   - Check dependencies are met
   - Ensure no blockers exist

3. **Recommend next tasks** in priority order:

```markdown
# 🎯 Next Priority Tasks

## Current Phase: [Phase name and number]

### 🔥 Immediate Priorities (Do Now)
1. **[Task Name]**
   - File: `path/to/file`
   - Action: [Specific action needed]
   - Why: [Why this is important]
   - Acceptance: [How to verify it's done]

2. **[Task Name]**
   - File: `path/to/file`
   - Action: [Specific action needed]
   - Why: [Why this is important]
   - Acceptance: [How to verify it's done]

3. **[Task Name]**
   - File: `path/to/file`
   - Action: [Specific action needed]
   - Why: [Why this is important]
   - Acceptance: [How to verify it's done]

### ⏭️ Up Next (After Current Tasks)
4. [Next task]
5. [Next task]

## ⚠️ Prerequisites Check
[List any prerequisites that need to be met first]

## 📋 Suggested Approach
[Step-by-step approach for tackling these tasks]
```

4. **Follow the critical path**: Docker → Tests → Documentation
5. **Be specific**: Include exact file paths and commands where applicable
6. **Consider dependencies**: Don't suggest tasks that can't be done yet

Based on CLAUDE.md Implementation Checklist, phases must be completed sequentially.
