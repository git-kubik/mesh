#!/usr/bin/env python3
"""Process package list from node snapshot for Image Builder.

Reads installed package list from snapshot and filters out:
- Base system packages (included automatically by Image Builder)
- Kernel modules (handled by Image Builder, version-specific)
- Build artifacts

Outputs a clean package list suitable for the Image Builder PACKAGES variable.

Usage:
    python3 process-packages.py --snapshot /snapshots/mesh-node3
"""

import argparse
import sys
from pathlib import Path

# Packages automatically included by Image Builder (don't need to specify)
# These are part of the base system image
BASE_PACKAGES = {
    "base-files",
    "busybox",
    "ca-bundle",
    "dnsmasq",
    "dropbear",
    "firewall4",
    "fstools",
    "fwtool",
    "getrandom",
    "jsonfilter",
    "kernel",
    "libc",
    "libgcc",
    "libgcc1",
    "libpthread",
    "librt",
    "libubox",
    "libubus",
    "libuclient",
    "mtd",
    "netifd",
    "nftables",
    "odhcp6c",
    "odhcpd-ipv6only",
    "openwrt-keyring",
    "opkg",
    "ppp",
    "ppp-mod-pppoe",
    "procd",
    "procd-seccomp",
    "procd-ujail",
    "ubox",
    "ubus",
    "ubusd",
    "uci",
    "uclient-fetch",
    "urandom-seed",
    "urngd",
    # Profile-specific defaults for dlink_dir-1960-a1
    "wpad-basic-mbedtls",
    "libustream-mbedtls",
    "logd",
}

# Packages to explicitly exclude (conflicts or not needed in image)
EXCLUDE_PACKAGES = {
    # Build/temp packages
    "pkgtemp",
    # vnstat v1 conflicts with vnstat2 - we use vnstat2 with luci-app-vnstat2
    "vnstat",
    "vnstati",
}

# Packages to explicitly REMOVE from the default image (prefixed with -)
# These are included by default in OpenWrt but we don't want them
REMOVE_FROM_DEFAULTS = [
    "-dropbear",  # We use OpenSSH instead
]

# Packages to always include even if not in snapshot
# These are essential for the mesh network deployment
ALWAYS_INCLUDE = [
    "vnstat2",  # Bandwidth tracking (v2, replaces vnstat v1)
    "vnstati2",  # Graph generation for vnstat2
    "luci-app-vnstat2",  # Web UI for vnStat bandwidth graphs
]

# Packages that need special handling (replace default packages)
# Map from package name to list of packages to remove (prefixed with -)
PACKAGE_REPLACES = {
    # wpad-mesh-mbedtls replaces wpad-basic-mbedtls
    "wpad-mesh-mbedtls": ["-wpad-basic-mbedtls"],
}

# Kernel module prefixes - these are version-specific and handled by Image Builder
KMOD_PATTERNS = [
    "kmod-",
]

# Library ABI version patterns - these are dependencies, not installable packages
# Examples: libubox20240329, libubus20250102, libuci20250120
LIB_ABI_PATTERNS = [
    "libubox2",
    "libubus2",
    "libuci2",
    "libblobmsg-json2",
    "libjson-script2",
    "libuclient2",
    "libustream-mbedtls2",
    "libiwinfo2",
    "libucode2",
]


def load_package_list(snapshot_path: Path) -> list[str]:
    """Load installed packages from snapshot."""
    packages_file = snapshot_path / "packages" / "installed.txt"
    if not packages_file.exists():
        raise FileNotFoundError(f"Package list not found: {packages_file}")

    packages = []
    for line in packages_file.read_text().splitlines():
        package = line.strip()
        if package:
            packages.append(package)

    return packages


def is_kernel_module(package: str) -> bool:
    """Check if package is a kernel module."""
    for pattern in KMOD_PATTERNS:
        if package.startswith(pattern):
            return True
    return False


def is_lib_abi_version(package: str) -> bool:
    """Check if package is a library ABI version (not directly installable)."""
    for pattern in LIB_ABI_PATTERNS:
        if package.startswith(pattern):
            return True
    return False


def filter_packages(packages: list[str], include_kmods: bool = False) -> list[str]:
    """
    Filter package list for Image Builder.

    Args:
        packages: List of package names
        include_kmods: If True, include kernel modules (for full rebuild)

    Returns:
        Filtered list of packages
    """
    filtered = []
    removals = list(REMOVE_FROM_DEFAULTS)  # Start with packages to remove from defaults

    for package in packages:
        # Skip base packages (auto-included)
        if package in BASE_PACKAGES:
            continue

        # Skip explicitly excluded packages
        if package in EXCLUDE_PACKAGES:
            continue

        # Handle kernel modules
        if is_kernel_module(package):
            if not include_kmods:
                continue

        # Skip library ABI versions (dependencies handled automatically)
        if is_lib_abi_version(package):
            continue

        # Check if this package replaces a default package
        if package in PACKAGE_REPLACES:
            removals.extend(PACKAGE_REPLACES[package])

        filtered.append(package)

    # Add always-include packages if not already present
    for pkg in ALWAYS_INCLUDE:
        if pkg not in filtered:
            filtered.append(pkg)

    # Add removal packages at the beginning
    return removals + sorted(filtered)


def format_packages(packages: list[str], one_per_line: bool = False) -> str:
    """Format package list for output."""
    if one_per_line:
        return "\n".join(packages)
    else:
        return " ".join(packages)


def main() -> None:
    """Process packages from snapshot for Image Builder."""
    parser = argparse.ArgumentParser(
        description="Process package list from node snapshot for Image Builder"
    )
    parser.add_argument(
        "--snapshot",
        required=True,
        type=Path,
        help="Path to snapshot directory",
    )
    parser.add_argument(
        "--include-kmods",
        action="store_true",
        help="Include kernel modules (not recommended)",
    )
    parser.add_argument(
        "--one-per-line",
        action="store_true",
        help="Output one package per line",
    )
    parser.add_argument(
        "--count",
        action="store_true",
        help="Show package count instead of list",
    )

    args = parser.parse_args()

    try:
        packages = load_package_list(args.snapshot)
        filtered = filter_packages(packages, include_kmods=args.include_kmods)

        if args.count:
            print(
                f"Original: {len(packages)}, Filtered: {len(filtered)}",
                file=sys.stderr,
            )
            print(len(filtered))
        else:
            output = format_packages(filtered, one_per_line=args.one_per_line)
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
