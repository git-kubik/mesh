# Initial Mesh Node Setup Guide

This guide walks through the initial setup of the first OpenWrt mesh node before running Ansible automation. Follow these steps to prepare your D-Link DIR-1960 A1 router for mesh network deployment.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Hardware Requirements](#hardware-requirements)
- [Step 1: Flash OpenWrt Firmware](#step-1-flash-openwrt-firmware)
- [Step 2: Initial Network Access](#step-2-initial-network-access)
- [Step 3: Configure Basic Network Settings](#step-3-configure-basic-network-settings)
- [Step 4: Enable SSH Access](#step-4-enable-ssh-access)
- [Step 5: Install Required Packages](#step-5-install-required-packages)
- [Step 6: Verify Prerequisites](#step-6-verify-prerequisites)
- [Next Steps](#next-steps)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have:

- **Hardware**: D-Link DIR-1960 A1 router (or compatible OpenWrt device)
- **Computer**: Connected via Ethernet cable
- **Network**: Internet access for downloading packages
- **Tools**: Web browser or SSH client
- **Time**: ~30 minutes for first node

## Hardware Requirements

### D-Link DIR-1960 A1 Specifications

- **CPU**: MediaTek MT7621AT (880 MHz, dual-core)
- **RAM**: 256 MB
- **Flash**: 128 MB NAND
- **Wireless**: Dual-band (2.4GHz + 5GHz)
- **Ethernet**: 5x Gigabit ports (1 WAN + 4 LAN)

### Port Assignment for Mesh Network

- **WAN**: Internet connection (gateway nodes only)
- **LAN1**: Client devices / AP
- **LAN2**: Reserved
- **LAN3**: Mesh link to Node 2
- **LAN4**: Mesh link to Node 3

## Step 1: Flash OpenWrt Firmware

### Download OpenWrt Firmware

1. Visit the OpenWrt firmware selector: <https://firmware-selector.openwrt.org/>
2. Search for "D-Link DIR-1960 A1"
3. Download the **factory image** (for initial installation)
4. Verify the SHA256 checksum

**Current Recommended Version**: OpenWrt 24.10.4

### Flash via Web Interface (Recommended)

1. **Connect to router**:
   - Power on the DIR-1960
   - Connect computer to LAN port via Ethernet
   - Access router admin panel: `http://192.168.0.1`

2. **Upload firmware**:
   - Log in with default credentials
   - Navigate to **Firmware Upgrade** section
   - Select the downloaded OpenWrt factory image
   - Click **Upload** and wait for flash to complete (~5 minutes)

3. **Wait for reboot**:
   - Router will reboot automatically
   - LED will stabilize when ready (~2 minutes)

### Alternative: Flash via TFTP (Advanced)

If web interface fails, use TFTP recovery mode:

```bash
# Set static IP: 192.168.0.2/24
# Router TFTP IP: 192.168.0.1

# Power on while holding reset button
# Wait for LED to blink
# Upload firmware via TFTP
tftp 192.168.0.1 -c put openwrt-factory.bin
```

## Step 2: Initial Network Access

After OpenWrt boots, access the router:

1. **Set static IP** on your computer:
   - IP: `192.168.1.2`
   - Netmask: `255.255.255.0`
   - Gateway: `192.168.1.1`

2. **Access LuCI web interface**:
   - Open browser: `http://192.168.1.1`
   - Default: **No password set** (root user)

3. **Or connect via SSH**:

   ```bash
   ssh root@192.168.1.1
   # No password required on fresh install
   ```

## Step 3: Configure Basic Network Settings

### Set Root Password (CRITICAL)

**Via Web Interface (LuCI)**:

1. Navigate to **System** → **Administration**
2. Set a **strong root password**
3. Click **Save & Apply**

**Via SSH**:

```bash
ssh root@192.168.1.1
passwd
# Enter new password twice
```

⚠️ **Security Note**: This password will be replaced by Ansible automation. Choose a temporary password for initial setup.

### Configure Management IP

Set a static IP that matches your deployment inventory:

**For Node 1** (from `inventory/hosts.yml`):

```bash
# SSH into router
ssh root@192.168.1.1

# Edit network configuration
vi /etc/config/network

# Find the 'lan' interface, set:
config interface 'lan'
    option proto 'static'
    option ipaddr '10.11.12.1'
    option netmask '255.255.255.0'

# Restart network
/etc/init.d/network restart
```

**Via LuCI**:

1. Navigate to **Network** → **Interfaces**
2. Edit **LAN** interface
3. Set **IPv4 address**: `10.11.12.1`
4. Set **IPv4 netmask**: `255.255.255.0`
5. Click **Save & Apply**

### Update System

Connect the WAN port to internet and update packages:

```bash
# SSH to new IP
ssh root@10.11.12.1

# Update package lists
opkg update

# Upgrade installed packages
opkg list-upgrades | cut -d ' ' -f 1 | xargs opkg upgrade
```

## Step 4: Enable SSH Access

### Install OpenSSH and Remove Dropbear

OpenWrt uses Dropbear by default, but OpenSSH provides better compatibility with Ansible and modern SSH features.

1. **Install OpenSSH**:

   ```bash
   # Update package list
   opkg update

   # Install OpenSSH server and SFTP support
   opkg install openssh-server openssh-sftp-server

   # Optional: Install OpenSSH client (if you need ssh-keygen on the router)
   opkg install openssh-client openssh-keygen
   ```

2. **Configure OpenSSH**:

   Edit `/etc/ssh/sshd_config` to ensure these settings:

   ```bash
   vi /etc/ssh/sshd_config

   # Recommended settings:
   Port 22
   PermitRootLogin yes
   PasswordAuthentication yes
   PubkeyAuthentication yes
   ChallengeResponseAuthentication no
   UsePAM no
   ```

3. **Remove Dropbear and Enable OpenSSH**:

   ```bash
   # Stop and disable dropbear
   /etc/init.d/dropbear stop
   /etc/init.d/dropbear disable

   # Enable and start OpenSSH
   /etc/init.d/sshd enable
   /etc/init.d/sshd start

   # Remove dropbear (optional, but recommended)
   opkg remove dropbear
   ```

4. **Test SSH access** from your workstation:

   ```bash
   ssh root@10.11.12.1
   # Should connect with password
   ```

   **Note**: If you get disconnected during the switch from Dropbear to OpenSSH, wait 30 seconds and reconnect.

### Prepare for SSH Key Authentication

Ansible will configure key-based authentication automatically. For now, ensure password authentication works:

```bash
# Test from your machine
ssh root@10.11.12.1 'echo "SSH working"'
# Should print: SSH working
```

## Step 5: Install Required Packages

Install packages required for mesh networking (Ansible will also install these, but pre-installing speeds up deployment):

```bash
ssh root@10.11.12.1

# Install Batman-adv and dependencies
opkg install kmod-batman-adv batctl

# Install wireless mesh dependencies
opkg install wpad-mesh-openssl

# Install network utilities
opkg install ip-full tcpdump-mini

# Verify installation
batctl -v
# Should show: batctl 2023.x

# Check kernel module
lsmod | grep batman
# Should show: batman_adv
```

## Step 6: Verify Prerequisites

Before proceeding to Ansible deployment, verify:

### Checklist

- [ ] **OpenWrt installed**: `cat /etc/openwrt_release`
- [ ] **Correct IP**: Node 1 = `10.11.12.1`
- [ ] **Root password set**: Can SSH with password
- [ ] **Internet access**: `ping -c 3 8.8.8.8` works
- [ ] **Batman-adv installed**: `batctl -v` shows version
- [ ] **Package manager working**: `opkg list | head` shows packages

### Verification Commands

Run these commands to verify setup:

```bash
# SSH into node
ssh root@10.11.12.1

# System info
uname -a
cat /etc/openwrt_release

# Network config
ip addr show br-lan
ip route

# Package versions
opkg list-installed | grep -E 'batman|batctl|wpad'

# Wireless capabilities
iw list | grep -A 5 "Supported interface modes"
```

### Expected Output

```bash
# OpenWrt version
root@OpenWrt:~# cat /etc/openwrt_release
DISTRIB_ID='OpenWrt'
DISTRIB_RELEASE='24.10.4'

# IP address
root@OpenWrt:~# ip addr show br-lan
br-lan: inet 10.11.12.1/24

# Batman-adv
root@OpenWrt:~# batctl -v
batctl 2023.x

# Kernel module
root@OpenWrt:~# lsmod | grep batman
batman_adv
```

## Next Steps

### For First Node Only

After completing this setup, proceed to Ansible deployment:

```bash
# From your development machine with Docker running

# 1. Generate SSH keys for Ansible
cd docker
./manage-ssh-keys.sh generate

# 2. Copy SSH key to node (will prompt for password)
docker exec mesh_ansible ssh-copy-id root@10.11.12.1

# 3. Test Ansible connectivity
docker exec mesh_ansible ansible mesh_nodes -m ping -l node1

# 4. Deploy configuration to first node
docker exec mesh_ansible ansible-playbook \
    -i /ansible/inventory/hosts.yml \
    /ansible/playbooks/deploy.yml \
    --limit node1
```

### For Subsequent Nodes (Node 2 and Node 3)

Repeat Steps 1-6 with these IP addresses:

- **Node 2**: `10.11.12.2`
- **Node 3**: `10.11.12.3`

After all nodes are set up, deploy to all:

```bash
# Deploy to all nodes
docker exec mesh_ansible ansible-playbook \
    -i /ansible/inventory/hosts.yml \
    /ansible/playbooks/deploy.yml

# Verify deployment
docker exec mesh_ansible ansible-playbook \
    /ansible/playbooks/verify.yml
```

## Troubleshooting

### Cannot Access Router After Flashing

**Issue**: Router not accessible at `192.168.1.1` after OpenWrt flash

**Solutions**:

1. Verify static IP on your computer: `192.168.1.2/24`
2. Check Ethernet cable connection (use LAN port, not WAN)
3. Wait 3-5 minutes for full boot
4. Try factory reset: Hold reset button for 10 seconds while powered on
5. Try TFTP recovery mode

### SSH Connection Refused

**Issue**: `Connection refused` when trying to SSH

**Solutions**:

1. Verify router IP: `ping 10.11.12.1`
2. Check SSH service: `telnet 10.11.12.1 22`
3. Restart dropbear: `/etc/init.d/dropbear restart`
4. Check firewall: `iptables -L INPUT -n`

### Package Installation Fails

**Issue**: `opkg install` fails or hangs

**Solutions**:

1. Update package lists: `opkg update`
2. Check internet connectivity: `ping 8.8.8.8`
3. Verify DNS resolution: `nslookup openwrt.org`
4. Check available space: `df -h`
5. Clear package cache: `rm -rf /tmp/opkg-lists/*`

### Wrong OpenWrt Version

**Issue**: Incompatible OpenWrt version installed

**Solution**:

- Download correct firmware from <https://firmware-selector.openwrt.org/>
- Flash via **sysupgrade** (not factory) if OpenWrt already installed:

  ```bash
  scp openwrt-sysupgrade.bin root@10.11.12.1:/tmp/
  ssh root@10.11.12.1
  sysupgrade -v /tmp/openwrt-sysupgrade.bin
  ```

### Batman-adv Module Not Loading

**Issue**: `lsmod | grep batman` shows nothing

**Solutions**:

1. Manually load module: `modprobe batman-adv`
2. Verify kernel version compatibility
3. Reinstall package: `opkg remove kmod-batman-adv && opkg install kmod-batman-adv`
4. Check kernel logs: `dmesg | grep batman`

### Network Interface Issues

**Issue**: LAN interface not coming up

**Solutions**:

1. Check physical link: `ip link show`
2. Verify network config: `cat /etc/config/network`
3. Restart network: `/etc/init.d/network restart`
4. Check switch config: `swconfig dev switch0 show`

## Additional Resources

### Official Documentation

- **OpenWrt Installation Guide**: <https://openwrt.org/docs/guide-user/installation/generic.flashing>
- **D-Link DIR-1960 A1 Page**: <https://openwrt.org/toh/d-link/dir-1960>
- **Batman-adv Documentation**: <https://www.open-mesh.org/projects/batman-adv/wiki>

### Project Documentation

- **Ansible Quick Start**: `docs/ANSIBLE-QUICKSTART.md`
- **Full Deployment Guide**: `docs/openwrt-batman-mesh-setup.md`
- **Docker Setup**: `docker/README.md`
- **Testing Guide**: `docs/TESTING.md`

### Support

- **GitHub Issues**: <https://github.com/git-kubik/mesh/issues>
- **OpenWrt Forum**: <https://forum.openwrt.org/>
- **Batman-adv Mailing List**: <https://www.open-mesh.org/projects/batman-adv/wiki/Mailing-list>

---

**Document Version**: 1.0
**Last Updated**: November 6, 2025
**Tested With**: OpenWrt 24.10.4, D-Link DIR-1960 A1
