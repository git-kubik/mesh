# OpenWrt Mesh Node Audit & Preparation System

## Overview

The Node Audit & Preparation System provides automated tools to:

1. **Connect** to mesh nodes and verify connectivity
2. **Identify** hardware specifications and software configuration
3. **Compare** installed software against project requirements
4. **Report** comprehensive findings in JSON format
5. **Generate** preparation scripts to configure nodes for automation

This system ensures nodes are ready for full Ansible deployment before proceeding with mesh network configuration.

## Architecture

### Components

1. **`playbooks/audit.yml`** - Main audit playbook
   - Connects to nodes via SSH
   - Gathers hardware/software information
   - Performs package comparison analysis
   - Generates reports and preparation scripts

2. **`filter_plugins/package_audit.py`** - Python filter plugin
   - Parses opkg output
   - Compares installed vs required packages
   - Identifies conflicts and missing dependencies
   - Generates install/remove command lists

3. **`templates/prepare_node.sh.j2`** - Preparation script template
   - Backs up current configuration
   - Updates package repositories
   - Removes conflicting packages
   - Installs required packages
   - Verifies installation success

4. **Audit Reports** - JSON output files
   - Hardware specifications
   - Software inventory
   - Package audit results
   - Service status
   - Actionable recommendations

## Usage

### Quick Start

```bash
# Audit all mesh nodes
make audit

# Audit specific node
make audit-node1

# Audit with custom report directory
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml \
  -e "audit_report_dir=/path/to/reports"
```

### Manual Execution

```bash
# Full audit of all nodes
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml

# Audit single node
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml -l node1

# Run only specific phases (tags)
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml \
  --tags "hardware,software"
```

### Available Tags

- `info` - Basic system information
- `hardware` - Hardware identification
- `software` - Software inventory
- `analysis` - Package comparison
- `services` - Service status checks
- `report` - Report generation
- `script` - Preparation script generation
- `summary` - Display summary output

## Workflow

### 1. Initial Audit

Run audit on new or existing nodes:

```bash
cd openwrt-mesh-ansible
make audit
```

### 2. Review Reports

Check generated reports in `./audit_reports/`:

```bash
# View JSON report
cat audit_reports/node1_audit_YYYY-MM-DD_HH-MM-SS.json | jq

# Review preparation script
cat audit_reports/node1_prepare.sh
```

### 3. Execute Preparation Script

Copy and execute the preparation script on the node:

```bash
# Copy to node
scp audit_reports/node1_prepare.sh root@10.11.12.1:/tmp/

# Execute on node
ssh root@10.11.12.1 'sh /tmp/node1_prepare.sh'
```

### 4. Verify Readiness

Re-run audit to confirm node is ready:

```bash
make audit-node1
```

Look for: `Audit Status: READY`

### 5. Full Deployment

Once audit shows "READY", proceed with deployment:

```bash
make deploy-node1
```

## Report Structure

### JSON Report Format

```json
{
  "metadata": {
    "hostname": "node1",
    "audit_timestamp": "2024-01-15_14-30-45",
    "ansible_host": "10.11.12.1"
  },
  "hardware": {
    "model": "D-Link DIR-1960 A1",
    "cpu": "ARMv7 Processor rev 0 (v7l)",
    "memory_mb": "512",
    "flash_size": "128M",
    "network_interfaces": ["eth0", "eth1", "wlan0", "wlan1"]
  },
  "software": {
    "openwrt_version": "23.05.2",
    "kernel_version": "5.15.150",
    "batman_module": "not_loaded",
    "opkg_update": "success"
  },
  "packages": {
    "installed_count": 87,
    "installed_list": [
      {"name": "base-files", "version": "1509-r24106-10cc5fcd00"},
      ...
    ],
    "audit": {
      "missing_required": ["kmod-batman-adv", "batctl", "wpad-mesh-mbedtls"],
      "conflicting": ["wpad-basic-mbedtls"],
      "installed_required": ["ip-full", "tcpdump-mini"],
      "installed_optional": ["iperf3"],
      "extra_packages": [...],
      "audit_status": "needs_packages",
      "summary": {
        "total_installed": 87,
        "required_count": 5,
        "missing_count": 3,
        "conflict_count": 1,
        "installed_required_count": 2,
        "installed_optional_count": 1
      }
    }
  },
  "services": {
    "status": [
      "network: ENABLED",
      "firewall: ENABLED",
      "dnsmasq: ENABLED"
    ],
    "ssh_config": [...]
  },
  "recommendations": {
    "status": "needs_packages",
    "actions_required": true,
    "remove_packages": ["wpad-basic-mbedtls"],
    "install_packages": ["kmod-batman-adv", "batctl", "wpad-mesh-mbedtls"]
  }
}
```

### Audit Status Values

- **`ready`** - Node is ready for deployment
- **`needs_packages`** - Missing required packages
- **`has_conflicts`** - Conflicting packages must be removed

## Preparation Script Features

The generated preparation script (`prepare_node.sh`) includes:

### Safety Features

- Runs pre-flight checks (root access, internet connectivity, storage space)
- Creates automatic backup before making changes
- Uses error handling (`set -e`)
- Validates all installations before completing

### Execution Phases

1. **Pre-flight Checks** - Verify environment
2. **Backup** - Create sysupgrade backup
3. **Update** - Refresh opkg package lists
4. **Remove** - Uninstall conflicting packages
5. **Install** - Install required packages
6. **Optional** - Install optional packages (best effort)
7. **Verify** - Confirm all changes successful
8. **Summary** - Display results and next steps

### Output

- Colored console output (info, success, warning, error)
- Progress indicators
- Detailed error messages
- Summary with next steps

## Package Requirements

### Required Packages (from `group_vars/all.yml`)

- `kmod-batman-adv` - Batman-adv kernel module
- `batctl` - Batman-adv control utility
- `wpad-mesh-mbedtls` - WiFi daemon with mesh support
- `ip-full` - Full iproute2 package
- `tcpdump-mini` - Packet capture utility

### Conflicting Packages (must be removed)

- `wpad-basic-mbedtls` - Conflicts with mesh mode
- `wpad-basic-wolfssl` - Conflicts with mesh mode
- `wpad-basic` - Conflicts with mesh mode

### Optional Packages

- `iperf3` - Network throughput testing
- `ethtool` - Network diagnostics
- `nano` - Text editor
- `htop` - System monitor
- `rsync` - File synchronization

## Troubleshooting

### Audit Fails to Connect

**Problem:** `wait_for_connection` timeout

**Solutions:**

1. Verify node is powered on and accessible
2. Check IP address in `inventory/hosts.yml`
3. Test SSH manually: `ssh root@10.11.12.1`
4. Verify SSH keys or password authentication

### opkg update Fails

**Problem:** Package list update fails

**Solutions:**

1. Check internet connectivity on node
2. Verify DNS resolution: `nslookup openwrt.org`
3. Check firewall rules allow outbound HTTP/HTTPS
4. Manually update: `opkg update`

### Package Installation Fails

**Problem:** Required packages fail to install

**Solutions:**

1. Check available storage: `df -h`
2. Remove unnecessary packages to free space
3. Verify package name is correct for OpenWrt version
4. Check opkg repositories in `/etc/opkg/distfeeds.conf`

### Conflicting Packages Won't Remove

**Problem:** `opkg remove` fails due to dependencies

**Solutions:**

1. Remove packages in specific order
2. Use `opkg remove --force-depends` (caution!)
3. Check which packages depend on it: `opkg whatdepends <package>`

### Preparation Script Errors

**Problem:** Script exits with error

**Solutions:**

1. Check script output for specific error
2. Ensure internet connectivity
3. Verify sufficient storage space
4. Run script sections manually for debugging
5. Check `/tmp/opkg.lock` isn't stuck

## Integration with Deployment

### Recommended Workflow

```bash
# Step 1: Initial audit (before any changes)
make audit

# Step 2: Review reports and prepare nodes
for node in node1 node2 node3; do
  scp audit_reports/${node}_prepare.sh root@10.11.12.${node#node}:/tmp/
  ssh root@10.11.12.${node#node} 'sh /tmp/'${node}'_prepare.sh'
done

# Step 3: Re-audit to verify readiness
make audit

# Step 4: Deploy if all nodes show "READY"
make deploy-node1  # Deploy first node
make verify        # Verify mesh status

make deploy-node2  # Deploy second node
make verify

make deploy-node3  # Deploy third node
make verify

# Step 5: Final verification
make batman-status
```

### Sequential Deployment

Always deploy nodes one at a time to maintain network connectivity:

1. Audit all nodes
2. Prepare all nodes
3. Deploy node1 → verify
4. Deploy node2 → verify
5. Deploy node3 → verify

## Advanced Usage

### Custom Package Lists

Override package requirements at runtime:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml \
  -e "required_packages=['custom-pkg1','custom-pkg2']"
```

### Audit-Only Mode (No Script Generation)

```bash
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml \
  --skip-tags script
```

### Generate Reports Without Node Access

Use cached data (requires previous run):

```bash
ansible-playbook -i inventory/hosts.yml playbooks/audit.yml \
  --tags report \
  -e "use_cached_data=true"
```

## Filter Plugin Reference

### parse_opkg_list

Converts opkg output to structured data.

```yaml
- set_fact:
    packages: "{{ opkg_output.stdout | parse_opkg_list }}"
```

### compare_packages

Compares installed packages against requirements.

```yaml
- set_fact:
    audit: "{{ installed | compare_packages(required, remove, optional) }}"
```

### generate_install_commands

Creates installation command list.

```yaml
- set_fact:
    cmds: "{{ missing_packages | generate_install_commands }}"
```

### generate_remove_commands

Creates removal command list.

```yaml
- set_fact:
    cmds: "{{ conflicting | generate_remove_commands }}"
```

## Best Practices

1. **Always audit before deployment** - Verify node state first
2. **Review preparation scripts** - Don't execute blindly
3. **Keep backups** - Download sysupgrade backups before changes
4. **Test on one node first** - Validate workflow before scaling
5. **Re-audit after preparation** - Confirm readiness before deploying
6. **Monitor storage** - Ensure sufficient space before installing packages
7. **Check internet connectivity** - Required for opkg operations
8. **Sequential deployment** - One node at a time prevents total outage

## Files Created

```
openwrt-mesh-ansible/
├── playbooks/
│   └── audit.yml                    # Main audit playbook
├── filter_plugins/
│   └── package_audit.py             # Package comparison logic
├── templates/
│   └── prepare_node.sh.j2           # Preparation script template
└── audit_reports/                   # Generated reports (not in git)
    ├── node1_audit_2024-01-15_14-30-45.json
    ├── node1_prepare.sh
    ├── node2_audit_2024-01-15_14-30-45.json
    ├── node2_prepare.sh
    ├── node3_audit_2024-01-15_14-30-45.json
    └── node3_prepare.sh
```

## See Also

- [ANSIBLE-QUICKSTART.md](ANSIBLE-QUICKSTART.md) - Ansible basics
- [openwrt-batman-mesh-setup.md](openwrt-batman-mesh-setup.md) - Technical details
- `group_vars/all.yml` - Package requirements configuration
- `inventory/hosts.yml` - Node definitions
