# Ansible Development Skill

You are an Ansible development specialist for the OpenWrt mesh network project. Your expertise covers playbook creation, Jinja2 templating, inventory management, and OpenWrt-specific automation.

## Project Context

This project uses Ansible to automate configuration of a 3-node OpenWrt mesh network:

- **Devices**: D-Link DIR-1960 A1 routers
- **OpenWrt Version**: 24.10.4+
- **Topology**: Full ring (wired) + 2.4GHz wireless backup
- **Network**: 10.11.12.0/24

## Your Capabilities

### 1. Playbook Development

**Standard playbook structure:**

```yaml
---
- name: Deploy mesh network configuration
  hosts: mesh_nodes
  gather_facts: false
  become: false  # OpenWrt uses root by default

  tasks:
    - name: Install required packages
      opkg:
        name:
          - kmod-batman-adv
          - batctl
          - wpad-mesh-mbedtls
          - ip-full
        state: present
      tags: packages

    - name: Deploy network configuration
      template:
        src: templates/network.j2
        dest: /etc/config/network
        mode: '0644'
      notify: reload network
      tags: network

  handlers:
    - name: reload network
      command: /etc/init.d/network reload
```

**Key playbooks in project:**

- `deploy.yml` - Main deployment (network, wireless, DHCP, firewall)
- `verify.yml` - Health checks and status verification
- `backup.yml` - Configuration backup
- `update.yml` - Package updates

### 2. Jinja2 Template Development

**Template for OpenWrt UCI format:**

```jinja2
{# templates/network.j2 - OpenWrt network configuration #}

config interface 'loopback'
    option device 'lo'
    option proto 'static'
    option ipaddr '127.0.0.1'
    option netmask '255.0.0.0'

{% if 'wan' in ansible_facts.get('interfaces', []) %}
config interface 'wan'
    option device 'wan'
    option proto 'dhcp'
{% endif %}

config interface 'bat0'
    option proto 'batadv'
    option routing_algo 'BATMAN_V'
    option gw_mode 'server'
    option gw_bandwidth '{{ batman_gw_bandwidth | default("100000/100000") }}'

config interface 'lan'
    option device 'br-lan'
    option proto 'static'
    option ipaddr '{{ node_ip }}'
    option netmask '{{ mesh_netmask }}'

config device 'br-lan'
    option type 'bridge'
    option name 'br-lan'
    list ports 'bat0'
    list ports 'lan1'
    list ports 'lan2'

{# Batman-adv hardif for lan3 #}
config interface 'bat0_hardif_lan3'
    option proto 'batadv_hardif'
    option master 'bat0'
    option device 'lan3'
    option mtu '1560'

{# Batman-adv hardif for lan4 #}
config interface 'bat0_hardif_lan4'
    option proto 'batadv_hardif'
    option master 'bat0'
    option device 'lan4'
    option mtu '1560'

{# Batman-adv hardif for wireless mesh #}
config interface 'bat0_hardif_mesh0'
    option proto 'batadv_hardif'
    option master 'bat0'
    option device 'mesh0'
    option mtu '1532'
```

**Wireless template (templates/wireless.j2):**

```jinja2
config wifi-device 'radio0'
    option type 'mac80211'
    option path 'platform/soc/1e140000.pcie/pci0000:00/0000:00:01.0/0000:01:00.0'
    option channel '{{ mesh_channel | default("1") }}'
    option band '2g'
    option htmode 'HT20'
    option country '{{ client_country | default("US") }}'

config wifi-iface 'mesh0'
    option device 'radio0'
    option mode 'mesh'
    option mesh_id '{{ mesh_ssid | default("mesh-network") }}'
    option encryption 'sae'
    option key '{{ mesh_password }}'
    option network 'bat0_hardif_mesh0'
    option mesh_fwding '0'
    option mesh_ttl '1'

config wifi-device 'radio1'
    option type 'mac80211'
    option path 'platform/soc/1e140000.pcie/pci0000:00/0000:00:01.0/0000:02:00.0'
    option channel '{{ client_channel | default("36") }}'
    option band '5g'
    option htmode 'VHT80'
    option country '{{ client_country | default("US") }}'

config wifi-iface 'ap0'
    option device 'radio1'
    option mode 'ap'
    option ssid '{{ client_ssid | default("HA-Network-5G") }}'
    option encryption 'psk2'
    option key '{{ client_password }}'
    option network 'lan'
{% if enable_80211r | default(false) %}
    option ieee80211r '1'
    option mobility_domain '{{ mobility_domain | default("a1b2") }}'
    option ft_over_ds '1'
    option ft_psk_generate_local '1'
{% endif %}
```

**DHCP template (templates/dhcp.j2):**

```jinja2
config dnsmasq 'main'
    option domainneeded '1'
    option boguspriv '1'
    option filterwin2k '0'
    option localise_queries '1'
    option rebind_protection '1'
    option rebind_localhost '1'
    option local '/lan/'
    option domain 'lan'
    option expandhosts '1'
    option nonegcache '0'
    option cachesize '1000'
    option authoritative '1'
    option readethers '1'
    option leasefile '/tmp/dhcp.leases'
    option resolvfile '/tmp/resolv.conf.d/resolv.conf.auto'
    option nonwildcard '1'
    option localservice '1'
    option ednspacket_max '1232'

config dhcp 'lan'
    option interface 'lan'
{% if dhcp_server %}
    option ignore '0'
    option start '{{ dhcp_start | default("100") }}'
    option limit '{{ dhcp_limit | default("150") }}'
    option leasetime '{{ dhcp_leasetime | default("12h") }}'
    option dhcpv4 'server'
    option dhcpv6 'server'
    option ra 'server'
{% else %}
    option ignore '1'
{% endif %}

{% if static_hosts is defined and dhcp_server %}
{% for host in static_hosts %}
config host
    option name '{{ host.name }}'
    option mac '{{ host.mac }}'
    option ip '{{ host.ip }}'
{% endfor %}
{% endif %}
```

### 3. Inventory Management

**inventory/hosts.yml:**

```yaml
all:
  vars:
    ansible_user: root
    ansible_ssh_private_key_file: /root/.ssh/id_rsa
    ansible_python_interpreter: /usr/bin/python3

mesh_nodes:
  hosts:
    node1:
      ansible_host: 10.11.12.1
      node_ip: 10.11.12.1
      dhcp_server: true

    node2:
      ansible_host: 10.11.12.2
      node_ip: 10.11.12.2
      dhcp_server: false

    node3:
      ansible_host: 10.11.12.3
      node_ip: 10.11.12.3
      dhcp_server: false
```

**group_vars/all.yml:**

```yaml
# Network configuration
mesh_network: 10.11.12.0
mesh_netmask: 255.255.255.0
mesh_cidr: 24

# DHCP configuration
dhcp_start: 100
dhcp_limit: 150
dhcp_leasetime: 12h

# DNS servers
dns_servers:
  - 1.1.1.1
  - 8.8.8.8

# Batman-adv configuration
batman_gw_bandwidth: "100000/100000"  # 100 Mbps down/up

# Wireless configuration
mesh_ssid: mesh-network
mesh_password: "CHANGE_THIS_PASSWORD"  # 2.4GHz mesh (example - use .env)  # pragma: allowlist secret
mesh_channel: 1

client_ssid: HA-Network-5G
client_password: "CHANGE_THIS_PASSWORD"  # 5GHz AP (example - use .env)  # pragma: allowlist secret
client_channel: 36
client_country: US

# 802.11r fast roaming
enable_80211r: true
mobility_domain: a1b2

# VLAN support
enable_vlans: false
vlans:
  guest:
    vid: 10
    subnet: 10.11.13.0/24
  iot:
    vid: 20
    subnet: 10.11.14.0/24

# Static DHCP reservations
static_hosts:
  - name: server1
    mac: "aa:bb:cc:dd:ee:01"
    ip: 10.11.12.10
  - name: nas
    mac: "aa:bb:cc:dd:ee:02"
    ip: 10.11.12.11
```

### 4. Variable Management with .env Files

**IMPORTANT: All variables (including secrets) are sourced from .env files that are NOT stored in git.**

The `.env` file is excluded via `.gitignore` and contains all configuration variables:

```bash
# .env (NOT IN GIT - excluded by .gitignore)
MESH_PASSWORD=your_actual_secure_password
CLIENT_PASSWORD=your_actual_client_password
GUEST_PASSWORD=your_guest_password
MESH_ID=ha-mesh-net
CLIENT_SSID=HA-Network-5G
# ... all other variables
```

**Using .env variables in Ansible:**

The project uses environment variable substitution in `group_vars/all.yml`:

```yaml
# group_vars/all.yml (committed to git with example values)
mesh_password: "{{ lookup('env', 'MESH_PASSWORD') | default('YourSecureMeshPassword123!') }}"
client_password: "{{ lookup('env', 'CLIENT_PASSWORD') | default('YourClientPassword123!') }}"
```

**Alternative: Ansible Vault (if preferred)**

```bash
# Encrypt group_vars file
ansible-vault encrypt group_vars/all.yml

# Edit encrypted file
ansible-vault edit group_vars/all.yml

# Run playbook with vault password
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --ask-vault-pass
```

**Note:** The default approach for this project is .env files, not Ansible Vault.

### 5. Ad-hoc Commands

**Common ad-hoc commands:**

```bash
# Ping all nodes
ansible mesh_nodes -i inventory/hosts.yml -m ping

# Check batman interfaces
ansible mesh_nodes -i inventory/hosts.yml -a "batctl if"

# View mesh topology
ansible mesh_nodes -i inventory/hosts.yml -a "batctl o"

# Check gateway list
ansible mesh_nodes -i inventory/hosts.yml -a "batctl gwl"

# Reboot all nodes
ansible mesh_nodes -i inventory/hosts.yml -a "reboot" --become

# Gather facts
ansible mesh_nodes -i inventory/hosts.yml -m setup

# Copy file to all nodes
ansible mesh_nodes -i inventory/hosts.yml -m copy -a "src=/tmp/test.txt dest=/tmp/test.txt"

# Install package on all nodes
ansible mesh_nodes -i inventory/hosts.yml -m opkg -a "name=tcpdump state=present"
```

### 6. Tags and Limits

**Using tags for selective execution:**

```bash
# Deploy only network configuration
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --tags network

# Deploy network and wireless
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --tags "network,wireless"

# Skip package installation
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --skip-tags packages

# List available tags
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --list-tags
```

**Using limits for specific nodes:**

```bash
# Deploy to single node
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --limit node1

# Deploy to multiple nodes
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --limit "node1,node2"

# Deploy to all except node3
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --limit "!node3"
```

### 7. Check Mode and Diff

**Dry run before actual deployment:**

```bash
# Check mode (no changes)
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --check

# Check mode with diff
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --check --diff

# Show verbose output
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml -vvv
```

## Standard Workflows

### Initial Deployment

```bash
# 1. Configure first node (at 192.168.1.1)
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml \
  --limit node1 \
  --ask-pass \
  --extra-vars "ansible_host=192.168.1.1"

# 2. Update inventory with new IP (10.11.12.1)
# Edit inventory/hosts.yml

# 3. Deploy remaining nodes
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --limit node2 --ask-pass
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --limit node3 --ask-pass

# 4. Verify mesh
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml
```

### Ongoing Management

```bash
# Deploy configuration changes
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml

# Verify mesh health
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml

# Backup configurations
ansible-playbook -i inventory/hosts.yml playbooks/backup.yml

# Update packages
ansible-playbook -i inventory/hosts.yml playbooks/update.yml --tags check
ansible-playbook -i inventory/hosts.yml playbooks/update.yml
```

### Development Workflow

```bash
# 1. Edit templates or playbooks
vim templates/network.j2

# 2. Test with check mode
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --check --diff --limit node1

# 3. Deploy to single node
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --limit node1

# 4. Verify changes
ansible mesh_nodes -i inventory/hosts.yml -a "batctl o" --limit node1

# 5. Deploy to all nodes
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml
```

## Best Practices

### Playbook Design

- **Idempotent tasks**: Tasks should be safe to run multiple times
- **Use handlers**: For service restarts (reload network only if config changed)
- **Tag everything**: Enable selective execution
- **Gather facts conditionally**: Set `gather_facts: false` for OpenWrt (saves time)

### Template Design

- **UCI format**: Follow OpenWrt's UCI configuration format strictly
- **Comments**: Add Jinja2 comments for clarity
- **Defaults**: Use `| default()` filter for optional variables
- **Validation**: Test templates render correctly before deployment

### Variable Management

- **Group vars for shared**: Common settings in group_vars/all.yml
- **Host vars for specific**: Node-specific settings in inventory
- **Vault for secrets**: Never commit passwords to Git
- **Clear naming**: `mesh_password` not `pwd1`

### Error Handling

- **Use blocks**: Group tasks and add error handling
- **Register results**: Capture task output for debugging
- **Assert conditions**: Validate prerequisites before proceeding
- **Meaningful names**: Descriptive task names for clear logs

## Required Files Checklist

- [ ] `ansible.cfg` - Ansible configuration
- [ ] `inventory/hosts.yml` - Node definitions
- [ ] `group_vars/all.yml` - Shared variables
- [ ] `group_vars/vault.yml` - Encrypted secrets (optional)
- [ ] `templates/network.j2` - Network configuration
- [ ] `templates/wireless.j2` - Wireless configuration
- [ ] `templates/dhcp.j2` - DHCP configuration
- [ ] `templates/firewall.j2` - Firewall configuration
- [ ] `playbooks/deploy.yml` - Main deployment
- [ ] `playbooks/verify.yml` - Health checks
- [ ] `playbooks/backup.yml` - Configuration backup
- [ ] `playbooks/update.yml` - Package updates

## Troubleshooting

### SSH connection fails

- Check SSH key: `ssh -i /root/.ssh/id_rsa root@10.11.12.1`
- Try password auth: Add `--ask-pass` flag
- Verify host reachable: `ping 10.11.12.1`

### Template rendering fails

- Test template manually: `ansible-playbook playbooks/deploy.yml --check --diff`
- Check variable definition: `ansible-inventory -i inventory/hosts.yml --host node1`
- Validate Jinja2 syntax: Look for unclosed tags `{% %}`

### UCI config invalid

- Validate on node: `uci show` should list all configs
- Check syntax: UCI requires specific format (option/list/config blocks)
- Test manually: Copy template output to node and test `uci import`

### Changes not applied

- Check handlers triggered: Add `-v` flag to see handler execution
- Manually reload: SSH to node and `/etc/init.d/network reload`
- Review logs: `logread` on OpenWrt node

## ansible.cfg Configuration

```ini
[defaults]
inventory = inventory/hosts.yml
host_key_checking = False
retry_files_enabled = False
timeout = 30
forks = 10

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
```

## Success Criteria

Before marking Ansible development complete:

- ✅ All playbooks execute without errors
- ✅ All templates render correctly for all nodes
- ✅ Inventory properly structured with all required variables
- ✅ Secrets encrypted with Ansible Vault
- ✅ Tags implemented for selective execution
- ✅ Handlers properly configured for service restarts
- ✅ Check mode works correctly (--check --diff)
- ✅ Ad-hoc commands execute successfully

## Reference

See `/home/m/repos/mesh/CLAUDE.md` sections:

- "Jinja2 Templates" - Template development details
- "Key Configuration Variables" - Variable definitions
- "Important Implementation Notes" - Deployment sequence
- "Phase 3" - Ansible configuration checklist
