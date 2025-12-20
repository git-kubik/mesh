# Loading Memory MCP Knowledge Graph

## Overview

The file `.claude/memory-init.json` contains the initial knowledge graph for the mesh project.

## How It Gets Loaded

When Claude connects to this repository and follows CLAUDE.md instructions:

1. **Session Start**: Claude calls Memory MCP `read_graph` to load existing knowledge
2. **First Session**: If graph is empty, Claude should create entities from `memory-init.json`
3. **Subsequent Sessions**: Graph persists and grows with new knowledge

## Manual Loading (for Claude)

If the knowledge graph is empty, Claude should execute these Memory MCP calls:

### 1. Create Entities

```json
// Call: memory.create_entities
{
  "entities": [
    // All entities from memory-init.json
  ]
}
```

### 2. Create Relations

```json
// Call: memory.create_relations
{
  "relations": [
    // All relations from memory-init.json
  ]
}
```

## Entity Types in This Project

| Type | Prefix/Pattern | Examples |
|------|----------------|----------|
| project | `mesh-project` | Main project entity |
| hardware | `mesh-node*`, `tp-link-switches` | Physical devices |
| technology | `batman-adv` | Core technologies |
| component | `*-config`, `*-infrastructure` | Subsystems |
| network | `network-*` | Network segments |
| config-file | `file:*` | Configuration files |
| playbook | `file:playbooks/*` | Ansible playbooks |
| ansible-role | `role:*` | Ansible roles |
| project-tracking | `phase-status` | Progress tracking |

## Updating the Knowledge Graph

During work sessions, Claude should:

1. **Add new entities** when discovering new components
2. **Add observations** when learning facts about existing entities
3. **Add relations** when understanding connections
4. **Update phase-status** observations when project progresses

## Verifying the Graph

```
// Call: memory.read_graph
// Returns all entities and relations

// Call: memory.search_nodes
{
  "query": "mesh"
}
// Returns entities matching "mesh"
```
