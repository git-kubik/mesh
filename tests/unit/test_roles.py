"""
Unit tests for Ansible role structure and syntax validation.

Tests validate all 9 roles in the mesh deployment:
- Role directory structure
- Task file syntax
- Default variable definitions
- Template existence and syntax
- Role dependencies
"""

from pathlib import Path
from typing import Dict, List

import pytest
import yaml
from jinja2 import Environment, TemplateSyntaxError


@pytest.mark.unit
class TestRoleStructure:
    """Tests for role directory structure."""

    def test_roles_directory_exists(self, roles_root: Path) -> None:
        """Test that roles directory exists."""
        assert roles_root.exists(), f"Roles directory not found: {roles_root}"
        assert roles_root.is_dir(), f"Roles path is not a directory: {roles_root}"

    def test_all_role_directories_exist(
        self, role_paths: Dict[str, Path], all_role_names: List[str]
    ) -> None:
        """Test that all expected role directories exist."""
        for role_name in all_role_names:
            role_path = role_paths[role_name]
            assert role_path.exists(), f"Role directory missing: {role_name}"
            assert role_path.is_dir(), f"Role path is not a directory: {role_name}"

    def test_all_roles_have_tasks_directory(
        self, role_paths: Dict[str, Path], all_role_names: List[str]
    ) -> None:
        """Test that all roles have a tasks directory."""
        for role_name in all_role_names:
            tasks_dir = role_paths[role_name] / "tasks"
            assert tasks_dir.exists(), f"Tasks directory missing for role: {role_name}"
            assert tasks_dir.is_dir(), f"Tasks path is not a directory for role: {role_name}"

    def test_all_roles_have_main_task_file(
        self, role_paths: Dict[str, Path], all_role_names: List[str]
    ) -> None:
        """Test that all roles have a main.yml task file."""
        for role_name in all_role_names:
            main_task = role_paths[role_name] / "tasks" / "main.yml"
            assert main_task.exists(), f"Main task file missing for role: {role_name}"

    def test_roles_with_defaults(self, role_paths: Dict[str, Path]) -> None:
        """Test that roles with defaults have defaults/main.yml."""
        roles_with_defaults = ["backup", "usb_storage"]
        for role_name in roles_with_defaults:
            defaults_file = role_paths[role_name] / "defaults" / "main.yml"
            assert defaults_file.exists(), f"Defaults file missing for role: {role_name}"


@pytest.mark.unit
class TestRoleTaskSyntax:
    """Tests for role task file YAML syntax."""

    def test_all_task_files_valid_yaml(
        self, role_paths: Dict[str, Path], all_role_names: List[str]
    ) -> None:
        """Test that all task files are valid YAML."""
        for role_name in all_role_names:
            tasks_dir = role_paths[role_name] / "tasks"
            for task_file in tasks_dir.glob("*.yml"):
                with open(task_file, "r") as f:
                    try:
                        yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        pytest.fail(f"Invalid YAML in {role_name}/{task_file.name}: {e}")

    def test_task_files_are_lists(
        self, role_paths: Dict[str, Path], all_role_names: List[str]
    ) -> None:
        """Test that task files contain lists of tasks."""
        for role_name in all_role_names:
            tasks_dir = role_paths[role_name] / "tasks"
            for task_file in tasks_dir.glob("*.yml"):
                with open(task_file, "r") as f:
                    content = yaml.safe_load(f)
                    assert isinstance(
                        content, list
                    ), f"Task file {role_name}/{task_file.name} should contain a list"

    def test_tasks_have_names(self, role_paths: Dict[str, Path], all_role_names: List[str]) -> None:
        """Test that all tasks have name fields."""
        for role_name in all_role_names:
            tasks_dir = role_paths[role_name] / "tasks"
            for task_file in tasks_dir.glob("*.yml"):
                with open(task_file, "r") as f:
                    tasks = yaml.safe_load(f)
                    for i, task in enumerate(tasks):
                        assert (
                            "name" in task
                        ), f"Task {i + 1} in {role_name}/{task_file.name} missing 'name'"


@pytest.mark.unit
class TestSSHTransitionRole:
    """Tests specific to ssh_transition role."""

    def test_ssh_transition_subtask_files_exist(
        self, role_paths: Dict[str, Path], ssh_transition_subtasks: List[str]
    ) -> None:
        """Test that all ssh_transition subtask files exist."""
        tasks_dir = role_paths["ssh_transition"] / "tasks"
        for subtask in ssh_transition_subtasks:
            subtask_file = tasks_dir / subtask
            assert subtask_file.exists(), f"SSH transition subtask missing: {subtask}"

    def test_ssh_transition_main_includes_all_subtasks(
        self, role_paths: Dict[str, Path], ssh_transition_subtasks: List[str]
    ) -> None:
        """Test that main.yml includes all subtask files."""
        main_task = role_paths["ssh_transition"] / "tasks" / "main.yml"
        with open(main_task, "r") as f:
            content = f.read()

        for subtask in ssh_transition_subtasks:
            assert subtask in content, f"SSH transition main.yml missing include for: {subtask}"

    def test_ssh_transition_uses_fqcn(self, role_paths: Dict[str, Path]) -> None:
        """Test that ssh_transition role uses FQCN for modules."""
        tasks_dir = role_paths["ssh_transition"] / "tasks"
        for task_file in tasks_dir.glob("*.yml"):
            with open(task_file, "r") as f:
                tasks = yaml.safe_load(f)
                for task in tasks:
                    # Check that raw, debug, etc. use ansible.builtin prefix
                    task_keys = set(task.keys()) - {
                        "name",
                        "register",
                        "changed_when",
                        "failed_when",
                        "when",
                        "tags",
                        "retries",
                        "delay",
                        "until",
                        "ignore_errors",
                        "ignore_unreachable",
                        "delegate_to",
                        "run_once",
                        "listen",
                    }
                    for key in task_keys:
                        if key in [
                            "raw",
                            "debug",
                            "set_fact",
                            "meta",
                            "pause",
                            "include_tasks",
                            "wait_for",
                        ]:
                            pytest.fail(
                                f"Non-FQCN module '{key}' in {task_file.name}: "
                                f"use ansible.builtin.{key}"
                            )


@pytest.mark.unit
class TestUSBStorageRole:
    """Tests specific to usb_storage role."""

    def test_usb_storage_subtask_files_exist(
        self, role_paths: Dict[str, Path], usb_storage_subtasks: List[str]
    ) -> None:
        """Test that all usb_storage subtask files exist."""
        tasks_dir = role_paths["usb_storage"] / "tasks"
        for subtask in usb_storage_subtasks:
            subtask_file = tasks_dir / subtask
            assert subtask_file.exists(), f"USB storage subtask missing: {subtask}"

    def test_usb_storage_main_includes_all_subtasks(
        self, role_paths: Dict[str, Path], usb_storage_subtasks: List[str]
    ) -> None:
        """Test that main.yml includes all subtask files."""
        main_task = role_paths["usb_storage"] / "tasks" / "main.yml"
        with open(main_task, "r") as f:
            content = f.read()

        for subtask in usb_storage_subtasks:
            assert subtask in content, f"USB storage main.yml missing include for: {subtask}"

    def test_usb_storage_has_defaults(self, role_paths: Dict[str, Path]) -> None:
        """Test that usb_storage role has default variables."""
        defaults_file = role_paths["usb_storage"] / "defaults" / "main.yml"
        assert defaults_file.exists(), "USB storage defaults file missing"

        with open(defaults_file, "r") as f:
            defaults = yaml.safe_load(f)

        expected_defaults = [
            "usb_mount_point",
            "usb_filesystem",
            "usb_mount_options",
        ]
        for default_var in expected_defaults:
            assert default_var in defaults, f"USB storage missing default var: {default_var}"


@pytest.mark.unit
class TestRoleTemplates:
    """Tests for role templates."""

    def test_roles_with_templates_have_template_directory(
        self, role_paths: Dict[str, Path], roles_with_templates: Dict[str, str]
    ) -> None:
        """Test that roles with templates have templates directory."""
        for role_name in roles_with_templates:
            templates_dir = role_paths[role_name] / "templates"
            assert templates_dir.exists(), f"Templates directory missing for role: {role_name}"

    def test_expected_templates_exist(
        self, role_paths: Dict[str, Path], roles_with_templates: Dict[str, str]
    ) -> None:
        """Test that expected template files exist in roles."""
        for role_name, template_name in roles_with_templates.items():
            template_file = role_paths[role_name] / "templates" / template_name
            assert (
                template_file.exists()
            ), f"Template missing: {role_name}/templates/{template_name}"

    def test_templates_valid_jinja2_syntax(
        self, role_paths: Dict[str, Path], roles_with_templates: Dict[str, str]
    ) -> None:
        """Test that all templates have valid Jinja2 syntax."""
        env = Environment()

        for role_name, template_name in roles_with_templates.items():
            template_file = role_paths[role_name] / "templates" / template_name
            with open(template_file, "r") as f:
                template_content = f.read()
                try:
                    env.parse(template_content)
                except TemplateSyntaxError as e:
                    pytest.fail(f"Jinja2 syntax error in {role_name}/{template_name}: {e}")


@pytest.mark.unit
class TestBackupRole:
    """Tests specific to backup role."""

    def test_backup_has_defaults(self, role_paths: Dict[str, Path]) -> None:
        """Test that backup role has default variables."""
        defaults_file = role_paths["backup"] / "defaults" / "main.yml"
        assert defaults_file.exists(), "Backup defaults file missing"

        with open(defaults_file, "r") as f:
            defaults = yaml.safe_load(f)

        assert "backup_config_backup_dir" in defaults, "Backup missing config_backup_dir default"

    def test_backup_creates_backup_directory(self, role_paths: Dict[str, Path]) -> None:
        """Test that backup role creates backup directory."""
        main_task = role_paths["backup"] / "tasks" / "main.yml"
        with open(main_task, "r") as f:
            content = f.read()

        # Using ansible.builtin.file with state: directory instead of mkdir
        assert (
            "state: directory" in content or "mkdir" in content
        ), "Backup role should create backup directory"


@pytest.mark.unit
class TestPackageManagementRole:
    """Tests specific to package_management role."""

    def test_package_management_updates_opkg(self, role_paths: Dict[str, Path]) -> None:
        """Test that package_management role runs opkg update."""
        main_task = role_paths["package_management"] / "tasks" / "main.yml"
        with open(main_task, "r") as f:
            content = f.read()

        assert "opkg update" in content, "Package management should run opkg update"

    def test_package_management_installs_packages(self, role_paths: Dict[str, Path]) -> None:
        """Test that package_management role installs packages."""
        main_task = role_paths["package_management"] / "tasks" / "main.yml"
        with open(main_task, "r") as f:
            content = f.read()

        assert "opkg install" in content, "Package management should install packages"


@pytest.mark.unit
class TestSystemConfigRole:
    """Tests specific to system_config role."""

    def test_system_config_sets_hostname(self, role_paths: Dict[str, Path]) -> None:
        """Test that system_config role sets hostname."""
        main_task = role_paths["system_config"] / "tasks" / "main.yml"
        with open(main_task, "r") as f:
            content = f.read()

        assert "hostname" in content.lower(), "System config should set hostname"

    def test_system_config_sets_timezone(self, role_paths: Dict[str, Path]) -> None:
        """Test that system_config role sets timezone."""
        main_task = role_paths["system_config"] / "tasks" / "main.yml"
        with open(main_task, "r") as f:
            content = f.read()

        assert "timezone" in content.lower(), "System config should set timezone"


@pytest.mark.unit
class TestNetworkConfigRole:
    """Tests specific to network_config role."""

    def test_network_config_has_template(self, role_paths: Dict[str, Path]) -> None:
        """Test that network_config role has network.j2 template."""
        template_file = role_paths["network_config"] / "templates" / "network.j2"
        assert template_file.exists(), "Network config missing network.j2 template"

    def test_network_config_deploys_template(self, role_paths: Dict[str, Path]) -> None:
        """Test that network_config role deploys template."""
        main_task = role_paths["network_config"] / "tasks" / "main.yml"
        with open(main_task, "r") as f:
            content = f.read()

        assert "network.j2" in content, "Network config should deploy network.j2 template"
        assert (
            "/etc/config/network" in content
        ), "Network config should deploy to /etc/config/network"


@pytest.mark.unit
class TestWirelessConfigRole:
    """Tests specific to wireless_config role."""

    def test_wireless_config_has_template(self, role_paths: Dict[str, Path]) -> None:
        """Test that wireless_config role has wireless.j2 template."""
        template_file = role_paths["wireless_config"] / "templates" / "wireless.j2"
        assert template_file.exists(), "Wireless config missing wireless.j2 template"

    def test_wireless_config_deploys_template(self, role_paths: Dict[str, Path]) -> None:
        """Test that wireless_config role deploys template."""
        main_task = role_paths["wireless_config"] / "tasks" / "main.yml"
        with open(main_task, "r") as f:
            content = f.read()

        assert "wireless.j2" in content, "Wireless config should deploy wireless.j2 template"
        assert (
            "/etc/config/wireless" in content
        ), "Wireless config should deploy to /etc/config/wireless"


@pytest.mark.unit
class TestDHCPConfigRole:
    """Tests specific to dhcp_config role."""

    def test_dhcp_config_has_template(self, role_paths: Dict[str, Path]) -> None:
        """Test that dhcp_config role has dhcp.j2 template."""
        template_file = role_paths["dhcp_config"] / "templates" / "dhcp.j2"
        assert template_file.exists(), "DHCP config missing dhcp.j2 template"

    def test_dhcp_config_deploys_template(self, role_paths: Dict[str, Path]) -> None:
        """Test that dhcp_config role deploys template."""
        main_task = role_paths["dhcp_config"] / "tasks" / "main.yml"
        with open(main_task, "r") as f:
            content = f.read()

        assert "dhcp.j2" in content, "DHCP config should deploy dhcp.j2 template"
        assert "/etc/config/dhcp" in content, "DHCP config should deploy to /etc/config/dhcp"


@pytest.mark.unit
class TestFirewallConfigRole:
    """Tests specific to firewall_config role."""

    def test_firewall_config_has_template(self, role_paths: Dict[str, Path]) -> None:
        """Test that firewall_config role has firewall.j2 template."""
        template_file = role_paths["firewall_config"] / "templates" / "firewall.j2"
        assert template_file.exists(), "Firewall config missing firewall.j2 template"

    def test_firewall_config_deploys_template(self, role_paths: Dict[str, Path]) -> None:
        """Test that firewall_config role deploys template."""
        main_task = role_paths["firewall_config"] / "tasks" / "main.yml"
        with open(main_task, "r") as f:
            content = f.read()

        assert "firewall.j2" in content, "Firewall config should deploy firewall.j2 template"
        assert (
            "/etc/config/firewall" in content
        ), "Firewall config should deploy to /etc/config/firewall"


@pytest.mark.unit
class TestRoleDefaults:
    """Tests for role default variables."""

    def test_defaults_are_valid_yaml(self, role_paths: Dict[str, Path]) -> None:
        """Test that all defaults files are valid YAML."""
        for role_name, role_path in role_paths.items():
            defaults_dir = role_path / "defaults"
            if defaults_dir.exists():
                for defaults_file in defaults_dir.glob("*.yml"):
                    with open(defaults_file, "r") as f:
                        try:
                            yaml.safe_load(f)
                        except yaml.YAMLError as e:
                            pytest.fail(
                                f"Invalid YAML in {role_name}/defaults/{defaults_file.name}: {e}"
                            )

    def test_defaults_are_dictionaries(self, role_paths: Dict[str, Path]) -> None:
        """Test that defaults files contain dictionaries (or are documentation-only)."""
        for role_name, role_path in role_paths.items():
            defaults_dir = role_path / "defaults"
            if defaults_dir.exists():
                for defaults_file in defaults_dir.glob("*.yml"):
                    with open(defaults_file, "r") as f:
                        content = yaml.safe_load(f)
                        # Defaults can be None if file is documentation-only (comments)
                        # or a dict with actual variables
                        assert content is None or isinstance(
                            content, dict
                        ), f"Defaults in {role_name}/{defaults_file.name} should be a dict or empty"
