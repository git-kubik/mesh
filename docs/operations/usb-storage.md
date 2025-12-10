# USB Storage Configuration for OpenWrt Mesh Nodes

This document describes how to configure USB storage on OpenWrt mesh nodes using the provided Ansible playbook.

## Overview

USB storage is **automatically configured during node deployment** if a USB device is detected. The setup includes:

- Flash-optimized F2FS filesystem (default)
- Auto-detection of USB devices
- Persistent mounting at `/x00`
- Automatic remount on reboot

### Automatic Deployment Integration

When you run `make deploy-node NODE=1`, the deployment will:

1. Check for attached USB storage devices
2. Automatically partition, format, and mount any detected USB device
3. Configure persistent mounting at `/x00`
4. Deploy monitoring (collectd + vnStat) if `ENABLE_MONITORING=true` (default)
5. No user confirmation required - fully automated

**Note:** If `ENABLE_MONITORING=true` in `.env`, monitoring will automatically be deployed to use the USB storage. See [Monitoring Guide](monitoring.md) for details.

## Prerequisites

- OpenWrt nodes (USB drivers are automatically installed as required packages)
- USB storage device connected to the node(s)
- Sufficient space in /overlay for packages (~3-4MB for USB support)

## Supported Filesystems

The playbook supports multiple filesystems optimized for different use cases:

| Filesystem | Best For | Mount Options |
|------------|----------|---------------|
| **F2FS** (default) | USB flash drives, SSDs | `noatime,nodiratime,background_gc=on,discard` |
| **ext4** | General purpose | `noatime,nodiratime,nobarrier` (journaling disabled) |
| **exFAT** | Cross-platform compatibility | `noatime` |
| **vFAT** | Maximum compatibility | `noatime` |

## Usage

### Automatic Configuration During Deployment

USB storage is automatically configured when deploying nodes:

```bash
# Deploy node with USB auto-configuration (if USB device attached)
make deploy-node NODE=1
```

### Manual Configuration on Already Deployed Nodes

If you add USB storage after deployment, you can manually configure it:

```bash
# Setup USB storage on node 1 (will prompt for confirmation)
make usb-storage NODE=1

# With verbose output for debugging
make usb-storage NODE=1 VERBOSE=1
```

### Configure USB Storage on All Nodes

```bash
# Setup USB storage on all nodes (will prompt for confirmation)
make usb-storage
```

**⚠️ WARNING:** Manual configuration will FORMAT the USB drives, destroying all existing data!

### Check USB Storage Status

```bash
# Check status on a single node
make usb-status NODE=1

# Check status on all nodes
make usb-status
```

## Manual Playbook Execution

If you prefer to run the playbook directly:

```bash
# Single node
ansible-playbook -i inventory/hosts.yml playbooks/usb-storage.yml --limit node1

# All nodes
ansible-playbook -i inventory/hosts.yml playbooks/usb-storage.yml

# Custom filesystem (default is f2fs)
ansible-playbook -i inventory/hosts.yml playbooks/usb-storage.yml \
  -e "usb_filesystem=ext4"

# Custom mount point (default is /x00)
ansible-playbook -i inventory/hosts.yml playbooks/usb-storage.yml \
  -e "usb_mount_point=/mnt/usb"
```

## What the Playbook Does

### Phase 1: USB Drivers (Installed Automatically)

USB storage drivers are now part of the **required packages** and installed during node deployment:

- `kmod-usb-storage` - USB storage support
- `kmod-usb2`, `kmod-usb3` - USB 2.0/3.0 support
- `kmod-fs-f2fs`, `f2fs-tools` - F2FS filesystem (flash-optimized)
- `fdisk` - Partitioning tool
- `block-mount` - Auto-mount support

### Phase 2: Detect USB Device

- Automatically finds connected USB storage
- Supports devices at /dev/sda, /dev/sdb, /dev/sdc

### Phase 3: Partition Drive

- Creates new partition table
- Single partition using full capacity

### Phase 4: Format Filesystem

- Formats with selected filesystem (default: F2FS)
- Applies flash-optimized settings
- Sets volume label "MESH-USB"

### Phase 5: Mount Storage

- Creates mount point at `/x00`
- Mounts with optimized options for flash storage

### Phase 6: Configure Persistence

- Sets up auto-mount on boot via UCI/fstab
- Uses UUID for reliable device identification

### Phase 7: Verification

- Confirms mount status
- Tests write access
- Displays capacity information

## Verifying Installation

After running the playbook, verify USB storage is working:

```bash
# SSH to node
ssh root@10.11.12.1

# Check mount status
df -h /x00

# List contents
ls -la /x00/

# Test write
echo "test" > /x00/test.txt
cat /x00/test.txt

# Check auto-mount configuration
uci show fstab
cat /etc/fstab
```

## Troubleshooting

### USB Device Not Detected

- Ensure USB device is properly connected
- Check if USB modules are loaded: `lsmod | grep usb_storage`
- Try different USB port
- Check device appears in: `ls -la /dev/sd*`

### Mount Fails

- Check filesystem support: `opkg list-installed | grep f2fs`
- Try different filesystem: `-e "usb_filesystem=ext4"`
- Check system logs: `logread | grep -i usb`

### No Space for Packages

- Clean package cache: `opkg clean`
- Remove unnecessary packages
- Check overlay space: `df -h /overlay`

### Mount Not Persistent

- Check fstab config: `uci show fstab`
- Verify block-mount service: `/etc/init.d/fstab status`
- Check UUID detection: `block info`

## Performance Tips

For USB flash drives:

- Use F2FS filesystem (default)
- Enable TRIM/discard for better wear leveling
- Minimize writes with noatime mount option

For external HDDs:

- Use ext4 filesystem
- Enable journaling for data integrity

For cross-platform use:

- Use exFAT for Windows/Mac compatibility
- Use vFAT for maximum compatibility (4GB file size limit)

## Security Considerations

- USB storage is mounted with full read/write access
- No encryption is configured by default
- Consider adding encryption if storing sensitive data
- Implement proper backup strategy for critical data

## Related Documentation

- [OpenWrt USB Storage Guide](https://openwrt.org/docs/guide-user/storage/usb-drives)
- [F2FS Filesystem](https://www.kernel.org/doc/html/latest/filesystems/f2fs.html)
- [Block Mount Configuration](https://openwrt.org/docs/guide-user/storage/fstab)
