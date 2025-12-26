"""
JSON reporter for machine-readable output.

Outputs validation results as JSON for monitoring systems and CI/CD.
"""

import json
import sys
from typing import Optional, TextIO

from validate.core.results import ValidationResult


class JSONReporter:
    """Reporter that outputs JSON results."""

    def __init__(
        self,
        output: TextIO = sys.stdout,
        indent: int = 2,
        compact: bool = False,
    ):
        """
        Initialize JSON reporter.

        Args:
            output: Output stream (default: stdout).
            indent: JSON indentation (default: 2).
            compact: If True, output single-line JSON.
        """
        self.output = output
        self.indent = None if compact else indent

    def report(self, result: ValidationResult) -> None:
        """
        Output validation result as JSON.

        Args:
            result: ValidationResult to output.
        """
        data = result.to_dict()
        json.dump(data, self.output, indent=self.indent, default=str)
        self.output.write("\n")
        self.output.flush()


def create_reporter(
    output: Optional[TextIO] = None,
    indent: int = 2,
    compact: bool = False,
) -> JSONReporter:
    """
    Create a JSON reporter.

    Args:
        output: Output stream (default: stdout).
        indent: JSON indentation.
        compact: Single-line output.

    Returns:
        Configured JSONReporter.
    """
    return JSONReporter(
        output=output or sys.stdout,
        indent=indent,
        compact=compact,
    )
