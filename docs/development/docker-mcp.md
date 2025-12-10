# Docker MCP Catalog and Toolkit

This guide explains how to set up Docker's official MCP (Model Context Protocol) Catalog and Toolkit for use with Claude Code and other AI assistants.

## What is Docker MCP Catalog and Toolkit?

Docker's MCP solution consists of three components:

| Component | Description |
|-----------|-------------|
| **MCP Catalog** | Curated repository of verified MCP servers on Docker Hub with security metadata, SBOMs, and versioning |
| **MCP Toolkit** | GUI in Docker Desktop for discovering, configuring, and managing MCP servers |
| **MCP Gateway** | Open-source CLI plugin (`docker mcp`) that manages containers and provides a unified endpoint for AI clients |

### Key Benefits

- **Centralized management** - One place to manage all MCP servers across multiple AI clients
- **Security by default** - Containers run with CPU/memory limits, filesystem isolation, and secret filtering
- **No dependency conflicts** - Each server runs in its own isolated container
- **Dynamic MCP** - AI agents can discover and add servers on-demand during conversations
- **OAuth handling** - Built-in authentication flows for GitHub, Notion, Linear, etc.

## Installation Methods

### Option 1: Docker Desktop with MCP Toolkit (GUI)

Requires Docker Desktop 4.48 or newer.

1. Open Docker Desktop
2. Go to **Settings** → **Beta features**
3. Enable **Docker MCP Toolkit**
4. Navigate to **MCP Toolkit** in the left sidebar
5. Browse the **Catalog** tab to add servers
6. Connect clients in the **Clients** tab

### Option 2: Docker Desktop on Linux

Docker MCP Toolkit requires Docker Desktop - it does not work with standalone Docker Engine.

```bash
# Install Docker Desktop on Debian/Ubuntu
# Download from: https://docs.docker.com/desktop/install/linux/

# For Debian/Ubuntu:
sudo apt install -y ./docker-desktop-<version>-amd64.deb

# Start Docker Desktop
systemctl --user start docker-desktop

# Enable MCP Toolkit in Docker Desktop settings
```

Once Docker Desktop is running:

1. Open Docker Desktop
2. Go to **Settings** → **Beta features**
3. Enable **Docker MCP Toolkit**
4. Use the MCP Toolkit GUI or CLI commands

### Option 3: Docker Engine Without Desktop (Patched Build)

!!! success "Docker MCP Now Works with Docker Engine"
    With a patched build of mcp-gateway, Docker MCP CLI works on standalone Docker Engine.
    The patch implements lazy feature initialization to defer Docker API calls until after
    CLI initialization, fixing the "no context store initialized" error.

    **Note**: Some features that rely on Docker Desktop sockets (OAuth, secrets management)
    will show warnings but core MCP functionality works.

#### Step 1: Install Docker Engine

```bash
# Update package index
sudo apt update

# Install prerequisites
sudo apt install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository (Debian)
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# For Ubuntu, replace 'debian' with 'ubuntu' in the above command

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker run hello-world
```

#### Step 2: Install Go (Required for Building)

The MCP Gateway requires Go 1.22+ to build:

```bash
# Option A: Install via apt (recommended for Debian/Ubuntu)
sudo apt install -y golang-go

# Option B: Install via snap (gets latest version)
sudo snap install go --classic

# Verify Go installation (need 1.22+)
go version
```

#### Step 3: Build and Install Patched Docker MCP CLI Plugin

The upstream mcp-gateway has a bug that prevents it from working with Docker Engine.
A patched version with lazy feature initialization is required:

```bash
# Clone the MCP Gateway repository
git clone https://github.com/docker/mcp-gateway.git
cd mcp-gateway

# Create CLI plugins directory
mkdir -p ~/.docker/cli-plugins

# Apply the lazy initialization patch (see below)
# Then build the plugin
make docker-mcp

# Verify installation
docker mcp --help
docker mcp version
```

#### Required Patch for Docker Engine Compatibility

The following changes implement lazy feature initialization to fix the
"no context store initialized" error on Docker Engine:

**File: `cmd/docker-mcp/main.go`** - Add metadata call detection:

```go
// Add this function before main()
func isMetadataCall() bool {
    for _, arg := range os.Args {
        if arg == metadata.MetadataSubcommandName {
            return true
        }
    }
    return false
}

// In main(), change features.New() to features.NewLazy():
plugin.Run(func(dockerCli command.Cli) *cobra.Command {
    var feat features.Features
    if isMetadataCall() {
        feat = features.AllDisabled()
    } else {
        feat = features.NewLazy(ctx, dockerCli)
    }
    return commands.Root(ctx, cwd, dockerCli, feat)
}, ...)
```

**File: `pkg/features/features.go`** - Add lazy features implementation:

```go
// Add after the existing featuresImpl struct

type lazyFeatures struct {
    ctx       context.Context
    dockerCli command.Cli
    once      sync.Once
    inner     Features
    initDone  bool
}

func NewLazy(ctx context.Context, dockerCli command.Cli) Features {
    return &lazyFeatures{
        ctx:       ctx,
        dockerCli: dockerCli,
    }
}

func (f *lazyFeatures) tryInit() bool {
    // Check if Docker CLI is ready
    if f.dockerCli.ContextStore() == nil {
        return false
    }
    f.once.Do(func() {
        f.inner = New(f.ctx, f.dockerCli)
        f.initDone = true
    })
    return f.initDone && f.inner != nil
}

func (f *lazyFeatures) InitError() error {
    if !f.tryInit() { return nil }
    return f.inner.InitError()
}

func (f *lazyFeatures) IsProfilesFeatureEnabled() bool {
    if !f.tryInit() { return false }
    return f.inner.IsProfilesFeatureEnabled()
}

func (f *lazyFeatures) IsRunningInDockerDesktop() bool {
    if !f.tryInit() { return false }
    return f.inner.IsRunningInDockerDesktop()
}
```

!!! info "Why This Patch is Needed"
    The upstream code calls `dockerCli.Client().Info()` during command construction,
    before the CLI is initialized (which happens in `PersistentPreRunE`). This causes
    "no context store initialized" errors. The patch defers these calls until the CLI
    is ready by checking if `ContextStore()` returns nil.

#### Step 4: Initialize the MCP Catalog

```bash
# Download the official Docker MCP Catalog
docker mcp catalog init

# List available catalogs
docker mcp catalog ls

# View available servers in the catalog
docker mcp catalog show docker-mcp
```

#### Step 5: Enable MCP Servers

```bash
# Enable servers from the catalog
docker mcp server enable github-official
docker mcp server enable playwright
docker mcp server enable filesystem
docker mcp server enable duckduckgo

# List enabled servers
docker mcp server ls

# Inspect a specific server
docker mcp server inspect github-official
```

#### Step 6: Configure Authentication (if needed)

```bash
# For GitHub - OAuth flow
docker mcp oauth authorize github

# View authorized services
docker mcp oauth ls

# Set secrets for servers that need them
docker mcp secret set grafana.url=http://localhost:3000
docker mcp secret set grafana.api_key=your-api-key

# View current configuration
docker mcp config read
```

#### Step 7: Connect Claude Code

```bash
# Connect Claude Code as a client
docker mcp client connect claude-code

# List connected clients
docker mcp client ls

# Get manual configuration instructions
docker mcp client manual-instructions claude-code
```

#### Step 8: Run the Gateway

```bash
# Run gateway in stdio mode (default for Claude Code)
docker mcp gateway run

# Run gateway with verbose logging
docker mcp gateway run --verbose

# Run gateway in SSE mode (for web clients)
docker mcp gateway run --port 8080 --transport sse
```

## CLI Command Reference

### Catalog Management

```bash
docker mcp catalog init              # Initialize default Docker MCP Catalog
docker mcp catalog ls                # List available catalogs
docker mcp catalog show <name>       # View servers in a catalog
docker mcp catalog add <url>         # Add a custom catalog
docker mcp catalog rm <name>         # Remove a catalog
docker mcp catalog update            # Update catalog data
```

### Server Management

```bash
docker mcp server ls                 # List enabled servers
docker mcp server enable <name>      # Enable a server
docker mcp server disable <name>     # Disable a server
docker mcp server inspect <name>     # Get server details
docker mcp server reset              # Reset all server settings
```

### Client Management

```bash
docker mcp client ls                 # List connected clients
docker mcp client connect <name>     # Connect a client
docker mcp client disconnect <name>  # Disconnect a client
docker mcp client manual-instructions <name>  # Get manual config
```

### OAuth & Secrets

```bash
docker mcp oauth authorize <service> # Start OAuth flow
docker mcp oauth ls                  # List authorized services
docker mcp oauth revoke <service>    # Revoke authorization

docker mcp secret set <key>=<value>  # Set a secret
docker mcp secret ls                 # List secrets
docker mcp secret rm <key>           # Remove a secret
```

### Gateway Operations

```bash
docker mcp gateway run               # Run the gateway (stdio mode)
docker mcp gateway run --verbose     # Run with debug logging
docker mcp gateway run --port 8080   # Run on specific port
docker mcp gateway run --transport sse  # Use SSE transport
```

### Tools Management

```bash
docker mcp tools ls                  # List all available tools
docker mcp tools count               # Count available tools
docker mcp tools inspect <name>      # Inspect a specific tool
docker mcp tools call <name> <args>  # Call a tool directly
docker mcp tools enable <name>       # Enable a tool
docker mcp tools disable <name>      # Disable a tool
```

### Configuration

```bash
docker mcp config read               # View current configuration
docker mcp config write '<yaml>'     # Update configuration
docker mcp config dump               # Export full config
docker mcp config reset              # Reset to defaults
docker mcp config restore            # Restore from backup
```

## Available MCP Servers

Popular servers in the Docker MCP Catalog:

| Server | Description | Auth Required |
|--------|-------------|---------------|
| `github-official` | GitHub repository management | OAuth |
| `playwright` | Browser automation | None |
| `filesystem` | Local file operations | None |
| `duckduckgo` | Web search | None |
| `brave-search` | Web search with Brave | API Key |
| `context7` | Documentation lookup | None |
| `sequentialthinking` | Reasoning chains | None |
| `mongodb` | MongoDB operations | Connection string |
| `postgres` | PostgreSQL operations | Connection string |
| `redis` | Redis operations | Connection string |
| `grafana` | Dashboard management | API Key |
| `notion` | Notion workspace | OAuth |
| `linear` | Linear issue tracking | OAuth |
| `slack` | Slack messaging | OAuth |
| `firecrawl` | Web scraping | API Key |
| `puppeteer` | Browser automation | None |

View the full catalog:

```bash
docker mcp catalog show docker-mcp
```

Or browse online at: https://hub.docker.com/mcp

## Configuration Files

The MCP Gateway stores configuration in `~/.docker/mcp/`:

| File | Purpose |
|------|---------|
| `docker-mcp.yaml` | Server catalog definitions |
| `registry.yaml` | Enabled servers list |
| `config.yaml` | Per-server configuration |
| `tools.yaml` | Tool enablement settings |
| `secrets.yaml` | Encrypted secrets |

## Claude Code Integration

### Automatic Connection

```bash
# Connect Claude Code as a client
docker mcp client connect claude-code

# Restart Claude Code to pick up changes
```

### Manual Configuration

Add to your Claude Code settings (`~/.claude.json` or `.mcp.json`):

```json
{
  "mcpServers": {
    "MCP_DOCKER": {
      "command": "docker",
      "args": ["mcp", "gateway", "run"],
      "type": "stdio"
    }
  }
}
```

Or use the CLI:

```bash
claude mcp add --transport stdio MCP_DOCKER -- docker mcp gateway run
```

### Verify Connection

In Claude Code, run `/mcp` to see connected servers. You should see `MCP_DOCKER` with all enabled servers listed.

## Security Architecture

### Build-time Security

- All `mcp/` images are Docker-built and digitally signed
- Software Bill of Materials (SBOM) included
- Source verification through image signatures
- Continuous security scanning

### Runtime Security

| Protection | Description |
|------------|-------------|
| CPU limits | 1 CPU per container |
| Memory limits | 2GB maximum per container |
| Filesystem isolation | No host access by default |
| Secret filtering | Requests with sensitive data blocked |
| Network isolation | Restricted network access |

## Example Workflows

### Enable GitHub + Playwright for Claude Code

```bash
# Initialize catalog
docker mcp catalog init

# Enable servers
docker mcp server enable github-official
docker mcp server enable playwright

# Authenticate with GitHub
docker mcp oauth authorize github

# Connect Claude Code
docker mcp client connect claude-code

# Verify
docker mcp server ls
docker mcp tools count
```

### Multi-Server Development Setup

```bash
# Enable development servers
docker mcp server enable filesystem
docker mcp server enable postgres
docker mcp server enable redis
docker mcp server enable duckduckgo

# Configure database connections (example placeholder values)
docker mcp secret set postgres.connection_string="postgresql://user:pass@localhost:5432/db"  # pragma: allowlist secret
docker mcp secret set redis.url="redis://localhost:6379"

# Start gateway
docker mcp gateway run
```

### Call Tools Directly (Testing)

```bash
# Search with DuckDuckGo
docker mcp tools call duckduckgo__search query="Docker MCP tutorial"

# List GitHub repos
docker mcp tools call github__list_repos

# Read a local file
docker mcp tools call filesystem__read_file path="/etc/hostname"
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `no context store initialized` | Apply the lazy initialization patch and rebuild from source |
| `docker mcp: command not found` | Install CLI plugin to `~/.docker/cli-plugins/` |
| `Invalid Plugins: mcp` | Apply the patch - upstream binary has initialization bug |
| Gateway won't start | Check `docker ps` works, verify Docker is running |
| OAuth fails | OAuth requires Docker Desktop sockets - use API keys instead |
| Server not appearing | Run `docker mcp catalog update` then `docker mcp server enable` |
| Permission denied | Add user to docker group: `sudo usermod -aG docker $USER` |
| Secrets/OAuth warnings | Expected on Docker Engine - core functionality still works |

### Docker Engine vs Docker Desktop

!!! info "Docker MCP Works on Both (with patch)"
    With the lazy initialization patch, Docker MCP CLI works on standalone Docker Engine.
    Some features that rely on Docker Desktop sockets will show warnings but are non-blocking.

| Feature | Docker Desktop | Docker Engine (patched) |
|---------|---------------|------------------------|
| MCP Toolkit GUI | Available | Not available |
| `docker mcp` CLI | Works | **Works (with patch)** |
| Catalog browsing | Works | Works |
| Server enable/disable | Works | Works |
| Gateway run | Works | Works |
| OAuth authentication | Works | Shows warning (use API keys) |
| Secrets via Desktop | Works | Shows warning (use env vars) |
| Direct container MCP | Works | Works |

### Diagnostic Commands

```bash
# Check Docker MCP version
docker mcp version

# View enabled servers
docker mcp server ls

# Check tool availability
docker mcp tools count
docker mcp tools ls

# View configuration
docker mcp config read

# Check OAuth status
docker mcp oauth ls

# Run gateway with verbose logging
docker mcp gateway run --verbose
```

### Reset Everything

```bash
# Reset all configurations
docker mcp config reset
docker mcp server reset

# Re-initialize
docker mcp catalog init
```

## Quick Setup Summary

### Docker Desktop (Recommended)

**On macOS/Windows:**

1. Install Docker Desktop from https://docker.com/products/docker-desktop
2. Enable MCP Toolkit in Settings → Beta features
3. Open MCP Toolkit → Catalog → Add servers
4. Go to Clients → Connect Claude Code
5. Restart Claude Code

**On Linux with Docker Desktop:**

```bash
# Install Docker Desktop for Linux
# Download .deb from: https://docs.docker.com/desktop/install/linux/
sudo apt install -y ./docker-desktop-<version>-amd64.deb
systemctl --user start docker-desktop

# Then use GUI or CLI
docker mcp catalog init
docker mcp server enable github-official
docker mcp client connect claude-code
```

### Docker Engine (Headless Linux)

!!! success "Now Supported with Patch"
    Docker MCP works on Docker Engine with the lazy initialization patch applied.

```bash
# 1. Install Docker Engine
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 2. Install Go and build patched mcp-gateway
sudo apt install -y golang-go
git clone https://github.com/docker/mcp-gateway.git
cd mcp-gateway

# 3. Apply the lazy initialization patch (see Option 3 above)
# 4. Build and install
make docker-mcp

# 5. Initialize and use
docker mcp catalog init
docker mcp server enable filesystem
docker mcp server enable duckduckgo

# 6. Connect to Claude Code
docker mcp client connect claude-code
# Or manually add to ~/.claude.json
```

### Alternative: Direct Container MCP

For simpler setups without the full MCP toolkit:

```bash
# Configure Claude Code to use MCP server containers directly
# Add to ~/.claude.json or .mcp.json:
{
  "mcpServers": {
    "filesystem": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "/path/to/files:/data", "mcp/filesystem"],
      "type": "stdio"
    }
  }
}
```

### Docker Desktop (GUI)

1. Enable MCP Toolkit in Docker Desktop Beta features
2. Open MCP Toolkit → Catalog
3. Add desired servers
4. Go to Clients → Connect Claude Desktop/Code
5. Restart Claude

## Related Resources

- [Docker Setup](docker.md) - General Docker development environment
- [Testing Guide](testing.md) - Running tests in containers
- [Contributing](contributing.md) - Development workflow

## External Documentation

- [Docker MCP Catalog](https://hub.docker.com/mcp) - Browse available servers
- [Docker MCP Toolkit Docs](https://docs.docker.com/ai/mcp-catalog-and-toolkit/)
- [MCP Gateway GitHub](https://github.com/docker/mcp-gateway)
- [Model Context Protocol](https://modelcontextprotocol.io/)
