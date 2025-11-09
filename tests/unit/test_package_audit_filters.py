#!/usr/bin/env python3
"""
Unit tests for package_audit Ansible filter plugin.

Tests the package comparison and command generation logic.
"""

import sys
from pathlib import Path

import pytest

# Add filter_plugins to path
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "openwrt-mesh-ansible" / "filter_plugins")
)

from package_audit import FilterModule  # noqa: E402


class TestParseOpkgList:
    """Test parse_opkg_list filter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.filter_module = FilterModule()
        self.filters = self.filter_module.filters()

    def test_parse_single_package(self):
        """Test parsing single package."""
        opkg_output = "batctl - 2023.0-3"
        result = self.filters["parse_opkg_list"](opkg_output)

        assert len(result) == 1
        assert result[0]["name"] == "batctl"
        assert result[0]["version"] == "2023.0-3"

    def test_parse_multiple_packages(self):
        """Test parsing multiple packages."""
        opkg_output = """batctl - 2023.0-3
kmod-batman-adv - 5.15.150+2023.0-1
ip-full - 6.7.0-1"""
        result = self.filters["parse_opkg_list"](opkg_output)

        assert len(result) == 3
        assert result[0]["name"] == "batctl"
        assert result[1]["name"] == "kmod-batman-adv"
        assert result[2]["name"] == "ip-full"

    def test_parse_empty_output(self):
        """Test parsing empty output."""
        opkg_output = ""
        result = self.filters["parse_opkg_list"](opkg_output)

        assert len(result) == 0

    def test_parse_output_with_empty_lines(self):
        """Test parsing output with empty lines."""
        opkg_output = """batctl - 2023.0-3

kmod-batman-adv - 5.15.150+2023.0-1

"""
        result = self.filters["parse_opkg_list"](opkg_output)

        assert len(result) == 2
        assert result[0]["name"] == "batctl"
        assert result[1]["name"] == "kmod-batman-adv"


class TestComparePackages:
    """Test compare_packages filter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.filter_module = FilterModule()
        self.filters = self.filter_module.filters()

        # Sample installed packages
        self.installed = [
            {"name": "base-files", "version": "1509-r24106"},
            {"name": "ip-full", "version": "6.7.0-1"},
            {"name": "tcpdump-mini", "version": "4.99.4-1"},
            {"name": "wpad-basic-mbedtls", "version": "2023.09.25-1"},
            {"name": "iperf3", "version": "3.15-1"},
        ]

        # Sample requirements
        self.required = [
            "kmod-batman-adv",
            "batctl",
            "wpad-mesh-mbedtls",
            "ip-full",
            "tcpdump-mini",
        ]

        self.remove = [
            "wpad-basic-mbedtls",
            "wpad-basic-wolfssl",
        ]

        self.optional = [
            "iperf3",
            "ethtool",
            "nano",
        ]

    def test_missing_required_packages(self):
        """Test detection of missing required packages."""
        result = self.filters["compare_packages"](
            self.installed, self.required, self.remove, self.optional
        )

        assert "kmod-batman-adv" in result["missing_required"]
        assert "batctl" in result["missing_required"]
        assert "wpad-mesh-mbedtls" in result["missing_required"]
        assert len(result["missing_required"]) == 3

    def test_conflicting_packages(self):
        """Test detection of conflicting packages."""
        result = self.filters["compare_packages"](
            self.installed, self.required, self.remove, self.optional
        )

        assert "wpad-basic-mbedtls" in result["conflicting"]
        assert len(result["conflicting"]) == 1

    def test_installed_required_packages(self):
        """Test detection of already installed required packages."""
        result = self.filters["compare_packages"](
            self.installed, self.required, self.remove, self.optional
        )

        assert "ip-full" in result["installed_required"]
        assert "tcpdump-mini" in result["installed_required"]
        assert len(result["installed_required"]) == 2

    def test_installed_optional_packages(self):
        """Test detection of installed optional packages."""
        result = self.filters["compare_packages"](
            self.installed, self.required, self.remove, self.optional
        )

        assert "iperf3" in result["installed_optional"]
        assert len(result["installed_optional"]) == 1

    def test_audit_status_has_conflicts(self):
        """Test audit status when conflicts exist."""
        result = self.filters["compare_packages"](
            self.installed, self.required, self.remove, self.optional
        )

        assert result["audit_status"] == "has_conflicts"

    def test_audit_status_needs_packages(self):
        """Test audit status when packages are missing."""
        # Remove conflicting package
        installed_no_conflicts = [
            pkg for pkg in self.installed if pkg["name"] != "wpad-basic-mbedtls"
        ]

        result = self.filters["compare_packages"](
            installed_no_conflicts, self.required, self.remove, self.optional
        )

        assert result["audit_status"] == "needs_packages"

    def test_audit_status_ready(self):
        """Test audit status when node is ready."""
        # Create installed list with all required packages and no conflicts
        installed_ready = [
            {"name": "kmod-batman-adv", "version": "5.15.150+2023.0-1"},
            {"name": "batctl", "version": "2023.0-3"},
            {"name": "wpad-mesh-mbedtls", "version": "2023.09.25-1"},
            {"name": "ip-full", "version": "6.7.0-1"},
            {"name": "tcpdump-mini", "version": "4.99.4-1"},
        ]

        result = self.filters["compare_packages"](
            installed_ready, self.required, self.remove, self.optional
        )

        assert result["audit_status"] == "ready"
        assert len(result["missing_required"]) == 0
        assert len(result["conflicting"]) == 0

    def test_summary_counts(self):
        """Test summary statistics."""
        result = self.filters["compare_packages"](
            self.installed, self.required, self.remove, self.optional
        )

        assert result["summary"]["total_installed"] == len(self.installed)
        assert result["summary"]["required_count"] == len(self.required)
        assert result["summary"]["missing_count"] == 3
        assert result["summary"]["conflict_count"] == 1
        assert result["summary"]["installed_required_count"] == 2
        assert result["summary"]["installed_optional_count"] == 1

    def test_extra_packages(self):
        """Test detection of extra packages."""
        result = self.filters["compare_packages"](
            self.installed, self.required, self.remove, self.optional
        )

        assert "base-files" in result["extra_packages"]


class TestGenerateInstallCommands:
    """Test generate_install_commands filter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.filter_module = FilterModule()
        self.filters = self.filter_module.filters()

    def test_generate_with_update(self):
        """Test command generation with opkg update."""
        packages = ["kmod-batman-adv", "batctl", "wpad-mesh-mbedtls"]
        result = self.filters["generate_install_commands"](packages, opkg_update=True)

        assert len(result) == 2
        assert result[0] == "opkg update"
        assert result[1] == "opkg install kmod-batman-adv batctl wpad-mesh-mbedtls"

    def test_generate_without_update(self):
        """Test command generation without opkg update."""
        packages = ["kmod-batman-adv", "batctl"]
        result = self.filters["generate_install_commands"](packages, opkg_update=False)

        assert len(result) == 1
        assert result[0] == "opkg install kmod-batman-adv batctl"

    def test_generate_empty_list(self):
        """Test command generation with empty package list."""
        packages: list[str] = []
        result = self.filters["generate_install_commands"](packages)

        assert len(result) == 1
        assert result[0] == "opkg update"

    def test_generate_single_package(self):
        """Test command generation with single package."""
        packages = ["batctl"]
        result = self.filters["generate_install_commands"](packages)

        assert len(result) == 2
        assert result[1] == "opkg install batctl"


class TestGenerateRemoveCommands:
    """Test generate_remove_commands filter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.filter_module = FilterModule()
        self.filters = self.filter_module.filters()

    def test_generate_multiple_packages(self):
        """Test command generation for multiple packages."""
        packages = ["wpad-basic-mbedtls", "wpad-basic-wolfssl"]
        result = self.filters["generate_remove_commands"](packages)

        assert len(result) == 2
        assert result[0] == "opkg remove wpad-basic-mbedtls"
        assert result[1] == "opkg remove wpad-basic-wolfssl"

    def test_generate_single_package(self):
        """Test command generation for single package."""
        packages = ["wpad-basic-mbedtls"]
        result = self.filters["generate_remove_commands"](packages)

        assert len(result) == 1
        assert result[0] == "opkg remove wpad-basic-mbedtls"

    def test_generate_empty_list(self):
        """Test command generation with empty package list."""
        packages: list[str] = []
        result = self.filters["generate_remove_commands"](packages)

        assert len(result) == 0


class TestFilterModuleIntegration:
    """Integration tests for the filter module."""

    def setup_method(self):
        """Set up test fixtures."""
        self.filter_module = FilterModule()

    def test_filters_registration(self):
        """Test that all filters are registered."""
        filters = self.filter_module.filters()

        assert "parse_opkg_list" in filters
        assert "compare_packages" in filters
        assert "generate_install_commands" in filters
        assert "generate_remove_commands" in filters

    def test_complete_workflow(self):
        """Test complete audit workflow."""
        filters = self.filter_module.filters()

        # Step 1: Parse opkg output
        opkg_output = """base-files - 1509-r24106
ip-full - 6.7.0-1
wpad-basic-mbedtls - 2023.09.25-1"""

        installed = filters["parse_opkg_list"](opkg_output)
        assert len(installed) == 3

        # Step 2: Compare packages
        required = ["kmod-batman-adv", "batctl", "ip-full"]
        remove = ["wpad-basic-mbedtls"]
        optional = ["iperf3"]

        audit = filters["compare_packages"](installed, required, remove, optional)

        assert audit["audit_status"] == "has_conflicts"
        assert len(audit["missing_required"]) == 2
        assert len(audit["conflicting"]) == 1

        # Step 3: Generate commands
        install_cmds = filters["generate_install_commands"](audit["missing_required"])
        remove_cmds = filters["generate_remove_commands"](audit["conflicting"])

        assert len(install_cmds) == 2
        assert len(remove_cmds) == 1
        assert "kmod-batman-adv" in install_cmds[1] and "batctl" in install_cmds[1]
        assert "wpad-basic-mbedtls" in remove_cmds[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
