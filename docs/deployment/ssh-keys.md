# SSH Key Authentication Guide

## Overview

The OpenWrt mesh network uses **passwordless SSH key authentication** for secure, automated access to nodes. This document explains how SSH keys are managed and used.

## Authentication Flow

### Phase 1: Initial Setup (Dropbear + No Password)

```
┌─────────────────────────────────────────────────┐
│ Fresh OpenWrt Node                              │
│ - SSH Server: Dropbear                          │
│ - IP: 192.168.1.1                               │
│ - Root Password: Not set (factory default)      │
│ - Auth: No password required                    │
└─────────────────────────────────────────────────┘
                    │
                    │ make deploy-initial-node1
                    ▼
┌─────────────────────────────────────────────────┐
│ Deployment Process                              │
│ 1. Generate SSH key pair (if needed)            │
│ 2. Deploy public key to node                    │
│ 3. Install OpenSSH                              │
│ 4. Configure key-based auth                     │
│ 5. Set root password (console only)             │
│ 6. Remove Dropbear                              │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Configured OpenWrt Node                         │
│ - SSH Server: OpenSSH                           │
│ - IP: 10.11.12.1                                │
│ - Auth: SSH Key (passwordless)                  │
│ - Password Auth: DISABLED for SSH               │
└─────────────────────────────────────────────────┘
```

### Phase 2: Production (OpenSSH + SSH Key)

```
┌─────────────────────────────────────────────────┐
│ Control Machine                                 │
│ - Private Key: ~/.ssh/openwrt_mesh_rsa          │
└─────────────────────────────────────────────────┘
                    │
                    │ SSH with private key
                    ▼
┌─────────────────────────────────────────────────┐
│ OpenWrt Nodes                                   │
│ - Public Key: /root/.ssh/authorized_keys        │
│ - Password Auth: Disabled                       │
│ - Only accepts key-based authentication         │
└─────────────────────────────────────────────────┘
```

## SSH Key Configuration

### Default Settings

Configured in `group_vars/all.yml`:

```yaml
# SSH Key Configuration
ssh_key_path: ~/.ssh/openwrt_mesh_rsa  # Private key location
ssh_key_type: rsa                      # Key algorithm
ssh_key_bits: 4096                     # Key size
ssh_key_comment: "ansible@openwrt-mesh" # Key comment
```

### Key Generation

The deployment automatically generates SSH keys if they don't exist:

```bash
# Automatic during deployment:
ssh-keygen -t rsa -b 4096 \
  -f ~/.ssh/openwrt_mesh_rsa \
  -C "ansible@openwrt-mesh" \
  -N ""  # No passphrase
```

**Files created:**

- `~/.ssh/openwrt_mesh_rsa` - Private key (keep secure!)
- `~/.ssh/openwrt_mesh_rsa.pub` - Public key (deployed to nodes)

### Manual Key Generation (Optional)

If you prefer to generate keys manually before deployment:

```bash
# Generate RSA 4096-bit key
ssh-keygen -t rsa -b 4096 \
  -f ~/.ssh/openwrt_mesh_rsa \
  -C "ansible@openwrt-mesh"

# Set correct permissions
chmod 600 ~/.ssh/openwrt_mesh_rsa
chmod 644 ~/.ssh/openwrt_mesh_rsa.pub
```

For Ed25519 (modern, smaller, faster):

```bash
ssh-keygen -t ed25519 \
  -f ~/.ssh/openwrt_mesh_ed25519 \
  -C "ansible@openwrt-mesh"

# Update group_vars/all.yml:
# ssh_key_path: ~/.ssh/openwrt_mesh_ed25519
# ssh_key_type: ed25519
```

## OpenSSH Configuration

The deployment configures OpenSSH with these security settings:

```
/etc/ssh/sshd_config:

Port 22
PermitRootLogin prohibit-password    # Only key-based root login
PubkeyAuthentication yes              # Enable key authentication
AuthorizedKeysFile /root/.ssh/authorized_keys
PasswordAuthentication no             # DISABLED for security
ChallengeResponseAuthentication no    # DISABLED
UsePAM no                             # Not needed
X11Forwarding no                      # Not needed
Subsystem sftp /usr/libexec/sftp-server
```

**Security Features:**

- ✅ SSH key authentication only
- ✅ Password authentication disabled
- ✅ Root login allowed ONLY with key
- ✅ No interactive authentication methods
- ❌ Console/serial access still uses password

## Usage

### Initial Deployment

```bash
# 1. Connect to fresh node at 192.168.1.1
make check-initial-node1

# 2. Deploy (SSH key auto-generated and deployed)
make deploy-initial-node1

# Output shows:
# ✅ SSH Server Transition Complete
# - SSH Key: /home/user/.ssh/openwrt_mesh_rsa
# - Public Key Deployed: ssh-rsa AAAAB3Nza...
# - Root Password: Set (console access only)
# - PasswordAuthentication: Disabled
# - PubkeyAuthentication: Enabled
```

### Production Access

```bash
# Automatic (uses SSH key from inventory)
make check-node1
make deploy-node1

# Manual SSH access
ssh -i ~/.ssh/openwrt_mesh_rsa root@10.11.12.1

# Or add to ~/.ssh/config:
Host openwrt-node1
    HostName 10.11.12.1
    User root
    IdentityFile ~/.ssh/openwrt_mesh_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

# Then simply:
ssh openwrt-node1
```

## Key Management

### Viewing Keys

```bash
# View public key
cat ~/.ssh/openwrt_mesh_rsa.pub

# View key fingerprint
ssh-keygen -lf ~/.ssh/openwrt_mesh_rsa

# View key on node
ssh -i ~/.ssh/openwrt_mesh_rsa root@10.11.12.1 \
  'cat /root/.ssh/authorized_keys'
```

### Backup Keys

**IMPORTANT**: Back up your private key securely!

```bash
# Backup private key (KEEP SECURE!)
cp ~/.ssh/openwrt_mesh_rsa ~/backups/openwrt_mesh_rsa.backup

# Encrypt with GPG
gpg -c ~/.ssh/openwrt_mesh_rsa

# Store in password manager or secure vault
```

### Key Rotation

To rotate SSH keys:

```bash
# 1. Generate new key pair
ssh-keygen -t rsa -b 4096 \
  -f ~/.ssh/openwrt_mesh_rsa_new \
  -C "ansible@openwrt-mesh-$(date +%Y%m%d)"

# 2. Update group_vars/all.yml
# ssh_key_path: ~/.ssh/openwrt_mesh_rsa_new

# 3. Re-deploy to update authorized_keys
make deploy-node1
make deploy-node2
make deploy-node3

# 4. Test new key
ansible -i inventory/hosts.yml all -m ping

# 5. Remove old key
rm ~/.ssh/openwrt_mesh_rsa{,.pub}
mv ~/.ssh/openwrt_mesh_rsa_new ~/.ssh/openwrt_mesh_rsa
```

## Troubleshooting

### Cannot Connect with SSH Key

**Symptom**: `Permission denied (publickey)`

**Solutions**:

```bash
# 1. Verify private key exists and has correct permissions
ls -l ~/.ssh/openwrt_mesh_rsa
# Should show: -rw------- (600)

chmod 600 ~/.ssh/openwrt_mesh_rsa

# 2. Verify public key is deployed on node
# (Use initial inventory with password to check)
ansible -i inventory/hosts-initial.yml node1 -m raw \
  -a "cat /root/.ssh/authorized_keys"

# 3. Check OpenSSH is running
ansible -i inventory/hosts.yml node1 -m raw \
  -a "/etc/init.d/sshd status"

# 4. Check OpenSSH config
ansible -i inventory/hosts.yml node1 -m raw \
  -a "cat /etc/ssh/sshd_config"

# 5. Verbose SSH for debugging
ssh -vvv -i ~/.ssh/openwrt_mesh_rsa root@10.11.12.1
```

### Lost Private Key

**Symptom**: Private key deleted or corrupted

**Solutions**:

**Option 1: Restore from backup**

```bash
cp ~/backups/openwrt_mesh_rsa.backup ~/.ssh/openwrt_mesh_rsa
chmod 600 ~/.ssh/openwrt_mesh_rsa
```

**Option 2: Reset via serial console**

```bash
# 1. Connect via serial cable to router
# 2. Login with root password (the one you set in group_vars/all.yml)
# 3. Remove authorized_keys to allow password auth
rm /root/.ssh/authorized_keys

# 4. Edit sshd_config to allow password auth temporarily
vi /etc/ssh/sshd_config
# Change: PasswordAuthentication yes

# 5. Restart sshd
/etc/init.d/sshd restart

# 6. Re-deploy from control machine
make deploy-initial-node1  # Will generate new key
```

**Option 3: Factory reset and re-deploy**

```bash
# 1. Reset router to factory defaults
# 2. Start from Phase 1 initial setup
make check-initial-node1
make deploy-initial-node1
```

### Wrong Permissions

**Symptom**: SSH key works but Ansible complains

```bash
# Fix permissions on control machine
chmod 700 ~/.ssh
chmod 600 ~/.ssh/openwrt_mesh_rsa
chmod 644 ~/.ssh/openwrt_mesh_rsa.pub

# Fix permissions on node (if needed)
ssh -i ~/.ssh/openwrt_mesh_rsa root@10.11.12.1 \
  'chmod 700 /root/.ssh && chmod 600 /root/.ssh/authorized_keys'
```

## Security Considerations

### Best Practices

1. ✅ **Keep private key secure**
   - Never commit to git
   - Never share or email
   - Store encrypted backups only

2. ✅ **Use strong keys**
   - RSA: Minimum 4096 bits
   - Ed25519: 256 bits (recommended)

3. ✅ **Protect your control machine**
   - Encrypt home directory
   - Use full disk encryption
   - Lock screen when away

4. ✅ **Regular key rotation**
   - Rotate keys annually
   - Rotate immediately if compromised

5. ✅ **Backup strategy**
   - Encrypted backups only
   - Store in password manager
   - Test restore procedure

### What About Passphrases?

The default configuration uses **no passphrase** for automation. This is acceptable because:

- ✅ Control machine should be secured
- ✅ Keys are only for mesh network (not production servers)
- ✅ Mesh network is isolated/controlled environment
- ✅ Automation requires passwordless access

**For enhanced security**, you can use a passphrase:

```bash
# Generate with passphrase
ssh-keygen -t rsa -b 4096 -f ~/.ssh/openwrt_mesh_rsa

# Use ssh-agent for automation
eval $(ssh-agent)
ssh-add ~/.ssh/openwrt_mesh_rsa
# Enter passphrase once

# Now automation works without re-entering passphrase
make deploy-node1
```

## Comparison: Password vs SSH Key

| Aspect | Password Auth | SSH Key Auth |
|--------|---------------|---------------|
| Security | ❌ Weak (brute force) | ✅ Strong (4096-bit) |
| Automation | ⚠️ Needs sshpass | ✅ Native support |
| Convenience | ❌ Type password | ✅ Passwordless |
| Rotation | ❌ Manual per node | ✅ Automated |
| Audit Trail | ❌ Limited | ✅ Key fingerprints |
| Breach Impact | ❌ High (password reuse) | ✅ Low (isolated key) |
| Console Access | ✅ Works | ❌ Needs password |

**Recommendation**: Use SSH keys for SSH access, password for console/serial access only.

## Advanced Configuration

### Multiple SSH Keys

```yaml
# group_vars/all.yml
ssh_key_path: ~/.ssh/openwrt_mesh_rsa  # Primary key

# For specific nodes (in inventory):
node1:
  ansible_ssh_private_key_file: ~/.ssh/node1_specific_key
```

### SSH Agent Forwarding

```bash
# Enable in ~/.ssh/config
Host openwrt-node*
    ForwardAgent yes

# Now you can jump through nodes
ssh openwrt-node1  # Then from node1:
ssh 10.11.12.2     # Uses your local key
```

### Restricted Keys (Advanced)

Limit what a key can do:

```bash
# On node: /root/.ssh/authorized_keys
command="/usr/bin/batctl o" ssh-rsa AAAAB3...

# This key can ONLY run "batctl o"
```

---

**Last Updated**: 2025-11-09
**OpenWrt Version**: 24.10.4
**Security Review**: Recommended annually
