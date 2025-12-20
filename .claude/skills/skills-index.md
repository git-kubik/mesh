# Claude Code Skills Index

This directory contains specialized skills for working with the OpenWrt Mesh Network project.

## Available Skills

| Skill | Description | Use When |
|-------|-------------|----------|
| [diagram-generator](diagram-generator.md) | SVG/Mermaid diagram generation | Creating architecture, topology, or flow diagrams |

## Invoking Skills

Reference skills in your prompts:

```
Use the diagram-generator skill to create a network topology diagram
```

Or ask Claude to use specific skill capabilities:

```
Generate a Mermaid diagram showing the VLAN architecture
```

## Skill Structure

Each skill markdown file contains:

1. **Capabilities** - What the skill can do
2. **Output Formats** - Supported output types
3. **Examples** - Ready-to-use templates
4. **Usage Instructions** - How to apply the skill
5. **Best Practices** - Guidelines for best results

## Adding New Skills

Create a new `.md` file in this directory with:

```markdown
# Skill Name

Brief description of the skill's purpose.

## Capabilities
- Capability 1
- Capability 2

## Usage
How to use this skill...

## Examples
Concrete examples...
```

## Project-Specific Context

These skills are tailored for:

- **Hardware**: D-Link DIR-1960 A1 routers, TP-Link TL-SG108E switches
- **Software**: OpenWrt 24.10, Batman-adv V, Ansible
- **Network**: 3-node mesh with VLANs (10, 20, 30, 100, 200)
- **Documentation**: MkDocs Material with Mermaid support
