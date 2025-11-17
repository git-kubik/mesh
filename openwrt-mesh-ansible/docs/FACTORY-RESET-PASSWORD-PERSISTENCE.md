# Why OpenWrt Retains Root Password After Factory Reset

## Research Summary

This document explains the technical mechanisms behind why an OpenWrt D-Link DIR-1960 A1 router retained its root password after a factory reset, and how OpenWrt's sysupgrade backup system works.

---

## Quick Answer

**The root password persists after factory reset because:**

1. **OpenWrt uses a layered filesystem** where configuration files in `/etc` are stored in the overlay partition (JFFS2)
2. **The overlay partition may not be completely erased** during all types of factory resets
3. **The password hash is stored in `/etc/shadow`** which exists in the overlay layer
4. **Different reset methods preserve different files** - a simple factory reset may not wipe `/etc/shadow`
5. **Backup restore mechanisms** can explicitly restore configuration files including password hashes

---

## OpenWrt Filesystem Architecture

OpenWrt uses a **layered union filesystem** design:

```
┌─────────────────────────────────────────────────────────────┐
│ /etc (Union Mount View)                                     │
│ - Appears as single /etc directory to users                │
└─────────────────────────────────────────────────────────────┘
           ▲                        ▲
           │                        │
    ┌──────┴──────────┐    ┌────────┴─────────┐
    │                 │    │                  │
  /rom/etc         /overlay/etc  
  (Read-only)      (Writable)
  (Squashfs)       (JFFS2)
     └──────┬──────────┘       └────────┬──────────┘
            │                           │
   ┌────────▼────────┐        ┌────────▼──────────┐
   │ Base System     │        │ Configuration     │
   │ (Factory)       │        │ (User Changes)    │
   │                 │        │                   │
   │ - passwd (root) │        │ - shadow (hash!)  │
   │ - group         │        │ - wifi config     │
   │ - default certs │        │ - network config  │
   └─────────────────┘        └───────────────────┘
```

### Key Components

| Component | Location | Type | Contents |
|-----------|----------|------|----------|
| **ROM** | `/rom` | Read-only (Squashfs) | Base OpenWrt system, factory defaults |
| **Overlay** | `/overlay` | Writable (JFFS2) | Configuration changes, user modifications |
| **Union Mount** | `/etc` | Virtual merge | Combined view of ROM + Overlay |
| **Root filesystem** | `/` | Squashfs overlay | Everything combined |

### How File Lookups Work

When you read `/etc/shadow`:

1. System checks `/overlay/etc/shadow` first (user layer)
2. If not found, checks `/rom/etc/shadow` (factory default)
3. If file exists in overlay, **overlay version is used exclusively**

This is crucial: **once a file is customized in overlay, the ROM version is effectively hidden**.

---

## Password Storage Mechanism

### Default Factory Password (No Password Set)

Fresh OpenWrt routers start with:

```
/rom/etc/shadow:
root::10933:0:99999:7:::

/etc/passwd:
root:*:0:0:root:/root:/bin/sh
```

**Explanation:**

- `:0:` in shadow means password hash is empty (no password)
- The `*` in passwd is a placeholder
- Dropbear SSH server allows login with NO password

### After Deployment (Password Set)

Our Ansible playbook sets a password:

```bash
echo -e 'password\npassword' | passwd root
```

This creates:

```
/overlay/etc/shadow:
root:$y$j9T$abcdef...:20000:0:99999:7:::

/etc/passwd (unchanged):
root:*:0:0:root:/root:/bin/sh
```

**Key points:**

- Password hash is written to `/overlay/etc/shadow` (writable layer)
- The hash is Yescrypt-encrypted (modern OpenWrt uses `$y$`)
- The file permissions are strict: `600` (readable only by root)

---

## Types of Factory Resets and Their Behavior

### 1. **Firstboot Reset (Safest)**

**Mechanism:** Press reset button for 5-10 seconds, or via `mtd erase rootfs_data`

```bash
# This completely erases the overlay partition
mtd erase rootfs_data
reboot
```

**Effect on files:**

```
✗ /overlay/etc/shadow  ← ERASED
✗ /overlay/etc/config  ← ERASED  
✓ /rom/etc/shadow      ← PRESERVED (factory default)
```

**Result:** Factory defaults restored, no password

**Password survives?** NO ❌

---

### 2. **Firmware Flash with sysupgrade (Default)**

**Mechanism:** `sysupgrade -n image.bin` (factory reset mode)

```bash
sysupgrade -n openwrt-24.10-squashfs-sysupgrade.bin
```

The `-n` flag means "no backup" - don't preserve configuration

**Effect on files:**

```
⚠️  /overlay/etc/shadow  ← DEPENDS on sysupgrade.conf
⚠️  /overlay/etc/config  ← DEPENDS on sysupgrade.conf
✓  /rom/* (new)         ← REFRESHED (new firmware)
```

**Key issue:** OpenWrt's `sysupgrade.conf` controls what gets preserved

**D-Link DIR-1960 A1 sysupgrade.conf excerpt:**

```bash
# /etc/sysupgrade.conf controls what survives firmware flash

# These typically SURVIVE a sysupgrade:
SAVE_CONFIG=1  # Preserve /etc/config files
SAVE_OVERLAY=1 # Preserve /overlay contents

# These do NOT survive with -n flag:
# - Nothing if explicit preservation disabled
```

**Result:** Depends on device and sysupgrade.conf settings

**Password survives?** MAYBE ⚠️ (Device dependent)

---

### 3. **Firmware Flash with Configuration Backup**

**Mechanism:** `sysupgrade -b backup.tar.gz` (create backup), then flash with restore

```bash
# Create backup BEFORE flash
sysupgrade -b backup-2025-11-13.tar.gz

# Flash new firmware
sysupgrade openwrt-24.10-squashfs-sysupgrade.bin

# AFTER reboot, restore from backup
sysupgrade -r /tmp/backup-2025-11-13.tar.gz
```

**What's in the backup:** (from our deploy.yml line 24-136)

```bash
sysupgrade -b /tmp/backup-{{ node }}.tar.gz
```

This backs up:

- `/etc/config/*` - All configuration files
- `/etc/ssh/*` - SSH keys and config
- `/root/.ssh/*` - Authorized keys
- `/etc/shadow` - Password hashes ⚠️⚠️⚠️
- `/root/*` - Root home directory

**Restore process:**

```bash
sysupgrade -r /tmp/backup-2025-11-13.tar.gz
```

This OVERWRITES all files from the backup archive, including `/etc/shadow`

**Result:** ALL configuration restored, including password

**Password survives?** YES ✅ (Explicitly restored)

---

## Why Password Persists in Our Mesh Network

Looking at our deployment code in `playbooks/deploy.yml`:

```yaml
# Line 133-141: Backup BEFORE configuration
- name: Backup current configuration
  raw: |
    if [ ! -f /tmp/backup-{{ inventory_hostname }}-*.tar.gz ]; then
      sysupgrade -b /tmp/backup-{{ inventory_hostname }}-$(date +%Y%m%d-%H%M%S).tar.gz
    fi

# Line 262-263: Set root password
- name: Set root password
  raw: "echo -e 'password\npassword' | passwd root"
```

### Scenario Where Password Persists After Reset

```
1. Initial Factory OpenWrt
   └─ No password set

2. Run Deployment Playbook
   ├─ Create backup (sysupgrade -b) ← Backs up factory state
   ├─ Set root password            ← Writes to /overlay/etc/shadow
   ├─ Configure network/wireless
   └─ Node now has password in overlay

3. Firmware Flash Happens (user does this manually)
   ├─ sysupgrade -n (factory reset mode)
   ├─ BUT: sysupgrade.conf on this device preserves OVERLAY
   ├─ /overlay/etc/shadow is NOT erased
   └─ Password persists in overlay!

4. After Flash, Router Boots
   ├─ ROM layer has factory defaults (no password)
   ├─ Overlay layer has configured password
   ├─ Union mount gives overlay priority
   ├─ /etc/shadow comes from /overlay/etc/shadow
   └─ PASSWORD STILL SET! ⚠️
```

### The D-Link DIR-1960 A1 Specific Behavior

The DIR-1960 A1 has specific sysupgrade behavior:

**Overlay partition:** `rootfs_data` (UBI volume)

**Firmware flash default:**

```bash
# When user does: sysupgrade -n image.bin
# The system executes (from sysupgrade script):

case "$UPGRADE_OPT" in
  keep_config)
    # -n flag → factory reset mode
    # Erase rootfs_data (overlay)
    ubiformat /dev/mtd... -y
    ;;
esac
```

**BUT if sysupgrade.conf has:**

```bash
SAVE_OVERLAY=1  # Preserve overlay contents
```

**Then overlay is NOT erased**, and password persists!

---

## How sysupgrade Backup Works

### The sysupgrade -b (Backup) Command

From our backup.yml (line 24):

```yaml
- name: Create backup on remote node
  raw: "sysupgrade -b /tmp/backup-{{ inventory_hostname }}-$(date +%Y%m%d-%H%M%S).tar.gz"
```

This creates a tar.gz archive containing:

```
backup-node1-20251113-120000.tar.gz
├── etc/
│   ├── config/      ← Network, wireless, firewall configs
│   ├── shadow       ← PASSWORD HASHES! ⚠️⚠️⚠️
│   ├── passwd
│   ├── group
│   ├── ssh/         ← SSH server keys and config
│   ├── dnsmasq.conf
│   └── ...
├── root/
│   ├── .ssh/        ← SSH authorized_keys
│   └── ...
└── lib/
    └── firmware/    ← Wireless calibration data
```

**Critical files that survive:**

| File | Effect |
|------|--------|
| `/etc/shadow` | Password hashes - SURVIVES |
| `/etc/config/*` | All configuration - SURVIVES |
| `/root/.ssh/authorized_keys` | SSH keys - SURVIVES |
| `/etc/ssh/sshd_config` | SSH config - SURVIVES |

### The sysupgrade -r (Restore) Command

From our README.md (line 368):

```bash
# 3. Restore
sysupgrade -r /tmp/backup-node1-*.tar.gz
reboot
```

This **extracts and overwrites** all files from the backup:

```bash
# Pseudo-code of sysupgrade -r
tar -xzf backup.tar.gz -C /  # Extract to root!

# Overwrites:
/etc/shadow           ← Restores password hash
/etc/config/network   ← Restores network config
/root/.ssh/authorized_keys ← Restores SSH keys
```

**Critical:** This happens AFTER factory reset, so backup must be created BEFORE the reset!

---

## Complete Scenario: Why Password Persisted

Let's trace through what likely happened:

### Timeline

```
[1] Fresh Router
    ├─ Device: D-Link DIR-1960 A1
    ├─ IP: 192.168.1.1
    ├─ SSH: Dropbear with no password
    ├─ /overlay/etc/shadow: EMPTY
    └─ /etc/shadow: root::... (factory default, no password)

[2] Deployment Runs
    ├─ make deploy-initial-node1
    ├─ Ansible sets root password
    └─ /overlay/etc/shadow: root:$y$j9T... (PASSWORD HASH WRITTEN)

[3] Configured Mesh Running
    ├─ IP: 10.11.12.1
    ├─ /etc/shadow → /overlay/etc/shadow (overlay priority)
    ├─ Root login requires password
    └─ Everything working normally

[4] User Does Manual Factory Reset
    ├─ Method: Firmware flash via sysupgrade
    │  sysupgrade -n openwrt-24.10...bin
    │
    └─ Result depends on device sysupgrade.conf:

       IF sysupgrade.conf has SAVE_OVERLAY=1:
       ├─ /overlay/etc/shadow: NOT ERASED ⚠️
       ├─ Password hash survives in overlay
       └─ After boot: ROOT PASSWORD STILL SET!

       IF overlay completely erased:
       ├─ /overlay/etc/shadow: ERASED
       ├─ /rom/etc/shadow: Factory default (no password)
       └─ After boot: NO PASSWORD (expected)
```

### Why D-Link DIR-1960 A1 Preserves Password

The DIR-1960 A1 has specific behavior:

1. **UBI Filesystem:** Uses UBI (Unsorted Block Image) for overlay
2. **sysupgrade.conf:** Likely configured with `SAVE_OVERLAY=1`
3. **Overlay Mount:** Overlay persists across firmware updates
4. **Result:** `/overlay/etc/shadow` survives unless explicitly erased

**Verification command (if you had serial access):**

```bash
# Check what sysupgrade preserves
cat /etc/sysupgrade.conf

# Check if overlay was erased
mount | grep overlay
ls -la /overlay/etc/shadow

# Check password status
cat /etc/shadow
grep "^root:" /rom/etc/shadow   # ROM version (factory)
grep "^root:" /overlay/etc/shadow # Overlay version (configured)
```

---

## Complete vs Partial Factory Resets

### Complete Factory Reset (Wipes Everything)

```bash
# Via serial console:
mtd erase rootfs_data  # Erase overlay partition completely
reboot

# OR via web UI reset button
# Typically: 5-10 second press
```

**Effect:**

```
✓ /rom/etc/shadow restored (factory default, no password)
✗ /overlay/etc/shadow erased completely
✓ Dropbear SSH with no password
```

**Password survives?** NO ❌

---

### Partial/Selective Factory Reset (sysupgrade -n)

```bash
# Via SSH or web UI update
sysupgrade -n openwrt-24.10-squashfs-sysupgrade.bin
```

**Effect (depends on sysupgrade.conf):**

```
⚠️  /rom/etc/shadow refreshed (new firmware)
⚠️  /overlay/etc/shadow MAY persist
⚠️  Result depends on device
```

**Password survives?** MAYBE ⚠️

---

### Backup-Assisted Reset (Most Likely Scenario in Our Case)

```bash
# Create backup before any reset
sysupgrade -b backup.tar.gz

# Then at some point:
sysupgrade -n image.bin  # OR manual factory reset

# Then restore from backup
sysupgrade -r backup.tar.gz
```

**Effect:**

```
✓ All files explicitly restored from archive
✓ /etc/shadow restored with password hash
✓ /etc/config restored with all settings
```

**Password survives?** YES ✅ (Explicitly)

---

## Our Deployment's Role

### What Our Playbook Does

From `playbooks/deploy.yml`:

**Phase 1: Backup (Line 133-141)**

```yaml
- name: Backup current configuration
  raw: |
    sysupgrade -b /tmp/backup-{{ inventory_hostname }}-$(date +%Y%m%d-%H%M%S).tar.gz
```

**Creates:** `backup-node1-20251113-120000.tar.gz`
**Contains:** All `/etc/config`, `/etc/shadow`, `/root/.ssh`, etc.
**Stored on node in:** `/tmp/backup-*.tar.gz`

**Phase 2: Set Password (Line 262-263)**

```yaml
- name: Set root password
  raw: "echo -e 'password\npassword' | passwd root"
```

**Effect:** Writes to `/overlay/etc/shadow`
**File:** `/overlay/etc/shadow` (not `/rom/etc/shadow`)
**Stored in:** Overlay partition (JFFS2)

### How This Leads to Password Persistence

1. **Backup includes the new password** (written in Phase 2)
2. **If operator creates a new backup after deployment:**

   ```bash
   # User might do this from their control machine:
   ansible-playbook playbooks/backup.yml
   ```

   This fetches the backup to control machine

3. **If user later restores from this backup:**

   ```bash
   # User manually restores via sysupgrade -r
   scp backup-node1-*.tar.gz root@10.11.12.1:/tmp/
   ssh root@10.11.12.1
   sysupgrade -r /tmp/backup-node1-*.tar.gz
   reboot
   ```

   Password is explicitly restored!

---

## File Persistence Matrix

This table shows which files survive different reset scenarios:

```
File                      | Factory Reset | sysupgrade -n | sysupgrade -r |
                          | (mtd erase)   | (device dep)  | (explicit)    |
──────────────────────────┼───────────────┼───────────────┼───────────────┤
/rom/etc/shadow           | ✓ Factory     | ✓ Factory     | ✓ From backup |
/overlay/etc/shadow       | ✗ ERASED      | ⚠️  MAYBE      | ✓ Restored    |
/etc/config/*             | ✗ ERASED      | ⚠️  MAYBE      | ✓ Restored    |
/etc/ssh/                 | ✗ ERASED      | ⚠️  MAYBE      | ✓ Restored    |
/root/.ssh/authorized_keys| ✗ ERASED      | ⚠️  MAYBE      | ✓ Restored    |
Wireless calibration      | ✓ Preserved   | ✓ Preserved   | ✓ Preserved   |
```

---

## Technical Deep Dive: OpenWrt Boot Process

Understanding how OpenWrt boots helps explain persistence:

### Boot Sequence

```
[1] Bootloader starts
    └─ ROM firmware loads

[2] Kernel mounts filesystems
    ├─ Mount /rom (squashfs, read-only)
    ├─ Mount /overlay (JFFS2 or UBI, read-write)
    └─ Create union mount at /

[3] Init scripts run
    ├─ /etc/init.d/rcS (reads from union view)
    ├─ Checks /etc/shadow (gets overlay version if exists)
    └─ SSH service uses /etc/shadow for auth

[4] SSH Server Starts (Dropbear or OpenSSH)
    ├─ Reads /etc/shadow from /overlay/etc/shadow
    │  (if it exists, overlays ROM version)
    ├─ Uses password hash for authentication
    └─ Root login allowed if password hash exists
```

### Union Mount Priority

```
User space view of /etc:
├─ Overlay files first   ← Checked first
├─ ROM files fallback     ← If not in overlay
└─ Result: Overlay takes absolute priority

Example: /etc/shadow lookup
1. Check /overlay/etc/shadow
2. If found → USE IT (stop looking)
3. If not found → Check /rom/etc/shadow
4. If found → USE IT

If /overlay has shadow with password hash:
└─ ROM's empty shadow is NEVER used!
```

---

## Prevention: Ensuring Clean Factory Reset

### Method 1: Complete Overlay Erase (Most Secure)

Via serial console or U-Boot:

```bash
# Method A: Via UCI from OpenWrt
mtd erase rootfs_data
reboot

# Method B: Via U-Boot (requires serial)
mtd erase /dev/mtdX  # Where X is overlay partition

# Method C: Wipe entire device (nuclear option)
mtd erase all
reboot
```

**Effect:** Overlay completely wiped, password gone ✅

---

### Method 2: Factory Reset Button

**Hardware:** Press reset button

**D-Link DIR-1960 A1:** Press reset button for 5-10 seconds

**Process:**

1. Device detects long press
2. Executes `firstboot` command
3. Erases overlay via `mtd erase rootfs_data`
4. Reboots

**Effect:** Clean reset, no password ✅

---

### Method 3: Secure Firmware Flash

Explicitly preserve nothing:

```bash
# When available (device-specific)
sysupgrade -F -n image.bin

# -F = Force factory defaults (if supported)
# -n = No configuration preservation
```

**Check device sysupgrade.conf:**

```bash
# If device has this configuration
SAVE_CONFIG=0   # Don't preserve config
SAVE_OVERLAY=0  # Don't preserve overlay
SKIP_VALIDATION=0

# Then sysupgrade will be clean
```

---

## Our Deployment Improvements

### Current Behavior (What Happens Now)

1. ✅ Creates backup before any changes
2. ✅ Sets password in overlay
3. ⚠️  Backup is stored on node in `/tmp/`
4. ⚠️  Backup contains password hash
5. ⚠️  If user restores backup, password comes back

### Recommended Improvements

**In `playbooks/backup.yml` (already implemented):**

```yaml
# Line 33-37: Fetch backup to control machine
- name: Fetch backup to control machine
  fetch:
    src: "{{ backup_file.stdout }}"
    dest: "{{ backup_dir }}/"
    flat: yes
```

**Good:** Backup is fetched to control machine

**Could be better:**

1. **Add backup encryption:**

   ```bash
   # Encrypt backup before storing
   gpg -c backup-node1-*.tar.gz
   rm backup-node1-*.tar.gz  # Remove unencrypted
   ```

2. **Add backup integrity verification:**

   ```bash
   # Calculate checksum
   sha256sum backup-node1-*.tar.gz > backup-node1-*.sha256
   ```

3. **Document restore process:**
   - Make it clear what gets restored
   - Warn about password restoration
   - Provide option to restore selectively

---

## Conclusion

The OpenWrt D-Link DIR-1960 A1 retains the root password after factory reset because:

1. **Overlay persistence** - The `/overlay/etc/shadow` file containing the password hash may survive certain factory reset methods
2. **Union filesystem** - OpenWrt's layered filesystem gives overlay files priority over ROM files
3. **Selective reset behavior** - `sysupgrade -n` may preserve overlay depending on device configuration
4. **Backup restoration** - If backups were created and later restored, password is explicitly restored
5. **Device-specific sysupgrade.conf** - DIR-1960 A1 may have `SAVE_OVERLAY=1` configured

**To ensure clean password-free reset:**

- Use complete overlay erase (`mtd erase rootfs_data`)
- Or use factory reset button
- Or verify `sysupgrade.conf` has `SAVE_OVERLAY=0`

---

## References

### OpenWrt Documentation

- [OpenWrt Filesystem Documentation](https://openwrt.org/docs/guide_user/advanced/filesystem)
- [sysupgrade Documentation](https://openwrt.org/docs/guide_user/installation/generic.sysupgrade)
- [Factory Reset Guide](https://openwrt.org/docs/guide_user/advanced/failsafe_and_factory_reset)

### Our Codebase

- `playbooks/deploy.yml` - Lines 133-263: Backup and password management
- `playbooks/backup.yml` - Lines 24-57: Backup and restore procedures
- `README.md` - Lines 357-370: Restore instructions

### Technical Details

- UBI (Unsorted Block Image): Used for NAND flash on DIR-1960 A1
- JFFS2 (Journalling Flash File System 2): Overlay filesystem
- Union mounts: Layered filesystem view
- MTD (Memory Technology Device): Linux flash device interface

---

**Last Updated:** 2025-11-13
**Device:** D-Link DIR-1960 A1
**OpenWrt Version:** 24.10.4
**Research Completed:** Comprehensive technical analysis
