# Advanced Features

This section covers advanced features for power users, including offline deployment, custom firmware, and extended storage.

## Section Contents

| Document | Description |
|----------|-------------|
| [Image Builder](image-builder.md) | Create custom OpenWrt firmware images |
| [Local Repository](local-repository.md) | Set up offline package repository |
| [Repository Implementation](repo-implementation.md) | Technical repository details |
| [Full Archive Mode](full-archive.md) | Complete offline deployment |
| [Monitoring & Alerting](monitoring-alerting.md) | Advanced monitoring setup |

## When to Use Advanced Features

| Feature | Use Case |
|---------|----------|
| **Local Repository** | Deploying multiple nodes, slow/expensive internet |
| **Image Builder** | Custom packages, faster deployments, consistent images |
| **Full Archive** | Air-gapped networks, disaster recovery |
| **USB Storage** | Persistent logs, large configs, monitoring data |

## Feature Comparison

```
Standard Deploy
      │
      ├── Need Faster? ──► Local Repository
      │
      ├── Need Offline? ──► Full Archive Mode
      │
      ├── Need Storage? ──► USB Storage (see Operations)
      │
      └── Need Custom FW? ──► Image Builder
```

## Quick Start: Local Repository

```bash
# Download all packages (~500MB-1GB)
make repo-setup

# Start local HTTP server
make repo-start

# Deploy using local repo
OPKG_REPO_URL=http://your-ip:8080 make deploy-node NODE=1
```

## Quick Start: Image Builder

```bash
# Create config snapshot
make snapshot NODE=1

# Build custom image
make image-build NODE=1

# Flash to node
make sysupgrade NODE=1
```

## Quick Start: Full Archive

```bash
# Create complete offline archive
make archive-full

# Deploy from archive (no internet required)
make deploy-offline NODE=1
```

## Performance Benefits

| Feature | Benefit |
|---------|---------|
| Local Repo | 60% faster package installation |
| Custom Image | 80% faster deployments (packages pre-installed) |
| Full Archive | 100% offline capability |

## Combining Features

For maximum efficiency, combine features:

1. **Build custom image** with all packages pre-installed
2. **Use USB storage** for persistent logs and metrics
3. **Keep full archive** for disaster recovery

```bash
# Complete advanced setup
make repo-setup                  # Cache packages
make snapshot NODE=1             # Capture current config
make image-build NODE=1          # Build with packages
make deploy-monitoring NODE=1    # Enable monitoring
```

## Related Documentation

- [Operations](../operations/index.md) - USB Storage and Monitoring
- [Deployment](../deployment/index.md) - Standard deployment methods
- [Reference](../reference/index.md) - Command reference
