# Claude Code Skills for Mesh Network Project

This directory contains custom Claude Code skills for managing the OpenWrt mesh network deployment project.

## Available Skills

### Project Management

#### `mesh-pm` - Mesh Network Project Manager

**Purpose**: Comprehensive project management for the OpenWrt mesh network deployment.

**Usage**:
```
User: pm status
User: pm next
User: pm validate phase 1
User: pm blockers
User: pm report
User: pm ready?
```

**What it does**:
- Tracks progress across all 12 implementation phases
- Identifies next priority tasks
- Validates phase completion
- Identifies blockers and risks
- Generates status reports
- Evaluates production readiness

---

### Development Skills

#### `docker-dev` - Docker Development & Containerization

**Purpose**: Docker container development, Docker Compose orchestration, and web interface integration.

**Expertise**:
- Multi-stage Dockerfile development
- Docker Compose service orchestration
- Semaphore/AWX web interface setup
- Volume and network configuration
- Container security and optimization
- Entrypoint scripts and initialization

**Use when**: Building Docker infrastructure, debugging containers, or setting up the Ansible web interface.

---

#### `python-test` - Python Testing with UV

**Purpose**: Python test development using pytest and UV package management.

**Expertise**:
- pytest test suite development (unit, integration, functional, performance, failover)
- UV dependency management and virtual environments
- Test fixtures and conftest.py configuration
- Coverage reporting and CI/CD integration
- Test automation and report generation

**Use when**: Writing tests, managing Python dependencies with UV, or setting up test automation.

---

#### `ansible-dev` - Ansible Development

**Purpose**: Ansible playbook development and automation for OpenWrt configuration.

**Expertise**:
- Playbook creation and debugging
- Jinja2 template development for OpenWrt UCI configs
- Inventory and group_vars management
- Ansible Vault for secrets
- Ad-hoc commands and verification
- Tags and limits for selective execution

**Use when**: Creating or modifying Ansible playbooks, developing templates, or managing inventory.

---

#### `openwrt-config` - OpenWrt Configuration

**Purpose**: OpenWrt system configuration and administration.

**Expertise**:
- UCI (Unified Configuration Interface) system
- Package management with opkg
- Network interface configuration
- Wireless configuration (802.11r, mesh mode)
- Firewall and routing rules
- System administration and debugging

**Use when**: Configuring OpenWrt nodes, troubleshooting UCI configs, or managing packages.

---

#### `batman-mesh` - Batman-adv Mesh Networking

**Purpose**: Batman-adv mesh protocol configuration and optimization.

**Expertise**:
- B.A.T.M.A.N. V protocol understanding
- Mesh topology design and troubleshooting
- Gateway selection and failover
- TQ (Transmit Quality) analysis
- batctl commands and diagnostics
- Performance optimization

**Use when**: Configuring batman-adv, troubleshooting mesh topology, or optimizing mesh performance.

---

#### `tech-docs` - Technical Documentation

**Purpose**: Creating comprehensive technical documentation.

**Expertise**:
- User guides (deployment, operation, troubleshooting)
- Developer guides (testing, contributing)
- API/configuration reference
- Architecture documentation
- Markdown best practices
- Diagram creation

**Use when**: Writing or updating documentation, creating guides, or improving existing docs.

---

#### `mesh-test` - Mesh Network Testing

**Purpose**: Network testing, performance benchmarking, and failover validation.

**Expertise**:
- Network connectivity testing (ping, traceroute, etc.)
- Performance benchmarking (iperf3, latency tests)
- Mesh-specific validation (batman topology, TQ values)
- Failover scenario testing
- DHCP/DNS testing
- Automated test execution

**Use when**: Testing mesh functionality, benchmarking performance, or validating failover scenarios.

---

#### `project-standards` - Project Standards and Best Practices

**Purpose**: Code quality, documentation standards, testing requirements, security practices, and development workflows.

**Expertise**:
- Code style standards (Python PEP 8, YAML, Jinja2, Bash)
- Documentation standards (Markdown, MkDocs)
- Testing standards (pytest, coverage requirements)
- Security standards (secrets management, SSH keys, passwords)
- Git workflow standards (branching, commits, PR templates)
- Infrastructure as Code best practices
- CI/CD pipeline requirements
- Code review guidelines
- Automated enforcement tools (pre-commit hooks, linters)

**Use when**: Setting up development environment, reviewing code, enforcing quality standards, or ensuring security compliance.

---

## How Skills Work

Claude Code skills are reusable command sets that give Claude specific context and capabilities. When you invoke a skill, Claude loads the skill's instructions and operates within that context.

### Invoking Skills

Skills are automatically invoked when you ask questions or request actions related to their domain:

**Examples**:
- "Help me write a Dockerfile" → Invokes `docker-dev`
- "Create a pytest test for the mesh topology" → Invokes `python-test`
- "How do I configure UCI on OpenWrt?" → Invokes `openwrt-config`
- "Check the batman-adv gateway list" → Invokes `batman-mesh`
- "Write a troubleshooting guide" → Invokes `tech-docs`
- "Benchmark throughput between nodes" → Invokes `mesh-test`

You can also explicitly request a skill:
```
User: Use the docker-dev skill to help me with containers
User: I need the batman-mesh skill for troubleshooting
```

## Skill Organization

### By Development Phase

**Phase 1-4: Docker Infrastructure**
- Primary: `docker-dev`
- Supporting: `ansible-dev`

**Phase 5-9: Test Implementation**
- Primary: `python-test`, `mesh-test`
- Supporting: `ansible-dev`, `batman-mesh`, `openwrt-config`

**Phase 10: Test Automation**
- Primary: `python-test`
- Supporting: `docker-dev`

**Phase 12: Documentation**
- Primary: `tech-docs`
- Supporting: All other skills (as reference)

### By Technical Domain

**Infrastructure & Deployment**:
- `docker-dev` - Containerization
- `ansible-dev` - Automation

**Network & Mesh**:
- `openwrt-config` - System configuration
- `batman-mesh` - Mesh routing

**Quality & Validation**:
- `python-test` - Test development
- `mesh-test` - Network testing

**Documentation**:
- `tech-docs` - All documentation types

**Project Management**:
- `mesh-pm` - Progress tracking

## Creating New Skills

To create a new skill:

1. Create a markdown file in `.claude/skills/`
2. Define the skill's purpose and capabilities
3. Provide clear instructions for Claude
4. Document usage examples
5. Update this README with skill information

## Skill Best Practices

- **Focused domain**: Keep skills specialized on specific areas
- **Clear instructions**: Provide actionable guidance
- **Validation criteria**: Include success metrics
- **Expected outputs**: Document what results should look like
- **Reference files**: Link to relevant project files
- **Examples**: Show concrete usage patterns

## Skill Maintenance

### When to Update Skills

- **Project changes**: When requirements or structure changes
- **New learnings**: When discovering better approaches
- **User feedback**: When skills don't provide expected help
- **Tool updates**: When dependencies or tools change

### Updating Skills

1. Edit the skill's markdown file
2. Test changes with relevant questions
3. Update this README if usage changes
4. Document changes in Git commit

## Getting Help with Skills

If a skill isn't providing the help you need:

1. **Be specific**: Provide detailed context about what you're trying to do
2. **Reference files**: Mention specific files you're working with
3. **Clarify intent**: Explain your end goal, not just the immediate task
4. **Request skill**: Explicitly ask for a specific skill if needed

## Reference

- Main project instructions: `/home/m/repos/mesh/CLAUDE.md`
- Technical documentation: `/home/m/repos/mesh/docs/`
- Ansible playbooks: `/home/m/repos/mesh/openwrt-mesh-ansible/`
