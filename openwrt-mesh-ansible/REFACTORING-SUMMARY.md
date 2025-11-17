# Inventory Refactoring Summary

## Problem Statement

The original inventory configuration failed because it tried to use a single IP address (10.11.12.1) for all phases of deployment, but OpenWrt routers go through distinct phases with different network configurations:

1. **Factory State**: Fresh OpenWrt at 192.168.1.1 with Dropbear SSH and no password
2. **Production State**: Configured mesh at 10.11.12.x with OpenSSH and password

## Solution: Two-Phase Inventory Architecture

### Phase 1: Initial Setup (`inventory/hosts-initial.yml`)

- **Purpose**: Configure fresh OpenWrt routers one at a time
- **IP Address**: 192.168.1.1 (factory default)
- **SSH Server**: Dropbear (lightweight)
- **Root Password**: Not set (factory default - no password)
- **Authentication**: Empty password (`ansible_ssh_pass: ''`)
- **Limitation**: Only one node at a time (all start at same IP)

### Phase 2: Production (`inventory/hosts.yml`)

- **Purpose**: Manage configured mesh network
- **IP Addresses**: 10.11.12.1, 10.11.12.2, 10.11.12.3
- **SSH Server**: OpenSSH (full-featured)
- **Authentication**: **SSH KEY** (passwordless, key-based)
- **SSH Key**: `~/.ssh/openwrt_mesh_rsa` (auto-generated)
- **Root Password**: Set (console access only, SSH password auth disabled)
- **Capability**: Manage all nodes simultaneously

## Files Modified/Created

### ✅ Created

1. **`inventory/hosts-initial.yml`**
   - Fresh node inventory with dropbear configuration
   - Blank password authentication
   - Dropbear-specific SSH options

2. **`inventory/README.md`**
   - Complete documentation of two-phase approach
   - Authentication details for each phase
   - Requirements (sshpass, openssh-client)
   - Workflow examples and quick reference

3. **`REFACTORING-SUMMARY.md`** (this file)

### ✅ Modified

1. **`inventory/hosts.yml`**
   - Updated comments for production use
   - OpenSSH-specific configuration
   - Password authentication via `root_password` variable

2. **`ansible.cfg`**
   - Added comments explaining dropbear vs openssh
   - Timeout settings for slow connections
   - SSH connection options documented

3. **`group_vars/all.yml`**
   - Added `root_password` variable
   - Added openssh packages to `required_packages`:
     - `openssh-server`
     - `openssh-sftp-server`
     - `openssh-keygen`
   - Documented SSH transition process

4. **`playbooks/deploy.yml`**
   - Added SSH server transition section
   - Set root password task
   - Install and enable OpenSSH
   - Stop and remove Dropbear
   - Updated header documentation

5. **`playbooks/check-connectivity.yml`**
   - Fixed authentication test to use `raw` command
   - Works with both dropbear and openssh

6. **`Makefile`**
   - Added Phase 1 targets:
     - `check-initial-node1/2/3`
     - `deploy-initial-node1/2/3`
   - Reorganized help text to show phases
   - Updated `.PHONY` declaration

## Key Technical Changes

### SSH Authentication Flow

**Before:**

```
OpenWrt (192.168.1.1, dropbear, no root password set)
  → Ansible tries to connect to 10.11.12.1 ❌ FAIL
```

**After:**

```
Phase 1 (Initial):
  OpenWrt (192.168.1.1, dropbear, no root password set)
    → Ansible connects with hosts-initial.yml ✅
    → Deploy playbook:
       1. Generates SSH key pair (if needed)
       2. Deploys public key to node
       3. Installs openssh packages
       4. Configures openssh (key-based auth only)
       5. Sets root password (console only)
       6. Starts openssh
       7. Removes dropbear
    → Node now at 10.11.12.1 with openssh + SSH key ✅

Phase 2 (Production):
  OpenWrt (10.11.12.x, openssh, SSH key)
    → Ansible connects with hosts.yml using SSH key ✅
    → Passwordless authentication
    → Password auth disabled for SSH (security)
```

### Dropbear → OpenSSH Transition with SSH Keys

The deployment playbook now handles this automatically:

1. **Generate SSH Key Pair** (on control machine, if doesn't exist)

   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/openwrt_mesh_rsa -C "ansible@openwrt-mesh"
   ```

2. **Deploy Public Key to Node**

   ```bash
   mkdir -p /root/.ssh && chmod 700 /root/.ssh
   echo '<public-key>' > /root/.ssh/authorized_keys
   chmod 600 /root/.ssh/authorized_keys
   ```

3. **Install OpenSSH** (from `required_packages`)

   ```yaml
   - openssh-server
   - openssh-sftp-server
   - openssh-keygen
   ```

4. **Configure OpenSSH** (key-based auth only)

   ```
   /etc/ssh/sshd_config:
     PermitRootLogin prohibit-password
     PubkeyAuthentication yes
     PasswordAuthentication no  # DISABLED for security
   ```

5. **Set Root Password** (console access only)

   ```bash
   echo -e 'password\npassword' | passwd root
   ```

6. **Start OpenSSH**

   ```bash
   /etc/init.d/sshd enable && /etc/init.d/sshd start
   ```

7. **Remove Dropbear**

   ```bash
   /etc/init.d/dropbear stop
   /etc/init.d/dropbear disable
   opkg remove dropbear
   ```

## System Requirements

### New Dependency: sshpass

**Why?** Ansible requires `sshpass` for password authentication (both blank passwords for dropbear and configured passwords for openssh).

**Installation:**

```bash
# Debian/Ubuntu
apt-get install sshpass

# RHEL/CentOS
yum install sshpass
```

## Usage Examples

### Initial Setup Workflow

```bash
# 1. Flash OpenWrt on first router (at 192.168.1.1)
# 2. Connect directly to router LAN port
# 3. Check connectivity
make check-initial-node1

# 4. Deploy (switches to openssh, moves to 10.11.12.1)
make deploy-initial-node1

# 5. Disconnect first router, repeat for others
make check-initial-node2
make deploy-initial-node2

make check-initial-node3
make deploy-initial-node3
```

### Production Management Workflow

```bash
# After all nodes configured, use production inventory

# Check all nodes
make check-all

# Deploy to all nodes
make deploy

# Deploy to specific node
make deploy-node1

# Check individual node
make check-node1
```

## Testing Results

### ✅ Connectivity Check (Phase 1)

```
make check-initial-node1

Results:
  [✓] Network - SSH port reachable at 192.168.1.1:22
  [✓] Authentication - SSH login successful (blank password)
  [⚠] Python - Not found (expected, will be installed)
  [✓] OpenWrt - Valid system (DIR-1960 A1, v24.10.4)
  [✓] Commands - Execution working

Status: READY for deployment
```

### ✅ Direct SSH Test

```bash
ssh root@192.168.1.1 'echo test'
# Works with no password (factory default)
```

### ✅ Ansible Raw Command Test

```bash
ansible -i inventory/hosts-initial.yml node1 -m raw -a "echo test"
# node1 | CHANGED | rc=0 >> test
```

## Migration Checklist

If you have existing nodes to migrate:

- [ ] Back up current configuration: `make backup`
- [ ] Create `.env` file: `cp .env.example .env`
- [ ] Edit `.env` and set all required passwords (minimum: ROOT_PASSWORD, MESH_PASSWORD, CLIENT_PASSWORD)
- [ ] Secure `.env` file: `chmod 600 .env`
- [ ] Load environment variables: `set -a; source .env; set +a`
- [ ] Validate environment configuration: `make validate-env`
- [ ] For fresh nodes: Use `make check-initial-nodeX` and `make deploy-initial-nodeX`
- [ ] For configured nodes: Continue using `make check-nodeX` and `make deploy`
- [ ] Verify sshpass is installed: `which sshpass`
- [ ] Test connectivity: `make check-all`

## Benefits

1. **Clear Separation**: Initial setup vs production management
2. **No Manual IP Changes**: Inventory files are ready to use
3. **Better Security**: SSH key authentication (passwordless, 4096-bit RSA)
4. **Documented Process**: README explains each phase clearly
5. **One Node at a Time**: Proper workflow for identical factory IPs
6. **Automated Transition**: Deploy playbook handles SSH server change and key deployment

## SSH Key Authentication (Key Security Feature)

### What Changed

- **Before**: Production used password authentication
- **After**: Production uses **SSH key** authentication (passwordless)

### Security Benefits

1. ✅ **No password transmission** over network
2. ✅ **4096-bit RSA key** (much stronger than passwords)
3. ✅ **Password authentication disabled** for SSH
4. ✅ **Automated key generation** and deployment
5. ✅ **Better audit trail** with key fingerprints

### How It Works

```bash
# Initial setup (uses dropbear + blank password)
make deploy-initial-node1

# Deployment automatically:
# 1. Generates SSH key: ~/.ssh/openwrt_mesh_rsa
# 2. Deploys public key to node
# 3. Configures OpenSSH (key-based only)
# 4. Disables password authentication

# Production access (passwordless)
make check-node1
ssh -i ~/.ssh/openwrt_mesh_rsa root@10.11.12.1
```

### Documentation

See `docs/SSH-KEY-AUTHENTICATION.md` for:

- Key management and rotation
- Troubleshooting guides
- Security best practices
- Backup procedures

## Environment Variable Configuration (Phase 0)

### Problem

- Configuration values hardcoded in `group_vars/all.yml`
- Passwords visible in git repository (security risk)
- No easy way to customize deployments
- Difficult to manage multiple environments

### Solution: Complete .env Refactoring

**All configuration moved to environment variables** sourced from `.env` file.

### Files Created

1. **`.env.example`** (278 lines, 60+ variables)
   - Comprehensive template for all configuration
   - Organized into logical sections:
     - Security & Authentication (passwords)
     - SSH Key Configuration
     - Network Configuration (IPs, subnets, gateway, DNS)
     - DHCP Configuration (per-node pools)
     - Batman-adv Mesh Routing
     - Wireless Mesh (2.4GHz backbone)
     - Client WiFi (5GHz access point)
     - 802.11r Fast Roaming
     - MTU Settings
     - System Configuration (timezone, hostname)
     - VLAN Configuration (optional networks)
     - Package Configuration
     - Service Configuration
   - Includes configuration tips and best practices

2. **`playbooks/validate-env.yml`**
   - Validates required environment variables before deployment
   - Checks: ROOT_PASSWORD, MESH_PASSWORD, CLIENT_PASSWORD
   - Validates VLAN passwords if VLANs enabled
   - Displays helpful error messages for missing variables
   - Shows configuration summary when valid

3. **`.gitignore` updates**
   - Excludes `.env` files from git
   - Prevents accidental password commits

### Files Modified

1. **`group_vars/all.yml`** (completely rewritten)
   - **ALL hardcoded values removed**
   - Every variable uses `lookup('env', 'VAR_NAME') | default('default', true)`
   - Example transformations:

   ```yaml
   # Before (hardcoded)
   mesh_network: 10.11.12.0
   mesh_gateway: 10.11.12.1
   dns_servers:
     - 1.1.1.1
     - 8.8.8.8

   # After (environment variables)
   mesh_network: "{{ lookup('env', 'MESH_NETWORK') | default('10.11.12.0', true) }}"
   mesh_gateway: "{{ lookup('env', 'MESH_GATEWAY') | default('10.11.12.1', true) }}"
   dns_servers:
     - "{{ lookup('env', 'DNS_PRIMARY') | default('1.1.1.1', true) }}"
     - "{{ lookup('env', 'DNS_SECONDARY') | default('8.8.8.8', true) }}"
   ```

   - Type conversions added where needed:

   ```yaml
   mesh_cidr: "{{ lookup('env', 'MESH_CIDR') | default('24', true) | int }}"
   enable_vlans: "{{ lookup('env', 'ENABLE_VLANS') | default('true', true) | bool }}"
   ```

   - Comma-separated string to list conversion:

   ```yaml
   required_packages: "{{ lookup('env', 'REQUIRED_PACKAGES') | default('kmod-batman-adv,batctl,...', true) | split(',') }}"
   ```

2. **`Makefile`** - Added PHASE 0: Environment Setup

   ```makefile
   # PHASE 0: Environment Validation
   validate-env:
       ansible-playbook playbooks/validate-env.yml
   ```

### Environment Variables by Category

**Required (must be set):**

- `ROOT_PASSWORD` - Root password for console access
- `MESH_PASSWORD` - 2.4GHz mesh network password (WPA3-SAE)
- `CLIENT_PASSWORD` - 5GHz client AP password
- `MGMT_PASSWORD` - Management VLAN password (if VLANs enabled)
- `GUEST_PASSWORD` - Guest VLAN password (if VLANs enabled)

**Network Configuration (60+ optional variables with defaults):**

- Network: MESH_NETWORK, MESH_NETMASK, MESH_CIDR, MESH_GATEWAY
- DNS: DNS_PRIMARY, DNS_SECONDARY
- DHCP: DHCP_LEASETIME, DHCP_NODE[1-3]_START/LIMIT
- Batman: BATMAN_ROUTING_ALGO, BATMAN_GW_BANDWIDTH, BATMAN_ORIG_INTERVAL
- Wireless Mesh: MESH_ID, MESH_CHANNEL, MESH_HTMODE, MESH_ENCRYPTION
- Client WiFi: CLIENT_SSID, CLIENT_CHANNEL, CLIENT_HTMODE, CLIENT_COUNTRY
- VLANs: MGMT_VLAN_*, GUEST_VLAN_*
- System: TIMEZONE, ZONENAME, HOSTNAME_PREFIX

### Usage Workflow

```bash
# 1. Create .env from template
cp .env.example .env

# 2. Edit .env and set all required passwords
nano .env
# At minimum, set:
#   ROOT_PASSWORD=YourSecureRootPassword123!
#   MESH_PASSWORD=YourSecureMeshPassword123!
#   CLIENT_PASSWORD=YourSecureClientPassword123!

# 3. Secure .env file
chmod 600 .env

# 4. Load environment variables
set -a; source .env; set +a

# 5. Validate configuration
make validate-env

# 6. Proceed with deployment
make check-initial-node1
make deploy-initial-node1
```

### Validation Output Example

```
================================================================================
Environment Variable Validation
================================================================================

✅ All required variables are set:
  - ROOT_PASSWORD: ***
  - MESH_PASSWORD: ***
  - CLIENT_PASSWORD: ***

VLANs are ENABLED - checking VLAN passwords...
✅ All VLAN passwords are set

Configuration summary:
  - Mesh Network: 10.11.12.0/24
  - Gateway: 10.11.12.1
  - Mesh SSID: ha-mesh-net
  - Client SSID: HA-Network-5G
  - Country: AU
  - Timezone: Australia/Adelaide

Ready for deployment!
================================================================================
```

### Security Benefits

1. ✅ **No passwords in git** - `.env` excluded via `.gitignore`
2. ✅ **Secure file permissions** - `chmod 600 .env`
3. ✅ **Easy rotation** - Update `.env` and redeploy
4. ✅ **Environment-specific** - Different `.env` for dev/staging/prod
5. ✅ **Validation** - Catches missing/invalid variables before deployment

### Documentation

See `docs/ENV-CONFIGURATION.md` for:

- Complete variable reference
- Password generation examples
- Security best practices
- Troubleshooting guide
- Migration from hardcoded values

## Next Steps

1. ✅ Refactoring complete
2. ⏭️ **Configure passwords in `.env` file** (IMPORTANT - see `docs/ENV-CONFIGURATION.md`)

   ```bash
   cp .env.example .env
   nano .env  # Add your passwords
   chmod 600 .env
   set -a; source .env; set +a
   ```

3. ⏭️ (Optional) Customize `SSH_KEY_PATH` in `.env`
4. ⏭️ Run `make deploy-initial-node1` when ready
5. ⏭️ SSH key will be auto-generated and deployed
6. ⏭️ After all nodes deployed, use production commands (passwordless!)

## Notes

- **Passwords**: All passwords now sourced from `.env` file (never committed to git!)
- **Security**: `.env` must have 600 permissions and is excluded in `.gitignore`
- **Environment**: Load with `set -a; source .env; set +a` before deployment
- **SSH Keys**: Auto-generated at `~/.ssh/openwrt_mesh_rsa` (backup securely!)
- **Root Password**: Still set (for console/serial access only, from `.env`)
- **Password Auth**: Disabled for SSH (security), enabled for console
- **Python**: Will be installed during deployment (not on factory OpenWrt)
- **Dropbear**: Completely removed after openssh installation
- **Connection Test**: Always use `make check-initial-nodeX` or `make check-nodeX` first
- **Documentation**: See `docs/ENV-CONFIGURATION.md` for complete .env setup guide

---

**Refactoring Date**: 2025-11-09
**OpenWrt Version**: 24.10.4
**Device**: D-Link DIR-1960 A1
