---
name: Test Implementation
about: Create a new test for the test suite
title: '[Test] '
labels: type-testing, priority-medium
assignees: ''
---

## Test: [Test Name]

**Test Category**: [Unit/Integration/Functional/Performance/Failover]
**Phase**: [5-9]
**Priority**: [Critical/High/Medium/Low]
**Estimated Effort**: [X hours]

## Description
[What this test validates]

## Test Scope
[What specific functionality or scenario this test covers]

## Acceptance Criteria
- [ ] Test file created in correct directory
- [ ] Test implements all required scenarios
- [ ] Test passes consistently
- [ ] Test has clear assertions with failure messages
- [ ] Test is properly documented (docstring)
- [ ] Test uses appropriate fixtures
- [ ] Test execution time is reasonable (< X seconds)

## Implementation Details
- **File to create**: `tests/[category]/test_[name].py`
- **Fixtures needed**: [List fixtures from conftest.py]
- **Dependencies**: [External tools like iperf3, if needed]
- **Prerequisites**: [Node access, specific configuration, etc.]

## Test Scenarios

### Scenario 1: [Scenario Name]
- **Given**: [Initial state]
- **When**: [Action performed]
- **Then**: [Expected outcome]

### Scenario 2: [Scenario Name]
- **Given**: [Initial state]
- **When**: [Action performed]
- **Then**: [Expected outcome]

## Example Test Structure

```python
import pytest

@pytest.mark.[category]
def test_[name](fixture1, fixture2):
    """
    Test description.

    This test validates [what it validates] by [how it validates].
    """
    # Arrange
    # ... setup

    # Act
    # ... perform action

    # Assert
    assert condition, "Clear failure message"
```

## Performance/Benchmark Requirements
[If this is a performance test, specify thresholds]
- Throughput: ≥ X Mbps
- Latency: < X ms
- Success rate: ≥ X%

## Definition of Done
- [ ] Test implemented and passing
- [ ] Test documented with clear docstring
- [ ] Test added to appropriate test file
- [ ] Test runs in CI/CD pipeline
- [ ] Code coverage maintained or improved
- [ ] PR reviewed and merged

## Related Issues
- Part of Milestone X: [Test Implementation Milestone]
- Depends on: [Infrastructure requirements]
- Related tests: [Similar or related test issues]

## References
- pytest docs: https://docs.pytest.org/
- Use `python-test` or `mesh-test` skill for guidance
- See `docs/TESTING.md` (when created)
