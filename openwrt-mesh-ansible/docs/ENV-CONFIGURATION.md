# Environment Configuration Guide

## Overview

This project uses **environment variables** stored in a `.env` file for all sensitive configuration including passwords and secrets. This approach provides:

✅ **Security**: Passwords never committed to git
✅ **Flexibility**: Easy to change without editing code
✅ **Best Practice**: Industry standard for secrets management
✅ **Team-Friendly**: Each developer has their own `.env` file

**IMPORTANT**: The `.env` file is located at the **repository root** (`/home/m/repos/mesh/.env`), not in the `openwrt-mesh-ansible/` subdirectory. This allows both Docker and Ansible to share the same configuration.

## Quick Start

```bash
# Navigate to repository root
cd /home/m/repos/mesh

# 1. Copy the example file
cp .env.example .env

# 2. Edit with your passwords
nano .env  # or vim, code, etc.

# 3. Set secure permissions
chmod 600 .env

# 4. Load environment (for current shell)
set -a; source .env; set +a

# 5. Deploy
make deploy-initial-node1
```

## Environment Variables Reference

### Required Variables

These **must** be set before deployment:

| Variable | Purpose | Example | Notes |
|----------|---------|---------|-------|
| `ROOT_PASSWORD` | Root console access | `MySecurePass123!` | For serial/console only, NOT SSH |
| `MESH_PASSWORD` | 2.4GHz mesh backhaul | `MeshNetwork2024!` | WPA3-SAE, min 8 chars |
| `CLIENT_PASSWORD` | 5GHz client WiFi | `ClientWiFi2024!` | WPA2/WPA3, min 8 chars |

### Optional Variables

These have defaults but can be overridden:

| Variable | Purpose | Default | Override Example |
|----------|---------|---------|------------------|
| `MGMT_PASSWORD` | Management network | (required if VLANs enabled) | `MgmtAccess2024!` |
| `GUEST_PASSWORD` | Guest network | (required if VLANs enabled) | `GuestWiFi2024!` |
| `SSH_KEY_PATH` | SSH private key location | `~/.ssh/openwrt_mesh_rsa` | `~/.ssh/custom_key` |
| `MESH_NETWORK` | Mesh subnet | `10.11.12.0` | `192.168.100.0` |
| `BATMAN_GW_BANDWIDTH` | WAN bandwidth (kbit/s) | `100000/100000` | `500000/50000` |

## Setup Instructions

### 1. Create Your .env File

```bash
# In the project root directory
cd /home/m/repos/mesh/openwrt-mesh-ansible

# Copy the example
cp .env.example .env
```

### 2. Generate Strong Passwords

**Option A: Using openssl**

```bash
# Generate random 24-character passwords
openssl rand -base64 24

# Run multiple times for each password
for i in ROOT MESH CLIENT MGMT GUEST; do
  echo "${i}_PASSWORD=$(openssl rand -base64 24)"
done
```

**Option B: Using pwgen**

```bash
# Install pwgen if needed
sudo apt-get install pwgen

# Generate secure 20-character passwords
pwgen -s 20 5  # Generates 5 passwords
```

**Option C: Using a password manager**

- 1Password: Generate password (min 16 chars)
- Bitwarden: Generate password (passphrase or random)
- KeePass: Tools → Generate Password

### 3. Edit the .env File

```bash
# Open with your preferred editor
nano .env
```

**Example .env file:**

```bash
# System Security
ROOT_PASSWORD=jK8#mP2$nQ9@vR5%

# Wireless Networks
MESH_PASSWORD=SecureMesh2024!Network
CLIENT_PASSWORD=HomeWiFi2024!Secure

# Optional Networks (if VLANs enabled)
MGMT_PASSWORD=AdminAccess2024!Mgmt
GUEST_PASSWORD=GuestWiFi2024!Limited
```

### 4. Secure the .env File

```bash
# Set restrictive permissions (owner read/write only)
chmod 600 .env

# Verify it's not in git
git status  # Should NOT show .env

# Verify .env is in .gitignore
grep "^\.env$" .gitignore  # Should output: .env
```

### 5. Load Environment Variables

**Option A: One-time load (current shell only)**

```bash
# Load variables into current shell
set -a; source .env; set +a

# Verify variables are loaded
echo $ROOT_PASSWORD  # Should show your password
```

**Option B: Auto-load (recommended)**

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Auto-load .env in project directory
if [ -f ~/repos/mesh/openwrt-mesh-ansible/.env ]; then
  set -a
  source ~/repos/mesh/openwrt-mesh-ansible/.env
  set +a
fi
```

**Option C: direnv (automatic)**

```bash
# Install direnv
sudo apt-get install direnv

# Add to ~/.bashrc
eval "$(direnv hook bash)"

# Allow direnv in project
cd /home/m/repos/mesh/openwrt-mesh-ansible
echo 'dotenv' > .envrc
direnv allow

# Now .env loads automatically when entering directory
```

## Usage

### Deployment

Once `.env` is configured and loaded:

```bash
# Check environment is loaded
env | grep _PASSWORD  # Should show masked values

# Deploy to nodes
make deploy-initial-node1
make deploy-initial-node2
make deploy-initial-node3

# Production management
make deploy
make check-all
```

### Verifying Configuration

```bash
# Check a specific variable
echo $MESH_PASSWORD

# Check all password variables are set
for var in ROOT_PASSWORD MESH_PASSWORD CLIENT_PASSWORD; do
  if [ -z "${!var}" ]; then
    echo "ERROR: $var not set"
  else
    echo "✓ $var is set"
  fi
done
```

### Ansible Behavior

Ansible reads environment variables using the `lookup` plugin:

```yaml
# In group_vars/all.yml
root_password: "{{ lookup('env', 'ROOT_PASSWORD') | default('CHANGE_THIS_PASSWORD', true) }}"
```

**Fallback behavior:**

- If `ROOT_PASSWORD` is set → uses environment value ✅
- If `ROOT_PASSWORD` is NOT set → uses `CHANGE_THIS_PASSWORD` ⚠️

## Security Best Practices

### Password Requirements

1. **Minimum Length**: 16 characters (recommended)
2. **Complexity**: Mix of uppercase, lowercase, numbers, symbols
3. **Uniqueness**: Different password for each service
4. **Avoid**: Dictionary words, common patterns, personal information

### File Security

```bash
# Correct permissions
chmod 600 .env                    # ✅ Owner read/write only
chmod 644 .env                    # ❌ World readable!

# Check permissions
ls -l .env
# Should show: -rw------- (600)

# Check .env is excluded from git
git check-ignore .env
# Should output: .env
```

### Never Commit .env

```bash
# ❌ NEVER do this:
git add .env
git commit -m "Add passwords"  # NO!

# ✅ If .env was accidentally committed:
git rm --cached .env
git commit -m "Remove .env from git"

# Then rotate ALL passwords (they're now compromised)
```

### Backup Strategy

```bash
# Backup .env securely (encrypted)
gpg -c .env
mv .env.gpg ~/secure-backups/openwrt-mesh-env-$(date +%Y%m%d).gpg

# Store encrypted backup in password manager
# Or secure vault (not in git!)

# Restore from backup
gpg -d ~/secure-backups/openwrt-mesh-env-20250109.gpg > .env
chmod 600 .env
```

## Troubleshooting

### Error: "CHANGE_THIS_PASSWORD" in Deployment

**Symptom:**

```
The task includes an option with an undefined variable. The error was: 'ROOT_PASSWORD' is undefined
```

**Solution:**

```bash
# 1. Check .env exists
ls -la .env

# 2. Check .env has passwords
cat .env | grep PASSWORD

# 3. Load environment
set -a; source .env; set +a

# 4. Verify it's loaded
echo $ROOT_PASSWORD
```

### Error: Permission Denied

**Symptom:**

```
bash: .env: Permission denied
```

**Solution:**

```bash
# Fix permissions
chmod 600 .env

# Make sure it's not executable
chmod -x .env
```

### Passwords Not Loading

**Symptom:**

```
echo $ROOT_PASSWORD
# (shows nothing)
```

**Solutions:**

```bash
# Option 1: Reload environment
set -a; source .env; set +a

# Option 2: Check syntax
# Make sure no spaces around =
ROOT_PASSWORD=value   # ✅ Correct
ROOT_PASSWORD = value # ❌ Wrong

# Option 3: Check for BOM/encoding issues
file .env  # Should show: ASCII text

# If shows UTF-8 with BOM, fix:
dos2unix .env
```

### Variables Not Passed to Ansible

**Symptom:**
Ansible still uses default values instead of .env values

**Solution:**

```bash
# Make sure environment is exported
export ROOT_PASSWORD="your-password"  # pragma: allowlist secret

# Or use set -a before sourcing
set -a
source .env
set +a

# Verify Ansible can see variables
ansible localhost -m debug -a "msg={{ lookup('env', 'ROOT_PASSWORD') }}"
```

## Advanced Configuration

### Using Ansible Vault (Alternative)

If you prefer Ansible Vault instead of .env:

```bash
# Create vault file
ansible-vault create group_vars/vault.yml

# Add passwords
root_password: YourSecurePassword
mesh_password: YourMeshPassword

# Reference in group_vars/all.yml
root_password: "{{ vault_root_password }}"
```

### Environment-Specific Configs

```bash
# Development
.env.development

# Production
.env.production

# Load specific environment
source .env.production
```

### Docker Integration

If using Docker (future):

```bash
# docker-compose.yml
env_file:
  - .env

# Or explicit environment
environment:
  - ROOT_PASSWORD=${ROOT_PASSWORD}
```

## Migration from Hardcoded Passwords

If upgrading from hardcoded passwords:

```bash
# 1. Extract current passwords
grep "password:" group_vars/all.yml

# 2. Create .env with current values
cat > .env << 'EOF'
ROOT_PASSWORD=YourSecureRootPassword123!
MESH_PASSWORD=YourSecureMeshPassword123!
CLIENT_PASSWORD=YourClientPassword123!
EOF

# 3. Test deployment works
set -a; source .env; set +a
make check-node1

# 4. Change passwords (now that .env works)
# Generate new strong passwords
# Update .env
# Re-deploy
```

## Summary

**Setup checklist:**

- [ ] Copy `.env.example` to `.env`
- [ ] Generate strong passwords
- [ ] Update `.env` with passwords
- [ ] Set permissions: `chmod 600 .env`
- [ ] Verify `.env` in `.gitignore`
- [ ] Load environment: `set -a; source .env; set +a`
- [ ] Test: `echo $ROOT_PASSWORD`
- [ ] Deploy: `make deploy-initial-node1`
- [ ] Backup `.env` securely (encrypted)
- [ ] Never commit `.env` to git

**Security checklist:**

- [ ] All passwords are 16+ characters
- [ ] Each service has unique password
- [ ] `.env` has 600 permissions
- [ ] `.env` is in `.gitignore`
- [ ] Encrypted backup exists
- [ ] Team members have own `.env` files

---

**Last Updated**: 2025-11-09
**Security Review**: Recommended annually
