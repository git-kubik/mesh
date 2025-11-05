# Claude Code Project Management Commands

This directory contains slash commands for managing the OpenWrt Mesh Network deployment project.

## Available Commands

### `/pm-status` - Project Status Overview
**Description**: Generate a quick status snapshot of the project
**Usage**: `/pm-status`
**Output**: Phase completion, current focus, next tasks, metrics
**When to use**: Daily check-in, quick status updates

### `/pm-next` - Next Priority Tasks
**Description**: Get the next 3-5 priority tasks to work on
**Usage**: `/pm-next`
**Output**: Prioritized task list with file paths and acceptance criteria
**When to use**: Starting a work session, need direction on what to do

### `/pm-validate` - Phase Validation
**Description**: Validate completion of a phase or check production readiness
**Usage**:
- `/pm-validate` - Check overall project readiness
- `/pm-validate 1` - Validate Phase 1
- `/pm-validate phase 5` - Validate Phase 5

**Output**: Detailed validation report with pass/fail for each requirement
**When to use**: Before moving to next phase, checking production readiness

### `/pm-blockers` - Blockers and Risks
**Description**: Identify current blockers, risks, and dependencies
**Usage**: `/pm-blockers`
**Output**: Categorized list of blockers (Critical/Major/Minor) with resolutions
**When to use**: Stuck on something, weekly risk review, project planning

### `/pm-report` - Comprehensive Report
**Description**: Generate complete stakeholder-ready project status report
**Usage**: `/pm-report`
**Output**: Multi-page detailed report with all metrics and analysis
**When to use**: Weekly/monthly reporting, project reviews, documentation

## Typical Workflows

### Starting a New Work Session
```
1. /pm-status          # See where we are
2. /pm-blockers        # Check for any issues
3. /pm-next            # Get tasks to work on
4. [Do the work]
5. /pm-status          # Confirm progress
```

### Completing a Phase
```
1. [Finish phase tasks]
2. /pm-validate [phase #]   # Check if phase is complete
3. [Address any gaps found]
4. /pm-validate [phase #]   # Re-validate
5. /pm-next                 # Move to next phase
```

### Weekly Check-in
```
1. /pm-report          # Generate full report
2. /pm-blockers        # Review risks
3. /pm-next            # Plan week's work
```

### Production Readiness Check
```
1. /pm-validate        # Overall validation
2. /pm-blockers        # Check for any blockers
3. /pm-report          # Final comprehensive report
```

## Command Integration

These commands work best with:
- **TodoWrite tool**: Create task lists from pm-next output
- **CLAUDE.md**: Reference document for all requirements
- **Git**: Track progress via commits

## Quick Tips

### Be Specific
Commands provide specific file paths and actions - use them!

### Follow the Path
Phases must be completed sequentially (1→2→3...)

### Validate Often
Use `/pm-validate` before moving to next phase

### Track Blockers
Run `/pm-blockers` weekly to catch issues early

### Document Progress
Use `/pm-report` for documentation and stakeholder updates

## Example Usage

**Starting the project:**
```
User: /pm-status
Claude: [Shows Phase 1 is current priority]

User: /pm-next
Claude: [Lists Docker infrastructure tasks]

User: [Creates Dockerfile]

User: /pm-status
Claude: [Shows progress on Phase 1]
```

**Validating a phase:**
```
User: /pm-validate 1
Claude: [Checks all Phase 1 requirements]
        - ✅ Dockerfile exists
        - ✅ docker-compose.yml exists
        - ❌ Container not building

User: [Fixes Docker build issue]

User: /pm-validate 1
Claude: Phase 1 COMPLETE ✅
```

**Checking production readiness:**
```
User: /pm-validate
Claude: NOT READY ❌
        Missing:
        - 15 test files
        - Performance benchmarks
        - TESTING.md documentation

User: [Continues work]

User: /pm-validate
Claude: READY FOR PRODUCTION ✅
        All criteria met!
```

## Project Management Philosophy

These commands implement a rigorous project management approach:

1. **Visibility**: Always know project status
2. **Prioritization**: Focus on what matters now
3. **Validation**: Ensure quality before moving forward
4. **Risk Management**: Identify and address issues early
5. **Documentation**: Keep stakeholders informed

## Integration with CLAUDE.md

All commands reference `/home/m/repos/mesh/CLAUDE.md` which contains:
- 12-phase implementation checklist
- Acceptance criteria for each phase
- Project success criteria
- Technical specifications

These commands bring that structure to life with actionable tasks and real-time status.

## Troubleshooting

**Command not found**: Make sure you're in `/home/m/repos/mesh` directory

**Unexpected output**: Commands scan the actual repository state - output reflects reality

**Validation failing**: This is good! It shows what needs to be done before moving forward

**Too much detail**: Use `/pm-status` for quick updates, `/pm-report` for comprehensive details

## Contributing

To add new commands:
1. Create `[command-name].md` in this directory
2. Add `description` in front matter
3. Provide clear instructions for Claude
4. Document in this README

## Support

For questions about:
- **Commands themselves**: See this README
- **Project requirements**: See CLAUDE.md
- **Technical implementation**: See docs/TESTING.md (when created)

---

**Pro Tip**: Start each day with `/pm-status` and `/pm-next` to stay on track! 🚀
