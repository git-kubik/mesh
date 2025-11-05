---
description: Validate completion of a specific phase or the entire project
---

# Phase Validation

You are the project manager. Validate whether a phase is complete or check overall project readiness.

## Instructions

If user specified a phase number (e.g., "/pm-validate 1" or "/pm-validate phase 5"):

1. Check that specific phase's requirements from CLAUDE.md
2. Verify all files exist
3. Validate all acceptance criteria met
4. Report pass/fail for each requirement

If no phase specified:

1. Check overall project status
2. Validate against "Project Success Criteria" in CLAUDE.md
3. Determine production readiness

## Output Format

```markdown
# ✓ Phase Validation Report

## Phase [X]: [Phase Name]

### Requirements Checklist
- [ ] Requirement 1 - [Status/Notes]
- [ ] Requirement 2 - [Status/Notes]
- [ ] Requirement 3 - [Status/Notes]
...

### Files Verification
✅ **Found**:
- path/to/file1
- path/to/file2

❌ **Missing**:
- path/to/missing/file

### Acceptance Criteria
- [ ] Criterion 1: [Met/Not Met - Details]
- [ ] Criterion 2: [Met/Not Met - Details]

### Phase Status: [COMPLETE ✅ | INCOMPLETE ❌ | IN PROGRESS 🔄]

### Blocking Issues
[List any issues preventing phase completion]

### Next Steps to Complete This Phase
1. [Specific action]
2. [Specific action]
```

## Validation Rules

**Phase 1-4 (Docker)**: Must have working container environment
**Phase 5-9 (Tests)**: Must have test files AND tests passing
**Phase 10 (Automation)**: Must have working CI/CD pipeline
**Phase 12 (Documentation)**: Must have complete documentation files

A phase is only COMPLETE when:

- All required files exist
- All tests pass (if applicable)
- All acceptance criteria met
- No blocking issues

## Production Readiness Check

If validating overall readiness, check:

1. All 12 phases complete
2. All tests passing (zero failures)
3. All performance benchmarks met
4. All failover scenarios validated
5. Complete documentation available
6. Web interface functional

Output: **READY FOR PRODUCTION ✅** or **NOT READY ❌** with specific gaps.
