---
description: Identify and report current blockers, risks, and dependencies
---

# Project Blockers and Risks Analysis

You are the project manager. Identify anything blocking progress or posing risks to successful completion.

## Instructions

1. **Scan the repository** for current state
2. **Review CLAUDE.md** for requirements and dependencies
3. **Identify blockers** in these categories:
   - Missing prerequisites
   - Failed tests
   - Missing dependencies
   - Configuration issues
   - Technical debt
   - Documentation gaps

4. **Generate report**:

```markdown
# 🚧 Blockers and Risks Report

## 🔴 Critical Blockers (Stopping Progress)
[Issues that completely prevent moving forward]

1. **[Blocker Name]**
   - Impact: [What's blocked]
   - Details: [Specific problem]
   - Resolution: [How to fix]
   - Owner: [Who should fix this]

## 🟡 Major Risks (Could Delay Project)
[Issues that might cause problems]

1. **[Risk Name]**
   - Probability: [High/Medium/Low]
   - Impact: [What could happen]
   - Mitigation: [How to prevent/reduce]

## 🟢 Minor Issues (Should Fix Soon)
[Issues that won't block progress but should be addressed]

1. **[Issue Name]**
   - Details: [What's wrong]
   - Suggested Fix: [How to resolve]

## 📋 Dependency Check
- [ ] Docker installed: [Yes/No/Unknown]
- [ ] Ansible installed: [Yes/No/Unknown]
- [ ] Python 3.x available: [Yes/No/Unknown]
- [ ] pytest installed: [Yes/No/Unknown]
- [ ] Access to OpenWrt nodes: [Yes/No/Unknown]

## ⚠️ Prerequisites Status
[Check phase dependencies from CLAUDE.md]
- Phase 1 prereq: [Status]
- Phase 2 prereq: [Status]
...

## 🎯 Recommended Actions
1. [Immediate action to unblock]
2. [Next action]
3. [Follow-up action]

## 📊 Risk Score: [Low/Medium/High/Critical]
[Overall project risk assessment]
```

## Common Blockers to Check

**Phase 1-4**:
- Docker not installed
- No access to web interface port (3000/80)
- SSH connectivity issues
- Missing credentials

**Phase 5-9**:
- Tests not passing
- Performance benchmarks not met
- Missing test dependencies
- No access to physical nodes

**Phase 10**:
- CI/CD not configured
- Test automation failing
- Report generation broken

**Phase 12**:
- Documentation incomplete
- Examples missing
- Procedures not documented

Be specific about what's blocking progress and how to resolve it.
