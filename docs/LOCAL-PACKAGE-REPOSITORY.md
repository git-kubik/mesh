# Local OpenWrt Package Repository Guide

This guide explains how to set up and use a local OpenWrt package repository for faster deployments and offline capability.

## Overview

A local package repository provides several benefits:

- **Faster Deployments**: Packages download from local network (100+ Mbps) instead of internet
- **Offline Capability**: Deploy nodes without internet access
- **Bandwidth Savings**: Download each package once, use many times
- **Consistent Versions**: All nodes get identical package versions
- **Reduced Load**: Less strain on OpenWrt official mirrors

### Architecture

```
┌─────────────────┐
│  Control PC     │
│                 │
│  HTTP Server    │◄─────┐
│  Port 8080      │      │
│                 │      │
│  openwrt-repo/  │      │
│  ├── packages/  │      │  opkg install
│  └── targets/   │      │  (via local repo)
└─────────────────┘      │
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐      ┌────▼────┐     ┌────▼────┐
   │ Node 1  │      │ Node 2  │     │ Node 3  │
   │ opkg    │      │ opkg    │     │ opkg    │
   └─────────┘      └─────────┘     └─────────┘
```

## Prerequisites

- **Disk Space**: ~500 MB - 2 GB (depending on how many packages you cache)
- **Python 3**: For running the HTTP server
- **wget**: For downloading packages (usually pre-installed)
- **Internet**: Initial setup requires internet to download packages

## Quick Start

### 1. Setup Local Repository

Download all required packages and firmware images:

```bash
cd openwrt-mesh-ansible
./scripts/setup-local-repo.sh
```

This will:

- Create `openwrt-repo/` directory structure
- Download package indexes for all feeds
- Download all packages listed in REQUIRED_PACKAGES and OPTIONAL_PACKAGES
- Download monitoring packages (collectd, vnstat)
- Download firmware images for D-Link DIR-1960 A1
- Display repository statistics

**Expected output:**

```
========================================
OpenWrt Local Repository Setup
========================================

Version: 24.10.4
Target: ramips/mt7621
Architecture: mipsel_24kc
Repository: /path/to/openwrt-repo

Creating repository directories...
Downloading package indexes...
  Downloading base index...
  Downloading luci index...
  Downloading packages index...
  Downloading routing index...
  Downloading telephony index...

Downloading required packages...
    python3 (base)
    batctl-full (packages)
    kmod-batman-adv (base)
    ...

Downloading monitoring packages...
    collectd (packages)
    collectd-mod-cpu (packages)
    ...

Downloading firmware images...
    Downloaded: openwrt-24.10.4-ramips-mt7621-dlink_dir-1960-a1-squashfs-sysupgrade.bin
    Downloaded: openwrt-24.10.4-ramips-mt7621-dlink_dir-1960-a1-squashfs-factory.bin

========================================
Repository setup complete!
========================================

Location: /path/to/openwrt-repo
Total size: 450M
Packages cached: 85
Images cached: 2
```

### 2. Start HTTP Server

Start the local repository server:

```bash
./scripts/start-local-repo.sh
```

**Expected output:**

```
========================================
OpenWrt Local Repository Server
========================================

Repository: /path/to/openwrt-repo
Listening on: http://192.168.1.100:8080

Configure nodes with:
  OPKG_REPO_URL=http://192.168.1.100:8080

Press Ctrl+C to stop the server
```

**Keep this terminal open** - the server needs to stay running during deployment.

### 3. Configure Environment

Edit `.env` file and set the repository URL:

```bash
# Edit .env
OPKG_REPO_URL=http://192.168.1.100:8080

# Enable package upgrades (recommended)
UPGRADE_INSTALLED_PACKAGES=yes
```

Replace `192.168.1.100` with your control PC's IP address shown by the server.

**Note:** `UPGRADE_INSTALLED_PACKAGES=yes` ensures all installed packages are upgraded to the repository versions during deployment. This maintains version consistency across all nodes.

### 4. Deploy Nodes

Deploy nodes normally - they will now use the local repository:

```bash
make deploy-node NODE=1
make deploy-node NODE=2
make deploy-node NODE=3
```

You should see much faster package downloads (MB/s instead of KB/s).

## Usage

### Starting the Server

The server must be running whenever you deploy or update nodes:

```bash
# Start server (foreground)
./scripts/start-local-repo.sh

# Or run in background
./scripts/start-local-repo.sh &

# Or use screen/tmux
screen -S openwrt-repo
./scripts/start-local-repo.sh
# Press Ctrl+A, D to detach
```

### Stopping the Server

```bash
# If running in foreground
Press Ctrl+C

# If running in background
pkill -f "python3 -m http.server.*8080"
```

### Updating the Cache

To update packages when a new OpenWrt version is released:

```bash
# Update scripts/setup-local-repo.sh with new version
# Edit line: OPENWRT_VERSION="24.10.4"

# Re-run setup to download new packages
./scripts/setup-local-repo.sh
```

### Adding More Packages

To add additional packages to the cache:

1. Edit `.env` and add packages to `REQUIRED_PACKAGES` or `OPTIONAL_PACKAGES`
2. Re-run setup script:

   ```bash
   ./scripts/setup-local-repo.sh
   ```

### Package Upgrades

The deployment automatically upgrades installed packages to match repository versions:

```bash
# Enable upgrades (default)
UPGRADE_INSTALLED_PACKAGES=yes

# Disable upgrades (faster but may have version mismatches)
UPGRADE_INSTALLED_PACKAGES=no
```

**What happens during upgrade:**

1. Deployment runs `opkg list-upgradable` to check for updates
2. Shows list of packages that can be upgraded
3. Extracts package names from the upgradable list
4. Runs `opkg upgrade <package1> <package2> ...` to update all packages
5. Ensures version consistency across all nodes

**Example output:**

```
Checking for package upgrades...

=== Upgradable Packages ===
base-files - 1604-r25380 - 1604-r25400
busybox - 1.36.1-6 - 1.36.1-7
dropbear - 2024.85-2 - 2024.85-3

Found 3 packages that can be upgraded

=== Upgrading Packages ===
Upgrading base-files on root from 1604-r25380 to 1604-r25400...
Upgrading busybox on root from 1.36.1-6 to 1.36.1-7...
Upgrading dropbear on root from 2024.85-2 to 2024.85-3...

=== Upgrade Complete ===
```

**When to disable upgrades:**

- First deployment (no packages installed yet)
- Testing specific package versions
- Troubleshooting upgrade issues

**Recommendation:** Keep enabled to maintain consistent package versions.

### Switching Back to Official Repositories

To disable local repository and use official OpenWrt mirrors:

```bash
# Edit .env
OPKG_REPO_URL=

# Deploy nodes (will restore official repos)
make deploy
```

## Directory Structure

```
openwrt-repo/
├── packages/
│   └── 24.10.4/
│       └── mipsel_24kc/
│           ├── base/
│           │   ├── Packages
│           │   ├── Packages.gz
│           │   ├── Packages.sig
│           │   └── *.ipk (package files)
│           ├── luci/
│           │   └── *.ipk
│           ├── packages/
│           │   └── *.ipk
│           ├── routing/
│           │   └── *.ipk
│           └── telephony/
│               └── *.ipk
└── targets/
    └── ramips/
        └── mt7621/
            ├── sha256sums
            ├── sha256sums.sig
            ├── *-sysupgrade.bin (upgrade image)
            └── *-factory.bin (factory image)
```

## Package Feeds

The repository mirrors these OpenWrt feeds:

| Feed | Description | Example Packages |
|------|-------------|------------------|
| **base** | Core system packages | kernel modules, drivers, basic utilities |
| **luci** | Web interface | luci, luci-apps, themes |
| **packages** | Additional software | collectd, vnstat, monitoring tools |
| **routing** | Routing protocols | batman-adv, olsrd, babel |
| **telephony** | VoIP packages | asterisk, linphone |

## Troubleshooting

### Server Won't Start - Port In Use

```
Error: Port 8080 already in use
```

**Solution**: The script automatically finds next available port. Check output for actual port:

```
Listening on: http://192.168.1.100:8081
```

### Nodes Can't Reach Repository

**Symptoms**: Package installation fails with "Cannot download packages"

**Check**:

1. Server is running:

   ```bash
   curl http://192.168.1.100:8080
   # Should show directory listing
   ```

2. Nodes can reach server:

   ```bash
   ssh root@10.11.12.1
   wget -O- http://192.168.1.100:8080
   ```

3. Firewall allows port 8080:

   ```bash
   sudo ufw allow 8080
   # or
   sudo firewall-cmd --add-port=8080/tcp
   ```

### Package Not Found

**Symptoms**: `opkg install package_name` fails with "Package not found"

**Solution**:

1. Check package is in REQUIRED_PACKAGES or OPTIONAL_PACKAGES in .env
2. Re-run setup script:

   ```bash
   ./scripts/setup-local-repo.sh
   ```

3. Verify package was downloaded:

   ```bash
   find openwrt-repo -name "*package_name*.ipk"
   ```

### Wrong Architecture

**Symptoms**: "Incompatible architecture" errors

**Solution**: Verify target and architecture in `scripts/setup-local-repo.sh`:

```bash
TARGET="ramips/mt7621"      # Should match your hardware
ARCH="mipsel_24kc"          # Should match your hardware
```

Check your hardware:

```bash
ssh root@10.11.12.1 'cat /etc/openwrt_release'
```

### Disk Space Full

**Symptoms**: "No space left on device"

**Check repository size**:

```bash
du -sh openwrt-repo
```

**Solutions**:

1. Remove old versions:

   ```bash
   rm -rf openwrt-repo/packages/OLD_VERSION/
   ```

2. Remove unused feeds:

   ```bash
   rm -rf openwrt-repo/packages/*/mipsel_24kc/telephony/
   ```

3. Keep only required packages (manual cleanup)

## Performance Comparison

### Without Local Repository

```
Deploying to node1...
Installing python3... (downloading from downloads.openwrt.org)
  Speed: 500 KB/s
  Time: 4 seconds

Installing batctl-full... (downloading)
  Speed: 300 KB/s
  Time: 2 seconds

Total package download time: ~60 seconds
Total deployment time: ~5 minutes
```

### With Local Repository

```
Deploying to node1...
Installing python3... (from local repo)
  Speed: 50 MB/s
  Time: 0.1 seconds

Installing batctl-full... (from local repo)
  Speed: 80 MB/s
  Time: 0.05 seconds

Total package download time: ~2 seconds
Total deployment time: ~2 minutes
```

**Improvement**: ~3 minutes faster deployment, 30x faster package downloads!

## Advanced Configuration

### Using Different Port

Edit `scripts/start-local-repo.sh`:

```bash
PORT=9000  # Change from 8080
```

Then update `.env`:

```bash
OPKG_REPO_URL=http://192.168.1.100:9000
```

### Using nginx Instead of Python Server

For better performance, use nginx:

```bash
# Install nginx
sudo apt install nginx

# Create nginx config
sudo tee /etc/nginx/sites-available/openwrt-repo << 'EOF'
server {
    listen 8080;
    server_name _;

    root /path/to/openwrt-repo;
    autoindex on;

    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/openwrt-repo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Serving Over HTTPS

For secure package downloads (recommended for production):

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/openwrt-repo.key \
  -out /etc/ssl/certs/openwrt-repo.crt

# Update nginx config to use HTTPS
# ... (nginx HTTPS configuration)

# Update .env
OPKG_REPO_URL=https://192.168.1.100:8443
```

**Note**: You'll need to trust the self-signed certificate on nodes.

## Firmware Image Usage

The repository also caches firmware images for upgrades:

### Sysupgrade Image

```bash
# Location
openwrt-repo/targets/ramips/mt7621/openwrt-24.10.4-ramips-mt7621-dlink_dir-1960-a1-squashfs-sysupgrade.bin

# Use for upgrades
scp openwrt-repo/targets/ramips/mt7621/*-sysupgrade.bin root@10.11.12.1:/tmp/
ssh root@10.11.12.1 'sysupgrade -n /tmp/*-sysupgrade.bin'
```

### Factory Image

```bash
# Location
openwrt-repo/targets/ramips/mt7621/openwrt-24.10.4-ramips-mt7621-dlink_dir-1960-a1-squashfs-factory.bin

# Use for initial flashing via stock firmware
```

## Best Practices

1. **Keep Server Running**: Start server before deployments, stop after
2. **Regular Updates**: Re-run setup script monthly to get package updates
3. **Backup Repository**: The repository directory can be backed up and restored
4. **Monitor Disk Space**: Repository can grow to 1-2 GB over time
5. **Version Pinning**: Keep repository version in sync with node OpenWrt versions

## Security Considerations

- **Local Network Only**: Repository server should only be accessible from local network
- **No Authentication**: Python HTTP server has no authentication (use nginx with auth for production)
- **Package Integrity**: Packages are verified using signatures from Packages.sig files
- **Firewall**: Restrict access to port 8080 to mesh network only

## Summary

The local package repository provides:

- ✅ **60% faster deployments** (3 min vs 5 min)
- ✅ **30x faster package downloads** (MB/s vs KB/s)
- ✅ **Offline capability** for deployments
- ✅ **Bandwidth savings** on repeated deployments
- ✅ **Version consistency** across all nodes

Perfect for development, testing, and production deployments where speed and reliability matter!
