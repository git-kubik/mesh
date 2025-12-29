"""
Validation runner with phase orchestration.

Executes validation checks in ordered phases with proper dependency handling.
"""

import time
from datetime import datetime
from typing import Callable, Dict, List, Optional, Tuple

from validate.core.results import CheckResult, CheckStatus, PhaseResult, Tier, ValidationResult

# Type alias for check functions
CheckFunc = Callable[[], CheckResult]


class ValidationRunner:
    """
    Orchestrates validation checks across phases.

    Phases execute in order, with Phase 1 (prerequisites) being required
    to pass before continuing to subsequent phases.
    """

    def __init__(self, tier: Tier = Tier.STANDARD):
        """
        Initialize validation runner.

        Args:
            tier: Validation tier to run (determines which checks).
        """
        self.tier = tier
        self._phases: Dict[int, Tuple[str, List[Tuple[str, CheckFunc]]]] = {}

    def register_phase(self, phase_num: int, name: str) -> None:
        """
        Register a new phase.

        Args:
            phase_num: Phase number (1-based).
            name: Human-readable phase name.
        """
        if phase_num not in self._phases:
            self._phases[phase_num] = (name, [])

    def register_check(
        self,
        phase_num: int,
        category: str,
        check_func: CheckFunc,
        min_tier: Tier = Tier.SMOKE,
    ) -> None:
        """
        Register a check function to a phase.

        Args:
            phase_num: Phase to add check to.
            category: Check category (e.g., "connectivity.ping").
            check_func: Function that performs the check.
            min_tier: Minimum tier required to run this check.
        """
        if self.tier.value < min_tier.value:
            return  # Skip checks above our tier

        if phase_num not in self._phases:
            self.register_phase(phase_num, f"Phase {phase_num}")

        self._phases[phase_num][1].append((category, check_func))

    def run(
        self,
        abort_on_phase1_fail: bool = True,
        on_check_complete: Optional[Callable[[CheckResult], None]] = None,
        on_phase_complete: Optional[Callable[[PhaseResult], None]] = None,
    ) -> ValidationResult:
        """
        Execute all registered checks in phase order.

        Args:
            abort_on_phase1_fail: If True, abort if any Phase 1 check fails.
            on_check_complete: Callback after each check completes.
            on_phase_complete: Callback after each phase completes.

        Returns:
            ValidationResult with all phase and check results.
        """
        result = ValidationResult(
            tier=self.tier,
            timestamp=datetime.now(),
        )

        start_time = time.time()

        # Execute phases in order
        for phase_num in sorted(self._phases.keys()):
            phase_name, checks = self._phases[phase_num]

            phase_result = self._run_phase(
                phase_num=phase_num,
                name=phase_name,
                checks=checks,
                on_check_complete=on_check_complete,
            )

            result.phases.append(phase_result)

            if on_phase_complete:
                on_phase_complete(phase_result)

            # Abort on Phase 1 failure if configured
            if abort_on_phase1_fail and phase_num == 1 and not phase_result.passed:
                result.aborted = True
                result.abort_reason = (
                    f"Phase 1 (Prerequisites) failed: "
                    f"{phase_result.failed_count}/{phase_result.total_count} checks failed"
                )
                break

        result.duration_ms = int((time.time() - start_time) * 1000)
        return result

    def _run_phase(
        self,
        phase_num: int,
        name: str,
        checks: List[Tuple[str, CheckFunc]],
        on_check_complete: Optional[Callable[[CheckResult], None]] = None,
    ) -> PhaseResult:
        """
        Execute all checks in a phase.

        Args:
            phase_num: Phase number.
            name: Phase name.
            checks: List of (category, check_func) tuples.
            on_check_complete: Callback after each check.

        Returns:
            PhaseResult with all check results.
        """
        phase_result = PhaseResult(phase=phase_num, name=name)
        phase_start = time.time()

        for category, check_func in checks:
            check_start = time.time()

            try:
                check_result = check_func()
                check_result.category = category  # Ensure category is set
            except Exception as e:
                check_result = CheckResult(
                    category=category,
                    status=CheckStatus.ERROR,
                    message=f"Check error: {e}",
                )

            check_result.duration_ms = int((time.time() - check_start) * 1000)
            phase_result.checks.append(check_result)

            if on_check_complete:
                on_check_complete(check_result)

        phase_result.duration_ms = int((time.time() - phase_start) * 1000)
        return phase_result

    def get_phase_names(self) -> List[Tuple[int, str]]:
        """Get list of registered phases."""
        return [(num, self._phases[num][0]) for num in sorted(self._phases.keys())]

    def get_check_count(self) -> int:
        """Get total number of registered checks."""
        return sum(len(checks) for _, checks in self._phases.values())


def create_runner(tier: Tier) -> ValidationRunner:
    """
    Create a validation runner pre-configured with all checks for the tier.

    Args:
        tier: Validation tier to run.

    Returns:
        Configured ValidationRunner instance.
    """
    # Import checks here to avoid circular imports
    from validate.checks import batman, connectivity

    runner = ValidationRunner(tier=tier)

    # Phase 1: Prerequisites (must pass to continue)
    runner.register_phase(1, "Prerequisites")
    runner.register_check(1, "connectivity.ping", connectivity.check_ping, Tier.SMOKE)
    runner.register_check(1, "connectivity.ssh", connectivity.check_ssh, Tier.SMOKE)
    runner.register_check(1, "batman.module", batman.check_module, Tier.SMOKE)

    # Phase 2: Foundation
    runner.register_phase(2, "Foundation")
    runner.register_check(2, "batman.interfaces", batman.check_interfaces, Tier.STANDARD)
    runner.register_check(2, "batman.neighbors", batman.check_neighbors, Tier.STANDARD)
    runner.register_check(2, "batman.originators", batman.check_originators, Tier.STANDARD)
    runner.register_check(2, "batman.gateways", batman.check_gateways, Tier.STANDARD)

    # Phase 3: Network (Tier 2+)
    runner.register_phase(3, "Network")

    # Import more checks for higher tiers
    if tier.value >= Tier.STANDARD.value:
        from validate.checks import vlans

        runner.register_check(3, "vlans.mesh", vlans.check_mesh_vlan, Tier.STANDARD)
        runner.register_check(3, "vlans.client", vlans.check_client_vlan, Tier.STANDARD)

    # Phase 4: Services (Tier 3+)
    if tier.value >= Tier.COMPREHENSIVE.value:
        from validate.checks import infrastructure, security, services, wan

        runner.register_phase(4, "Services")
        runner.register_check(
            4, "vlans.management", vlans.check_management_vlan, Tier.COMPREHENSIVE
        )
        runner.register_check(4, "vlans.iot", vlans.check_iot_vlan, Tier.COMPREHENSIVE)
        runner.register_check(4, "vlans.guest", vlans.check_guest_vlan, Tier.COMPREHENSIVE)
        runner.register_check(4, "services.dhcp", services.check_dhcp, Tier.COMPREHENSIVE)
        runner.register_check(4, "services.firewall", services.check_firewall, Tier.COMPREHENSIVE)
        runner.register_check(4, "security.ssh", security.check_ssh_hardening, Tier.COMPREHENSIVE)
        runner.register_check(4, "security.https", security.check_https, Tier.COMPREHENSIVE)
        runner.register_check(4, "wan.connectivity", wan.check_connectivity, Tier.COMPREHENSIVE)
        runner.register_check(4, "wan.dns", wan.check_dns, Tier.COMPREHENSIVE)
        runner.register_check(
            4, "infrastructure.switches", infrastructure.check_switches, Tier.COMPREHENSIVE
        )

    # Phase 5: Certification (Tier 4)
    if tier.value >= Tier.CERTIFICATION.value:
        from validate.checks import failover, performance, wireless

        runner.register_phase(5, "Certification")
        runner.register_check(5, "failover.link", failover.check_link_failover, Tier.CERTIFICATION)
        runner.register_check(5, "failover.wan", failover.check_wan_failover, Tier.CERTIFICATION)
        runner.register_check(5, "failover.node", failover.check_node_failover, Tier.CERTIFICATION)
        runner.register_check(5, "wireless.mesh", wireless.check_mesh_wireless, Tier.CERTIFICATION)
        runner.register_check(5, "wireless.roaming", wireless.check_roaming, Tier.CERTIFICATION)
        runner.register_check(5, "wireless.bla", wireless.check_bla, Tier.CERTIFICATION)
        runner.register_check(
            5, "performance.latency", performance.check_latency, Tier.CERTIFICATION
        )
        runner.register_check(
            5, "performance.stress", performance.check_stress_ping, Tier.CERTIFICATION
        )

    return runner
