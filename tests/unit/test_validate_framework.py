"""
Unit tests for the validation framework.

Tests the core framework components without requiring network access.
"""

from validate.core.results import (
    CheckResult,
    CheckStatus,
    NodeResult,
    PhaseResult,
    Tier,
    ValidationResult,
)
from validate.core.runner import ValidationRunner, create_runner


class TestCheckStatus:
    """Tests for CheckStatus enum."""

    def test_status_values(self) -> None:
        """Check all status values exist."""
        assert CheckStatus.PASS.value == "PASS"
        assert CheckStatus.FAIL.value == "FAIL"
        assert CheckStatus.SKIP.value == "SKIP"
        assert CheckStatus.ERROR.value == "ERROR"


class TestTier:
    """Tests for Tier enum."""

    def test_tier_values(self) -> None:
        """Check all tier values exist."""
        assert Tier.SMOKE.value == 1
        assert Tier.STANDARD.value == 2
        assert Tier.COMPREHENSIVE.value == 3
        assert Tier.CERTIFICATION.value == 4


class TestNodeResult:
    """Tests for NodeResult dataclass."""

    def test_create_node_result(self) -> None:
        """Create a node result."""
        result = NodeResult(
            node="node1",
            status=CheckStatus.PASS,
            message="All good",
            data={"latency": 1.5},
        )
        assert result.node == "node1"
        assert result.status == CheckStatus.PASS
        assert result.message == "All good"
        assert result.data["latency"] == 1.5

    def test_node_result_defaults(self) -> None:
        """Check node result defaults."""
        result = NodeResult(node="node2", status=CheckStatus.FAIL)
        assert result.message == ""
        assert result.data == {}


class TestCheckResult:
    """Tests for CheckResult dataclass."""

    def test_create_check_result(self) -> None:
        """Create a check result."""
        result = CheckResult(
            category="connectivity.ping",
            status=CheckStatus.PASS,
            message="All nodes respond",
        )
        assert result.category == "connectivity.ping"
        assert result.status == CheckStatus.PASS
        assert result.passed is True
        assert result.failed is False

    def test_check_result_failed(self) -> None:
        """Check failed status properties."""
        result = CheckResult(
            category="batman.module",
            status=CheckStatus.FAIL,
            message="Not loaded",
        )
        assert result.passed is False
        assert result.failed is True

    def test_add_node_result(self) -> None:
        """Add node results to a check."""
        result = CheckResult(
            category="test.check",
            status=CheckStatus.PASS,
        )
        result.add_node_result("node1", CheckStatus.PASS, "OK")
        result.add_node_result("node2", CheckStatus.FAIL, "Failed")

        assert len(result.nodes) == 2
        assert result.nodes["node1"].status == CheckStatus.PASS
        assert result.nodes["node2"].status == CheckStatus.FAIL

    def test_aggregate_status_all_pass(self) -> None:
        """Aggregate status when all nodes pass."""
        result = CheckResult(category="test", status=CheckStatus.FAIL)
        result.add_node_result("node1", CheckStatus.PASS)
        result.add_node_result("node2", CheckStatus.PASS)
        result.add_node_result("node3", CheckStatus.PASS)
        result.aggregate_status()

        assert result.status == CheckStatus.PASS

    def test_aggregate_status_one_fail(self) -> None:
        """Aggregate status when one node fails."""
        result = CheckResult(category="test", status=CheckStatus.PASS)
        result.add_node_result("node1", CheckStatus.PASS)
        result.add_node_result("node2", CheckStatus.FAIL)
        result.add_node_result("node3", CheckStatus.PASS)
        result.aggregate_status()

        assert result.status == CheckStatus.FAIL

    def test_aggregate_status_error_priority(self) -> None:
        """Aggregate status gives ERROR priority over FAIL."""
        result = CheckResult(category="test", status=CheckStatus.PASS)
        result.add_node_result("node1", CheckStatus.PASS)
        result.add_node_result("node2", CheckStatus.FAIL)
        result.add_node_result("node3", CheckStatus.ERROR)
        result.aggregate_status()

        assert result.status == CheckStatus.ERROR

    def test_aggregate_status_all_skip(self) -> None:
        """Aggregate status when all nodes skip."""
        result = CheckResult(category="test", status=CheckStatus.PASS)
        result.add_node_result("node1", CheckStatus.SKIP)
        result.add_node_result("node2", CheckStatus.SKIP)
        result.aggregate_status()

        assert result.status == CheckStatus.SKIP

    def test_aggregate_status_empty(self) -> None:
        """Aggregate does nothing with no nodes."""
        result = CheckResult(category="test", status=CheckStatus.PASS)
        result.aggregate_status()

        assert result.status == CheckStatus.PASS


class TestPhaseResult:
    """Tests for PhaseResult dataclass."""

    def test_create_phase_result(self) -> None:
        """Create a phase result."""
        result = PhaseResult(phase=1, name="Prerequisites")
        assert result.phase == 1
        assert result.name == "Prerequisites"
        assert result.checks == []

    def test_phase_passed_empty(self) -> None:
        """Empty phase passes."""
        result = PhaseResult(phase=1, name="Test")
        assert result.passed is True

    def test_phase_passed_with_checks(self) -> None:
        """Phase with passing checks passes."""
        result = PhaseResult(phase=1, name="Test")
        result.checks.append(CheckResult(category="test1", status=CheckStatus.PASS))
        result.checks.append(CheckResult(category="test2", status=CheckStatus.PASS))

        assert result.passed is True
        assert result.passed_count == 2
        assert result.failed_count == 0
        assert result.total_count == 2

    def test_phase_failed_with_checks(self) -> None:
        """Phase with failing check fails."""
        result = PhaseResult(phase=1, name="Test")
        result.checks.append(CheckResult(category="test1", status=CheckStatus.PASS))
        result.checks.append(CheckResult(category="test2", status=CheckStatus.FAIL))

        assert result.passed is False
        assert result.passed_count == 1
        assert result.failed_count == 1


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_create_validation_result(self) -> None:
        """Create a validation result."""
        result = ValidationResult(tier=Tier.SMOKE)
        assert result.tier == Tier.SMOKE
        assert result.phases == []
        assert result.aborted is False

    def test_validation_passed(self) -> None:
        """Validation with passing phases passes."""
        result = ValidationResult(tier=Tier.SMOKE)
        phase = PhaseResult(phase=1, name="Test")
        phase.checks.append(CheckResult(category="test", status=CheckStatus.PASS))
        result.phases.append(phase)

        assert result.passed is True
        assert result.status == CheckStatus.PASS
        assert result.total_checks == 1
        assert result.passed_checks == 1
        assert result.failed_checks == 0

    def test_validation_aborted(self) -> None:
        """Aborted validation fails."""
        result = ValidationResult(tier=Tier.SMOKE, aborted=True)
        assert result.passed is False
        assert result.status == CheckStatus.FAIL

    def test_all_checks_property(self) -> None:
        """Get all checks across phases."""
        result = ValidationResult(tier=Tier.STANDARD)
        phase1 = PhaseResult(phase=1, name="Phase 1")
        phase1.checks.append(CheckResult(category="check1", status=CheckStatus.PASS))
        phase2 = PhaseResult(phase=2, name="Phase 2")
        phase2.checks.append(CheckResult(category="check2", status=CheckStatus.PASS))
        phase2.checks.append(CheckResult(category="check3", status=CheckStatus.FAIL))
        result.phases = [phase1, phase2]

        assert len(result.all_checks) == 3
        assert result.failed_check_list[0].category == "check3"

    def test_to_dict(self) -> None:
        """Convert result to dict."""
        result = ValidationResult(tier=Tier.SMOKE)
        phase = PhaseResult(phase=1, name="Prerequisites")
        check = CheckResult(
            category="test.check",
            status=CheckStatus.PASS,
            message="OK",
        )
        phase.checks.append(check)
        result.phases.append(phase)

        d = result.to_dict()
        assert d["tier"] == "smoke"
        assert d["result"] == "PASS"
        assert d["summary"]["total"] == 1
        assert len(d["phases"]) == 1
        assert d["phases"][0]["checks"][0]["category"] == "test.check"


class TestValidationRunner:
    """Tests for ValidationRunner class."""

    def test_create_runner(self) -> None:
        """Create a validation runner."""
        runner = ValidationRunner(tier=Tier.SMOKE)
        assert runner.tier == Tier.SMOKE
        assert runner._phases == {}

    def test_register_phase(self) -> None:
        """Register a phase."""
        runner = ValidationRunner(tier=Tier.SMOKE)
        runner.register_phase(1, "Prerequisites")
        runner.register_phase(2, "Foundation")

        assert 1 in runner._phases
        assert 2 in runner._phases
        assert runner._phases[1] == ("Prerequisites", [])

    def test_register_check(self) -> None:
        """Register a check function."""
        runner = ValidationRunner(tier=Tier.SMOKE)
        runner.register_phase(1, "Test")

        def mock_check() -> CheckResult:
            return CheckResult(
                category="mock.check",
                status=CheckStatus.PASS,
            )

        runner.register_check(1, "mock.check", mock_check, Tier.SMOKE)
        assert len(runner._phases[1][1]) == 1

    def test_run_single_check(self) -> None:
        """Run a single check."""
        runner = ValidationRunner(tier=Tier.SMOKE)
        runner.register_phase(1, "Test Phase")

        def passing_check() -> CheckResult:
            return CheckResult(
                category="test.pass",
                status=CheckStatus.PASS,
                message="Passed",
            )

        runner.register_check(1, "test.pass", passing_check, Tier.SMOKE)
        result = runner.run()

        assert result.passed is True
        assert result.total_checks == 1
        assert len(result.phases) == 1

    def test_run_phase1_fail_aborts(self) -> None:
        """Phase 1 failure aborts validation."""
        runner = ValidationRunner(tier=Tier.SMOKE)
        runner.register_phase(1, "Prerequisites")
        runner.register_phase(2, "Foundation")

        def failing_check() -> CheckResult:
            return CheckResult(
                category="test.fail",
                status=CheckStatus.FAIL,
                message="Failed",
            )

        def passing_check() -> CheckResult:
            return CheckResult(
                category="test.pass",
                status=CheckStatus.PASS,
            )

        runner.register_check(1, "test.fail", failing_check, Tier.SMOKE)
        runner.register_check(2, "test.pass", passing_check, Tier.SMOKE)

        result = runner.run()

        assert result.aborted is True
        assert "Phase 1" in result.abort_reason
        assert len(result.phases) == 1  # Phase 2 not run

    def test_run_continue_on_fail(self) -> None:
        """Continue on fail skips abort."""
        runner = ValidationRunner(tier=Tier.SMOKE)
        runner.register_phase(1, "Prerequisites")
        runner.register_phase(2, "Foundation")

        def failing_check() -> CheckResult:
            return CheckResult(
                category="test.fail",
                status=CheckStatus.FAIL,
            )

        def passing_check() -> CheckResult:
            return CheckResult(
                category="test.pass",
                status=CheckStatus.PASS,
            )

        runner.register_check(1, "test.fail", failing_check, Tier.SMOKE)
        runner.register_check(2, "test.pass", passing_check, Tier.SMOKE)

        result = runner.run(abort_on_phase1_fail=False)

        assert result.aborted is False
        assert len(result.phases) == 2  # Both phases run

    def test_callbacks(self) -> None:
        """Test callback invocation."""
        runner = ValidationRunner(tier=Tier.SMOKE)
        runner.register_phase(1, "Test")

        def mock_check() -> CheckResult:
            return CheckResult(
                category="test.check",
                status=CheckStatus.PASS,
            )

        runner.register_check(1, "test.check", mock_check, Tier.SMOKE)

        # Track callbacks
        callback_log: list[str] = []

        def on_check_complete(result: CheckResult) -> None:
            callback_log.append(f"check:{result.category}")

        def on_phase_complete(result: PhaseResult) -> None:
            callback_log.append(f"phase:{result.phase}")

        runner.run(
            on_check_complete=on_check_complete,
            on_phase_complete=on_phase_complete,
        )

        assert "check:test.check" in callback_log
        assert "phase:1" in callback_log


class TestCreateRunner:
    """Tests for create_runner factory function."""

    def test_create_smoke_runner(self) -> None:
        """Create a smoke tier runner."""
        runner = create_runner(Tier.SMOKE)
        assert runner.tier == Tier.SMOKE
        # Should have Phase 1 with connectivity and batman checks
        assert 1 in runner._phases
        # Smoke tier has 3 checks
        assert runner.get_check_count() == 3

    def test_create_standard_runner(self) -> None:
        """Create a standard tier runner."""
        runner = create_runner(Tier.STANDARD)
        assert runner.tier == Tier.STANDARD
        # Should have Phases 1, 2, 3
        assert 1 in runner._phases
        assert 2 in runner._phases
        assert 3 in runner._phases
        # Standard has more checks
        assert runner.get_check_count() > 3

    def test_create_comprehensive_runner(self) -> None:
        """Create a comprehensive tier runner."""
        runner = create_runner(Tier.COMPREHENSIVE)
        assert runner.tier == Tier.COMPREHENSIVE
        # Should have Phases 1-4 (Tier 3 checks)
        assert 1 in runner._phases
        assert 4 in runner._phases
        # Comprehensive has most checks
        assert runner.get_check_count() > 10
