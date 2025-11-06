# Docker Environment for OpenWrt Mesh Network

This directory contains the Docker infrastructure for deploying and managing the OpenWrt mesh network using Ansible.

## Overview

The Docker environment provides:

- **Ansible Runtime**: Container with Ansible and all dependencies
- **Semaphore Web Interface**: Web-based UI for running Ansible playbooks
- **PostgreSQL Database**: Backend for Semaphore
- **Persistent Storage**: Volumes for SSH keys, backups, and configuration

## Quick Start

### 1. Initial Setup

```bash
# Copy environment variables template
cp .env.example .env

# Edit .env with your actual values
nano .env

# IMPORTANT: Set secure passwords for:
# - POSTGRES_PASSWORD
# - SEMAPHORE_ADMIN_PASSWORD
# - MESH_PASSWORD, CLIENT_PASSWORD, GUEST_PASSWORD
```

### 2. Start Services

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access Web Interface

Open browser to: <http://localhost:3000>

- **Username**: admin (or value from .env)
- **Password**: Value from SEMAPHORE_ADMIN_PASSWORD in .env

## Container Services

### Ansible Container

The main Ansible runtime for executing playbooks.

**Access shell:**

```bash
docker-compose exec ansible sh
```

**Run playbooks:**

```bash
# Check mode (dry-run)
docker-compose exec ansible ansible-playbook -i /ansible/inventory/hosts.yml /ansible/playbooks/deploy.yml --check

# Execute deployment
docker-compose exec ansible ansible-playbook -i /ansible/inventory/hosts.yml /ansible/playbooks/deploy.yml

# Verify deployment
docker-compose exec ansible ansible-playbook -i /ansible/inventory/hosts.yml /ansible/playbooks/verify.yml
```

**Check Ansible version:**

```bash
docker-compose exec ansible ansible --version
```

### Semaphore Web Interface

Web-based Ansible management interface.

**Automated Setup (Recommended):**

First, ensure you have a `.env` file with credentials:

```bash
cp .env.example .env
# Edit .env and set SEMAPHORE_ADMIN_PASSWORD
```

Then run the automated configuration script:

```bash
./setup-semaphore.sh
```

This will automatically create:

- Project: "OpenWrt Mesh Network"
- Inventory: "Mesh Nodes" pointing to `/ansible/inventory/hosts.yml`
- Environment: "Production"
- Templates: Deploy, Verify, and Backup playbooks

**Note**: The script requires `.env` file with `SEMAPHORE_ADMIN` and `SEMAPHORE_ADMIN_PASSWORD` set.

**Manual Configuration (Optional):**

If you prefer manual setup:

1. Log in to <http://localhost:3000>
2. Create a new project pointing to `/ansible`
3. Add inventory from `/ansible/inventory/hosts.yml`
4. Create job templates for playbooks:
   - Deploy: `/ansible/playbooks/deploy.yml`
   - Verify: `/ansible/playbooks/verify.yml`
   - Backup: `/ansible/playbooks/backup.yml`

### PostgreSQL Database

Database backend for Semaphore. Managed automatically.

**Access database (if needed):**

```bash
docker-compose exec postgres psql -U semaphore -d semaphore
```

## SSH Key Management

SSH keys for accessing OpenWrt nodes are stored in a Docker volume.

### Generate New SSH Keys

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "mesh-ansible" -f mesh_key

# Copy to Docker volume
docker run --rm -v mesh_ssh-keys:/keys -v $(pwd):/src alpine sh -c "cp /src/mesh_key* /keys/ && chmod 600 /keys/mesh_key && chmod 644 /keys/mesh_key.pub"

# Verify
docker-compose exec ansible ls -la /root/.ssh/
```

### Copy Public Key to Nodes

```bash
# For each node (adjust IP as needed):
ssh-copy-id -i mesh_key.pub root@192.168.1.1
ssh-copy-id -i mesh_key.pub root@10.11.12.2
ssh-copy-id -i mesh_key.pub root@10.11.12.3
```

## Data Persistence

### Volumes

- **mesh_ssh-keys**: SSH keys for node access
- **mesh_backups**: Node configuration backups
- **mesh_postgres-data**: PostgreSQL database
- **mesh_semaphore-data**: Semaphore configuration

### Backup Volumes

```bash
# Backup SSH keys
docker run --rm -v mesh_ssh-keys:/data -v $(pwd):/backup alpine tar czf /backup/ssh-keys-backup.tar.gz -C /data .

# Backup Semaphore data
docker run --rm -v mesh_semaphore-data:/data -v $(pwd):/backup alpine tar czf /backup/semaphore-backup.tar.gz -C /data .

# Backup PostgreSQL
docker-compose exec postgres pg_dump -U semaphore semaphore > postgres-backup.sql
```

### Restore Volumes

```bash
# Restore SSH keys
docker run --rm -v mesh_ssh-keys:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/ssh-keys-backup.tar.gz"

# Restore Semaphore data
docker run --rm -v mesh_semaphore-data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/semaphore-backup.tar.gz"

# Restore PostgreSQL
docker-compose exec -T postgres psql -U semaphore semaphore < postgres-backup.sql
```

## Development Workflow

### Rebuild After Changes

```bash
# Rebuild Ansible container
docker-compose down
docker-compose build --no-cache ansible
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ansible
docker-compose logs -f semaphore
```

### Run Tests

```bash
# Run pytest in Ansible container
docker-compose exec ansible pytest /tests/unit -v --cov

# Run specific test
docker-compose exec ansible pytest /tests/unit/test_config.py -v
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs ansible

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Can't Reach Nodes

```bash
# Test connectivity from container
docker-compose exec ansible ping -c 3 10.11.12.1

# Check routing
docker-compose exec ansible ip route

# Test SSH
docker-compose exec ansible ssh -i /root/.ssh/mesh_key root@10.11.12.1
```

### Semaphore Won't Load

```bash
# Check database connection
docker-compose logs postgres
docker-compose logs semaphore

# Restart services
docker-compose restart semaphore
```

### Reset Everything

```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart specific service
docker-compose restart ansible

# View running containers
docker-compose ps

# Access Ansible shell
docker-compose exec ansible sh

# Run Ansible playbook
docker-compose exec ansible ansible-playbook /ansible/playbooks/deploy.yml

# Check Ansible inventory
docker-compose exec ansible ansible-inventory --list

# View resource usage
docker stats

# Clean up unused resources
docker system prune -a
```

## Security Notes

- **Never commit .env file** - Contains passwords and secrets
- **Secure SSH keys** - Stored in Docker volume, not in Git
- **Change default passwords** - Update SEMAPHORE_ADMIN_PASSWORD
- **Restrict web access** - Bind to localhost (127.0.0.1:3000) in production
- **Regular backups** - Backup volumes and database regularly

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Host Machine                    │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │         Docker Compose Network             │ │
│  │                                            │ │
│  │  ┌──────────┐  ┌───────────┐  ┌────────┐ │ │
│  │  │ Ansible  │  │ Semaphore │  │Postgres│ │ │
│  │  │Container │◄─┤  Web UI   │◄─┤   DB   │ │ │
│  │  └────┬─────┘  └─────┬─────┘  └────────┘ │ │
│  │       │              │                    │ │
│  │       │              │                    │ │
│  └───────┼──────────────┼────────────────────┘ │
│          │              │                       │
│          │              └─► Port 3000           │
│          │                                      │
│          └─► SSH to OpenWrt Nodes               │
│              (192.168.1.1, 10.11.12.0/24)       │
└─────────────────────────────────────────────────┘
```

## Files

- `Dockerfile` - Ansible container image definition
- `docker-compose.yml` - Service orchestration
- `entrypoint.sh` - Container initialization script
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template
- `.dockerignore` - Build context exclusions
- `README.md` - This file

## Support

For issues or questions:

1. Check logs: `docker-compose logs -f`
2. Review [CONTRIBUTING.md](CONTRIBUTING.md)
3. Consult Docker skill: Use `docker-dev` skill in Claude Code
4. Open GitHub issue with relevant logs

## Next Steps

After successful Docker setup:

1. Configure Semaphore web interface
2. Import SSH keys for node access
3. Test playbook execution from web UI
4. Set up automated backups
5. Proceed to Phase 2-4 implementation
