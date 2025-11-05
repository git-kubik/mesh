# OpenWrt Mesh Network - Ansible Deployment

Automated deployment and management of a highly-available OpenWrt mesh network using Ansible.

## Overview

This Ansible project automates the deployment and configuration of a 3-node OpenWrt mesh network with:

- Full ring topology with wired connections
- 2.4GHz wireless mesh backup
- Multi-gateway high availability
- 5GHz client access point with roaming
- Batman-adv mesh routing
- Optional VLAN support

## Directory Structure

```
openwrt-mesh-ansible/
├── inventory/
│   └── hosts.yml              # Node definitions and connection info
├── group_vars/
│   └── all.yml                # Common configuration variables
├── host_vars/                 # Node-specific variables (optional)
├── templates/
│   ├── network.j2             # Network configuration template
│   ├── wireless.j2            # Wireless configuration template
│   ├── dhcp.j2                # DHCP/DNS configuration template
│   └── firewall.j2            # Firewall configuration template
├── playbooks/
│   ├── deploy.yml             # Main deployment playbook
│   ├── verify.yml             # Verification playbook
│   ├── backup.yml             # Backup playbook
│   └── update.yml             # Update playbook
├── backups/                   # Backup storage (created automatically)
└── README.md                  # This file
```

## Prerequisites

### Control Machine (Your Workstation)

1. **Ansible installed:**

   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install ansible

   # macOS
   brew install ansible

   # Python pip
   pip install ansible
   ```

2. **SSH access to OpenWrt nodes:**
   - Ensure you can SSH to each node
   - Initially nodes will be at 192.168.1.1 (default)
   - After configuration, nodes will be at 10.11.12.1, .2, .3

3. **Network connectivity:**
   - Control machine must be able to reach nodes
   - Configure ONE node at a time initially

### Target Nodes (OpenWrt Routers)

1. **OpenWrt installed:**
   - Flash OpenWrt firmware (see main setup guide)
   - Root password set
   - SSH enabled (default)

2. **Python3 available:**
   - Usually pre-installed on OpenWrt
   - If not: `opkg update && opkg install python3-light`

## Quick Start

### 1. Clone or Download This Project

```bash
git clone <repository> openwrt-mesh-ansible
cd openwrt-mesh-ansible
```

### 2. Customize Configuration

**Edit `group_vars/all.yml`:**

```yaml
# REQUIRED: Change these passwords!
mesh_password: YourSecureMeshPassword123!
client_password: YourClientPassword123!

# Adjust to your WAN speeds (in kbit/s)
batman_gw_bandwidth: 100000/100000

# Optional: Add static host reservations
static_hosts:
  - name: admin-workstation
    mac: 'AA:BB:CC:DD:EE:FF'
    ip: 10.11.12.10
```

**Edit `inventory/hosts.yml`:**

```yaml
# For initial setup, set ansible_host to 192.168.1.1
# After node is configured, change to 10.11.12.X

# Optional: Set password for initial connection
# ansible_ssh_pass: your_initial_password
```

### 3. Initial Node Setup (One at a Time)

**Configure Node 1:**

```bash
# 1. Connect ONLY Node 1 to your network
# 2. Set its IP in inventory to 192.168.1.1
# 3. Deploy configuration
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --limit node1

# 4. After deployment, node1 will be at 10.11.12.1
# 5. Update inventory/hosts.yml with ansible_host: 10.11.12.1
```

**Configure Node 2:**

```bash
# 1. Disconnect Node 1, connect Node 2
# 2. Set Node 2's IP in inventory to 192.168.1.1
# 3. Deploy configuration
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --limit node2

# 4. Update inventory with ansible_host: 10.11.12.2
```

**Configure Node 3:**

```bash
# Same process as Node 2
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --limit node3
```

### 4. Physical Wiring

After all nodes are configured:

1. Connect the wired ring (LAN3 and LAN4 between nodes)
2. Connect WAN ports to internet
3. Power on all nodes

### 5. Verify Deployment

```bash
# Check all nodes
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml

# Should show:
# - All nodes reachable
# - Batman interfaces active
# - Mesh topology complete
# - Gateways available
```

## Usage

### Deploy Configuration

**Deploy to all nodes:**

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml
```

**Deploy to specific node:**

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --limit node1
```

**Dry run (check mode):**

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --check
```

**Deploy only specific components:**

```bash
# Network configuration only
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --tags network

# Wireless configuration only
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --tags wireless

# DHCP configuration only
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --tags dhcp

# Skip package installation
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --skip-tags packages
```

### Verify Mesh Status

```bash
# Check all nodes
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml

# Output shows:
# - Node reachability
# - Batman module status
# - Mesh topology
# - Gateway status
# - Interface status
# - WAN connectivity
```

### Backup Configuration

```bash
# Backup all nodes
ansible-playbook -i inventory/hosts.yml playbooks/backup.yml

# Backups saved to: backups/YYYY-MM-DD/
```

**Restore from backup:**

```bash
# 1. Copy backup to node
scp backups/2025-11-05/backup-node1-*.tar.gz root@10.11.12.1:/tmp/

# 2. SSH to node
ssh root@10.11.12.1

# 3. Restore
sysupgrade -r /tmp/backup-node1-*.tar.gz
reboot
```

### Update Packages

```bash
# Check for updates (dry run)
ansible-playbook -i inventory/hosts.yml playbooks/update.yml --tags check

# Perform updates (one node at a time)
ansible-playbook -i inventory/hosts.yml playbooks/update.yml
```

### Ad-hoc Commands

```bash
# Run arbitrary commands on all nodes
ansible mesh_nodes -i inventory/hosts.yml -a "batctl o"

# Check uptime
ansible mesh_nodes -i inventory/hosts.yml -a "uptime"

# Check batman interfaces
ansible mesh_nodes -i inventory/hosts.yml -a "batctl if"

# Restart network on all nodes
ansible mesh_nodes -i inventory/hosts.yml -a "/etc/init.d/network restart"

# Reboot all nodes
ansible mesh_nodes -i inventory/hosts.yml -a "reboot" --become
```

## Configuration Management

### Modifying Configuration

**To change network settings:**

1. Edit `group_vars/all.yml`
2. Run deployment: `ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml`
3. Configuration updated and services reloaded automatically

**To add static DHCP reservations:**

```yaml
# Edit group_vars/all.yml
static_hosts:
  - name: my-server
    mac: '00:11:22:33:44:55'
    ip: 10.11.12.50
```

**To change WiFi passwords:**

```yaml
# Edit group_vars/all.yml
mesh_password: NewMeshPassword123!
client_password: NewClientPassword123!

# Deploy
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --tags wireless
```

### Version Control

Track your configuration with Git:

```bash
git init
git add .
git commit -m "Initial mesh configuration"

# After changes
git add group_vars/all.yml
git commit -m "Updated WiFi passwords"
```

## VLAN Configuration

### Enable VLANs

**Edit `group_vars/all.yml`:**

```yaml
enable_vlans: true

vlans:
  management:
    vid: 10
    network: 10.11.10.0/24
    dhcp_start: 100
    dhcp_limit: 50

  guest:
    vid: 30
    network: 10.11.30.0/24
    dhcp_start: 100
    dhcp_limit: 50
    isolation: true
    guest_ssid: My-Guest-WiFi
    guest_password: GuestPassword123!
```

**Deploy VLAN configuration:**

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml
```

## Troubleshooting

### Connection Issues

**Can't connect to node:**

```bash
# Test SSH manually
ssh root@10.11.12.1

# Check if node is reachable
ping 10.11.12.1

# Try with password authentication
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml --ask-pass
```

**Wrong IP address in inventory:**

```bash
# Update inventory/hosts.yml with correct ansible_host
# Then test connection
ansible node1 -i inventory/hosts.yml -m ping
```

### Deployment Issues

**Package installation fails:**

```bash
# Update package lists manually
ansible mesh_nodes -i inventory/hosts.yml -a "opkg update"

# Then retry deployment
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --tags packages
```

**Configuration not applying:**

```bash
# Check for syntax errors
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --syntax-check

# Run in check mode
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --check

# Check node logs
ansible mesh_nodes -i inventory/hosts.yml -a "logread | tail -50"
```

**Services not reloading:**

```bash
# Manually reload services
ansible mesh_nodes -i inventory/hosts.yml -a "/etc/init.d/network restart"
ansible mesh_nodes -i inventory/hosts.yml -a "wifi reload"
ansible mesh_nodes -i inventory/hosts.yml -a "/etc/init.d/dnsmasq restart"
```

### Mesh Issues

**Batman interfaces not active:**

```bash
# Check batman module
ansible mesh_nodes -i inventory/hosts.yml -a "lsmod | grep batman"

# Check configuration
ansible mesh_nodes -i inventory/hosts.yml -a "uci show network | grep batadv"

# Restart network
ansible mesh_nodes -i inventory/hosts.yml -a "/etc/init.d/network restart"
```

**Nodes can't see each other:**

```bash
# Check mesh topology
ansible mesh_nodes -i inventory/hosts.yml -a "batctl o"

# Check physical connections
ansible mesh_nodes -i inventory/hosts.yml -a "ip link show | grep lan"

# Check wireless mesh
ansible mesh_nodes -i inventory/hosts.yml -a "iw dev mesh0 station dump"
```

## Advanced Usage

### SSH Key Authentication

**Setup SSH keys:**

```bash
# Generate key (if you don't have one)
ssh-keygen -t ed25519 -f ~/.ssh/openwrt_mesh

# Copy to each node
ssh-copy-id -i ~/.ssh/openwrt_mesh.pub root@10.11.12.1
ssh-copy-id -i ~/.ssh/openwrt_mesh.pub root@10.11.12.2
ssh-copy-id -i ~/.ssh/openwrt_mesh.pub root@10.11.12.3

# Update inventory to use key
# Edit inventory/hosts.yml:
ansible_ssh_private_key_file: ~/.ssh/openwrt_mesh
```

### Parallel Execution

```bash
# Deploy to multiple nodes simultaneously
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --forks 3

# Note: Use caution with parallel updates to maintain mesh availability
```

### Custom Playbooks

Create custom playbooks for specific tasks:

```yaml
---
# playbooks/custom_task.yml
- name: Custom Task
  hosts: mesh_nodes
  gather_facts: false
  tasks:
    - name: Your custom task
      raw: echo "Custom command"
```

### Integration with Other Tools

**Export configuration:**

```bash
# Export current config
ansible mesh_nodes -i inventory/hosts.yml -a "uci export network" > network_config.txt
```

**Monitor logs continuously:**

```bash
# Watch logs on all nodes
ansible mesh_nodes -i inventory/hosts.yml -a "logread -f" -f 10
```

## Security Best Practices

1. **Change default passwords:**
   - Edit `group_vars/all.yml` and update all password fields
   - Use strong, unique passwords

2. **Use SSH keys:**
   - Disable password authentication after setting up keys
   - Keep private keys secure

3. **Restrict SSH access:**
   - Configure firewall to allow SSH only from management network
   - Consider changing SSH port

4. **Regular updates:**
   - Run update playbook monthly
   - Subscribe to OpenWrt security announcements

5. **Backup regularly:**
   - Schedule regular backups
   - Store backups securely off-site

6. **Audit configuration:**
   - Review configuration changes before deploying
   - Use Git to track all changes

## Maintenance Schedule

### Daily

```bash
# Quick status check
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml
```

### Weekly

```bash
# Check for updates
ansible-playbook -i inventory/hosts.yml playbooks/update.yml --tags check

# Backup configuration
ansible-playbook -i inventory/hosts.yml playbooks/backup.yml
```

### Monthly

```bash
# Apply updates
ansible-playbook -i inventory/hosts.yml playbooks/update.yml

# Verify after updates
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml
```

### Quarterly

```bash
# Full configuration audit
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --check

# Review and clean old backups
ls -lh backups/
```

## Tips and Best Practices

1. **Test in check mode first:**
   - Always run `--check` before applying changes
   - Verify output before actual deployment

2. **One node at a time:**
   - For critical updates, use `--limit` to update one node
   - Verify mesh stays operational before proceeding

3. **Keep backups:**
   - Backup before any major changes
   - Keep backups for at least 30 days

4. **Document changes:**
   - Use Git commit messages to explain configuration changes
   - Keep notes on non-standard configurations

5. **Version your configurations:**
   - Tag stable configurations in Git
   - Easy rollback if needed

6. **Monitor performance:**
   - Regularly check mesh topology and link quality
   - Track gateway selection patterns

## Troubleshooting Common Ansible Errors

**"SSH Error: Permission denied"**

```bash
# Check SSH credentials
ansible mesh_nodes -i inventory/hosts.yml -m ping --ask-pass
```

**"Module not found" or "Python not available"**

```bash
# Install Python on nodes
ansible mesh_nodes -i inventory/hosts.yml -m raw -a "opkg update && opkg install python3-light"
```

**"Template error" or "Jinja2 error"**

```bash
# Check template syntax
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --syntax-check

# Check variables are defined
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --check
```

## Support and Resources

- OpenWrt Documentation: <https://openwrt.org/docs>
- Batman-adv Project: <https://www.open-mesh.org/>
- Ansible Documentation: <https://docs.ansible.com/>
- OpenWrt Forum: <https://forum.openwrt.org/>

## License

This project configuration is provided as-is for personal and educational use.

## Contributing

To improve these playbooks:

1. Test changes thoroughly
2. Document modifications
3. Share improvements with the community

---

**Last Updated:** 2025-11-05
**Version:** 1.0
