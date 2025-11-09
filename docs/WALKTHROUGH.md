# OpenWrt Mesh Network Setup - Complete Walkthrough

This guide walks you through setting up your 3-node OpenWrt mesh network from scratch, step-by-step.

## 📋 Prerequisites

**What you need:**

- 3x D-Link DIR-1960 A1 routers (fresh from factory or reset)
- 1x Computer with Ethernet port
- 1x Ethernet cable
- Cloned this repository
- SSH access configured

**Before we start:**

```bash
cd /home/m/repos/mesh/openwrt-mesh-ansible
```

**Important:** All fresh OpenWrt routers start with the same IP address (192.168.1.1), so you can only configure **ONE router at a time**.

---

## 🟢 NODE 1 SETUP

### Step 1: Prepare Your Workstation

**Find your Ethernet interface:**

```bash
ip link show
```

You'll see something like:

```
1: lo: <LOOPBACK,UP,LOWER_UP>...
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>...  ← This one!
3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP>...
```

**Set static IP on your workstation:**

```bash
# Replace 'eth0' with YOUR interface name
sudo ip addr add 192.168.1.100/24 dev eth0
sudo ip link set eth0 up
```

**Alternative for macOS:**

```bash
sudo ifconfig en0 192.168.1.100 netmask 255.255.255.0
```

**Alternative using NetworkManager:**

```bash
nmcli con add type ethernet ifname eth0 con-name openwrt-setup \
  ip4 192.168.1.100/24
```

**Verify:**

```bash
ip addr show eth0
# Should show: inet 192.168.1.100/24
```

### Step 2: Connect to Node1

**Physical connection:**

1. Power on the first D-Link router
2. Wait ~60 seconds for it to boot (watch LEDs - should stabilize)
3. Connect Ethernet cable: **Your computer → Any LAN port on router** (NOT the WAN port!)

**Test connectivity:**

```bash
ping -c 3 192.168.1.1
```

**Expected output:**

```
64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.5 ms
64 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=0.4 ms
64 bytes from 192.168.1.1: icmp_seq=3 ttl=64 time=0.3 ms
```

**If ping fails:**

- Check cable is properly connected
- Verify your IP: `ip addr show eth0`
- Try web UI: Open browser to `http://192.168.1.1`
- Power cycle the router and wait 2 minutes

### Step 3: Update Inventory for Initial Access

**Edit the inventory file:**

```bash
nano inventory/hosts.yml
```

**Find the node1 section and change the IP temporarily:**

```yaml
node1:
  ansible_host: 192.168.1.1  # ← Change from 10.11.12.1 to this
  node_ip: 10.11.12.1        # ← Leave this unchanged
  node_id: 1
  mesh_ports:
    lan3: node2
    lan4: node3
```

**Save and exit:**

- Nano: Ctrl+X, then Y, then Enter
- Vim: Escape, then `:wq`, then Enter

### Step 4: Check Connectivity

**Run the connectivity check:**

```bash
make check-node1
```

**Expected output:**

```
================================================================================
CONNECTIVITY CHECK SUMMARY: node1
================================================================================
Node IP: 192.168.1.1
User: root
Python: /usr/bin/python3

Checks:
  [✓] Network - SSH port reachable
  [✓] Authentication - SSH login successful
  [✓] Python - Interpreter available
  [✓] OpenWrt - Valid OpenWrt system
  [✓] Commands - Execution working

Overall Status: READY

✅ Node is ready for audit and deployment
================================================================================
```

**If it fails:**

- **Connection timeout**: Check cable, verify IP is set correctly
- **Authentication failed**: Try manual SSH: `ssh root@192.168.1.1`
  - Default password is usually blank (just press Enter)
  - Or check your router's default password
- **Python not found**: Don't worry, the audit can still run using raw commands

### Step 5: Run Audit

**Execute the audit playbook:**

```bash
make audit-node1
```

**This will:**

1. Connect to the node
2. Identify hardware (model, CPU, RAM, storage)
3. List all installed packages
4. Compare against project requirements
5. Generate JSON report and preparation script

**Expected output:**

```
================================================================================
AUDIT SUMMARY: node1
================================================================================
Hardware:
  Model: D-Link DIR-1960 A1
  Memory: 512 MB
  Storage: 128M
  OpenWrt: 23.05.2
  Kernel: 5.15.150

Package Status:
  Total Installed: 87
  Required Installed: 2/5
  Missing Required: 3
  Conflicts Found: 1

Audit Status: HAS_CONFLICTS

Missing Packages:
  - kmod-batman-adv
  - batctl
  - wpad-mesh-mbedtls

Conflicting Packages (must remove):
  - wpad-basic-mbedtls

Reports Generated:
  - ./audit_reports/node1_audit_2024-11-09_14-30-45.json
  - ./audit_reports/node1_prepare.sh
================================================================================
```

**Check the detailed report:**

```bash
# List generated reports
ls -lh audit_reports/

# View JSON report (if you have jq installed)
cat audit_reports/node1_audit_*.json | jq .

# View recommendations
cat audit_reports/node1_audit_*.json | jq .recommendations
```

**Example recommendations:**

```json
{
  "status": "needs_packages",
  "actions_required": true,
  "remove_packages": ["wpad-basic-mbedtls"],
  "install_packages": ["kmod-batman-adv", "batctl", "wpad-mesh-mbedtls"]
}
```

### Step 6: Execute Preparation Script (If Needed)

**If audit shows "needs_packages" or "has_conflicts", run the preparation script:**

**Copy script to the node:**

```bash
scp audit_reports/node1_prepare.sh root@192.168.1.1:/tmp/
```

**Execute the script on the node:**

```bash
ssh root@192.168.1.1 'sh /tmp/node1_prepare.sh'
```

**Watch the output:**

```
================================================================================
OpenWrt Mesh Node Preparation Script
================================================================================
Node: node1
Hardware: D-Link DIR-1960 A1
OpenWrt: 23.05.2
Generated: 2024-11-09_14-30-45
================================================================================

[INFO] Running pre-flight checks...
✅ SUCCESS: Pre-flight checks completed

[INFO] Creating backup of current configuration...
✅ SUCCESS: Backup created: /tmp/backup-before-prep-20241109-143045.tar.gz

[INFO] Updating package lists from repositories...
✅ SUCCESS: Package lists updated successfully

[INFO] Removing conflicting packages...
Packages to remove (1):
  - wpad-basic-mbedtls

[INFO] Removing wpad-basic-mbedtls...
✅ SUCCESS: Removed wpad-basic-mbedtls

[INFO] Installing required packages...
Packages to install (3):
  - kmod-batman-adv
  - batctl
  - wpad-mesh-mbedtls

[INFO] Installing all required packages...
✅ SUCCESS: All required packages installed successfully

[INFO] Verifying installation...
✅ SUCCESS: All required packages verified

================================================================================
PREPARATION COMPLETE
================================================================================
✅ Node node1 is ready for Ansible deployment

Summary:
  - Backup created: /tmp/backup-before-prep-20241109-143045.tar.gz
  - Removed 1 conflicting package(s)
  - Installed 3 required package(s)
  - All required packages verified

Next Steps:
  1. Download backup file from node
  2. Re-run audit playbook to verify readiness
  3. Proceed with full deployment
================================================================================
```

**Download the backup (recommended):**

```bash
# Create backups directory if it doesn't exist
mkdir -p backups

# Download the backup
scp root@192.168.1.1:/tmp/backup-before-prep-*.tar.gz ./backups/
```

### Step 7: Re-Audit to Verify

**Run the audit again to confirm readiness:**

```bash
make audit-node1
```

**Expected output:**

```
Audit Status: READY

✅ Node is ready for Ansible deployment
Next steps:
  - Run deployment: make deploy-node1
```

### Step 8: Deploy Configuration

**This step changes the node's IP from 192.168.1.1 to 10.11.12.1:**

```bash
make deploy-node1
```

**What happens during deployment:**

1. Creates automatic backup (sysupgrade format)
2. Updates package repositories
3. Ensures all required packages are installed
4. Sets hostname to `mesh-node1`
5. Configures network interfaces:
   - WAN: DHCP client
   - LAN: 10.11.12.1/24
   - Batman-adv mesh bridge
   - VLAN interfaces (if enabled)
6. Configures wireless:
   - 2.4GHz: Mesh network (backup)
   - 5GHz: Client AP with 802.11r roaming
7. Configures DHCP (10.11.12.100-149)
8. Configures firewall rules
9. Restarts all services

**Expected output:**

```
PLAY [Deploy OpenWrt Mesh Configuration] ***************************************

TASK [Wait for nodes to be reachable] ******************************************
ok: [node1]

TASK [Create backup directory] *************************************************
changed: [node1]

... (many tasks) ...

TASK [Reload network services] **************************************************
changed: [node1]

PLAY RECAP **********************************************************************
node1                      : ok=25   changed=15   unreachable=0    failed=0
```

**Wait for completion** - This takes ~2-3 minutes

**Important:** After deployment completes, the node will restart services and the IP will change to 10.11.12.1. You will lose connectivity to 192.168.1.1 - this is expected!

### Step 9: DISCONNECT Node1

**CRITICAL STEP:**

1. **Physically unplug** the Ethernet cable from node1
2. Leave node1 powered on (don't turn it off!)
3. Set it aside

**Why?** Node1 is now configured with IP 10.11.12.1. We need to disconnect it so we can configure node2 (which will also start at 192.168.1.1).

### Step 10: Reset Your Workstation Network

**Remove the static IP:**

```bash
# Ubuntu/Debian
sudo ip addr del 192.168.1.100/24 dev eth0

# macOS
sudo ipconfig set en0 DHCP

# NetworkManager
nmcli con delete openwrt-setup
```

**Verify it's removed:**

```bash
ip addr show eth0
# Should NOT show 192.168.1.100
```

### Step 11: Update Inventory to Final IP

**Edit the inventory file again:**

```bash
nano inventory/hosts.yml
```

**Change node1 back to its mesh network IP:**

```yaml
node1:
  ansible_host: 10.11.12.1  # ← Change back to this
  node_ip: 10.11.12.1
  node_id: 1
  mesh_ports:
    lan3: node2
    lan4: node3
```

**Save and exit**

### Step 12: Set Node1 Aside

**Node1 is now configured!**

- Keep it powered on
- Leave it disconnected from your computer
- We'll connect all the mesh links after all nodes are configured

---

## 🔵 NODE 2 SETUP

Now we repeat the exact same process for node2. The key difference is that we're working with a different physical router, but it also starts at 192.168.1.1.

### Step 1: Prepare Workstation (Again)

**Set static IP again:**

```bash
sudo ip addr add 192.168.1.100/24 dev eth0
sudo ip link set eth0 up
```

### Step 2: Connect Node2

**Physical connection:**

1. Power on the **second** D-Link router
2. Wait ~60 seconds for boot
3. Connect cable: **Your computer → Node2's LAN port**

**Test connectivity:**

```bash
ping -c 3 192.168.1.1  # Same IP as node1 had before!
```

### Step 3: Update Inventory

```bash
nano inventory/hosts.yml
```

**Change node2's IP temporarily:**

```yaml
node2:
  ansible_host: 192.168.1.1  # ← Temporary for initial setup
  node_ip: 10.11.12.2        # ← Leave unchanged
  node_id: 2
  mesh_ports:
    lan3: node1
    lan4: node3
```

### Step 4: Check Connectivity

```bash
make check-node2
```

**Expected: Same READY output as node1**

### Step 5: Run Audit

```bash
make audit-node2
```

### Step 6: Execute Preparation Script (If Needed)

```bash
# If audit shows needs_packages or has_conflicts:
scp audit_reports/node2_prepare.sh root@192.168.1.1:/tmp/
ssh root@192.168.1.1 'sh /tmp/node2_prepare.sh'

# Download backup
scp root@192.168.1.1:/tmp/backup-before-prep-*.tar.gz ./backups/
```

### Step 7: Re-Audit

```bash
make audit-node2
# Should show: READY
```

### Step 8: Deploy Configuration

```bash
make deploy-node2  # Changes node IP to 10.11.12.2
```

**Wait for completion (~2-3 minutes)**

### Step 9: Disconnect Node2

**Physically unplug the cable from node2**

### Step 10: Reset Network

```bash
sudo ip addr del 192.168.1.100/24 dev eth0
```

### Step 11: Update Inventory

```bash
nano inventory/hosts.yml
```

```yaml
node2:
  ansible_host: 10.11.12.2  # ← Back to mesh IP
  node_ip: 10.11.12.2
  node_id: 2
```

---

## 🟡 NODE 3 SETUP

**One more time! Same process for node3:**

### Quick Steps

```bash
# 1. Set workstation IP
sudo ip addr add 192.168.1.100/24 dev eth0

# 2. Connect node3, wait for boot
# Physical: Power on third router, connect cable to LAN port

# 3. Test connectivity
ping -c 3 192.168.1.1

# 4. Update inventory
nano inventory/hosts.yml
# Set: node3.ansible_host = 192.168.1.1

# 5. Check connectivity
make check-node3

# 6. Audit
make audit-node3

# 7. Prepare (if needed)
scp audit_reports/node3_prepare.sh root@192.168.1.1:/tmp/
ssh root@192.168.1.1 'sh /tmp/node3_prepare.sh'
scp root@192.168.1.1:/tmp/backup-before-prep-*.tar.gz ./backups/

# 8. Deploy
make deploy-node3  # Changes IP to 10.11.12.3

# 9. Disconnect node3
# Unplug cable

# 10. Reset network permanently
sudo ip addr del 192.168.1.100/24 dev eth0
# Restore your normal network
sudo dhclient eth0
# Or: nmcli con up <your-normal-connection>

# 11. Update inventory
nano inventory/hosts.yml
# Set: node3.ansible_host = 10.11.12.3
```

---

## 🌐 CONNECT THE MESH

All three nodes are now configured with their unique IPs. Time to wire them together!

### Physical Wiring - Ring Topology

**Connect the mesh links according to this topology:**

```
        node1 (10.11.12.1)
         /  \
    LAN3/    \LAN4
       /      \
      /        \
 node2 -------- node3
(10.11.12.2) (10.11.12.3)
    LAN4 - LAN3
```

**Detailed connections:**

**Node1:**

- **LAN3** → Node2's **LAN3** or **LAN4** (your choice)
- **LAN4** → Node3's **LAN3** or **LAN4** (your choice)

**Node2:**

- One port (LAN3 or LAN4) → Node1 (already connected above)
- Other port → Node3

**Node3:**

- One port → Node2 (already connected above)
- Other port → Node1 (already connected above)

**Result:** Full ring topology with 3 wired mesh links

### Connect Your Workstation to the Mesh

**Option A: Direct connection to a node (recommended for testing)**

```bash
# Connect to any LAN1 or LAN2 port on any node
# Your computer will automatically get DHCP address: 10.11.12.100-249
```

**Verify you got an IP:**

```bash
ip addr show eth0
# Should show something like: inet 10.11.12.123/24
```

**Option B: Add static route (if on different network)**

```bash
# If your workstation is on a different network
sudo ip route add 10.11.12.0/24 via <gateway-ip>
```

---

## ✅ VERIFY THE MESH

### Check Connectivity to All Nodes

```bash
make check-all
```

**Expected output: All 3 nodes show READY**

```
================================================================================
CONNECTIVITY CHECK SUMMARY: node1
================================================================================
Overall Status: READY

================================================================================
CONNECTIVITY CHECK SUMMARY: node2
================================================================================
Overall Status: READY

================================================================================
CONNECTIVITY CHECK SUMMARY: node3
================================================================================
Overall Status: READY
```

**If any node shows FAILED:**

1. Check physical connections
2. Verify node is powered on
3. Check inventory has correct IP (10.11.12.X)
4. Try ping: `ping 10.11.12.X`
5. Try manual SSH: `ssh root@10.11.12.X`

### Verify Mesh Deployment

```bash
make verify
```

**This checks:**

- SSH connectivity
- System uptime
- Batman-adv module loaded
- Mesh interfaces configured
- Gateway status
- Neighbor detection

### Check Batman-adv Status

```bash
make batman-status
```

**Expected output:**

```
=== Batman Interfaces ===
node1:
bat0: active
mesh-lan3: active (batman-adv)
mesh-lan4: active (batman-adv)
mesh0: active (batman-adv)

node2:
bat0: active
mesh-lan3: active (batman-adv)
mesh-lan4: active (batman-adv)
mesh0: active (batman-adv)

node3:
bat0: active
mesh-lan3: active (batman-adv)
mesh-lan4: active (batman-adv)
mesh0: active (batman-adv)

=== Batman Originators ===
node1:
Originator       last-seen (#/255) Nexthop          [outgoingIF]
mesh-node2       0.380s   (255)   mesh-node2       [mesh-lan3]
mesh-node3       0.520s   (255)   mesh-node3       [mesh-lan4]

node2:
Originator       last-seen (#/255) Nexthop          [outgoingIF]
mesh-node1       0.290s   (255)   mesh-node1       [mesh-lan3]
mesh-node3       0.410s   (255)   mesh-node3       [mesh-lan4]

node3:
Originator       last-seen (#/255) Nexthop          [outgoingIF]
mesh-node1       0.340s   (255)   mesh-node1       [mesh-lan4]
mesh-node2       0.470s   (255)   mesh-node2       [mesh-lan3]

=== Gateway Status ===
node1:
Originator       TQ (#/255) Nexthop          [outgoingIF] Bandwidth
=> mesh-node1    255        mesh-node1       [bat0]       100.0/100.0 MBit
   mesh-node2    255        mesh-node2       [mesh-lan3]  100.0/100.0 MBit
   mesh-node3    255        mesh-node3       [mesh-lan4]  100.0/100.0 MBit

(Similar output for node2 and node3)
```

**What this means:**

- **Batman Interfaces**: All mesh interfaces are active ✅
- **Originators**: Each node sees the other 2 nodes with TQ=255 (100% quality) ✅
- **Gateways**: All 3 nodes are functioning as gateways ✅

**If you don't see all nodes:**

1. Check physical cable connections
2. Verify cables are plugged into correct ports (LAN3/LAN4)
3. Wait 60 seconds and try again (batman-adv takes time to discover)
4. Check logs: `make logs`

### Test Wireless

**Scan for WiFi networks on your phone/laptop:**

You should see these SSIDs:

- **HA-Network-5G** (appears 3 times - one from each node)
  - Frequency: 5GHz
  - Security: WPA2-PSK
  - Password: From `group_vars/all.yml` → `client_password`

If VLANs are enabled, you'll also see:

- **HA-Management** (2.4GHz, VLAN 10)
- **HA-Guest** (5GHz, VLAN 30, isolated)

**Connect a device:**

1. Connect to **HA-Network-5G**
2. Enter the password
3. You should get IP: 10.11.12.100-249
4. Test internet: `ping 8.8.8.8`
5. Walk around - device should roam seamlessly (802.11r)

### Test Internet Connectivity

**From your computer (connected to mesh):**

```bash
# Test DNS
ping -c 3 google.com

# Test gateway failover
# 1. Note which node your computer is connected to
# 2. Unplug that node's WAN cable
# 3. Ping should continue working (using other node's WAN)
# 4. Replug WAN cable
```

---

## 🎉 SUCCESS - YOU'RE DONE

Your mesh network is now fully operational!

### What You Have

✅ **3-node mesh network**

- Node1: 10.11.12.1
- Node2: 10.11.12.2
- Node3: 10.11.12.3

✅ **Batman-adv routing**

- Automatic path selection
- Self-healing network
- Load balancing

✅ **Redundant connectivity**

- 3x wired mesh links (ring topology)
- 2.4GHz wireless mesh backup
- Multi-gateway WAN failover

✅ **Client access**

- 5GHz WiFi AP on all nodes
- 802.11r fast roaming
- DHCP from any node

✅ **Optional VLANs**

- Management network (if enabled)
- Guest network with isolation (if enabled)

---

## 📊 Monitoring & Maintenance

### Daily Monitoring

**Check mesh health:**

```bash
make batman-status
```

**Check node status:**

```bash
make verify
make uptime
```

**View logs:**

```bash
make logs
```

### Making Configuration Changes

**Edit configuration:**

```bash
# 1. Edit the configuration
nano group_vars/all.yml

# 2. Deploy to all nodes
make deploy

# Or deploy to specific node
make deploy-node1

# 3. Verify changes
make verify
```

**Example: Change WiFi password**

```yaml
# group_vars/all.yml
client_password: NewSecurePassword123!
```

```bash
make deploy-wireless  # Deploy only wireless config
```

### Backing Up

**Backup all nodes:**

```bash
make backup
```

**Backups are stored in:** `./backups/YYYY-MM-DD/`

### Updating Packages

**Check for updates:**

```bash
make update-check
```

**Install updates:**

```bash
make update
```

**This updates nodes one at a time** to maintain mesh availability.

---

## 🆘 Troubleshooting

### Node Won't Respond After Deploy

**Problem:** Can't reach node at 10.11.12.X after deployment

**Solutions:**

1. **Wait longer** - Services can take 2-3 minutes to fully restart
2. **Check physical connections** - Ensure cables are plugged in
3. **Power cycle** - Unplug power, wait 10 seconds, replug
4. **Try the old IP** - If deploy didn't complete, try `ssh root@192.168.1.1`
5. **Check from another node:**

   ```bash
   ssh root@10.11.12.1  # From node1
   ping 10.11.12.2      # Check if node2 responds
   ```

6. **Factory reset** - Press reset button for 10 seconds, start over

### Can't Connect to 192.168.1.1 Initially

**Problem:** Ping or SSH to 192.168.1.1 fails

**Solutions:**

1. **Verify your workstation IP:**

   ```bash
   ip addr show eth0
   # Must show: 192.168.1.100/24
   ```

2. **Check cable:**
   - Ensure cable is good (try a different one)
   - Connected to LAN port, NOT WAN
   - Router LEDs show activity

3. **Router not booted:**
   - Wait 2 full minutes after power on
   - Watch for stable LEDs

4. **Try web interface:**
   - Open browser: `http://192.168.1.1`
   - Should see OpenWrt LuCI interface

5. **Router might have different default IP:**
   - Some routers use 192.168.0.1
   - Try: `ping 192.168.0.1`

6. **Factory reset the router:**
   - Press and hold reset button for 10 seconds
   - Wait 2 minutes for reboot

### Lost Connection Mid-Deploy

**Problem:** SSH connection dropped during `make deploy`

**Don't panic!** The playbook will continue running on the node.

**What to do:**

1. **Wait 5 minutes** for the deployment to complete
2. **Try the new IP:** `ssh root@10.11.12.X`
3. **If that works:** Deployment succeeded! Continue to next step
4. **If that fails:**
   - Connect directly to node's LAN port
   - Try: `ssh root@192.168.1.1`
   - Re-run: `make deploy-nodeX`

### Mesh Not Forming

**Problem:** Batman-adv shows only local node, can't see neighbors

**Check:**

1. **Physical connections:**

   ```bash
   # On each node, check link status
   ssh root@10.11.12.1 'ip link show'
   # mesh-lan3 and mesh-lan4 should be UP
   ```

2. **Batman interfaces:**

   ```bash
   ssh root@10.11.12.1 'batctl if'
   # Should show: mesh-lan3, mesh-lan4, mesh0
   ```

3. **Wait longer:**
   - Batman-adv can take 1-2 minutes to discover neighbors
   - Try: `watch -n 5 'make batman-status'`

4. **Restart network:**

   ```bash
   make restart-network
   # Wait 2 minutes
   make batman-status
   ```

5. **Check logs for errors:**

   ```bash
   make logs
   # Look for batman-adv or network errors
   ```

### WiFi Not Visible

**Problem:** Can't see HA-Network-5G SSID

**Solutions:**

1. **Check wireless status:**

   ```bash
   ssh root@10.11.12.1 'wifi status'
   ```

2. **Restart wireless:**

   ```bash
   make restart-wireless
   # Wait 30 seconds
   ```

3. **Check configuration:**

   ```bash
   ssh root@10.11.12.1 'cat /etc/config/wireless'
   ```

4. **Re-deploy wireless config:**

   ```bash
   make deploy-wireless
   ```

5. **Check 5GHz support:**
   - Some devices don't show 5GHz if channel is restricted
   - Try 2.4GHz SSIDs (if VLAN enabled)

### Internet Not Working on Mesh

**Problem:** Connected to mesh but no internet

**Check:**

1. **WAN connection on nodes:**

   ```bash
   # Check if any node has internet
   ssh root@10.11.12.1 'ping -c 3 8.8.8.8'
   ```

2. **Gateway status:**

   ```bash
   make batman-status
   # All nodes should show as gateways
   ```

3. **DNS:**

   ```bash
   # From a client device
   ping 8.8.8.8        # Test raw internet
   ping google.com     # Test DNS
   ```

4. **Firewall:**

   ```bash
   make deploy-firewall
   ```

5. **DHCP:**

   ```bash
   # Renew DHCP lease
   sudo dhclient -r eth0
   sudo dhclient eth0
   ```

---

## 📚 Next Steps

### Learn More

- **[NODE-AUDIT.md](NODE-AUDIT.md)** - Detailed audit system documentation
- **[openwrt-batman-mesh-setup.md](openwrt-batman-mesh-setup.md)** - Technical deep dive
- **[ANSIBLE-QUICKSTART.md](ANSIBLE-QUICKSTART.md)** - Ansible basics

### Customize Your Network

**Change WiFi settings:**

```bash
nano group_vars/all.yml
# Edit: client_ssid, client_password, client_channel
make deploy-wireless
```

**Enable VLANs:**

```bash
nano group_vars/all.yml
# Set: enable_vlans: true
# Configure: vlans.management, vlans.guest
make deploy
```

**Adjust batman-adv settings:**

```bash
nano group_vars/all.yml
# Edit: batman_gw_bandwidth, batman_hop_penalty
make deploy-network
```

### Advanced Configuration

**Add more nodes:**

1. Add to `inventory/hosts.yml`
2. Wire mesh links
3. Run through setup process

**Monitor with graphs:**

- Install collectd
- Set up Grafana dashboard
- Monitor batman-adv metrics

**Set up continuous deployment:**

- Use GitHub Actions
- Auto-deploy on git push
- Automated testing

---

## 🎓 Understanding What You Built

### Network Architecture

```
Internet
   |
   | WAN (DHCP)
   |
[Node1] ←→ [Node2] ←→ [Node3]
   ↓         ↓         ↓
Batman-adv mesh bridge (bat0)
   ↓         ↓         ↓
LAN bridge (br-lan) 10.11.12.0/24
   ↓         ↓         ↓
Client devices (DHCP 10.11.12.100-249)
```

### How Batman-adv Works

1. **Mesh links** (LAN3, LAN4, wireless) send broadcast packets
2. **Neighbor discovery** - Nodes detect each other
3. **Route calculation** - Best path selected based on quality (TQ)
4. **Bridge mode** - All nodes appear on same network (10.11.12.0/24)
5. **Gateway selection** - Clients use best available WAN gateway
6. **Automatic failover** - If one link/gateway fails, traffic reroutes

### Why This Setup is Powerful

✅ **Self-healing** - Network reconfigures if links fail

✅ **Load balancing** - Traffic spreads across multiple paths

✅ **Seamless roaming** - Devices switch nodes transparently

✅ **Redundant gateways** - Any node's WAN can serve all clients

✅ **Scalable** - Easy to add more nodes

✅ **Infrastructure-as-Code** - All config in version control

---

**Congratulations! You've successfully deployed a production-ready mesh network!** 🎊

For questions or issues, check the docs or review the generated audit reports.
