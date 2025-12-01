#!/usr/bin/env python3
"""Generate UCI defaults script from node snapshot.

Converts UCI export to a shell script that applies configuration on first boot.
Handles node-specific substitutions for IP addresses, hostnames, and DHCP pools.

Usage:
    python3 generate-uci-defaults.py --snapshot /snapshots/mesh-node3 \
                                     --node node3 \
                                     --output /tmp/overlay/etc/uci-defaults/99-mesh-config
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# Node-specific configuration
NODE_CONFIG = {
    "node1": {
        "hostname": "mesh-node1",
        "lan_ip": "10.11.12.1",
        "batman_ip": "10.11.12.1",
        "mgmt_ip": "10.11.10.1",
        "guest_ip": "10.11.30.1",
        "dhcp_start": 100,
        "gw_mode": "server",
    },
    "node2": {
        "hostname": "mesh-node2",
        "lan_ip": "10.11.12.2",
        "batman_ip": "10.11.12.2",
        "mgmt_ip": "10.11.10.2",
        "guest_ip": "10.11.30.2",
        "dhcp_start": 150,
        "gw_mode": "client",
    },
    "node3": {
        "hostname": "mesh-node3",
        "lan_ip": "10.11.12.3",
        "batman_ip": "10.11.12.3",
        "mgmt_ip": "10.11.10.3",
        "guest_ip": "10.11.30.3",
        "dhcp_start": 200,
        "gw_mode": "server",  # node3 also gateway
    },
}


def parse_uci_export(uci_text: str) -> dict:  # type: ignore[type-arg] # noqa: C901
    """
    Parse UCI export format into structured data.

    Returns dict of packages, each containing list of config sections.
    """
    packages: dict[str, list] = {}  # type: ignore[type-arg]
    current_package = None
    current_config = None

    for line in uci_text.splitlines():
        line = line.rstrip()

        # Skip empty lines
        if not line:
            continue

        # Package declaration
        if line.startswith("package "):
            current_package = line.split()[1]
            packages[current_package] = []
            current_config = None

        # Config section start
        elif line.startswith("config "):
            parts = line.split()
            config_type = parts[1]
            config_name = parts[2].strip("'") if len(parts) > 2 else None
            current_config = {
                "type": config_type,
                "name": config_name,
                "options": [],
                "lists": [],
            }
            if current_package:
                packages[current_package].append(current_config)

        # Option
        elif line.startswith("\toption "):
            if current_config:
                match = re.match(r"\toption (\S+) '([^']*)'", line)
                if match:
                    current_config["options"].append((match.group(1), match.group(2)))

        # List item
        elif line.startswith("\tlist "):
            if current_config:
                match = re.match(r"\tlist (\S+) '([^']*)'", line)
                if match:
                    current_config["lists"].append((match.group(1), match.group(2)))

    return packages


def generate_uci_commands(packages: dict, node_config: dict) -> list:  # type: ignore[type-arg]
    """
    Generate UCI set/add_list commands from parsed packages.

    Applies node-specific substitutions.
    """
    commands = []

    # Counters for anonymous sections per package.type
    anon_counters = {}

    for package_name, configs in packages.items():
        for config in configs:
            config_type = config["type"]
            config_name = config["name"]

            # Build UCI path
            if config_name:
                # Named section
                path = f"{package_name}.{config_name}"
            else:
                # Anonymous section - use @type[n] notation
                key = f"{package_name}.{config_type}"
                if key not in anon_counters:
                    anon_counters[key] = 0
                path = f"{package_name}.@{config_type}[{anon_counters[key]}]"
                anon_counters[key] += 1

            # Add options
            for opt_name, opt_value in config["options"]:
                # Apply node-specific substitutions
                value = apply_substitutions(
                    package_name, config_name, opt_name, opt_value, node_config
                )
                commands.append(f"uci set {path}.{opt_name}='{value}'")

            # Add list items
            for list_name, list_value in config["lists"]:
                value = apply_substitutions(
                    package_name, config_name, list_name, list_value, node_config
                )
                commands.append(f"uci add_list {path}.{list_name}='{value}'")

    return commands


def apply_substitutions(
    package: str, config: str, opt: str, value: str, node_config: dict  # type: ignore[type-arg]
) -> str:
    """Apply node-specific substitutions to values."""
    # Hostname substitution
    if package == "system" and opt == "hostname":
        return str(node_config["hostname"])

    # LAN IP substitution
    if package == "network" and config == "lan" and opt == "ipaddr":
        return str(node_config["lan_ip"])

    # Management IP substitution
    if package == "network" and config == "management_bridge" and opt == "ipaddr":
        return str(node_config["mgmt_ip"])

    # Guest IP substitution
    if package == "network" and config == "guest_bridge" and opt == "ipaddr":
        return str(node_config["guest_ip"])

    # Batman gateway mode
    if package == "network" and config == "bat0" and opt == "gw_mode":
        return str(node_config["gw_mode"])

    # DHCP start substitution
    if package == "dhcp" and config == "lan" and opt == "start":
        return str(node_config["dhcp_start"])

    return value


def generate_script(snapshot_path: Path, node: str, source_hostname: str) -> str:
    """Generate complete UCI defaults script."""
    node_config = NODE_CONFIG.get(node)
    if not node_config:
        raise ValueError(f"Unknown node: {node}")

    uci_file = snapshot_path / "config" / "uci_export.txt"
    if not uci_file.exists():
        raise FileNotFoundError(f"UCI export not found: {uci_file}")

    uci_text = uci_file.read_text()
    packages = parse_uci_export(uci_text)

    # Skip certain packages that shouldn't be in defaults
    skip_packages = {
        "luci-opkg",  # Duplicate of luci
        "rpcd",  # System-managed
    }

    for skip in skip_packages:
        packages.pop(skip, None)

    commands = generate_uci_commands(packages, node_config)

    # Generate script
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    script = f"""#!/bin/sh
# /etc/uci-defaults/99-mesh-config
# Auto-generated UCI configuration for OpenWrt mesh node
#
# Source: {source_hostname} snapshot
# Target: {node_config['hostname']}
# Generated: {timestamp}
#
# This script runs on first boot to apply mesh configuration.
# It will be deleted after successful execution.

# Wait for UCI to be ready
sleep 2

# Apply configuration
"""

    # Group commands by package for readability
    current_package = None
    for cmd in commands:
        # Extract package name from command
        match = re.match(r"uci (?:set|add_list) (\w+)\.", cmd)
        if match:
            package = match.group(1)
            if package != current_package:
                script += f"\n# {package}\n"
                current_package = package
        script += f"{cmd}\n"

    script += """
# Commit all changes
uci commit

# Success - script will be deleted
exit 0
"""

    return script


def main() -> None:
    """Generate UCI defaults script from command line arguments."""
    parser = argparse.ArgumentParser(description="Generate UCI defaults script from node snapshot")
    parser.add_argument(
        "--snapshot",
        required=True,
        type=Path,
        help="Path to snapshot directory",
    )
    parser.add_argument(
        "--node",
        required=True,
        choices=["node1", "node2", "node3"],
        help="Target node name",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: stdout)",
    )

    args = parser.parse_args()

    # Determine source hostname from snapshot path
    source_hostname = args.snapshot.name

    try:
        script = generate_script(args.snapshot, args.node, source_hostname)

        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(script)
            args.output.chmod(0o755)
            print(f"Generated: {args.output}", file=sys.stderr)
        else:
            print(script)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
