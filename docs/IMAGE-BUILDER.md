# OpenWrt Custom Image Builder

Build custom OpenWrt firmware images with all packages and configuration baked in for instant deployment.

## Overview

The Image Builder creates custom sysupgrade images from node snapshots, allowing you to:

- Flash a fresh router to exact mesh configuration in minutes
- Replace failed hardware without reconfiguration
- Create pre-configured images for new nodes
- Build offline (uses local package repository)

## Prerequisites

1. **Docker** - Image Builder runs in a container
2. **Node Snapshot** - Run `make snapshot NODE=N` first
3. **Local Package Repository** - Run `make repo-setup` first

## Quick Start

```bash
# 1. Create snapshot of running node
make snapshot NODE=3

# 2. Build custom image from snapshot
make image-build NODE=3

# 3. Flash the image to router
# Via web UI: System > Backup/Flash > Flash new firmware
# Or via SSH: sysupgrade -v /tmp/mesh-node3-sysupgrade.bin
```

## Commands

| Command | Description |
|---------|-------------|
| `make image-build NODE=N` | Build image for node N |
| `make image-build-all` | Build images for all nodes with snapshots |
| `make image-info` | Show Image Builder profiles |
| `make image-shell` | Enter builder container shell |
| `make image-clean` | Remove built images |

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Build Container                        │
│                                                                  │
│  1. Read snapshot from /snapshots/mesh-nodeN/                   │
│  2. Use overlay/ directory directly (full filesystem copy)      │
│  3. Extract package list (filter base packages/kmods)           │
│  4. Run OpenWrt Image Builder with:                             │
│     - Profile: dlink_dir-1960-a1                                │
│     - Packages: from snapshot (122+ packages)                   │
│     - FILES: overlay/ directory (complete filesystem)           │
│  5. Output: images/mesh-nodeN-sysupgrade.bin                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Output Structure

```
images/
├── mesh-node1-sysupgrade.bin     # Custom image for node 1
├── mesh-node1-sysupgrade.bin.sha256
├── mesh-node2-sysupgrade.bin     # Custom image for node 2
├── mesh-node2-sysupgrade.bin.sha256
└── mesh-node3-sysupgrade.bin     # Custom image for node 3
    └── mesh-node3-sysupgrade.bin.sha256
```

## What's Included in the Image

Each custom image contains the **complete overlay filesystem** from the running node - everything that differs from factory default OpenWrt:

### From Snapshot (`overlay/` directory)

| Directory | Contents |
|-----------|----------|
| `/etc/config/` | All UCI configuration (network, wireless, firewall, etc.) |
| `/etc/ssh/` | SSH keys, authorized_keys, sshd_config |
| `/etc/shadow` | Root password hash |
| `/etc/passwd`, `/etc/group` | User accounts |
| `/etc/crontabs/` | Scheduled tasks |
| `/etc/dropbear/` | Dropbear keys (if used) |
| `/root/` | Root home directory contents |
| Any other customizations | Scripts, configs, data files |

### Installed Packages

All packages from the running node, minus base system packages and kernel modules (which are version-specific and included automatically by Image Builder).

## Node-Specific Configuration

Each image has these values baked in:

| Setting | Node 1 | Node 2 | Node 3 |
|---------|--------|--------|--------|
| Hostname | mesh-node1 | mesh-node2 | mesh-node3 |
| LAN IP | 10.11.12.1 | 10.11.12.2 | 10.11.12.3 |
| DHCP Pool Start | 100 | 150 | 200 |
| Gateway Mode | server | client | server |

## Flashing the Image

### Via LuCI Web Interface

1. Upload image to router: `scp images/mesh-node3-sysupgrade.bin root@10.11.12.3:/tmp/`
2. Open router web UI: `http://10.11.12.3`
3. Go to: System > Backup/Flash Firmware
4. Click "Flash new firmware image"
5. Select `/tmp/mesh-node3-sysupgrade.bin`
6. Uncheck "Keep settings" (configuration is in the image)
7. Click "Continue" then "Proceed"

### Via SSH (Headless)

```bash
# Upload image
scp images/mesh-node3-sysupgrade.bin root@10.11.12.3:/tmp/

# Verify checksum
ssh root@10.11.12.3 "sha256sum /tmp/mesh-node3-sysupgrade.bin"
cat images/mesh-node3-sysupgrade.bin.sha256

# Flash (router will reboot)
ssh root@10.11.12.3 "sysupgrade -n /tmp/mesh-node3-sysupgrade.bin"
```

**Note:** `-n` flag discards current settings. The image contains all configuration.

### Via TFTP Recovery

If router is bricked, use TFTP recovery:

1. Download TFTP server (e.g., tftpd-hpa)
2. Rename image to `factory.bin` or device-specific name
3. Set PC to 192.168.0.1
4. Hold reset button while powering on router
5. Router will download and flash via TFTP

## Troubleshooting

### Build Fails: "Package not found"

The local repository may be incomplete:

```bash
# Re-sync repository
make repo-setup

# Check specific package
ls openwrt-repo/packages/mipsel_24kc/*/batctl*
```

### Build Fails: "Snapshot not found"

Create a snapshot first:

```bash
make snapshot NODE=3
ls snapshots/mesh-node3/
```

### Image Too Large

The D-Link DIR-1960 has 16MB flash. Default images are ~7-8MB. If you've added many packages:

```bash
# Check image size
ls -lh images/mesh-node3-sysupgrade.bin

# Review package list
python3 scripts/process-packages.py --snapshot snapshots/mesh-node3 --one-per-line | wc -l
```

### Router Doesn't Apply Configuration

Check if UCI defaults script ran:

```bash
# After flashing, check if script was deleted (means it ran)
ssh root@10.11.12.3 "ls /etc/uci-defaults/"

# If 99-mesh-config still exists, run it manually
ssh root@10.11.12.3 "/etc/uci-defaults/99-mesh-config"
```

### Wrong Node Configuration

If you flash node3 image on node1 hardware:

```bash
# Check current hostname
ssh root@192.168.1.1 "uci get system.@system[0].hostname"

# Fix by re-deploying with Ansible
make deploy-node NODE=1
```

## Advanced Usage

### Dry Run (Preview Build)

```bash
cd docker/imagebuilder
docker compose run --rm imagebuilder /scripts/build-image.sh node3 --dry-run
```

### Custom Package List

Edit `scripts/process-packages.py` to modify BASE_PACKAGES or EXCLUDE_PACKAGES sets.

### Debug Container

```bash
make image-shell
# Inside container:
make info  # Show all profiles
make image PROFILE=dlink_dir-1960-a1 PACKAGES="batctl-full" FILES=/tmp/test
```

### Use Official Repository

Edit `docker/imagebuilder/repositories.conf` to use official OpenWrt repos instead of local.

## Architecture Details

- **Target:** ramips/mt7621
- **Profile:** dlink_dir-1960-a1
- **Architecture:** mipsel_24kc
- **OpenWrt Version:** 24.10.4
- **Image Builder:** Pre-compiled packages (no kernel compilation)

## Why Image Builder vs Full Buildroot?

| Feature | Image Builder | Full Buildroot |
|---------|---------------|----------------|
| Build time | 2-5 minutes | 2-4 hours |
| Disk space | ~500MB | ~15GB |
| Kernel | Pre-compiled | Compiled |
| Package compatibility | Official repos | Custom vermagic |
| Complexity | Low | High |

Image Builder uses official pre-compiled packages, ensuring compatibility with the official opkg repositories.
