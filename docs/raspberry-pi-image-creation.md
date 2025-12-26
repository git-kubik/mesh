# Raspberry Pi Image Creation Guide

This guide covers methods for creating custom Raspberry Pi images and cloning running systems.

## Table of Contents

- [Overview](#overview)
- [Method 1: rpi-image-gen (Official - Recommended)](#method-1-rpi-image-gen-official---recommended)
- [Method 2: pi-gen (Classic Official)](#method-2-pi-gen-classic-official)
- [Method 3: sdm (Simple Disk Manager)](#method-3-sdm-simple-disk-manager)
- [Cloning a Live Running Pi](#cloning-a-live-running-pi)
- [Tool Comparison](#tool-comparison)

---

## Overview

There are two main approaches to Raspberry Pi image management:

1. **Building custom images from scratch** - For reproducible deployments
2. **Cloning running systems** - For backup and duplication

---

## Method 1: rpi-image-gen (Official - Recommended)

**rpi-image-gen** is Raspberry Pi's newest official tool (released March 2025) for creating highly customized OS images. It's designed for embedded systems, industrial applications, and reproducible deployments.

- **Repository**: <https://github.com/raspberrypi/rpi-image-gen>
- **Documentation**: <https://raspberrypi.github.io/rpi-image-gen/>

### Key Features

| Feature | Description |
|---------|-------------|
| Fast builds | Uses pre-built packages, not source compilation |
| Declarative | YAML-based configuration |
| Layer system | Modular, composable components |
| No root required | Runs as regular user via `podman unshare` |
| SBOM generation | Software Bill of Materials for compliance |
| CVE reports | Security vulnerability tracking |
| Secure boot | Integrates with rpi-sb-provisioner |

### Quick Start

```bash
# Clone the repository
git clone https://github.com/raspberrypi/rpi-image-gen.git
cd rpi-image-gen

# Install dependencies
sudo ./install_deps.sh

# Build a minimal Bookworm image
./rpi-image-gen build -c ./config/bookworm-minbase.yaml

# Output: ./work/image-deb12-arm64-min/deb12-arm64-min.img
```

### Flash the Image

```bash
# Using rpi-imager CLI
sudo rpi-imager --cli ./work/image-deb12-arm64-min/deb12-arm64-min.img /dev/sdX

# Or use Raspberry Pi Imager GUI with "Use Custom" option
```

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                  rpi-image-gen                       │
├─────────────────────────────────────────────────────┤
│  Configuration (YAML/INI)                           │
│         ↓                                           │
│  Layer System (modular components)                  │
│         ↓                                           │
│  bdebstrap → mmdebstrap (filesystem construction)   │
│         ↓                                           │
│  genimage (disk image creation)                     │
│         ↓                                           │
│  Bootable .img file                                 │
└─────────────────────────────────────────────────────┘
```

**Underlying tools:**

- **bdebstrap** - Modular layer application
- **mmdebstrap** - Filesystem construction
- **genimage** - Disk image creation
- **podman unshare** - Namespace-based permissions

### Configuration System

#### Basic YAML Config

```yaml
# my-custom-image.yaml
include:
  file: bookworm-minbase.yaml

device:
  class: pi5
  storage_type: sd
  hostname: my-custom-pi

image:
  compression: zstd
  boot_part_size: 200%
  root_part_size: 300%
```

#### Variable Naming Convention

```bash
IGconf_<section>_<key>

# Examples:
IGconf_device_class=pi5
IGconf_device_hostname=kiosk-01
IGconf_image_compression=zstd
```

#### Command Line Overrides

```bash
./rpi-image-gen build -c config.yaml -- \
  IGconf_device_class=pi5 \
  IGconf_device_hostname=production-node
```

### Supported Device Classes

| Class | Device |
|-------|--------|
| `pi5` | Raspberry Pi 5 |
| `pi4` | Raspberry Pi 4 |
| `cm5` | Compute Module 5 |
| `cm4` | Compute Module 4 |
| `pi02w` | Pi Zero 2 W |

### Included Examples

| Example | Description |
|---------|-------------|
| `slim/` | Lightweight minimal images |
| `webkiosk/` | Chromium-based kiosk mode |
| `custom_layers/` | Creating your own layers |
| `custom_kernel/` | Custom kernel builds |
| `splash-screen/` | Boot splash customization |
| `container_chroot/` | Container-based builds |
| `debstore/` | Local package repository |

### Common Commands

```bash
# Build an image
./rpi-image-gen build -c config/my-system.yaml

# Build with custom source directory
./rpi-image-gen build -S /path/to/assets -c /path/to/config.yaml

# List all available layers
./rpi-image-gen layer --list

# Describe a specific layer
./rpi-image-gen layer --describe rpi5

# Validate/lint a custom layer
./rpi-image-gen metadata --lint /path/to/my/layer.yaml

# Generate config template
./rpi-image-gen config --gen

# Migrate INI to YAML
./rpi-image-gen config legacy.cfg --migrate > modern.yaml
```

### Directory Structure

```
rpi-image-gen/
├── bin/           # Executables and utilities
├── config/        # Built-in configurations
├── device/        # Device-specific assets
├── docs/          # Technical documentation
├── examples/      # Example configurations
├── image/         # Disk layout assets
├── keydir/        # Cryptographic assets
├── layer/         # Layer library
├── layer-hooks/   # Common layer hooks
├── lib/           # Execution helpers
├── package/       # Build recipes
├── scripts/       # Functional hooks
└── test/          # Test harness
```

### Requirements

- **Host OS**: Raspberry Pi OS or Debian Bookworm/Trixie (arm64)
- **Can run on x86_64** via QEMU emulation (not officially supported)
- Dependencies installed via `./install_deps.sh`

### Custom Configurations

We maintain custom configs and layers in the rpi-image-gen repository:

**Location**: `~/rpi-image-gen/config/custom/` and `~/rpi-image-gen/layer/custom/`

| Config | Target | Description |
|--------|--------|-------------|
| `rpi4-server.yaml` | Pi 4 | Docker server + auto-expand rootfs |
| `rpi4-builder.yaml` | Pi 4 | Native arm64 build server |
| `rpi5-builder.yaml` | Pi 5 | Native arm64 build server |

**Custom Layers**:

| Layer | Description |
|-------|-------------|
| `docker-expand` | Docker CE + auto-expand filesystem on first boot |
| `rpi-image-gen-builder` | All dependencies for native builds + USB storage support |

**Native Build Workflow** (5-10x faster than QEMU):

1. Build the builder image on x86_64
2. Write to SD card, boot on Pi with USB storage attached
3. Clone rpi-image-gen, link work directory to USB
4. Build images natively, write to second SD card

See `~/rpi-image-gen/config/custom/README.md` for detailed instructions.

---

## Method 2: pi-gen (Classic Official)

**pi-gen** is the tool used to build official Raspberry Pi OS images. Use this when you need to modify the standard distribution build process.

- **Repository**: <https://github.com/RPi-Distro/pi-gen>

### Quick Start

```bash
git clone https://github.com/RPi-Distro/pi-gen.git
cd pi-gen

# Configure
cp config-example config

# Edit config file
cat > config << EOF
IMG_NAME=my-custom-image
DEPLOY_ZIP=1
LOCALE_DEFAULT=en_US.UTF-8
TARGET_HOSTNAME=my-pi
KEYBOARD_KEYMAP=us
TIMEZONE_DEFAULT=America/New_York
FIRST_USER_NAME=pi
FIRST_USER_PASS=raspberry
ENABLE_SSH=1
EOF

# Build (requires root)
sudo ./build.sh
```

### Stage System

pi-gen uses a stage-based build system:

| Stage | Description |
|-------|-------------|
| Stage 0 | Bootstrap - minimal filesystem |
| Stage 1 | Core system - essential packages |
| Stage 2 | Lite image - base Raspberry Pi OS Lite |
| Stage 3 | Desktop prerequisites |
| Stage 4 | Full desktop with applications |
| Stage 5 | Development tools and extras |

### Customization

Add packages in stage files:

```bash
# stage2/01-sys-tweaks/00-packages
vim
htop
curl
```

Add custom scripts:

```bash
# stage2/02-custom/00-run.sh
#!/bin/bash -e
echo "Custom setup running..."
```

---

## Method 3: sdm (Simple Disk Manager)

**sdm** is a community tool that simplifies image customization without the complexity of pi-gen.

- **Repository**: <https://github.com/gitbls/sdm>

### Installation

```bash
sudo curl -L https://raw.githubusercontent.com/gitbls/sdm/master/EZsdmInstaller | bash
```

### Usage

```bash
# Download base image first
wget https://downloads.raspberrypi.org/raspios_lite_arm64/images/.../raspios.img.xz
xz -d raspios.img.xz

# Customize the image
sudo sdm --customize raspios.img \
  --plugin user:adduser=myuser \
  --plugin apps:install="vim htop curl git" \
  --plugin network:wificountry=US \
  --plugin L10n:host

# Burn to SD card
sudo sdm --burn /dev/sdX --hostname mypi raspios.img
```

### Plugin System

| Plugin | Purpose |
|--------|---------|
| `user` | Add users, set passwords |
| `apps` | Install packages |
| `network` | WiFi, hostname, static IP |
| `L10n` | Locale, timezone, keyboard |
| `copyfile` | Copy files into image |
| `runscript` | Run custom scripts |

---

## Cloning a Live Running Pi

### Method A: SD Card Copier (Built-in GUI)

On Raspberry Pi OS Desktop:

1. Insert USB SD card reader with destination card
2. Open **Accessories → SD Card Copier**
3. Select source and destination
4. Click **Start**

### Method B: rpi-clone (Recommended CLI)

```bash
# Install
git clone https://github.com/billw2/rpi-clone
cd rpi-clone
sudo cp rpi-clone /usr/local/sbin

# Clone to USB drive (e.g., sda)
sudo rpi-clone sda

# Clone with options
sudo rpi-clone sda -f  # Force, no confirmations
```

### Method C: dd (Traditional)

From another Linux machine with SD card inserted:

```bash
# Create image
sudo dd if=/dev/sdX of=raspberry-backup.img bs=4M status=progress

# Compressed backup
sudo dd if=/dev/sdX bs=4M status=progress | gzip > backup.img.gz

# Restore
sudo dd if=backup.img of=/dev/sdX bs=4M status=progress
```

### Method D: Hot-clone + PiShrink

Clone while running and shrink to actual size:

```bash
# Create image of running system (to external storage)
sudo dd if=/dev/mmcblk0 of=/mnt/external/backup.img bs=4M status=progress

# Install PiShrink
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
chmod +x pishrink.sh

# Shrink to actual used size
sudo ./pishrink.sh backup.img backup-shrunk.img
```

### Method E: Win32 Disk Imager (Windows)

1. Insert SD card via USB reader
2. Open Win32 Disk Imager
3. Select destination file path (`.img`)
4. Click **Read** to create backup
5. Click **Write** to restore

---

## Tool Comparison

### Image Building Tools

| Tool | Use Case | Complexity | Speed |
|------|----------|------------|-------|
| **rpi-image-gen** | Custom embedded/industrial | Medium | Fast |
| **pi-gen** | Modify official build | High | Slow |
| **sdm** | Quick customization | Low | Fast |

### Cloning Tools

| Tool | Platform | Use Case |
|------|----------|----------|
| SD Card Copier | Raspberry Pi | Quick GUI clone |
| rpi-clone | Raspberry Pi | CLI clone while running |
| dd | Any Linux | Full bit-for-bit backup |
| PiShrink | Linux | Shrink images to used size |
| Win32 Disk Imager | Windows | Windows backup/restore |

### Decision Guide

```
Need custom image from scratch?
├── Yes → Need SBOM/CVE compliance?
│         ├── Yes → rpi-image-gen
│         └── No → What complexity?
│                  ├── Low → sdm
│                  └── High → pi-gen
└── No → Need backup/clone?
         ├── GUI → SD Card Copier
         ├── CLI on Pi → rpi-clone
         ├── External Linux → dd + pishrink
         └── Windows → Win32 Disk Imager
```

---

## References

- [rpi-image-gen GitHub](https://github.com/raspberrypi/rpi-image-gen)
- [rpi-image-gen Documentation](https://raspberrypi.github.io/rpi-image-gen/)
- [pi-gen GitHub](https://github.com/RPi-Distro/pi-gen)
- [sdm GitHub](https://github.com/gitbls/sdm)
- [rpi-clone GitHub](https://github.com/billw2/rpi-clone)
- [PiShrink GitHub](https://github.com/Drewsif/PiShrink)
- [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
