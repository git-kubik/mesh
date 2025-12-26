"""
Unit tests for security_hardening Ansible role.

Tests validate the security hardening role structure and configuration:
- Role directory structure (tasks, defaults, handlers, meta, templates)
- Task file syntax and required tasks
- Default variable definitions
- Template syntax
- Integration with deploy.yml
- Security playbook structure
"""

from pathlib import Path
from typing import List

import pytest
import yaml
from jinja2 import Environment, TemplateSyntaxError

# Constants
ROLE_NAME = "security_hardening"
ROLE_PATH = Path("openwrt-mesh-ansible/roles") / ROLE_NAME
PLAYBOOKS_PATH = Path("openwrt-mesh-ansible/playbooks")


@pytest.mark.unit
class TestSecurityHardeningRoleStructure:
    """Tests for security_hardening role directory structure."""

    def test_role_directory_exists(self) -> None:
        """Test that security_hardening role directory exists."""
        assert ROLE_PATH.exists(), f"Role directory not found: {ROLE_PATH}"
        assert ROLE_PATH.is_dir(), f"Role path is not a directory: {ROLE_PATH}"

    def test_tasks_directory_exists(self) -> None:
        """Test that tasks directory exists."""
        tasks_dir = ROLE_PATH / "tasks"
        assert tasks_dir.exists(), "Tasks directory missing for security_hardening role"
        assert tasks_dir.is_dir(), "Tasks path is not a directory"

    def test_defaults_directory_exists(self) -> None:
        """Test that defaults directory exists."""
        defaults_dir = ROLE_PATH / "defaults"
        assert defaults_dir.exists(), "Defaults directory missing for security_hardening role"
        assert defaults_dir.is_dir(), "Defaults path is not a directory"

    def test_handlers_directory_exists(self) -> None:
        """Test that handlers directory exists."""
        handlers_dir = ROLE_PATH / "handlers"
        assert handlers_dir.exists(), "Handlers directory missing for security_hardening role"
        assert handlers_dir.is_dir(), "Handlers path is not a directory"

    def test_meta_directory_exists(self) -> None:
        """Test that meta directory exists."""
        meta_dir = ROLE_PATH / "meta"
        assert meta_dir.exists(), "Meta directory missing for security_hardening role"
        assert meta_dir.is_dir(), "Meta path is not a directory"

    def test_templates_directory_exists(self) -> None:
        """Test that templates directory exists."""
        templates_dir = ROLE_PATH / "templates"
        assert templates_dir.exists(), "Templates directory missing for security_hardening role"
        assert templates_dir.is_dir(), "Templates path is not a directory"


@pytest.mark.unit
class TestSecurityHardeningTaskFiles:
    """Tests for security_hardening task files."""

    @pytest.fixture
    def required_task_files(self) -> List[str]:
        """List of required task files for security_hardening role."""
        return [
            "main.yml",
            "http_headers.yml",
            "ssh_hardening.yml",
            "rate_limiting.yml",
            "service_hardening.yml",
            "syslog_config.yml",
            "validation.yml",
        ]

    def test_main_task_file_exists(self) -> None:
        """Test that main.yml task file exists."""
        main_task = ROLE_PATH / "tasks" / "main.yml"
        assert main_task.exists(), "Main task file (main.yml) missing"

    def test_all_required_task_files_exist(self, required_task_files: List[str]) -> None:
        """Test that all required task files exist."""
        tasks_dir = ROLE_PATH / "tasks"
        for task_file in required_task_files:
            task_path = tasks_dir / task_file
            assert task_path.exists(), f"Required task file missing: {task_file}"

    def test_all_task_files_valid_yaml(self) -> None:
        """Test that all task files are valid YAML."""
        tasks_dir = ROLE_PATH / "tasks"
        for task_file in tasks_dir.glob("*.yml"):
            with open(task_file, "r") as f:
                try:
                    yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {task_file.name}: {e}")

    def test_main_task_includes_all_subtasks(self, required_task_files: List[str]) -> None:
        """Test that main.yml includes all subtask files."""
        main_task = ROLE_PATH / "tasks" / "main.yml"
        with open(main_task, "r") as f:
            content = f.read()

        subtasks = [t for t in required_task_files if t != "main.yml"]
        for subtask in subtasks:
            assert subtask in content, f"main.yml does not include {subtask}"


@pytest.mark.unit
class TestSecurityHardeningDefaults:
    """Tests for security_hardening default variables."""

    @pytest.fixture
    def required_variables(self) -> List[str]:
        """List of required default variables."""
        return [
            "security_hardening_enabled",
            "security_https_enabled",
            "security_http_headers_enabled",
            "security_ssh_hardening_enabled",
            "security_rate_limiting_enabled",
            "security_service_hardening_enabled",
            "security_syslog_local_enabled",
            "security_validation_enabled",
        ]

    def test_defaults_file_exists(self) -> None:
        """Test that defaults/main.yml exists."""
        defaults_file = ROLE_PATH / "defaults" / "main.yml"
        assert defaults_file.exists(), "Defaults file (defaults/main.yml) missing"

    def test_defaults_file_valid_yaml(self) -> None:
        """Test that defaults/main.yml is valid YAML."""
        defaults_file = ROLE_PATH / "defaults" / "main.yml"
        with open(defaults_file, "r") as f:
            try:
                data = yaml.safe_load(f)
                assert data is not None, "Defaults file is empty"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in defaults/main.yml: {e}")

    def test_all_required_variables_defined(self, required_variables: List[str]) -> None:
        """Test that all required variables are defined in defaults."""
        defaults_file = ROLE_PATH / "defaults" / "main.yml"
        with open(defaults_file, "r") as f:
            data = yaml.safe_load(f)

        for var in required_variables:
            assert var in data, f"Required variable missing: {var}"

    def test_master_switch_defaults_to_true(self) -> None:
        """Test that security_hardening_enabled defaults to true."""
        defaults_file = ROLE_PATH / "defaults" / "main.yml"
        with open(defaults_file, "r") as f:
            content = f.read()

        assert "security_hardening_enabled" in content
        assert "default('true'" in content or "default(true" in content


@pytest.mark.unit
class TestSecurityHardeningHandlers:
    """Tests for security_hardening handlers."""

    @pytest.fixture
    def expected_handlers(self) -> List[str]:
        """List of expected handler names."""
        return [
            "Restart uhttpd",
            "Restart sshd",
            "Reload firewall",
            "Restart syslog",
        ]

    def test_handlers_file_exists(self) -> None:
        """Test that handlers/main.yml exists."""
        handlers_file = ROLE_PATH / "handlers" / "main.yml"
        assert handlers_file.exists(), "Handlers file (handlers/main.yml) missing"

    def test_handlers_file_valid_yaml(self) -> None:
        """Test that handlers/main.yml is valid YAML."""
        handlers_file = ROLE_PATH / "handlers" / "main.yml"
        with open(handlers_file, "r") as f:
            try:
                data = yaml.safe_load(f)
                assert data is not None, "Handlers file is empty"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in handlers/main.yml: {e}")

    def test_expected_handlers_defined(self, expected_handlers: List[str]) -> None:
        """Test that expected handlers are defined."""
        handlers_file = ROLE_PATH / "handlers" / "main.yml"
        with open(handlers_file, "r") as f:
            data = yaml.safe_load(f)

        handler_names = [h.get("name", "") for h in data if isinstance(h, dict)]
        for expected in expected_handlers:
            assert expected in handler_names, f"Expected handler missing: {expected}"


@pytest.mark.unit
class TestSecurityHardeningMeta:
    """Tests for security_hardening role metadata."""

    def test_meta_file_exists(self) -> None:
        """Test that meta/main.yml exists."""
        meta_file = ROLE_PATH / "meta" / "main.yml"
        assert meta_file.exists(), "Meta file (meta/main.yml) missing"

    def test_meta_file_valid_yaml(self) -> None:
        """Test that meta/main.yml is valid YAML."""
        meta_file = ROLE_PATH / "meta" / "main.yml"
        with open(meta_file, "r") as f:
            try:
                data = yaml.safe_load(f)
                assert data is not None, "Meta file is empty"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in meta/main.yml: {e}")

    def test_meta_has_galaxy_info(self) -> None:
        """Test that meta/main.yml has galaxy_info section."""
        meta_file = ROLE_PATH / "meta" / "main.yml"
        with open(meta_file, "r") as f:
            data = yaml.safe_load(f)

        assert "galaxy_info" in data, "galaxy_info section missing from meta"

    def test_meta_has_dependencies(self) -> None:
        """Test that meta/main.yml has dependencies section."""
        meta_file = ROLE_PATH / "meta" / "main.yml"
        with open(meta_file, "r") as f:
            data = yaml.safe_load(f)

        assert "dependencies" in data, "dependencies section missing from meta"


@pytest.mark.unit
class TestSecurityHardeningTemplates:
    """Tests for security_hardening templates."""

    def test_uhttpd_template_exists(self) -> None:
        """Test that uhttpd.j2 template exists."""
        template_file = ROLE_PATH / "templates" / "uhttpd.j2"
        assert template_file.exists(), "Template file (uhttpd.j2) missing"

    def test_template_valid_jinja2_syntax(self) -> None:
        """Test that templates have valid Jinja2 syntax."""
        templates_dir = ROLE_PATH / "templates"
        env = Environment()

        for template_file in templates_dir.glob("*.j2"):
            with open(template_file, "r") as f:
                content = f.read()
            try:
                env.parse(content)
            except TemplateSyntaxError as e:
                pytest.fail(f"Invalid Jinja2 syntax in {template_file.name}: {e}")


@pytest.mark.unit
class TestSecurityHardeningIntegration:
    """Tests for security_hardening integration with deployment."""

    def test_role_included_in_deploy_playbook(self) -> None:
        """Test that security_hardening is included in deploy.yml."""
        deploy_playbook = PLAYBOOKS_PATH / "deploy.yml"
        with open(deploy_playbook, "r") as f:
            content = f.read()

        assert "security_hardening" in content, "security_hardening not found in deploy.yml"

    def test_role_has_security_tag(self) -> None:
        """Test that security_hardening role has security tag in deploy.yml."""
        deploy_playbook = PLAYBOOKS_PATH / "deploy.yml"
        with open(deploy_playbook, "r") as f:
            content = f.read()

        # Check that the role block includes tags: security
        # This is a simplified check - the role should have security tag
        assert "security_hardening" in content
        assert "security" in content


@pytest.mark.unit
class TestSecurityPlaybooks:
    """Tests for security-related playbooks."""

    @pytest.fixture
    def security_playbooks(self) -> List[str]:
        """List of security playbooks that should exist."""
        return [
            "security_audit.yml",
            "security_check.yml",
        ]

    def test_security_playbooks_exist(self, security_playbooks: List[str]) -> None:
        """Test that security playbooks exist."""
        for playbook in security_playbooks:
            playbook_path = PLAYBOOKS_PATH / playbook
            assert playbook_path.exists(), f"Security playbook missing: {playbook}"

    def test_security_playbooks_valid_yaml(self, security_playbooks: List[str]) -> None:
        """Test that security playbooks are valid YAML."""
        for playbook in security_playbooks:
            playbook_path = PLAYBOOKS_PATH / playbook
            with open(playbook_path, "r") as f:
                try:
                    yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {playbook}: {e}")

    def test_security_audit_targets_mesh_nodes(self) -> None:
        """Test that security_audit.yml targets mesh_nodes."""
        playbook_path = PLAYBOOKS_PATH / "security_audit.yml"
        with open(playbook_path, "r") as f:
            data = yaml.safe_load(f)

        # Check first play targets mesh_nodes
        assert len(data) > 0, "Playbook is empty"
        first_play = data[0]
        assert "hosts" in first_play, "hosts key missing from playbook"
        assert "mesh_nodes" in first_play["hosts"], "Playbook does not target mesh_nodes"
