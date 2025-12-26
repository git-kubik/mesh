# Common Issues

This page covers frequently encountered problems and their solutions.

## SSH Connection Issues

### Can't SSH to Node

**Symptom**: `ssh root@10.11.12.1` times out or refuses connection.

**Solutions**:

1. **Check network connectivity**:

   ```bash
   ping 10.11.12.1
   ```

2. **Verify you're on the right network**:

   ```bash
   ip addr show | grep 10.11.12
   # You should have an IP in 10.11.12.x range
   ```

3. **Check SSH key is loaded**:

   ```bash
   ssh-add -l
   # Should show your key
   ssh-add ~/.ssh/openwrt_mesh
   ```

4. **Try with password** (if key auth not yet configured):

   ```bash
   ssh -o PreferredAuthentications=password root@10.11.12.1
   ```

5. **Check firewall on your machine**:

   ```bash
   sudo iptables -L | grep ssh
   ```

### SSH Key Rejected

**Symptom**: `Permission denied (publickey)`.

**Solutions**:

1. **Verify key is deployed**:

   ```bash
   ssh root@10.11.12.1 "cat /etc/dropbear/authorized_keys"
   # Or for OpenSSH:
   ssh root@10.11.12.1 "cat ~/.ssh/authorized_keys"
   ```

2. **Redeploy key**:

   ```bash
   ssh-copy-id -i ~/.ssh/openwrt_mesh root@10.11.12.1
   ```

3. **Check key permissions** (on your machine):

   ```bash
   chmod 600 ~/.ssh/openwrt_mesh
   chmod 644 ~/.ssh/openwrt_mesh.pub
   ```

### Connection Drops During Deployment

**Symptom**: SSH disconnects mid-playbook, deployment incomplete.

**Solutions**:

1. **Run playbook with SKIP_REBOOT**:

   ```bash
   SKIP_REBOOT=true make deploy-node NODE=1
   ```

2. **After network config changes, reconnect to new IP**:

   ```bash
   # Node changed from 192.168.1.1 → 10.11.12.1
   ssh root@10.11.12.1
   ```

3. **Use console access for initial setup**:
   - Connect serial cable
   - 115200 baud, 8N1
   - Configure basic networking first

## Mesh Not Forming

### Nodes Don't See Each Other

**Symptom**: `batctl n` shows no neighbors.

**Solutions**:

1. **Check physical connections**:

   ```bash
   # On each node
   ip link show | grep -E "(lan3|lan4)"
   # Should show "state UP"
   ```

2. **Verify VLAN interfaces exist**:

   ```bash
   ip link show | grep "lan3.100\|lan4.100"
   ```

3. **Check batman interfaces**:

   ```bash
   batctl if
   # Should show mesh interfaces with status "active"
   ```

4. **Verify batman is running**:

   ```bash
   lsmod | grep batman
   # Should show batman_adv module
   ```

5. **Check for MTU issues**:

   ```bash
   ip link show bat0 | grep mtu
   # Should be 1500 (after batman overhead)
   ```

### Wireless Mesh Not Working

**Symptom**: Wired mesh works but wireless backup doesn't.

**Solutions**:

1. **Check 802.11s interface**:

   ```bash
   iw dev mesh0 info
   # Should show type "mesh point"
   ```

2. **Verify mesh is in batman**:

   ```bash
   batctl if | grep mesh0
   ```

3. **Check wireless is on correct channel**:

   ```bash
   iw dev mesh0 info | grep channel
   # All nodes must be on same channel
   ```

4. **Verify mesh ID matches**:

   ```bash
   uci get wireless.mesh.mesh_id
   # Must match on all nodes
   ```

5. **Reload wireless**:

   ```bash
   wifi reload
   sleep 5
   batctl n
   ```

### Poor Mesh Quality (Low TQ)

**Symptom**: `batctl o` shows TQ values below 200.

**Solutions**:

1. **Check for interference** (wireless):

   ```bash
   iw dev wlan0 survey dump
   # Look for high "noise" values
   ```

2. **Check cable quality** (wired):

   ```bash
   ethtool lan3 | grep -i speed
   # Should show 1000Mb/s
   ```

3. **Verify VLAN tagging**:

   ```bash
   # On switch, check VLAN 100 tagging
   # On node:
   tcpdump -i lan3 -e | grep vlan
   ```

## WiFi Issues

### 5GHz AP Not Visible

**Symptom**: Can't see the client SSID.

**Solutions**:

1. **Check radio is enabled**:

   ```bash
   uci get wireless.radio1.disabled
   # Should be 0 or not set
   ```

2. **Check AP interface**:

   ```bash
   iw dev
   # Should show wlan1 with type "AP"
   ```

3. **Verify channel is valid for your region**:

   ```bash
   iw reg get
   # Check if channel 36 is allowed
   ```

4. **Restart wireless**:

   ```bash
   wifi reload
   ```

### Clients Can't Connect

**Symptom**: SSID visible but authentication fails.

**Solutions**:

1. **Verify password** (on node):

   ```bash
   uci get wireless.client.key
   ```

2. **Check encryption matches**:

   ```bash
   uci get wireless.client.encryption
   # Usually "psk2+ccmp" for WPA2
   ```

3. **Check hostapd is running**:

   ```bash
   pgrep hostapd
   ps | grep hostapd
   ```

4. **Review hostapd logs**:

   ```bash
   logread | grep hostapd | tail -20
   ```

### Clients Not Getting DHCP

**Symptom**: Connected but no IP address.

**Solutions**:

1. **Check dnsmasq is running**:

   ```bash
   pgrep dnsmasq
   ```

2. **Verify DHCP pool**:

   ```bash
   uci show dhcp.lan
   ```

3. **Check bridge configuration**:

   ```bash
   brctl show br-lan
   # wlan1 should be listed
   ```

4. **Restart DHCP server**:

   ```bash
   /etc/init.d/dnsmasq restart
   ```

5. **Check DHCP leases**:

   ```bash
   cat /tmp/dhcp.leases
   ```

## VLAN Issues

### VLAN Interfaces Missing

**Symptom**: `ip link show` doesn't show VLAN interfaces.

**Solutions**:

1. **Check 8021q module**:

   ```bash
   lsmod | grep 8021q
   modprobe 8021q
   ```

2. **Verify network config**:

   ```bash
   uci show network | grep vlan
   ```

3. **Recreate VLAN interfaces**:

   ```bash
   /etc/init.d/network restart
   ```

### VLAN Tagging Mismatch

**Symptom**: Traffic not reaching destination, works without VLANs.

**Solutions**:

1. **Verify switch VLAN config** matches node config
2. **Check PVID settings** on switch
3. **Use tcpdump to verify tagging**:

   ```bash
   tcpdump -i lan3 -e vlan
   ```

### IoT Devices Can Reach Main Network

**Symptom**: VLAN isolation not working.

**Solutions**:

1. **Check firewall zones**:

   ```bash
   uci show firewall | grep iot
   ```

2. **Verify forward policy**:

   ```bash
   uci get firewall.@zone[X].forward
   # Should be "REJECT" for IoT
   ```

3. **Check inter-zone rules**:

   ```bash
   iptables -L FORWARD -v
   ```

## Gateway Issues

### All Traffic Goes Through One Node

**Symptom**: Gateway list shows only one gateway selected.

**Solutions**:

1. **Check gateway mode on all nodes**:

   ```bash
   batctl gw_mode
   # Should be "server" on all nodes
   ```

2. **Verify gateway bandwidth configured**:

   ```bash
   uci get network.bat0.gw_bandwidth
   ```

3. **Check if WAN is up on all nodes**:

   ```bash
   ping -I wan 1.1.1.1
   ```

### Internet Not Working

**Symptom**: Can ping mesh IPs but not internet.

**Solutions**:

1. **Check default route**:

   ```bash
   ip route show default
   ```

2. **Verify NAT rules**:

   ```bash
   nft list table nat
   # Or: iptables -t nat -L
   ```

3. **Check WAN interface**:

   ```bash
   ip addr show wan
   ```

4. **Test DNS**:

   ```bash
   nslookup google.com 1.1.1.1
   ```

## Management Network Issues

### Intermittent Connectivity to Nodes

**Symptom**: Pings to node management IPs (10.11.10.x) sometimes fail, then work again. SSH sessions drop randomly.

**Cause**: In multi-switch topologies, short ARP cache times (default 30-60 seconds) can cause race conditions during MAC/ARP relearning, leading to brief connectivity outages.

**Solution**: Increase ARP cache times on all mesh nodes:

```bash
# Check current settings
cat /proc/sys/net/ipv4/neigh/br-mgmt/gc_stale_time
cat /proc/sys/net/ipv4/neigh/br-mgmt/base_reachable_time_ms

# Apply fix (if not deployed via Ansible)
sysctl -w net.ipv4.neigh.br-mgmt.gc_stale_time=300
sysctl -w net.ipv4.neigh.br-mgmt.base_reachable_time_ms=120000

# Make persistent
cat >> /etc/sysctl.conf << 'EOF'
# ARP cache settings for management network (br-mgmt)
net.ipv4.neigh.br-mgmt.gc_stale_time = 300
net.ipv4.neigh.br-mgmt.base_reachable_time_ms = 120000
EOF
```

**Note**: This fix is automatically applied by Ansible during deployment (see `group_vars/all.yml` for configuration).

**Verification**:

```bash
# Test all nodes from management network
for ip in 10.11.10.1 10.11.10.2 10.11.10.3; do
  ping -c 10 $ip
done
# All should show 0% packet loss
```

### Can't Reach Node from Different Switch

**Symptom**: Devices on Switch B can't reach Node 1 (connected to Switch A), but can reach other nodes.

**Solutions**:

1. **Check switch VLAN 10 configuration**:
   - VLAN 10 must be properly trunked between switches
   - Management traffic uses VLAN 10

2. **Verify BLA (Bridge Loop Avoidance) is working**:

   ```bash
   batctl cl   # Check claim table
   batctl bl   # Check backbone table
   ```

3. **Check ARP cache settings** (see above)

4. **Verify the path**:

   ```bash
   # On the affected device
   ip neigh show | grep 10.11.10
   # Check if MAC addresses are correct
   ```

## Performance Issues

### Slow Network Speeds

**Solutions**:

1. **Check mesh TQ values**:

   ```bash
   batctl o
   # Low values indicate poor link quality
   ```

2. **Test direct link speed**:

   ```bash
   # On one node:
   nc -l -p 5001 > /dev/null
   # On another:
   dd if=/dev/zero bs=1M count=100 | nc 10.11.12.1 5001
   ```

3. **Check for CPU overload**:

   ```bash
   top
   ```

4. **Verify Gigabit negotiation**:

   ```bash
   cat /sys/class/net/lan3/speed
   # Should show 1000
   ```

### High Latency

**Solutions**:

1. **Check hop count**:

   ```bash
   batctl traceroute <destination-MAC>
   ```

2. **Look for routing loops**:

   ```bash
   batctl o
   # Check for inconsistent next hops
   ```

3. **Check for interference** (wireless):

   ```bash
   iw dev wlan0 survey dump
   ```

## Getting More Help

If these solutions don't resolve your issue:

1. **Gather diagnostic info**:

   ```bash
   # Run audit playbook
   make audit-node NODE=1
   ```

2. **Check logs**:

   ```bash
   logread | tail -100
   dmesg | tail -50
   ```

3. **Open a GitHub issue** with:
   - OpenWrt version
   - Exact error messages
   - Output of diagnostic commands
   - Steps to reproduce

See also: [Debugging Guide](debugging.md) for advanced troubleshooting techniques.
