# SVG Diagram Generator Skill

This skill enables understanding codebase architecture and generating SVG diagrams for documentation.

## Capabilities

- Analyze code structure and generate architecture diagrams
- Create network topology visualizations
- Generate VLAN and traffic flow diagrams
- Produce deployment workflow diagrams
- Create component relationship diagrams
- Output pure SVG format

## SVG Output Format

All diagrams are generated as valid SVG markup:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000">
  <defs>
    <!-- Reusable definitions (gradients, markers, filters) -->
  </defs>
  <style>
    /* CSS styling */
  </style>
  <!-- Diagram elements -->
</svg>
```

## SVG Components Library

### Node Box (Router/Server)

```xml
<g class="node" transform="translate(100, 100)">
  <rect width="120" height="80" rx="8" fill="#4051b5" stroke="#303f9f" stroke-width="2"/>
  <text x="60" y="35" text-anchor="middle" fill="white" font-family="system-ui" font-size="14" font-weight="bold">Node 1</text>
  <text x="60" y="55" text-anchor="middle" fill="#e8eaf6" font-family="system-ui" font-size="11">10.11.12.1</text>
</g>
```

### Switch Box

```xml
<g class="switch" transform="translate(100, 100)">
  <rect width="160" height="60" rx="4" fill="#2e7d32" stroke="#1b5e20" stroke-width="2"/>
  <text x="80" y="28" text-anchor="middle" fill="white" font-family="system-ui" font-size="13" font-weight="bold">Switch A</text>
  <text x="80" y="45" text-anchor="middle" fill="#c8e6c9" font-family="system-ui" font-size="10">TL-SG108E</text>
</g>
```

### Cloud (Internet/WAN)

```xml
<g class="cloud" transform="translate(100, 50)">
  <path d="M25,60 Q0,60 0,40 Q0,20 25,20 Q30,0 55,0 Q80,0 85,20 Q110,20 110,40 Q110,60 85,60 Z"
        fill="#f57c00" stroke="#e65100" stroke-width="2"/>
  <text x="55" y="38" text-anchor="middle" fill="white" font-family="system-ui" font-size="12" font-weight="bold">Internet</text>
</g>
```

### Connection Lines

```xml
<!-- Solid line (wired) -->
<line x1="100" y1="100" x2="200" y2="200" stroke="#666" stroke-width="2"/>

<!-- Dashed line (wireless) -->
<line x1="100" y1="100" x2="200" y2="200" stroke="#7b1fa2" stroke-width="2" stroke-dasharray="8,4"/>

<!-- Arrow line -->
<defs>
  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#666"/>
  </marker>
</defs>
<line x1="100" y1="100" x2="200" y2="200" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
```

### Labels

```xml
<!-- Connection label -->
<text x="150" y="145" text-anchor="middle" fill="#666" font-family="system-ui" font-size="10">
  <tspan>LAN3</tspan>
  <tspan x="150" dy="12">VLAN 100</tspan>
</text>

<!-- Box with background -->
<g transform="translate(100, 100)">
  <rect x="-30" y="-10" width="60" height="20" rx="3" fill="#fff" stroke="#ccc"/>
  <text x="0" y="4" text-anchor="middle" fill="#333" font-family="system-ui" font-size="10">VLAN 10</text>
</g>
```

### VLAN Color Coding

```xml
<style>
  .vlan-10 { fill: #1976d2; }   /* Management - Blue */
  .vlan-20 { fill: #7b1fa2; }   /* Guest - Purple */
  .vlan-30 { fill: #f57c00; }   /* IoT - Orange */
  .vlan-100 { fill: #616161; }  /* Mesh - Gray */
  .vlan-200 { fill: #2e7d32; }  /* Client - Green */
</style>
```

## Complete Diagram Templates

### Network Topology

**Layout Best Practices:**

- **Consistent sizing**: All switches use same dimensions (340×70px)
- **Aligned positioning**: Place switches at same Y position (y=340) in horizontal row
- **Clear hierarchy**: Nodes above, switches middle, devices below
- Use `<path>` with right-angle segments to route around obstacles
- Stagger horizontal line Y-positions (e.g., 290, 298, 306) to prevent overlapping
- Connect device groups directly below their parent switch with vertical lines

**Label Positioning:**

- Place labels beside vertical line segments (not on them)
- Position labels above horizontal line segments
- Offset labels 5-10px from line paths to ensure readability
- For curved paths, place labels inside the curve arc

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#444"/>
    </marker>
  </defs>

  <style>
    .node-box { fill: #4051b5; stroke: #303f9f; stroke-width: 2; }
    .switch-a { fill: #2e7d32; stroke: #1b5e20; stroke-width: 2; }
    .switch-b { fill: #00838f; stroke: #006064; stroke-width: 2; }
    .switch-c { fill: #558b2f; stroke: #33691e; stroke-width: 2; }
    .cloud-shape { fill: #e65100; stroke: #bf360c; stroke-width: 2; }
    .label-primary { fill: white; font-family: system-ui, sans-serif; font-weight: bold; }
    .label-secondary { fill: #e8eaf6; font-family: system-ui, sans-serif; }
    .wire { stroke: #444; stroke-width: 2; }
    .wire-thick { stroke: #444; stroke-width: 3; }
    .wireless { stroke: #9c27b0; stroke-width: 2; stroke-dasharray: 8,4; }
    .text-dark { fill: #212121; font-family: system-ui, sans-serif; }
    .text-medium { fill: #424242; font-family: system-ui, sans-serif; }
  </style>

  <!-- Background -->
  <rect width="1200" height="1000" fill="#fafafa"/>

  <!-- Title -->
  <text x="600" y="35" text-anchor="middle" class="text-dark" font-size="22" font-weight="bold">OpenWrt Mesh Network Topology</text>
  <text x="600" y="58" text-anchor="middle" class="text-medium" font-size="13">3-Node Batman-adv Mesh with VLAN-Aware Switches</text>

  <!-- Internet Cloud -->
  <g transform="translate(490, 75)">
    <path class="cloud-shape" d="M50,55 Q5,55 5,32 Q5,10 50,10 Q62,-8 105,-8 Q148,-8 160,10 Q205,10 205,32 Q205,55 160,55 Z"/>
    <text x="105" y="32" text-anchor="middle" class="label-primary" font-size="15">Internet</text>
  </g>

  <!-- WAN Lines - curved paths avoid overlap -->
  <path class="wire" d="M500,130 Q370,150 300,175" fill="none" marker-end="url(#arrow)"/>
  <line class="wire" x1="595" y1="130" x2="595" y2="175" marker-end="url(#arrow)"/>
  <path class="wire" d="M690,130 Q820,150 890,175" fill="none" marker-end="url(#arrow)"/>
  <text x="380" y="138" class="text-medium" font-size="10" font-weight="bold">WAN</text>
  <text x="605" y="158" class="text-medium" font-size="10" font-weight="bold">WAN</text>
  <text x="810" y="138" class="text-medium" font-size="10" font-weight="bold">WAN</text>

  <!-- Nodes positioned with clear vertical paths -->
  <g transform="translate(200, 175)">
    <rect class="node-box" width="200" height="95" rx="10"/>
    <text x="100" y="25" text-anchor="middle" class="label-primary" font-size="16">Node 1</text>
    <text x="100" y="45" text-anchor="middle" class="label-secondary" font-size="12">D-Link DIR-1960 A1</text>
    <text x="100" y="63" text-anchor="middle" class="label-secondary" font-size="12">10.11.12.1 / 10.11.10.1</text>
    <text x="100" y="83" text-anchor="middle" fill="#90caf9" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">PRIMARY GATEWAY</text>
  </g>

  <g transform="translate(495, 175)">
    <rect class="node-box" width="200" height="95" rx="10"/>
    <text x="100" y="25" text-anchor="middle" class="label-primary" font-size="16">Node 2</text>
    <text x="100" y="45" text-anchor="middle" class="label-secondary" font-size="12">D-Link DIR-1960 A1</text>
    <text x="100" y="63" text-anchor="middle" class="label-secondary" font-size="12">10.11.12.2 / 10.11.10.2</text>
    <text x="100" y="83" text-anchor="middle" fill="#bdbdbd" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">RELAY NODE</text>
  </g>

  <g transform="translate(790, 175)">
    <rect class="node-box" width="200" height="95" rx="10"/>
    <text x="100" y="25" text-anchor="middle" class="label-primary" font-size="16">Node 3</text>
    <text x="100" y="45" text-anchor="middle" class="label-secondary" font-size="12">D-Link DIR-1960 A1</text>
    <text x="100" y="63" text-anchor="middle" class="label-secondary" font-size="12">10.11.12.3 / 10.11.10.3</text>
    <text x="100" y="83" text-anchor="middle" fill="#90caf9" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">SECONDARY GATEWAY</text>
  </g>

  <!-- Wireless mesh - arc above nodes -->
  <path class="wireless" d="M300,175 Q595,100 890,175" fill="none"/>
  <text x="595" y="125" text-anchor="middle" fill="#7b1fa2" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">2.4GHz HA-Mesh (SAE/WPA3 backup)</text>

  <!-- LAN3 connections - straight vertical lines -->
  <line class="wire-thick" x1="300" y1="270" x2="300" y2="340"/>
  <line class="wire-thick" x1="595" y1="270" x2="595" y2="340"/>
  <line class="wire-thick" x1="890" y1="270" x2="890" y2="340"/>
  <text x="315" y="310" class="text-dark" font-size="10" font-weight="bold">LAN3</text>
  <text x="610" y="310" class="text-dark" font-size="10" font-weight="bold">LAN3</text>
  <text x="905" y="310" class="text-dark" font-size="10" font-weight="bold">LAN3</text>

  <!-- Switch A - horizontal bar below nodes -->
  <g transform="translate(160, 340)">
    <rect class="switch-a" width="870" height="60" rx="6"/>
    <text x="435" y="22" text-anchor="middle" class="label-primary" font-size="14">Switch A - Main Distribution (TL-SG108E)</text>
    <text x="435" y="40" text-anchor="middle" fill="#c8e6c9" font-family="system-ui, sans-serif" font-size="10">10.11.10.11 | VLANs: 10, 30, 100, 200</text>
    <text x="435" y="54" text-anchor="middle" fill="#a5d6a7" font-family="system-ui, sans-serif" font-size="9">P1-3: Node trunks | P4: Switch B | P5: Mgmt | P6-8: Clients</text>
  </g>

  <!-- Switch B - LEFT side below Switch A -->
  <g transform="translate(30, 480)">
    <rect class="switch-b" width="320" height="60" rx="6"/>
    <text x="160" y="22" text-anchor="middle" class="label-primary" font-size="14">Switch B - Infrastructure (TL-SG108PE)</text>
    <text x="160" y="40" text-anchor="middle" fill="#b2ebf2" font-family="system-ui, sans-serif" font-size="10">10.11.10.12 | VLANs: 10, 30 | PoE+</text>
    <text x="160" y="54" text-anchor="middle" fill="#80deea" font-family="system-ui, sans-serif" font-size="9">P1: Uplink | P2-4: Infra | P5-8: IoT PoE</text>
  </g>

  <!-- Switch A to B - vertical path, no crossing -->
  <path class="wire-thick" d="M200,400 L200,440 L190,440 L190,480" fill="none"/>
  <text x="175" y="435" class="text-dark" font-size="9" font-weight="bold">P4</text>
  <text x="205" y="460" class="text-medium" font-size="8">VLANs 10,30</text>

  <!-- Switch C - RIGHT side -->
  <g transform="translate(600, 480)">
    <rect class="switch-c" width="420" height="60" rx="6"/>
    <text x="210" y="22" text-anchor="middle" class="label-primary" font-size="14">Switch C - Mesh Backbone (TL-SG108E)</text>
    <text x="210" y="40" text-anchor="middle" fill="#dcedc8" font-family="system-ui, sans-serif" font-size="10">10.11.10.13 | VLANs: 10, 100 (NO user VLANs)</text>
    <text x="210" y="54" text-anchor="middle" fill="#c5e1a5" font-family="system-ui, sans-serif" font-size="9">P1-3: Node LAN4 | P4-8: spare</text>
  </g>

  <!-- LAN4 connections - route RIGHT to avoid Switch B -->
  <path class="wire-thick" d="M380,270 L380,290 L550,290 L550,430 L660,430 L660,480" fill="none"/>
  <text x="395" y="285" class="text-dark" font-size="9" font-weight="bold">LAN4</text>
  <path class="wire-thick" d="M615,270 L615,290 L810,290 L810,480" fill="none"/>
  <text x="630" y="285" class="text-dark" font-size="9" font-weight="bold">LAN4</text>
  <path class="wire-thick" d="M910,270 L910,290 L960,290 L960,480" fill="none"/>
  <text x="925" y="285" class="text-dark" font-size="9" font-weight="bold">LAN4</text>

  <!-- Device groups - positioned in clear areas -->
  <g transform="translate(30, 570)">
    <rect width="140" height="50" rx="5" fill="#4dd0e1" stroke="#00acc1" stroke-width="1.5"/>
    <text x="70" y="20" text-anchor="middle" fill="#004d40" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">Infrastructure</text>
    <text x="70" y="35" text-anchor="middle" fill="#00695c" font-family="system-ui, sans-serif" font-size="9">Proxmox, VMs</text>
    <text x="70" y="47" text-anchor="middle" fill="#00695c" font-family="system-ui, sans-serif" font-size="8">VLAN 10</text>
  </g>
  <line x1="100" y1="570" x2="100" y2="540" stroke="#4dd0e1" stroke-width="1.5"/>

  <g transform="translate(200, 570)">
    <rect width="140" height="50" rx="5" fill="#ffb74d" stroke="#f57c00" stroke-width="1.5"/>
    <text x="70" y="20" text-anchor="middle" fill="#e65100" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">IoT Devices</text>
    <text x="70" y="35" text-anchor="middle" fill="#bf360c" font-family="system-ui, sans-serif" font-size="9">Cameras, Sensors</text>
    <text x="70" y="47" text-anchor="middle" fill="#bf360c" font-family="system-ui, sans-serif" font-size="8">VLAN 30 (PoE)</text>
  </g>
  <line x1="270" y1="570" x2="270" y2="540" stroke="#ffb74d" stroke-width="1.5"/>

  <g transform="translate(400, 430)">
    <rect width="140" height="50" rx="5" fill="#81c784" stroke="#43a047" stroke-width="1.5"/>
    <text x="70" y="20" text-anchor="middle" fill="#1b5e20" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">Wired Clients</text>
    <text x="70" y="35" text-anchor="middle" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="9">Switch A P6-8</text>
    <text x="70" y="47" text-anchor="middle" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="8">VLAN 200</text>
  </g>
  <line x1="470" y1="430" x2="470" y2="400" stroke="#81c784" stroke-width="1.5"/>

  <g transform="translate(400, 570)">
    <rect width="140" height="50" rx="5" fill="#64b5f6" stroke="#1976d2" stroke-width="1.5"/>
    <text x="70" y="20" text-anchor="middle" fill="#0d47a1" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">Mgmt Workstation</text>
    <text x="70" y="35" text-anchor="middle" fill="#1565c0" font-family="system-ui, sans-serif" font-size="9">Switch A P5</text>
    <text x="70" y="47" text-anchor="middle" fill="#1565c0" font-family="system-ui, sans-serif" font-size="8">All VLANs (trunk)</text>
  </g>
  <path d="M470,570 L470,420 L500,420 L500,400" stroke="#64b5f6" stroke-width="1.5" fill="none"/>

  <!-- Legend in box -->
  <g transform="translate(30, 680)">
    <rect width="500" height="70" rx="6" fill="#f5f5f5" stroke="#e0e0e0" stroke-width="1"/>
    <text x="15" y="20" class="text-dark" font-size="12" font-weight="bold">Legend</text>
    <line x1="15" y1="40" x2="55" y2="40" class="wire-thick"/>
    <text x="65" y="44" class="text-dark" font-size="10">Wired</text>
    <line x1="110" y1="40" x2="150" y2="40" class="wireless"/>
    <text x="160" y="44" class="text-dark" font-size="10">Wireless</text>
    <rect x="220" y="32" width="16" height="16" rx="3" fill="#4051b5"/>
    <text x="245" y="44" class="text-dark" font-size="10">Router</text>
    <rect x="300" y="32" width="16" height="16" rx="3" fill="#2e7d32"/>
    <text x="325" y="44" class="text-dark" font-size="10">Switch A</text>
    <rect x="385" y="32" width="16" height="16" rx="3" fill="#00838f"/>
    <text x="410" y="44" class="text-dark" font-size="10">B</text>
    <rect x="430" y="32" width="16" height="16" rx="3" fill="#558b2f"/>
    <text x="455" y="44" class="text-dark" font-size="10">C</text>
  </g>

  <!-- Footer -->
  <text x="1170" y="980" text-anchor="end" fill="#757575" font-family="system-ui, sans-serif" font-size="10">Batman-adv BLA enabled | Static IPs required</text>
</svg>
```

### VLAN Architecture

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000">
  <style>
    .vlan-box { stroke-width: 2; rx: 8; }
    .vlan-10 { fill: #1976d2; stroke: #0d47a1; }
    .vlan-20 { fill: #7b1fa2; stroke: #4a148c; }
    .vlan-30 { fill: #f57c00; stroke: #e65100; }
    .vlan-100 { fill: #616161; stroke: #424242; }
    .vlan-200 { fill: #2e7d32; stroke: #1b5e20; }
    .label { fill: white; font-family: system-ui, sans-serif; text-anchor: middle; }
    .sublabel { fill: rgba(255,255,255,0.85); font-family: system-ui, sans-serif; text-anchor: middle; }
    .text-dark { fill: #212121; font-family: system-ui, sans-serif; }
    .text-medium { fill: #424242; font-family: system-ui, sans-serif; }
  </style>

  <!-- Background for contrast -->
  <rect width="1200" height="1000" fill="#fafafa"/>

  <!-- Title -->
  <text x="600" y="40" text-anchor="middle" class="text-dark" font-size="24" font-weight="bold">VLAN Architecture</text>
  <text x="600" y="65" text-anchor="middle" class="text-medium" font-size="14">Network Segmentation with Batman-adv Mesh</text>

  <!-- VLAN 200 - Client -->
  <g transform="translate(60, 100)">
    <rect class="vlan-box vlan-200" width="200" height="180"/>
    <text x="100" y="35" class="label" font-size="18" font-weight="bold">VLAN 200</text>
    <text x="100" y="60" class="label" font-size="14">Client Network</text>
    <line x1="30" y1="75" x2="170" y2="75" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
    <text x="100" y="100" class="sublabel" font-size="12">10.11.12.0/24</text>
    <text x="100" y="125" class="sublabel" font-size="11">HA-Client (5GHz)</text>
    <text x="100" y="145" class="sublabel" font-size="11">802.11r Fast Roaming</text>
    <text x="100" y="170" class="sublabel" font-size="10">Interfaces: LAN1, lan3.200, bat0</text>
  </g>

  <!-- VLAN 10 - Management -->
  <g transform="translate(300, 100)">
    <rect class="vlan-box vlan-10" width="200" height="180"/>
    <text x="100" y="35" class="label" font-size="18" font-weight="bold">VLAN 10</text>
    <text x="100" y="60" class="label" font-size="14">Management</text>
    <line x1="30" y1="75" x2="170" y2="75" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
    <text x="100" y="100" class="sublabel" font-size="12">10.11.10.0/24</text>
    <text x="100" y="125" class="sublabel" font-size="11">HA-Management (2.4GHz)</text>
    <text x="100" y="145" class="sublabel" font-size="11">Admin Access Only</text>
    <text x="100" y="170" class="sublabel" font-size="10">Interfaces: lan3.10, bat0.10</text>
  </g>

  <!-- VLAN 20 - Guest -->
  <g transform="translate(540, 100)">
    <rect class="vlan-box vlan-20" width="200" height="180"/>
    <text x="100" y="35" class="label" font-size="18" font-weight="bold">VLAN 20</text>
    <text x="100" y="60" class="label" font-size="14">Guest Network</text>
    <line x1="30" y1="75" x2="170" y2="75" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
    <text x="100" y="100" class="sublabel" font-size="12">10.11.20.0/24</text>
    <text x="100" y="125" class="sublabel" font-size="11">HA-Guest (5GHz)</text>
    <text x="100" y="145" class="sublabel" font-size="11">Isolated from LAN</text>
    <text x="100" y="170" class="sublabel" font-size="10">Interfaces: bat0.20 only</text>
  </g>

  <!-- VLAN 30 - IoT -->
  <g transform="translate(780, 100)">
    <rect class="vlan-box vlan-30" width="200" height="180"/>
    <text x="100" y="35" class="label" font-size="18" font-weight="bold">VLAN 30</text>
    <text x="100" y="60" class="label" font-size="14">IoT Network</text>
    <line x1="30" y1="75" x2="170" y2="75" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
    <text x="100" y="100" class="sublabel" font-size="12">10.11.30.0/24</text>
    <text x="100" y="125" class="sublabel" font-size="11">HA-IoT (2.4GHz)</text>
    <text x="100" y="145" class="sublabel" font-size="11">MQTT + Home Assistant</text>
    <text x="100" y="170" class="sublabel" font-size="10">Interfaces: LAN2, lan3.30, bat0.30</text>
  </g>

  <!-- VLAN 100 - Mesh Backbone -->
  <g transform="translate(1020, 100)">
    <rect class="vlan-box vlan-100" width="140" height="180"/>
    <text x="70" y="35" class="label" font-size="16" font-weight="bold">VLAN 100</text>
    <text x="70" y="60" class="label" font-size="12">Mesh Backbone</text>
    <line x1="20" y1="75" x2="120" y2="75" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
    <text x="70" y="100" class="sublabel" font-size="11">Layer 2 Only</text>
    <text x="70" y="125" class="sublabel" font-size="10">Batman-adv</text>
    <text x="70" y="145" class="sublabel" font-size="10">BLA Enabled</text>
    <text x="70" y="170" class="sublabel" font-size="9">lan3.100, lan4.100</text>
  </g>

  <!-- Traffic Flow Section -->
  <g transform="translate(60, 320)">
    <text x="0" y="0" class="text-dark" font-size="18" font-weight="bold">Traffic Flow &amp; Isolation</text>

    <!-- Flow diagram -->
    <g transform="translate(0, 30)">
      <!-- Internet -->
      <rect x="450" y="0" width="100" height="40" rx="4" fill="#f57c00" stroke="#e65100" stroke-width="2"/>
      <text x="500" y="25" text-anchor="middle" fill="white" font-family="system-ui, sans-serif" font-size="12" font-weight="bold">Internet</text>

      <!-- Arrows from Internet -->
      <line x1="450" y1="20" x2="350" y2="80" stroke="#444" stroke-width="2" marker-end="url(#arrow-down)"/>
      <line x1="550" y1="20" x2="650" y2="80" stroke="#444" stroke-width="2" marker-end="url(#arrow-down)"/>

      <!-- Gateway nodes -->
      <rect x="280" y="80" width="140" height="50" rx="6" fill="#4051b5" stroke="#303f9f" stroke-width="2"/>
      <text x="350" y="110" text-anchor="middle" fill="white" font-family="system-ui, sans-serif" font-size="11">Node 1 (Primary GW)</text>

      <rect x="580" y="80" width="140" height="50" rx="6" fill="#4051b5" stroke="#303f9f" stroke-width="2"/>
      <text x="650" y="110" text-anchor="middle" fill="white" font-family="system-ui, sans-serif" font-size="11">Node 3 (Secondary GW)</text>

      <!-- Mesh backbone -->
      <rect x="380" y="160" width="240" height="40" rx="4" fill="#616161" stroke="#424242" stroke-width="2"/>
      <text x="500" y="185" text-anchor="middle" fill="white" font-family="system-ui, sans-serif" font-size="11">Batman-adv Mesh (VLAN 100)</text>

      <!-- Arrows to mesh -->
      <line x1="350" y1="130" x2="420" y2="160" stroke="#616161" stroke-width="2"/>
      <line x1="650" y1="130" x2="580" y2="160" stroke="#616161" stroke-width="2"/>
    </g>
  </g>

  <!-- Access Matrix -->
  <g transform="translate(60, 520)">
    <text x="0" y="0" class="text-dark" font-size="18" font-weight="bold">Access Matrix</text>

    <!-- Table headers -->
    <text x="180" y="50" class="text-medium" font-size="12" font-weight="bold">→ WAN</text>
    <text x="280" y="50" class="text-medium" font-size="12" font-weight="bold">→ LAN</text>
    <text x="380" y="50" class="text-medium" font-size="12" font-weight="bold">→ Mgmt</text>
    <text x="480" y="50" class="text-medium" font-size="12" font-weight="bold">→ IoT</text>

    <!-- Client row -->
    <rect x="0" y="65" width="140" height="35" fill="#2e7d32" rx="4"/>
    <text x="70" y="88" class="label" font-size="12">Client (200)</text>
    <text x="195" y="88" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="16">✓</text>
    <text x="295" y="88" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="16">✓</text>
    <text x="395" y="88" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="16">✓</text>
    <text x="495" y="88" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="16">✓</text>

    <!-- Management row -->
    <rect x="0" y="110" width="140" height="35" fill="#1976d2" rx="4"/>
    <text x="70" y="133" class="label" font-size="12">Management (10)</text>
    <text x="195" y="133" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="16">✓</text>
    <text x="295" y="133" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="16">✓</text>
    <text x="395" y="133" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="16">✓</text>
    <text x="495" y="133" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="16">✓</text>

    <!-- Guest row -->
    <rect x="0" y="155" width="140" height="35" fill="#7b1fa2" rx="4"/>
    <text x="70" y="178" class="label" font-size="12">Guest (20)</text>
    <text x="195" y="178" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="16">✓</text>
    <text x="295" y="178" fill="#c62828" font-family="system-ui, sans-serif" font-size="16">✗</text>
    <text x="395" y="178" fill="#c62828" font-family="system-ui, sans-serif" font-size="16">✗</text>
    <text x="495" y="178" fill="#c62828" font-family="system-ui, sans-serif" font-size="16">✗</text>

    <!-- IoT row -->
    <rect x="0" y="200" width="140" height="35" fill="#f57c00" rx="4"/>
    <text x="70" y="223" class="label" font-size="12">IoT (30)</text>
    <text x="195" y="223" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="16">✓</text>
    <text x="295" y="223" fill="#c62828" font-family="system-ui, sans-serif" font-size="16">✗</text>
    <text x="395" y="223" fill="#f57c00" font-family="system-ui, sans-serif" font-size="14">△</text>
    <text x="495" y="223" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="16">✓</text>
  </g>

  <!-- Legend -->
  <g transform="translate(700, 520)">
    <text x="0" y="0" class="text-dark" font-size="16" font-weight="bold">Legend</text>

    <text x="0" y="40" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="14">✓ Full access</text>
    <text x="0" y="70" fill="#c62828" font-family="system-ui, sans-serif" font-size="14">✗ Blocked</text>
    <text x="0" y="100" fill="#f57c00" font-family="system-ui, sans-serif" font-size="14">△ Limited (MQTT 1883/8883, HA 8123)</text>

    <!-- Port legend -->
    <text x="0" y="150" class="text-dark" font-size="14" font-weight="bold">Port Assignments:</text>
    <text x="0" y="175" class="text-medium" font-size="12">WAN = Internet uplink</text>
    <text x="0" y="195" class="text-medium" font-size="12">LAN1 = Client devices</text>
    <text x="0" y="215" class="text-medium" font-size="12">LAN2 = IoT direct connect</text>
    <text x="200" y="175" class="text-medium" font-size="12">LAN3 = Switch A (all VLANs)</text>
    <text x="200" y="195" class="text-medium" font-size="12">LAN4 = Switch C (mesh only)</text>
  </g>

  <!-- Footer note -->
  <text x="600" y="980" text-anchor="middle" fill="#757575" font-family="system-ui, sans-serif" font-size="11">Bridge Loop Avoidance (BLA) enabled on bat0 • Static IPs required on all nodes</text>
</svg>
```

### WiFi Radio Layout

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000">
  <style>
    .radio-box { fill: #37474f; stroke: #263238; stroke-width: 2; }
    .interface-box { stroke-width: 2; rx: 6; }
    .mesh { fill: #616161; stroke: #424242; }
    .mgmt { fill: #1976d2; stroke: #0d47a1; }
    .iot { fill: #f57c00; stroke: #e65100; }
    .client { fill: #2e7d32; stroke: #1b5e20; }
    .guest { fill: #7b1fa2; stroke: #4a148c; }
    .label { fill: white; font-family: system-ui, sans-serif; }
    .text-dark { fill: #212121; font-family: system-ui, sans-serif; }
    .text-medium { fill: #424242; font-family: system-ui, sans-serif; }
  </style>

  <!-- Background for contrast -->
  <rect width="1200" height="1000" fill="#fafafa"/>

  <!-- Title -->
  <text x="600" y="40" text-anchor="middle" class="text-dark" font-size="24" font-weight="bold">WiFi Radio Configuration</text>
  <text x="600" y="70" text-anchor="middle" class="text-medium" font-size="14">D-Link DIR-1960 A1 - Dual Band Configuration</text>

  <!-- 2.4GHz Radio -->
  <g transform="translate(60, 100)">
    <rect class="radio-box" width="500" height="380" rx="12"/>
    <text x="250" y="40" text-anchor="middle" class="label" font-size="20" font-weight="bold">2.4GHz Radio (radio0)</text>
    <text x="250" y="65" text-anchor="middle" fill="#90a4ae" font-family="system-ui, sans-serif" font-size="12">Channel 6 • HT40 • 20dBm</text>

    <!-- Mesh interface -->
    <g transform="translate(30, 90)">
      <rect class="interface-box mesh" width="440" height="80"/>
      <text x="220" y="25" text-anchor="middle" class="label" font-size="16" font-weight="bold">phy0-mesh0</text>
      <text x="220" y="48" text-anchor="middle" class="label" font-size="13">HA-Mesh (hidden SSID)</text>
      <text x="220" y="70" text-anchor="middle" fill="#bdbdbd" font-family="system-ui, sans-serif" font-size="11">Batman-adv hardif • SAE (WPA3) • mcast_rate=24000</text>
    </g>

    <!-- Management interface -->
    <g transform="translate(30, 185)">
      <rect class="interface-box mgmt" width="440" height="80"/>
      <text x="220" y="25" text-anchor="middle" class="label" font-size="16" font-weight="bold">phy0-ap0</text>
      <text x="220" y="48" text-anchor="middle" class="label" font-size="13">HA-Management</text>
      <text x="220" y="70" text-anchor="middle" fill="#bbdefb" font-family="system-ui, sans-serif" font-size="11">VLAN 10 • br-mgmt • psk2+ccmp</text>
    </g>

    <!-- IoT interface -->
    <g transform="translate(30, 280)">
      <rect class="interface-box iot" width="440" height="80"/>
      <text x="220" y="25" text-anchor="middle" class="label" font-size="16" font-weight="bold">phy0-ap1</text>
      <text x="220" y="48" text-anchor="middle" class="label" font-size="13">HA-IoT</text>
      <text x="220" y="70" text-anchor="middle" fill="#ffe0b2" font-family="system-ui, sans-serif" font-size="11">VLAN 30 • br-iot • psk2+ccmp • isolate=1</text>
    </g>
  </g>

  <!-- 5GHz Radio -->
  <g transform="translate(640, 100)">
    <rect class="radio-box" width="500" height="380" rx="12"/>
    <text x="250" y="40" text-anchor="middle" class="label" font-size="20" font-weight="bold">5GHz Radio (radio1)</text>
    <text x="250" y="65" text-anchor="middle" fill="#90a4ae" font-family="system-ui, sans-serif" font-size="12">Channel 36 • VHT80 • 23dBm</text>

    <!-- Client interface -->
    <g transform="translate(30, 90)">
      <rect class="interface-box client" width="440" height="80"/>
      <text x="220" y="25" text-anchor="middle" class="label" font-size="16" font-weight="bold">phy1-ap0</text>
      <text x="220" y="48" text-anchor="middle" class="label" font-size="13">HA-Client (Primary)</text>
      <text x="220" y="70" text-anchor="middle" fill="#c8e6c9" font-family="system-ui, sans-serif" font-size="11">802.11r • ft_over_ds=1 • rsn_preauth=1 • br-lan</text>
    </g>

    <!-- Guest interface -->
    <g transform="translate(30, 185)">
      <rect class="interface-box guest" width="440" height="80"/>
      <text x="220" y="25" text-anchor="middle" class="label" font-size="16" font-weight="bold">phy1-ap1</text>
      <text x="220" y="48" text-anchor="middle" class="label" font-size="13">HA-Guest</text>
      <text x="220" y="70" text-anchor="middle" fill="#e1bee7" font-family="system-ui, sans-serif" font-size="11">VLAN 20 • br-guest • isolate=1 • LAN blocked</text>
    </g>

    <!-- Empty slot indicator -->
    <g transform="translate(30, 280)">
      <rect width="440" height="80" rx="6" fill="none" stroke="#546e7a" stroke-width="2" stroke-dasharray="6,4"/>
      <text x="220" y="45" text-anchor="middle" fill="#78909c" font-family="system-ui, sans-serif" font-size="12">(available for expansion)</text>
    </g>
  </g>

  <!-- 802.11r Configuration Section -->
  <g transform="translate(60, 520)">
    <text x="0" y="0" class="text-dark" font-size="18" font-weight="bold">802.11r Fast Roaming Configuration</text>

    <g transform="translate(0, 30)">
      <!-- Mobility Domain -->
      <rect x="0" y="0" width="250" height="100" rx="8" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
      <text x="125" y="25" text-anchor="middle" fill="#1976d2" font-family="system-ui, sans-serif" font-size="14" font-weight="bold">Mobility Domain</text>
      <text x="125" y="50" text-anchor="middle" class="text-dark" font-size="12">mobility_domain: {{ ft_mobility_domain }}</text>
      <text x="125" y="70" text-anchor="middle" class="text-medium" font-size="11">Shared across all 3 nodes</text>
      <text x="125" y="88" text-anchor="middle" class="text-medium" font-size="11">Enables seamless handoff</text>

      <!-- FT Over DS -->
      <rect x="280" y="0" width="250" height="100" rx="8" fill="#e8f5e9" stroke="#2e7d32" stroke-width="2"/>
      <text x="405" y="25" text-anchor="middle" fill="#2e7d32" font-family="system-ui, sans-serif" font-size="14" font-weight="bold">FT Over DS</text>
      <text x="405" y="50" text-anchor="middle" class="text-dark" font-size="12">ft_over_ds: 1</text>
      <text x="405" y="70" text-anchor="middle" class="text-medium" font-size="11">Fast transition via mesh</text>
      <text x="405" y="88" text-anchor="middle" class="text-medium" font-size="11">(faster than over-air)</text>

      <!-- RSN Preauth -->
      <rect x="560" y="0" width="250" height="100" rx="8" fill="#fff3e0" stroke="#f57c00" stroke-width="2"/>
      <text x="685" y="25" text-anchor="middle" fill="#f57c00" font-family="system-ui, sans-serif" font-size="14" font-weight="bold">RSN Preauthentication</text>
      <text x="685" y="50" text-anchor="middle" class="text-dark" font-size="12">rsn_preauth: 1</text>
      <text x="685" y="70" text-anchor="middle" class="text-medium" font-size="11">Pre-authenticate before roam</text>
      <text x="685" y="88" text-anchor="middle" class="text-medium" font-size="11">Reduces handoff delay</text>
    </g>
  </g>

  <!-- Legend Section -->
  <g transform="translate(60, 680)">
    <text x="0" y="0" class="text-dark" font-size="16" font-weight="bold">Interface Legend</text>

    <g transform="translate(0, 25)">
      <rect x="0" y="0" width="20" height="20" rx="3" fill="#616161"/>
      <text x="30" y="15" class="text-dark" font-size="12">Mesh Backbone</text>

      <rect x="150" y="0" width="20" height="20" rx="3" fill="#1976d2"/>
      <text x="180" y="15" class="text-dark" font-size="12">Management VLAN 10</text>

      <rect x="340" y="0" width="20" height="20" rx="3" fill="#f57c00"/>
      <text x="370" y="15" class="text-dark" font-size="12">IoT VLAN 30</text>

      <rect x="500" y="0" width="20" height="20" rx="3" fill="#2e7d32"/>
      <text x="530" y="15" class="text-dark" font-size="12">Client Network</text>

      <rect x="660" y="0" width="20" height="20" rx="3" fill="#7b1fa2"/>
      <text x="690" y="15" class="text-dark" font-size="12">Guest VLAN 20</text>
    </g>
  </g>

  <!-- Footer -->
  <text x="600" y="980" text-anchor="middle" fill="#757575" font-family="system-ui, sans-serif" font-size="11">mesh_fwding=0 and mesh_ttl=1 set on mesh interface for batman-adv control</text>
</svg>
```

## Usage Instructions

### To Generate a Diagram

1. **Analyze the relevant code/config files**
   - Network: `roles/network_config/templates/network.j2`
   - Wireless: `roles/wireless_config/templates/wireless.j2`
   - Firewall: `roles/firewall_config/templates/firewall.j2`
   - Inventory: `inventory/hosts.yml`
   - Variables: `group_vars/all.yml`

2. **Choose appropriate diagram template**
   - Physical layout → Network Topology
   - VLAN segmentation → VLAN Architecture
   - Radio config → WiFi Radio Layout
   - Custom → Build from components

3. **Generate SVG**
   - Use the component library above
   - Maintain consistent styling
   - Include proper viewBox for scaling

4. **Save file**
   - Location: `docs/assets/diagrams/`
   - Naming: `{topic}-{type}.svg` (e.g., `network-topology.svg`)

### To Include in Documentation

Reference SVG files in markdown:

```markdown
![Network Topology](../assets/diagrams/network-topology.svg)
```

Or embed inline for small diagrams:

```html
<figure>
  <img src="../assets/diagrams/vlan-architecture.svg" alt="VLAN Architecture">
  <figcaption>VLAN network segmentation</figcaption>
</figure>
```

## Color Palette

| Element | Color | Hex |
|---------|-------|-----|
| Node (router) | Blue | #4051b5 |
| Switch | Green | #2e7d32 |
| Internet/WAN | Orange | #f57c00 |
| Wireless | Purple | #7b1fa2 |
| VLAN 10 (Mgmt) | Blue | #1976d2 |
| VLAN 20 (Guest) | Purple | #7b1fa2 |
| VLAN 30 (IoT) | Orange | #f57c00 |
| VLAN 100 (Mesh) | Gray | #616161 |
| VLAN 200 (Client) | Green | #2e7d32 |

## Line Routing Best Practices

### Consistent Spacing

When multiple lines connect to the same component (e.g., switch), use consistent spacing:

```xml
<!-- 40px spacing for entry points on Switch A (centered at x=220 on 360px wide switch) -->
<path d="M280,340 L280,360 L180,360 L180,460" fill="none"/>  <!-- Node 1 → x=180 -->
<path d="M560,340 L560,390 L220,390 L220,460" fill="none"/>  <!-- Node 2 → x=220 -->
<path d="M840,340 L840,435 L260,435 L260,460" fill="none"/>  <!-- Node 3 → x=260 -->
```

**Guidelines:**

- Calculate center of target component, distribute entry points evenly around it
- Use consistent pixel spacing (e.g., 40px between entry points)
- For 3 lines with 40px spacing centered at x=220: use x=180, 220, 260

### Non-Intersecting Line Routing

When routing multiple lines in the same direction, use staggered y-levels:

```xml
<!-- Horizontal segments at consistent 15px vertical intervals -->
<!-- Order from top to bottom based on distance from destination -->
y=360: LAN3 Node 1 (closest to Switch A)
y=375: LAN4 Node 3 (closest to Switch C)
y=390: LAN3 Node 2
y=405: LAN4 Node 2
y=420: LAN4 Node 1 (furthest from Switch C)
y=435: LAN3 Node 3 (furthest from Switch A, must pass under LAN4)
```

**Guidelines:**

- Lines going opposite directions (left vs right) can share y-levels if they don't overlap
- Lines going the same direction must use different y-levels
- Plan y-levels before drawing - list all horizontal segments and assign levels
- Use consistent spacing between levels (e.g., 15px)

### Path Routing Strategies

**Simple paths** (straight down with one turn):

```xml
<!-- Closest node to switch - minimal routing -->
<path d="M280,340 L280,360 L180,360 L180,460" fill="none"/>
```

**Passing under other lines:**

```xml
<!-- Must drop below y=420 (LAN4 Node 1) before going horizontal -->
<path d="M840,340 L840,435 L260,435 L260,460" fill="none"/>
```

**Key principle:** A vertical segment will cross any horizontal segment at the same y-level. To avoid:

- Route the vertical to a y-level below all horizontals it needs to pass
- Or route horizontally first before dropping down

### Avoiding Common Intersection Problems

1. **Vertical crosses horizontal:** If line A drops from y=340 to y=460 at x=840, and line B has a horizontal at y=410 from x=400 to x=940, they intersect at (840, 410). Solution: Line A must drop to below y=410 before x reaches the horizontal.

2. **Two horizontals at same y:** If both are at y=400 and overlap in x-range, they'll collide. Solution: Use different y-levels.

3. **Planning approach:**
   - List all connection pairs (source → destination)
   - Group by direction (going left vs going right)
   - Assign y-levels: closest connections get highest (smallest y), furthest get lowest
   - Verify no crossings by checking if any vertical passes through another line's horizontal

## Preventing Element Overlap

### CRITICAL: Calculate Positions Before Placing Elements

**Always verify that elements don't overlap by checking their bounding boxes:**

```
Element bounding box = (x, y, x + width, y + height)
Two elements overlap if their bounding boxes intersect
```

### Box Placement Rules

**Horizontal row of boxes:**

```xml
<!-- WRONG: 160px wide boxes at 100px intervals = 60px overlap! -->
<g transform="translate(220, 120)"><rect width="160" height="45"/></g>  <!-- 220-380 -->
<g transform="translate(320, 120)"><rect width="160" height="45"/></g>  <!-- 320-480 OVERLAPS! -->
<g transform="translate(420, 120)"><rect width="160" height="45"/></g>  <!-- 420-580 OVERLAPS! -->

<!-- CORRECT: 140px wide boxes at 160px intervals = 20px gap -->
<g transform="translate(130, 120)"><rect width="140" height="45"/></g>  <!-- 130-270 -->
<g transform="translate(290, 120)"><rect width="140" height="45"/></g>  <!-- 290-430 -->
<g transform="translate(450, 120)"><rect width="140" height="45"/></g>  <!-- 450-590 -->
```

**Formula for non-overlapping horizontal placement:**

```
spacing = width + gap
position[n] = start_x + (n * spacing)

Example: 3 boxes, each 140px wide, 20px gap, starting at x=130
- Box 1: x=130, ends at 270
- Box 2: x=130 + 160 = 290, ends at 430
- Box 3: x=130 + 320 = 450, ends at 590
```

### Connecting Lines to Box Centers

When drawing lines to boxes, calculate the center position:

```xml
<!-- Box at translate(130, 120) with width=140 -->
<!-- Center x = 130 + (140/2) = 200 -->
<line x1="200" y1="80" x2="200" y2="120"/>
```

### Pre-Placement Checklist

Before creating any group of elements:

1. **List all elements** with their widths/heights
2. **Calculate required spacing**: `spacing = max_width + desired_gap`
3. **Determine start position**: Consider centering the group
4. **Calculate each position**: `x[n] = start + (n * spacing)`
5. **Verify no overlaps**: Check that `x[n] + width < x[n+1]`
6. **Calculate center points**: For connecting lines

### Bidirectional Arrow Spacing

When showing two-way connections between elements, arrows must be clearly separated:

```xml
<!-- WRONG: Only 5px apart - arrows appear merged -->
<path d="M240,80 L320,80" marker-end="url(#arrow)"/>  <!-- right arrow -->
<path d="M320,75 L240,75" marker-end="url(#arrow)"/>  <!-- left arrow - TOO CLOSE! -->

<!-- CORRECT: 20px apart - arrows clearly distinguishable -->
<path d="M240,70 L320,70" marker-end="url(#arrow)"/>  <!-- right arrow at y=70 -->
<path d="M320,90 L240,90" marker-end="url(#arrow)"/>  <!-- left arrow at y=90 -->
```

**Guidelines for bidirectional arrows:**

- Minimum spacing: **15-20px** between parallel arrows
- Position arrows symmetrically around the center line
- For horizontal arrows: one above center (y - 10), one below (y + 10)
- For vertical arrows: one left of center (x - 10), one right (x + 10)
- Add comments indicating direction and position

**Calculation example:**

```
Box height = 80px, box starts at y=40
Box vertical center = 40 + (80/2) = 80
Arrow 1 (right): y = 80 - 10 = 70
Arrow 2 (left):  y = 80 + 10 = 90
Spacing = 90 - 70 = 20px ✓
```

### Common Overlap Mistakes

| Mistake | Why It Fails | Fix |
|---------|--------------|-----|
| Fixed spacing regardless of width | Box wider than spacing | spacing = width + gap |
| Copy-paste without adjusting position | Elements stack on each other | Calculate each position |
| Connecting lines to wrong points | Lines miss box centers | center = translate_x + width/2 |
| Not accounting for stroke width | Boxes touch at edges | Add stroke-width to gap |
| Bidirectional arrows too close | Arrows appear merged/overlapping | Minimum 15-20px spacing |

## Best Practices

1. **Use standard size** - All diagrams: `viewBox="0 0 1200 1000"` for consistency
2. **Use viewBox** - Enables proper scaling across all display sizes
3. **Group elements** - Use `<g>` with transforms for positioning
4. **Define styles** - Use `<style>` block for consistency
5. **Include labels** - All important elements should have text labels
6. **Add legends** - Explain colors and line styles
7. **Add titles** - Include diagram title at top (font-size="24") with optional subtitle
8. **Add footers** - Include relevant notes at bottom (y="980")
9. **Test rendering** - Verify in browser before committing
10. **Optimize** - Remove unnecessary whitespace for production
11. **VERIFY NO OVERLAPS** - Calculate bounding boxes before placing elements
