"""
Result models for network validation.

Provides structured result types for checks, phases, and overall validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class CheckStatus(Enum):
    """Status of a validation check."""

    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


class Tier(Enum):
    """Validation tier levels."""

    SMOKE = 1
    STANDARD = 2
    COMPREHENSIVE = 3
    CERTIFICATION = 4


@dataclass
class NodeResult:
    """Result for a single node within a check."""

    node: str
    status: CheckStatus
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckResult:
    """Result of a single validation check."""

    category: str  # e.g., "connectivity.ping", "batman.neighbors"
    status: CheckStatus
    message: str = ""
    duration_ms: int = 0
    nodes: Dict[str, NodeResult] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Optional[str] = None

    @property
    def passed(self) -> bool:
        """Check if this check passed."""
        return self.status == CheckStatus.PASS

    @property
    def failed(self) -> bool:
        """Check if this check failed."""
        return self.status == CheckStatus.FAIL

    def add_node_result(
        self,
        node: str,
        status: CheckStatus,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a result for a specific node."""
        self.nodes[node] = NodeResult(
            node=node,
            status=status,
            message=message,
            data=data or {},
        )

    def aggregate_status(self) -> None:
        """Aggregate node results into overall status."""
        if not self.nodes:
            return

        # All must pass for check to pass
        statuses = [n.status for n in self.nodes.values()]
        if all(s == CheckStatus.PASS for s in statuses):
            self.status = CheckStatus.PASS
        elif any(s == CheckStatus.ERROR for s in statuses):
            self.status = CheckStatus.ERROR
        elif any(s == CheckStatus.FAIL for s in statuses):
            self.status = CheckStatus.FAIL
        elif all(s == CheckStatus.SKIP for s in statuses):
            self.status = CheckStatus.SKIP
        else:
            self.status = CheckStatus.FAIL


@dataclass
class PhaseResult:
    """Result of a validation phase (group of checks)."""

    phase: int
    name: str
    checks: List[CheckResult] = field(default_factory=list)
    duration_ms: int = 0

    @property
    def passed(self) -> bool:
        """Check if all checks in this phase passed."""
        return all(c.passed for c in self.checks)

    @property
    def passed_count(self) -> int:
        """Number of passed checks."""
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed_count(self) -> int:
        """Number of failed checks."""
        return sum(1 for c in self.checks if c.failed)

    @property
    def total_count(self) -> int:
        """Total number of checks."""
        return len(self.checks)


@dataclass
class ValidationResult:
    """Overall result of a validation run."""

    tier: Tier
    phases: List[PhaseResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0
    aborted: bool = False
    abort_reason: str = ""

    @property
    def passed(self) -> bool:
        """Check all phases completed successfully without abort."""
        return not self.aborted and all(p.passed for p in self.phases)

    @property
    def status(self) -> CheckStatus:
        """Overall validation status."""
        if self.aborted:
            return CheckStatus.FAIL
        return CheckStatus.PASS if self.passed else CheckStatus.FAIL

    @property
    def total_checks(self) -> int:
        """Total number of checks across all phases."""
        return sum(p.total_count for p in self.phases)

    @property
    def passed_checks(self) -> int:
        """Total number of passed checks."""
        return sum(p.passed_count for p in self.phases)

    @property
    def failed_checks(self) -> int:
        """Total number of failed checks."""
        return sum(p.failed_count for p in self.phases)

    @property
    def all_checks(self) -> List[CheckResult]:
        """Flatten all checks from all phases."""
        return [check for phase in self.phases for check in phase.checks]

    @property
    def failed_check_list(self) -> List[CheckResult]:
        """Get list of failed checks."""
        return [c for c in self.all_checks if c.failed]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tier": self.tier.name.lower(),
            "result": "PASS" if self.passed else "FAIL",
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "aborted": self.aborted,
            "abort_reason": self.abort_reason if self.aborted else None,
            "summary": {
                "total": self.total_checks,
                "passed": self.passed_checks,
                "failed": self.failed_checks,
            },
            "phases": [
                {
                    "phase": p.phase,
                    "name": p.name,
                    "duration_ms": p.duration_ms,
                    "checks": [
                        {
                            "category": c.category,
                            "status": c.status.value,
                            "message": c.message,
                            "duration_ms": c.duration_ms,
                            "nodes": {
                                k: {
                                    "status": v.status.value,
                                    "message": v.message,
                                    "data": v.data,
                                }
                                for k, v in c.nodes.items()
                            },
                            "data": c.data,
                            "diagnostics": c.diagnostics,
                        }
                        for c in p.checks
                    ],
                }
                for p in self.phases
            ],
        }
