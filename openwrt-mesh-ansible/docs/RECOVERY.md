# Router Recovery Guide

Recovery procedures for D-Link DIR-1960 A1 mesh nodes running OpenWrt.

## Recovery Options Overview

| Situation | Recovery Method | Difficulty |
|-----------|-----------------|------------|
| Bad configuration, OpenWrt boots | Failsafe Mode | Easy |
| OpenWrt broken, bootloader works | D-Link Recovery GUI | Easy |
| Recovery GUI fails | TFTP Recovery | Medium |
| Complete brick | Serial Console | Hard |

## Prerequisites

Keep these files available for recovery:

```
openwrt-repo/targets/ramips/mt7621/
├── openwrt-24.10.4-ramips-mt7621-dlink_dir-1960-a1-squashfs-recovery.bin  # For bootloader recovery
└── openwrt-24.10.4-ramips-mt7621-dlink_dir-1960-a1-squashfs-sysupgrade.bin  # For normal upgrades
```

Download recovery image if missing:

```bash
wget -P openwrt-repo/targets/ramips/mt7621/ \
  https://downloads.openwrt.org/releases/24.10.4/targets/ramips/mt7621/openwrt-24.10.4-ramips-mt7621-dlink_dir-1960-a1-squashfs-recovery.bin
```

---

## Method 1: Failsafe Mode

**Use when:** OpenWrt boots but configuration is broken (can't access network, bad firewall rules, etc.)

Failsafe mode boots OpenWrt with minimal configuration, allowing you to fix or reset settings.

### Steps

1. **Power off** the router

2. **Connect** Ethernet cable from your PC to a LAN port (not WAN)

3. **Power on** and watch the LEDs closely

4. **Enter failsafe:** When the power LED starts flashing rapidly, press and release the reset button repeatedly (or hold it, depending on timing)

5. **Configure your PC** with static IP:

   ```bash
   # Linux
   sudo ip addr add 192.168.1.2/24 dev eth0

   # Or use NetworkManager
   nmcli con add type ethernet con-name failsafe ifname eth0 ip4 192.168.1.2/24
   ```

6. **Connect via SSH** (no password in failsafe):

   ```bash
   ssh root@192.168.1.1
   ```

7. **Choose recovery action:**

   **Option A: Reset to defaults (wipes all configuration)**

   ```bash
   firstboot && reboot -f
   ```

   **Option B: Mount filesystem and fix configuration**

   ```bash
   mount_root
   # Now you can edit files in /etc/
   vi /etc/config/network
   # When done:
   reboot -f
   ```

---

## Method 2: D-Link Recovery GUI

**Use when:** OpenWrt won't boot, but the bootloader is intact (most common recovery scenario)

The D-Link bootloader has a built-in recovery web interface.

### Steps

1. **Power off** the router

2. **Configure PC with static IP:**

   ```bash
   # Linux
   sudo ip addr add 192.168.0.11/24 dev eth0

   # Verify
   ip addr show eth0
   ```

   Or via NetworkManager GUI:
   - IP: `192.168.0.11`
   - Netmask: `255.255.255.0`
   - Gateway: leave empty
   - DNS: leave empty

3. **Connect** Ethernet cable from PC to any **LAN port** (not WAN)

4. **Enter recovery mode:**
   - Hold the **reset button** (small hole on back)
   - While holding reset, **power on** the router
   - Keep holding until the **blue LEDs start blinking** (~10 seconds)
   - Release the reset button

5. **Access recovery GUI:**
   - Open browser to: `http://192.168.0.1`
   - You should see D-Link recovery page

6. **Upload recovery image:**
   - Click "Browse" or "Choose File"
   - Select: `openwrt-24.10.4-ramips-mt7621-dlink_dir-1960-a1-squashfs-recovery.bin`
   - Click "Upload" or "Upgrade"

7. **Wait for completion:**
   - Progress bar will show upload status
   - Wait for "Upgrade successfully" message
   - **DO NOT** power off during this process (~2-3 minutes)

8. **Router reboots** to stock OpenWrt:
   - Change PC IP back to DHCP or `192.168.1.x`
   - Access router at `http://192.168.1.1`

9. **Restore mesh configuration:**

   ```bash
   # Either flash custom image:
   scp images/mesh-node3-sysupgrade.bin root@192.168.1.1:/tmp/
   ssh root@192.168.1.1 "sysupgrade -n /tmp/mesh-node3-sysupgrade.bin"

   # Or run Ansible deployment:
   make deploy NODE=3
   ```

### Troubleshooting Recovery GUI

**Can't reach 192.168.0.1:**

- Verify PC IP is `192.168.0.11/24`
- Try different LAN port
- Check cable connection
- Ensure LEDs are blinking (recovery mode active)
- Try different browser or clear cache

**Upload fails:**

- Use the `-recovery.bin` file, NOT `-sysupgrade.bin`
- Try a different browser (Firefox often works best)
- Disable browser extensions
- Try smaller file first to test connectivity

**Router doesn't enter recovery mode:**

- Hold reset button BEFORE powering on
- Hold for full 10 seconds until LEDs blink
- Try with only power and one LAN cable connected

---

## Method 3: TFTP Recovery

**Use when:** D-Link recovery GUI doesn't work

The bootloader can also fetch firmware via TFTP.

### Setup TFTP Server (Linux)

```bash
# Install TFTP server
sudo apt install tftpd-hpa

# Configure
sudo tee /etc/default/tftpd-hpa << 'EOF'
TFTP_USERNAME="tftp"
TFTP_DIRECTORY="/srv/tftp"
TFTP_ADDRESS=":69"
TFTP_OPTIONS="--secure --create"
EOF

# Create directory and copy firmware
sudo mkdir -p /srv/tftp
sudo cp openwrt-repo/targets/ramips/mt7621/openwrt-24.10.4-ramips-mt7621-dlink_dir-1960-a1-squashfs-recovery.bin /srv/tftp/
sudo chmod 644 /srv/tftp/*

# Start TFTP server
sudo systemctl restart tftpd-hpa
sudo systemctl status tftpd-hpa
```

### Configure Network

```bash
# Set static IP (common TFTP recovery addresses)
sudo ip addr add 192.168.0.66/24 dev eth0
# or
sudo ip addr add 192.168.1.66/24 dev eth0
```

### Trigger TFTP Recovery

1. Connect Ethernet to LAN port
2. Hold reset while powering on
3. Bootloader will broadcast TFTP request
4. Monitor TFTP server logs: `sudo tail -f /var/log/syslog | grep tftp`

**Note:** Exact TFTP filename and IP may vary. Serial console access helps identify what the bootloader expects.

---

## Method 4: Serial Console Recovery

**Use when:** All other methods fail (complete brick)

**Warning:** Requires opening the router and soldering. May void warranty.

### Requirements

- USB-to-TTL serial adapter (3.3V, **NOT 5V**)
- Soldering equipment
- Terminal software (minicom, screen, picocom)

### Serial Connection

| Serial Adapter | Router J1 Header |
|----------------|------------------|
| TX | RX |
| RX | TX |
| GND | GND |
| **Do NOT connect VCC** | |

### Serial Settings

- Baud rate: `115200`
- Data bits: `8`
- Parity: `None`
- Stop bits: `1`
- Flow control: `None`

### Connect via Serial

```bash
# Using screen
screen /dev/ttyUSB0 115200

# Using minicom
minicom -D /dev/ttyUSB0 -b 115200

# Using picocom
picocom -b 115200 /dev/ttyUSB0
```

### Bootloader Commands

Power on the router while connected via serial. Press keys to interrupt boot:

```
# Common bootloader interrupts:
# - Press any key
# - Press 'Enter' repeatedly
# - Press '4' for TFTP recovery (device-specific)

# Once in bootloader, common commands:
printenv                    # Show environment variables
tftpboot                    # Boot from TFTP
reset                       # Reboot
```

**Note:** Full U-Boot console on D-Link devices may require a password stored in flash. Failsafe mode (press 'f' during boot) may be accessible without password.

---

## Prevention: Best Practices

### Before Flashing

1. **Verify checksum:**

   ```bash
   cd images/
   sha256sum -c mesh-node3-sysupgrade.bin.sha256
   ```

2. **Test on one node first** before deploying to all

3. **Keep recovery image handy:**

   ```bash
   ls -la openwrt-repo/targets/ramips/mt7621/*recovery*
   ```

4. **Backup current configuration:**

   ```bash
   make snapshot NODE=3
   ```

### During Flashing

1. **Use stable power** - consider UPS
2. **Don't interrupt** - wait for full completion (2-3 minutes)
3. **Use `-n` flag** for custom images (config is baked in):

   ```bash
   sysupgrade -n /tmp/mesh-node3-sysupgrade.bin
   ```

### After Flashing

1. **Verify boot:**

   ```bash
   ping 10.11.12.3
   ssh root@10.11.12.3 "uname -a"
   ```

2. **Check services:**

   ```bash
   ssh root@10.11.12.3 "batctl o"  # Mesh status
   ```

---

## Quick Reference

### Recovery IPs

| Mode | Router IP | PC IP |
|------|-----------|-------|
| Failsafe | 192.168.1.1 | 192.168.1.2/24 |
| D-Link Recovery | 192.168.0.1 | 192.168.0.11/24 |
| Normal OpenWrt | 192.168.1.1 | DHCP or 192.168.1.x/24 |
| Mesh Node 1 | 10.11.12.1 | DHCP or 10.11.12.x/24 |
| Mesh Node 2 | 10.11.12.2 | DHCP or 10.11.12.x/24 |
| Mesh Node 3 | 10.11.12.3 | DHCP or 10.11.12.x/24 |

### Recovery Files

| File | Purpose |
|------|---------|
| `*-recovery.bin` | D-Link bootloader recovery GUI |
| `*-sysupgrade.bin` | Normal OpenWrt upgrades |
| `*-initramfs-kernel.bin` | RAM-based recovery/testing |
| `mesh-nodeN-sysupgrade.bin` | Custom mesh image with config |

### Emergency Commands

```bash
# Reset to defaults (from failsafe or SSH)
firstboot && reboot -f

# Flash recovery image (from working OpenWrt)
cd /tmp
wget http://192.168.1.100/openwrt-...-recovery.bin
sysupgrade -n /tmp/openwrt-...-recovery.bin

# Check flash health
dmesg | grep -i ubi
cat /proc/mtd
```
