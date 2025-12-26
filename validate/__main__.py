"""
Main entry point for the validation framework.

Usage:
    python -m validate [tier] [options]
    python -m validate smoke
    python -m validate standard --json
    python -m validate comprehensive --verbose
"""

import argparse
import sys
from typing import List, Optional, Union

from validate.core.results import CheckResult, PhaseResult, Tier
from validate.core.runner import create_runner
from validate.reporters.console import ConsoleReporter
from validate.reporters.json import JSONReporter


def parse_tier(tier_str: str) -> Tier:
    """Parse tier string to Tier enum."""
    tier_map = {
        "smoke": Tier.SMOKE,
        "1": Tier.SMOKE,
        "standard": Tier.STANDARD,
        "2": Tier.STANDARD,
        "comprehensive": Tier.COMPREHENSIVE,
        "full": Tier.COMPREHENSIVE,
        "3": Tier.COMPREHENSIVE,
        "certification": Tier.CERTIFICATION,
        "cert": Tier.CERTIFICATION,
        "4": Tier.CERTIFICATION,
    }
    return tier_map.get(tier_str.lower(), Tier.STANDARD)


def main(argv: Optional[List[str]] = None) -> int:
    """
    Run the validation framework.

    Args:
        argv: Command line arguments (default: sys.argv[1:]).

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Mesh Network Validation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Tiers:
  smoke (1)         Quick health check (~30s)
  standard (2)      Post-deployment verification (~3min)
  comprehensive (3) Full functional validation (~10min)
  certification (4) Production readiness (~30min)

Examples:
  python -m validate smoke
  python -m validate standard --verbose
  python -m validate comprehensive --json
        """,
    )

    parser.add_argument(
        "tier",
        nargs="?",
        default="standard",
        help="Validation tier: smoke, standard, comprehensive, certification (default: standard)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of colored text",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed node-level results",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "--continue-on-fail",
        action="store_true",
        help="Continue validation even if Phase 1 fails",
    )

    args = parser.parse_args(argv)
    tier = parse_tier(args.tier)

    # Create runner
    runner = create_runner(tier)

    # Create reporter
    reporter: Union[ConsoleReporter, JSONReporter]
    if args.json:
        reporter = JSONReporter()
    else:
        reporter = ConsoleReporter(
            color=not args.no_color,
            verbose=args.verbose,
        )

    # Print header if using console reporter
    if isinstance(reporter, ConsoleReporter):
        reporter.header(tier)

    # Run validation with real-time output for console
    if isinstance(reporter, ConsoleReporter):
        current_phase = [0]  # Mutable for closure

        def on_phase_start(phase_num: int, name: str) -> None:
            if phase_num != current_phase[0]:
                reporter.phase_start(phase_num, name)
                current_phase[0] = phase_num

        def on_check_complete(check: CheckResult) -> None:
            reporter.check_result(check)

        def on_phase_complete(phase: PhaseResult) -> None:
            reporter.phase_end(phase)

        # Run with callbacks
        result = runner.run(
            abort_on_phase1_fail=not args.continue_on_fail,
            on_check_complete=on_check_complete,
            on_phase_complete=on_phase_complete,
        )

        reporter.footer(result)
    else:
        # JSON mode - just run and output at end
        result = runner.run(abort_on_phase1_fail=not args.continue_on_fail)
        reporter.report(result)

    # Return exit code
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
