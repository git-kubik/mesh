"""
Console reporter with colored output.

Provides real-time feedback during validation with colored status indicators.
"""

import sys
from typing import Optional, TextIO

from validate.core.results import CheckResult, CheckStatus, PhaseResult, Tier, ValidationResult


class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_GREEN = "\033[42m"
    BG_RED = "\033[41m"


class ConsoleReporter:
    """Reporter that outputs colored results to the console."""

    def __init__(
        self,
        output: TextIO = sys.stdout,
        color: bool = True,
        verbose: bool = False,
    ):
        """
        Initialize console reporter.

        Args:
            output: Output stream (default: stdout).
            color: Enable colored output.
            verbose: Show detailed node-level results.
        """
        self.output = output
        self.color = color and output.isatty()
        self.verbose = verbose

    def _c(self, color: str, text: str) -> str:
        """Apply color to text if colors enabled."""
        if self.color:
            return f"{color}{text}{Colors.RESET}"
        return text

    def _status_symbol(self, status: CheckStatus) -> str:
        """Get colored symbol for status."""
        symbols = {
            CheckStatus.PASS: self._c(Colors.GREEN, "✓"),
            CheckStatus.FAIL: self._c(Colors.RED, "✗"),
            CheckStatus.SKIP: self._c(Colors.YELLOW, "○"),
            CheckStatus.ERROR: self._c(Colors.RED, "!"),
        }
        return symbols.get(status, "?")

    def _tier_name(self, tier: Tier) -> str:
        """Get display name for tier."""
        names = {
            Tier.SMOKE: "Smoke (Tier 1)",
            Tier.STANDARD: "Standard (Tier 2)",
            Tier.COMPREHENSIVE: "Comprehensive (Tier 3)",
            Tier.CERTIFICATION: "Certification (Tier 4)",
        }
        return names.get(tier, str(tier))

    def write(self, text: str = "", end: str = "\n") -> None:
        """Write text to output."""
        self.output.write(text + end)
        self.output.flush()

    def header(self, tier: Tier) -> None:
        """Print validation header."""
        line = "═" * 60
        self.write()
        self.write(self._c(Colors.BOLD, line))
        self.write(self._c(Colors.BOLD, f" MESH NETWORK VALIDATION - {self._tier_name(tier)}"))
        self.write(self._c(Colors.BOLD, line))
        self.write()

    def phase_start(self, phase: int, name: str) -> None:
        """Print phase header."""
        self.write(self._c(Colors.CYAN + Colors.BOLD, f"Phase {phase}: {name}"))

    def check_result(self, result: CheckResult) -> None:
        """Print check result."""
        symbol = self._status_symbol(result.status)
        category = result.category.ljust(25)
        message = result.message or result.status.value

        self.write(f"  {symbol} {category} {self._c(Colors.DIM, message)}")

        # Show node details in verbose mode or on failure
        if (self.verbose or result.failed) and result.nodes:
            for node_name, node_result in result.nodes.items():
                node_symbol = self._status_symbol(node_result.status)
                node_msg = node_result.message or node_result.status.value
                self.write(f"      {node_symbol} {node_name}: {self._c(Colors.DIM, node_msg)}")

    def phase_end(self, result: PhaseResult) -> None:
        """Print phase summary (optional, just adds spacing)."""
        self.write()

    def footer(self, result: ValidationResult) -> None:
        """Print final summary."""
        line = "═" * 60
        self.write(self._c(Colors.BOLD, line))

        # Overall result
        if result.passed:
            status_text = self._c(Colors.GREEN + Colors.BOLD, "PASS")
        else:
            status_text = self._c(Colors.RED + Colors.BOLD, "FAIL")

        self.write(
            f" RESULT: {status_text} "
            f"({result.passed_checks}/{result.total_checks} checks passed)"
        )

        # Duration
        duration_sec = result.duration_ms / 1000
        if duration_sec >= 60:
            duration_str = f"{int(duration_sec // 60)}m {int(duration_sec % 60)}s"
        else:
            duration_str = f"{duration_sec:.1f}s"
        self.write(f" Duration: {duration_str}")

        # Show abort reason if aborted
        if result.aborted:
            self.write(self._c(Colors.YELLOW, f" Aborted: {result.abort_reason}"))

        # Show failed checks summary
        if result.failed_checks > 0:
            self.write()
            self.write(self._c(Colors.RED, " Failed checks:"))
            for check in result.failed_check_list:
                self.write(f"   - {check.category}: {check.message}")

        self.write(self._c(Colors.BOLD, line))
        self.write()

    def report(self, result: ValidationResult) -> None:
        """
        Print complete validation report.

        This is called at the end to print the full report.
        For real-time output, use the individual methods.
        """
        self.header(result.tier)

        for phase in result.phases:
            self.phase_start(phase.phase, phase.name)
            for check in phase.checks:
                self.check_result(check)
            self.phase_end(phase)

        self.footer(result)


def create_reporter(
    output: Optional[TextIO] = None,
    color: bool = True,
    verbose: bool = False,
) -> ConsoleReporter:
    """
    Create a console reporter.

    Args:
        output: Output stream (default: stdout).
        color: Enable colors.
        verbose: Enable verbose output.

    Returns:
        Configured ConsoleReporter.
    """
    return ConsoleReporter(
        output=output or sys.stdout,
        color=color,
        verbose=verbose,
    )
