"""
Core validation framework components.

Provides execution, result handling, and orchestration.
"""

from validate.core.executor import NodeExecutor, run_local, run_on_node, ssh_command
from validate.core.results import CheckResult, CheckStatus, PhaseResult, ValidationResult
from validate.core.runner import ValidationRunner

__all__ = [
    "NodeExecutor",
    "run_local",
    "run_on_node",
    "ssh_command",
    "CheckResult",
    "CheckStatus",
    "PhaseResult",
    "ValidationResult",
    "ValidationRunner",
]
