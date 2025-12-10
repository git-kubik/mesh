# Backup and Restore

This guide covers backup strategies, procedures, and disaster recovery for the mesh network.

## Backup Types

| Type | Method | Contents | Use Case |
|------|--------|----------|----------|
| **Quick backup** | `sysupgrade -b` | Changed configs | Daily/routine |
| **Snapshot** | Ansible playbook | Full config + state | Pre-change, archival |
| **Image build** | OpenWrt Image Builder | Complete firmware | Disaster recovery |

## Quick Backup (sysupgrade)

The simplest backup method using OpenWrt's built-in tool.

### Create Backup

```bash
# On the node
sysupgrade -b /tmp/backup.tar.gz

# Or via Ansible
ansible node1 -a "sysupgrade -b /tmp/backup-$(date +%Y%m%d).tar.gz"

# Using Makefile
make backup
```

### What's Included

The `sysupgrade -b` backup includes:

- `/etc/config/` - All UCI configuration
- `/etc/passwd`, `/etc/shadow` - User accounts
- `/etc/dropbear/` or `/etc/ssh/` - SSH keys
- Files listed in `/etc/sysupgrade.conf`

### Fetch Backup to Control Machine

```bash
# Copy backup from node
scp root@10.11.12.1:/tmp/backup.tar.gz ./backups/node1-$(date +%Y%m%d).tar.gz

# Or using Ansible playbook
ansible-playbook -i inventory/hosts.yml playbooks/backup.yml
```

### Restore Backup

```bash
# Copy backup to node
scp backup.tar.gz root@10.11.12.1:/tmp/

# Restore (doesn't apply until reboot)
ssh root@10.11.12.1 'sysupgrade -r /tmp/backup.tar.gz'

# Reboot to apply
ssh root@10.11.12.1 'reboot'
```

## Configuration Snapshots

More comprehensive than quick backups, capturing the complete node state.

### Create Snapshot

```bash
# Single node
make snapshot NODE=1

# All nodes
make snapshot-all

# Or directly
ansible-playbook -i inventory/hosts.yml playbooks/snapshot.yml
```

### Snapshot Contents

```
snapshots/<hostname>/
├── metadata.json           # Node identification
├── system/
│   ├── openwrt_release    # Version info
│   ├── board_info         # Hardware model
│   └── kernel_version     # Kernel info
├── config/
│   ├── uci_export.txt     # Complete UCI export
│   ├── network            # Individual configs
│   ├── wireless
│   ├── firewall
│   ├── dhcp
│   └── system
├── etc/
│   ├── passwd             # User accounts
│   ├── shadow             # Password hashes
│   ├── fstab              # Mount points
│   ├── crontabs/root      # Scheduled tasks
│   └── ssh/
│       ├── authorized_keys
│       ├── sshd_config
│       └── ssh_host_*_key # Host keys
├── packages/
│   ├── installed.txt      # Package names
│   └── installed_full.txt # With versions
├── scripts/
│   └── *.sh               # Custom scripts
├── network/
│   ├── interfaces.txt     # Interface list
│   ├── ip_addresses.txt   # IP configuration
│   └── routes.txt         # Routing table
├── mesh/
│   ├── batman_if.txt      # Batman interfaces
│   ├── neighbors.txt      # Mesh neighbors
│   └── originators.txt    # Routing table
└── restore/
    ├── README.md          # Instructions
    └── restore.sh         # Restore script
```

### Compare Snapshots (Drift Detection)

```bash
# Show changes since last snapshot
make snapshot-diff NODE=1

# Manual comparison
diff -r snapshots/mesh-node1-old/ snapshots/mesh-node1-new/
```

### Restore from Snapshot

#### Automatic Restore

```bash
# Run the generated restore script
./snapshots/mesh-node1/restore/restore.sh 192.168.1.1
```

#### Manual Restore

```bash
# 1. Copy UCI export to node
scp snapshots/mesh-node1/config/uci_export.txt root@192.168.1.1:/tmp/

# 2. Import UCI configuration
ssh root@192.168.1.1 'uci import < /tmp/uci_export.txt && uci commit'

# 3. Restore SSH keys
scp snapshots/mesh-node1/etc/ssh/authorized_keys root@192.168.1.1:/root/.ssh/
ssh root@192.168.1.1 'chmod 600 /root/.ssh/authorized_keys'

# 4. Restore host keys (preserves identity)
scp snapshots/mesh-node1/etc/ssh/ssh_host_* root@192.168.1.1:/etc/ssh/
ssh root@192.168.1.1 'chmod 600 /etc/ssh/ssh_host_*_key'

# 5. Restore crontab
scp snapshots/mesh-node1/etc/crontabs/root root@192.168.1.1:/etc/crontabs/

# 6. Restore custom scripts
scp snapshots/mesh-node1/scripts/*.sh root@192.168.1.1:/usr/bin/
ssh root@192.168.1.1 'chmod +x /usr/bin/*.sh'

# 7. Reboot
ssh root@192.168.1.1 'reboot'
```

## Backup Schedule

### Recommended Schedule

| Frequency | Action | Retention |
|-----------|--------|-----------|
| Daily | Automated sysupgrade backup | 7 days |
| Weekly | Configuration snapshot | 4 weeks |
| Pre-change | Full snapshot | Permanent |
| Monthly | Verify backup restoration | N/A |

### Automated Backup with Cron

```bash
# On control machine, add to crontab
0 2 * * * cd /path/to/openwrt-mesh-ansible && make backup

# Or via Ansible cron module in playbook
```

## Disaster Recovery

### Scenario 1: Single Node Failure

**Symptoms**: One node unresponsive, mesh still operational

**Recovery**:

1. If hardware OK, restore from backup:

   ```bash
   # Flash vanilla OpenWrt
   make sysupgrade NODE=1 IMAGE_TYPE=vanilla

   # Wait for reboot, then restore
   ./snapshots/mesh-node1/restore/restore.sh 192.168.1.1
   ```

2. If hardware failed, on replacement device:

   ```bash
   # Full deployment from scratch
   make deploy-node NODE=1
   ```

### Scenario 2: Multiple Node Failure

**Symptoms**: Mesh partially or fully down

**Recovery**:

1. Identify operational nodes:

   ```bash
   make check-all
   ```

2. Restore failed nodes one at a time:

   ```bash
   make deploy-node NODE=1
   # Wait for mesh to form
   make deploy-node NODE=2
   # etc.
   ```

3. Verify mesh:

   ```bash
   make batman-status
   make verify
   ```

### Scenario 3: Total Infrastructure Loss

**Symptoms**: All nodes lost (fire, theft, etc.)

**Prerequisites**: Off-site backup of snapshots directory

**Recovery**:

1. Set up new hardware
2. Flash vanilla OpenWrt to all nodes
3. Restore from snapshots:

   ```bash
   # For each node
   make deploy-node NODE=1
   # Or restore from snapshot if config was customized
   ./snapshots/mesh-node1/restore/restore.sh 192.168.1.1
   ```

4. Reconfigure switches
5. Verify mesh operation

### Scenario 4: Configuration Corruption

**Symptoms**: Node boots but misbehaves

**Recovery**:

```bash
# Option 1: Revert recent changes
ssh root@10.11.12.1 'uci revert'
ssh root@10.11.12.1 '/etc/init.d/network restart'

# Option 2: Factory reset and redeploy
make factory-reset NODE=1
# Wait for reboot
make deploy-node NODE=1

# Option 3: Restore from known-good snapshot
./snapshots/mesh-node1/restore/restore.sh 10.11.12.1
```

## Best Practices

### Backup Storage

```
backups/
├── daily/
│   ├── 2024-01-15/
│   ├── 2024-01-14/
│   └── ...
├── weekly/
│   ├── 2024-W02/
│   └── ...
├── snapshots/
│   ├── mesh-node1/
│   ├── mesh-node2/
│   └── mesh-node3/
└── pre-change/
    ├── 2024-01-15-upgrade-openwrt/
    └── ...
```

### Off-site Backup

```bash
# Sync to remote server
rsync -avz backups/ backup-server:/mesh-backups/

# Or to cloud storage
rclone sync backups/ remote:mesh-backups/
```

### Backup Verification

Monthly verification checklist:

- [ ] Backups are being created
- [ ] Backup files are not corrupted (tar -tzf)
- [ ] Off-site sync is working
- [ ] Test restore on spare hardware
- [ ] Document any restore issues

### Pre-Change Backup

Always backup before changes:

```bash
# Before any deployment
make snapshot NODE=1
make deploy-node NODE=1

# Before OpenWrt upgrade
make snapshot-all
make sysupgrade NODE=1
```

## Backup Exclusions

Files NOT included in standard backups (intentionally):

| File | Reason |
|------|--------|
| `/etc/shadow` | Security (use snapshot for full backup) |
| `/x00/*` | USB storage data (too large) |
| RRD files | Can be regenerated |
| Log files | Ephemeral |

To backup USB data separately:

```bash
# On node
tar -czf /tmp/usb-backup.tar.gz -C /x00 .

# Fetch to control machine
scp root@10.11.12.1:/tmp/usb-backup.tar.gz ./backups/
```

## Restore Testing

### Test Environment

Set up a test node to verify restores:

1. Spare DIR-1960 or VM with OpenWrt
2. Isolated network (not connected to production)
3. Test restoration procedures monthly

### Verification Checklist

After restore, verify:

- [ ] SSH access works with correct keys
- [ ] Network configuration correct (IP addresses)
- [ ] Batman-adv interfaces active
- [ ] WiFi broadcasting
- [ ] DHCP serving addresses
- [ ] DNS resolving
- [ ] Custom scripts present and executable
- [ ] Cron jobs scheduled
- [ ] USB storage mounted (if applicable)
- [ ] Monitoring working (if applicable)

## Troubleshooting

### Backup File Corrupted

```bash
# Verify tar file
tar -tzf backup.tar.gz

# If corrupted, restore from older backup
```

### Restore Fails with UCI Errors

```bash
# Check UCI syntax
uci show 2>&1 | grep -i error

# Start fresh and import selectively
firstboot && reboot
# Then import individual configs
```

### SSH Keys Not Working After Restore

```bash
# Verify key permissions
chmod 600 /root/.ssh/authorized_keys
chmod 700 /root/.ssh

# Verify key content matches
cat /root/.ssh/authorized_keys
```

### Network Unreachable After Restore

```bash
# Access via console (serial or physical keyboard)
# Reset network to known state
uci revert network
/etc/init.d/network restart

# Or factory reset
firstboot && reboot
```
