# OpenWrt Mesh Network - Ansible Deployment Quick Start

## What This Provides

Complete Infrastructure-as-Code deployment for your 3-node OpenWrt mesh network using Ansible.

**Benefits:**
- ✅ Repeatable, automated deployment
- ✅ Version-controlled configuration
- ✅ Easy updates and changes
- ✅ Consistent configuration across all nodes
- ✅ Backup and restore capabilities
- ✅ No manual configuration file editing

## Files Included

```
openwrt-mesh-ansible.tar.gz contains:
├── inventory/hosts.yml          # Node definitions
├── group_vars/all.yml           # Configuration variables
├── templates/                   # Jinja2 configuration templates
│   ├── network.j2
│   ├── wireless.j2
│   ├── dhcp.j2
│   └── firewall.j2
├── playbooks/                   # Ansible playbooks
│   ├── deploy.yml              # Main deployment
│   ├── verify.yml              # Status verification
│   ├── backup.yml              # Configuration backup
│   └── update.yml              # Package updates
├── Makefile                    # Convenience commands
├── ansible.cfg                 # Ansible configuration
└── README.md                   # Comprehensive documentation
```

## Prerequisites

**On your control machine (laptop/workstation):**

```bash
# Install Ansible
# Ubuntu/Debian:
sudo apt update && sudo apt install ansible

# macOS:
brew install ansible

# Verify installation
ansible --version
```

## Setup Steps

### 1. Extract the Archive

```bash
tar -xzf openwrt-mesh-ansible.tar.gz
cd openwrt-mesh-ansible
```

### 2. Customize Your Configuration

**Edit `group_vars/all.yml` - REQUIRED CHANGES:**

```yaml
# CHANGE THESE PASSWORDS!
mesh_password: YourSecureMeshPassword123!
client_password: YourClientPassword123!

# Adjust to your WAN speeds (in kbit/s)
batman_gw_bandwidth: 100000/100000  # 100Mbps down/up

# Optional: Add static host reservations
static_hosts:
  - name: admin-workstation
    mac: 'AA:BB:CC:DD:EE:FF'
    ip: 10.11.12.10
```

**Other settings you might want to adjust:**
- WiFi channels (if interference issues)
- SSID names
- Network ranges (if 10.11.12.0/24 conflicts)
- Timezone

### 3. Initial Deployment (Important!)

You must configure nodes **ONE AT A TIME** initially:

**Node 1 First:**
```bash
# 1. Flash Node 1 with OpenWrt (see main guide)
# 2. Connect ONLY Node 1 to your network
# 3. Node 1 will be at 192.168.1.1 (default)

# Edit inventory/hosts.yml - set node1 ansible_host to 192.168.1.1
# Then deploy:
make deploy-node1

# Or:
ansible-playbook playbooks/deploy.yml --limit node1 --ask-pass

# 4. Node 1 is now at 10.11.12.1
# 5. Update inventory/hosts.yml: ansible_host: 10.11.12.1
```

**Node 2:**
```bash
# 1. Disconnect Node 1, connect Node 2
# 2. Set node2 ansible_host to 192.168.1.1 in inventory
# 3. Deploy
make deploy-node2

# 4. Update inventory with 10.11.12.2
```

**Node 3:**
```bash
# Same process as Node 2
make deploy-node3
```

**After all nodes configured:**
```bash
# Connect wired ring (LAN3/LAN4)
# Connect all WANs
# Power on all nodes
```

### 4. Verify Deployment

```bash
# Check all nodes
make verify

# Or:
ansible-playbook playbooks/verify.yml

# Should show:
# ✓ All nodes reachable
# ✓ Batman interfaces active
# ✓ Mesh topology established
# ✓ Gateways available
```

## Common Operations

### Deploy Configuration Changes

```bash
# After editing group_vars/all.yml:
make deploy

# Deploy to specific node:
make deploy-node1

# Dry run (check what would change):
make check
```

### Check Mesh Status

```bash
# Full status check
make verify

# Quick connectivity test
make ping

# Batman-specific status
make batman-status

# Check logs
make logs
```

### Backup Configurations

```bash
# Backup all nodes
make backup

# Backups saved to: backups/YYYY-MM-DD/
```

### Update Packages

```bash
# Check for updates
make update-check

# Apply updates (one node at a time)
make update
```

### Deploy Specific Components

```bash
# Network configuration only
make deploy-network

# Wireless configuration only
make deploy-wireless

# DHCP configuration only
make deploy-dhcp

# Firewall configuration only
make deploy-firewall
```

## Real-World Workflows

### Scenario 1: Change WiFi Password

```bash
# 1. Edit group_vars/all.yml
client_password: NewPassword123!

# 2. Deploy wireless config
make deploy-wireless

# 3. Reconnect your devices with new password
```

### Scenario 2: Add Static IP Reservation

```bash
# 1. Edit group_vars/all.yml
static_hosts:
  - name: my-server
    mac: '11:22:33:44:55:66'
    ip: 10.11.12.50

# 2. Deploy DHCP config (Node 1 only since it's DHCP server)
make deploy-node1 --tags dhcp

# 3. Renew DHCP on client device
```

### Scenario 3: Weekly Maintenance

```bash
# Backup configurations
make backup

# Check for updates
make update-check

# Verify mesh health
make verify
```

### Scenario 4: Rollback Configuration

```bash
# If deployment goes wrong:
# 1. Find backup
ls backups/

# 2. Restore from backup (per node)
scp backups/2025-11-04/backup-node1-*.tar.gz root@10.11.12.1:/tmp/
ssh root@10.11.12.1
sysupgrade -r /tmp/backup-node1-*.tar.gz
reboot
```

## Troubleshooting

### Can't Connect to Nodes

```bash
# Test SSH manually
ssh root@10.11.12.1

# Test with Ansible
ansible mesh_nodes -m ping --ask-pass

# Check inventory file has correct IPs
cat inventory/hosts.yml
```

### Configuration Not Applying

```bash
# Check syntax
make check

# Deploy with verbose output
ansible-playbook playbooks/deploy.yml -vv

# Check node logs
make logs
```

### Mesh Not Working After Deployment

```bash
# Restart network on all nodes
make restart-network

# Check batman interfaces
make batman-status

# Full verification
make verify

# If still issues, check physical wiring
ansible mesh_nodes -a "ip link show | grep lan"
```

## Advanced Tips

### Version Control with Git

```bash
# Initialize repository
git init
git add .
git commit -m "Initial mesh configuration"

# After changes
git add group_vars/all.yml
git commit -m "Updated WiFi passwords"

# Create tags for stable configs
git tag -a v1.0 -m "Production configuration"
```

### SSH Key Authentication

```bash
# Generate SSH key
ssh-keygen -t ed25519 -f ~/.ssh/openwrt_mesh

# Copy to each node
ssh-copy-id -i ~/.ssh/openwrt_mesh.pub root@10.11.12.1
ssh-copy-id -i ~/.ssh/openwrt_mesh.pub root@10.11.12.2
ssh-copy-id -i ~/.ssh/openwrt_mesh.pub root@10.11.12.3

# Update inventory/hosts.yml
ansible_ssh_private_key_file: ~/.ssh/openwrt_mesh

# Remove password from inventory
# Remove: ansible_ssh_pass: ...
```

### Custom Playbooks

Create custom playbooks for specific tasks:

```yaml
# playbooks/restart_services.yml
---
- hosts: mesh_nodes
  tasks:
    - name: Restart all services
      raw: |
        /etc/init.d/network restart
        wifi reload
        /etc/init.d/dnsmasq restart
```

Run with:
```bash
ansible-playbook playbooks/restart_services.yml
```

### Monitoring Integration

Export batman status for monitoring:

```bash
# Create monitoring script
cat > playbooks/export_metrics.yml <<'EOF'
---
- hosts: mesh_nodes
  tasks:
    - name: Get batman metrics
      raw: batctl o
      register: batman_out
    
    - name: Save metrics
      local_action:
        module: copy
        content: "{{ batman_out.stdout }}"
        dest: "/tmp/batman_metrics_{{ inventory_hostname }}.txt"
EOF

# Run periodically
ansible-playbook playbooks/export_metrics.yml
```

## Comparison: Manual vs Ansible

### Manual Configuration
- ❌ Edit files on each node individually
- ❌ Easy to make mistakes/typos
- ❌ Hard to keep nodes in sync
- ❌ No change tracking
- ❌ Time-consuming for updates
- ❌ Difficult to replicate

### Ansible Configuration
- ✅ Single source of truth
- ✅ Consistent across all nodes
- ✅ Version controlled
- ✅ Easy rollback
- ✅ Fast deployment
- ✅ Repeatable

## Integration with Your Existing Infrastructure

Given your background with Proxmox, Terraform, and infrastructure automation:

**Terraform + Ansible:**
```hcl
# terraform/main.tf
resource "null_resource" "deploy_mesh" {
  provisioner "local-exec" {
    command = "cd ../openwrt-mesh-ansible && ansible-playbook playbooks/deploy.yml"
  }
}
```

**CI/CD Pipeline:**
```yaml
# .gitlab-ci.yml or .github/workflows/deploy.yml
deploy:
  script:
    - ansible-playbook playbooks/deploy.yml --check
    - ansible-playbook playbooks/deploy.yml
    - ansible-playbook playbooks/verify.yml
```

**Monitoring Integration:**
- Export batman metrics to Prometheus
- Create Grafana dashboards
- Alert on mesh topology changes

## Next Steps

1. **Initial Setup:**
   - Extract archive
   - Customize configuration
   - Deploy to each node sequentially

2. **Testing:**
   - Verify mesh status
   - Test failover scenarios
   - Monitor performance

3. **Production:**
   - Set up regular backups
   - Configure monitoring
   - Document your specific setup

4. **Optimization:**
   - Fine-tune batman parameters
   - Adjust for your environment
   - Add VLANs if needed

## Support

For detailed documentation:
- See `README.md` in the archive
- Refer to main setup guide (openwrt-batman-mesh-setup.md)
- Check OpenWrt documentation: https://openwrt.org

For automation questions:
- Ansible docs: https://docs.ansible.com
- Jinja2 templates: https://jinja.palletsprojects.com

## Conclusion

This Ansible deployment gives you:
- **Professional-grade automation** for your mesh network
- **Infrastructure-as-Code** approach to network management
- **Easy maintenance** and updates
- **Version control** for all configuration changes
- **Quick disaster recovery** with backups

Perfect for someone with your IT infrastructure experience who values:
- Repeatability
- Documentation
- Version control
- Automation

Enjoy your automated, highly-available mesh network!

---

**Quick Reference Commands:**

```bash
# Setup
tar -xzf openwrt-mesh-ansible.tar.gz && cd openwrt-mesh-ansible
make help

# Deploy
make deploy-node1  # First time, then node2, node3
make deploy        # After all configured

# Maintain
make verify        # Check status
make backup        # Backup configs
make update-check  # Check updates

# Troubleshoot
make ping          # Test connectivity
make batman-status # Check mesh
make logs          # View logs
```

---

**Last Updated:** 2025-11-05
**Version:** 1.0
