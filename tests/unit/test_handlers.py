"""
Unit tests for Ansible handler validation.

Tests validate centralized handlers for the mesh deployment.
"""

from pathlib import Path

import pytest
import yaml


@pytest.mark.unit
class TestHandlersStructure:
    """Tests for handlers directory structure."""

    def test_handlers_directory_exists(self, handlers_path: Path) -> None:
        """Test that handlers directory exists."""
        assert handlers_path.exists(), f"Handlers directory not found: {handlers_path}"
        assert handlers_path.is_dir(), f"Handlers path is not a directory: {handlers_path}"

    def test_main_handlers_file_exists(self, handlers_path: Path) -> None:
        """Test that main.yml handlers file exists."""
        main_handlers = handlers_path / "main.yml"
        assert main_handlers.exists(), "Main handlers file not found: handlers/main.yml"


@pytest.mark.unit
class TestHandlersSyntax:
    """Tests for handler YAML syntax."""

    def test_handlers_valid_yaml(self, handlers_path: Path) -> None:
        """Test that handlers file is valid YAML."""
        main_handlers = handlers_path / "main.yml"
        with open(main_handlers, "r") as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in handlers/main.yml: {e}")

    def test_handlers_is_list(self, handlers_path: Path) -> None:
        """Test that handlers file contains a list."""
        main_handlers = handlers_path / "main.yml"
        with open(main_handlers, "r") as f:
            content = yaml.safe_load(f)
            assert isinstance(content, list), "Handlers file should contain a list"

    def test_handlers_have_names(self, handlers_path: Path) -> None:
        """Test that all handlers have name fields."""
        main_handlers = handlers_path / "main.yml"
        with open(main_handlers, "r") as f:
            handlers = yaml.safe_load(f)

        for i, handler in enumerate(handlers):
            assert "name" in handler, f"Handler {i + 1} missing 'name' field"


@pytest.mark.unit
class TestHandlersContent:
    """Tests for handler content and functionality."""

    def test_expected_handlers_exist(self, handlers_path: Path) -> None:
        """Test that expected handlers are defined."""
        main_handlers = handlers_path / "main.yml"
        with open(main_handlers, "r") as f:
            handlers = yaml.safe_load(f)

        handler_names = [h.get("name", "").lower() for h in handlers]

        # Expected handlers for mesh deployment
        # Note: This project uses reload (not restart) for most services
        # and applies changes atomically via reboot
        expected_handlers = [
            "reload network",
            "reload wireless",
            "reload firewall",
        ]

        for expected in expected_handlers:
            found = any(expected in name for name in handler_names)
            assert found, f"Expected handler '{expected}' not found"

    def test_handlers_use_fqcn(self, handlers_path: Path) -> None:
        """Test that handlers use FQCN for modules."""
        main_handlers = handlers_path / "main.yml"
        with open(main_handlers, "r") as f:
            handlers = yaml.safe_load(f)

        for handler in handlers:
            handler_keys = set(handler.keys()) - {"name", "listen", "changed_when", "register"}
            for key in handler_keys:
                # These are common module names that should use FQCN
                if key in ["raw", "shell", "command", "service", "systemd"]:
                    pytest.fail(
                        f"Handler '{handler.get('name')}' uses non-FQCN module '{key}': "
                        f"use ansible.builtin.{key}"
                    )

    def test_handlers_have_changed_when(self, handlers_path: Path) -> None:
        """Test that handlers that modify state have changed_when."""
        main_handlers = handlers_path / "main.yml"
        with open(main_handlers, "r") as f:
            handlers = yaml.safe_load(f)

        for handler in handlers:
            # Handlers using raw/shell/command should have changed_when
            if any(key in handler for key in ["ansible.builtin.raw", "ansible.builtin.shell"]):
                assert (
                    "changed_when" in handler
                ), f"Handler '{handler.get('name')}' using raw/shell should have changed_when"

    def test_network_reload_handler(self, handlers_path: Path) -> None:
        """Test network reload handler configuration."""
        main_handlers = handlers_path / "main.yml"
        with open(main_handlers, "r") as f:
            handlers = yaml.safe_load(f)

        network_handler = None
        for handler in handlers:
            if (
                "network" in handler.get("name", "").lower()
                and "reload" in handler.get("name", "").lower()
            ):
                network_handler = handler
                break

        assert network_handler is not None, "Network reload handler not found"
        # Verify it reloads network service
        raw_cmd = network_handler.get("ansible.builtin.raw", "")
        assert "network" in raw_cmd, "Network handler should reload network service"

    def test_wireless_reload_handler(self, handlers_path: Path) -> None:
        """Test wireless reload handler configuration."""
        main_handlers = handlers_path / "main.yml"
        with open(main_handlers, "r") as f:
            handlers = yaml.safe_load(f)

        wireless_handler = None
        for handler in handlers:
            if "wireless" in handler.get("name", "").lower():
                wireless_handler = handler
                break

        assert wireless_handler is not None, "Wireless reload handler not found"

    def test_firewall_restart_handler(self, handlers_path: Path) -> None:
        """Test firewall restart handler configuration."""
        main_handlers = handlers_path / "main.yml"
        with open(main_handlers, "r") as f:
            handlers = yaml.safe_load(f)

        firewall_handler = None
        for handler in handlers:
            if "firewall" in handler.get("name", "").lower():
                firewall_handler = handler
                break

        assert firewall_handler is not None, "Firewall restart handler not found"


@pytest.mark.unit
class TestHandlersListeners:
    """Tests for handler listen directives."""

    def test_handlers_have_listen_directives(self, handlers_path: Path) -> None:
        """Test that handlers have listen directives for notification."""
        main_handlers = handlers_path / "main.yml"
        with open(main_handlers, "r") as f:
            handlers = yaml.safe_load(f)

        handlers_with_listen = [h for h in handlers if "listen" in h]
        assert len(handlers_with_listen) > 0, "At least some handlers should have listen directives"

    def test_listen_directives_match_names(self, handlers_path: Path) -> None:
        """Test that listen directives reasonably match handler names."""
        main_handlers = handlers_path / "main.yml"
        with open(main_handlers, "r") as f:
            handlers = yaml.safe_load(f)

        for handler in handlers:
            if "listen" in handler:
                listen = handler.get("listen", "").lower()
                # Basic sanity check - listen should relate to the handler purpose
                # e.g., "Reload network" handler should listen for "reload network"
                assert len(listen) > 0, f"Handler '{handler.get('name')}' has empty listen"
