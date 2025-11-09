#!/usr/bin/env python3
"""
Ansible filter plugin for OpenWrt package auditing and comparison.

This plugin provides filters for comparing installed packages against
required packages defined in group_vars.
"""

from typing import Any, Dict, List, Optional


class FilterModule:
    """Ansible filter plugin for package auditing."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters."""
        return {
            "parse_opkg_list": self.parse_opkg_list,
            "compare_packages": self.compare_packages,
            "generate_install_commands": self.generate_install_commands,
            "generate_remove_commands": self.generate_remove_commands,
        }

    @staticmethod
    def parse_opkg_list(opkg_output: str) -> List[Dict[str, str]]:
        """
        Parse 'opkg list-installed' output into structured data.

        Args:
            opkg_output: Raw output from 'opkg list-installed' command

        Returns:
            List of dicts with 'name' and 'version' keys

        Example input:
            batctl - 2023.0-3
            kmod-batman-adv - 5.15.150+2023.0-1

        Example output:
            [
                {'name': 'batctl', 'version': '2023.0-3'},
                {'name': 'kmod-batman-adv', 'version': '5.15.150+2023.0-1'}
            ]
        """
        packages = []
        for line in opkg_output.strip().split("\n"):
            if not line.strip():
                continue

            parts = line.split(" - ", 1)
            if len(parts) == 2:
                packages.append({"name": parts[0].strip(), "version": parts[1].strip()})

        return packages

    @staticmethod
    def compare_packages(
        installed: List[Dict[str, str]],
        required: List[str],
        remove: Optional[List[str]] = None,
        optional: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compare installed packages against requirements.

        Args:
            installed: List of installed packages from parse_opkg_list()
            required: List of required package names
            remove: List of packages that should be removed (conflicts)
            optional: List of optional package names

        Returns:
            Dict containing:
                - missing_required: Packages that need to be installed
                - conflicting: Packages that need to be removed
                - installed_required: Required packages already installed
                - installed_optional: Optional packages already installed
                - extra_packages: Installed packages not in any list
                - audit_status: 'ready', 'needs_packages', or 'has_conflicts'
        """
        remove = remove or []
        optional = optional or []

        # Convert installed to set of names for fast lookup
        installed_names = {pkg["name"] for pkg in installed}

        # Find missing required packages
        missing_required = [pkg for pkg in required if pkg not in installed_names]

        # Find conflicting packages
        conflicting = [pkg for pkg in remove if pkg in installed_names]

        # Find installed required packages
        installed_required = [pkg for pkg in required if pkg in installed_names]

        # Find installed optional packages
        installed_optional = [pkg for pkg in optional if pkg in installed_names]

        # Find extra packages (not required, optional, or to be removed)
        all_known_packages = set(required) | set(optional) | set(remove)
        extra_packages = [pkg for pkg in installed_names if pkg not in all_known_packages]

        # Determine audit status
        if conflicting:
            audit_status = "has_conflicts"
        elif missing_required:
            audit_status = "needs_packages"
        else:
            audit_status = "ready"

        return {
            "missing_required": sorted(missing_required),
            "conflicting": sorted(conflicting),
            "installed_required": sorted(installed_required),
            "installed_optional": sorted(installed_optional),
            "extra_packages": sorted(extra_packages),
            "audit_status": audit_status,
            "summary": {
                "total_installed": len(installed),
                "required_count": len(required),
                "missing_count": len(missing_required),
                "conflict_count": len(conflicting),
                "installed_required_count": len(installed_required),
                "installed_optional_count": len(installed_optional),
            },
        }

    @staticmethod
    def generate_install_commands(packages: List[str], opkg_update: bool = True) -> List[str]:
        """
        Generate opkg install commands for missing packages.

        Args:
            packages: List of package names to install
            opkg_update: Whether to include 'opkg update' first

        Returns:
            List of shell commands
        """
        commands = []

        if opkg_update:
            commands.append("opkg update")

        if packages:
            # Install all packages in one command for efficiency
            commands.append(f"opkg install {' '.join(packages)}")

        return commands

    @staticmethod
    def generate_remove_commands(packages: List[str]) -> List[str]:
        """
        Generate opkg remove commands for conflicting packages.

        Args:
            packages: List of package names to remove

        Returns:
            List of shell commands
        """
        commands = []

        if packages:
            # Remove packages one by one to handle dependencies properly
            for pkg in packages:
                commands.append(f"opkg remove {pkg}")

        return commands
