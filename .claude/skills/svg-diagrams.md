# SVG Diagram Generator Skill

Expert guidance for creating accessible, responsive SVG diagrams following web standards and best practices.

## When to Use This Skill

- Converting ASCII art diagrams to SVG
- Creating architecture diagrams (infrastructure, system components)
- Network topology diagrams
- Data flow diagrams
- Any technical diagram requiring scalability and accessibility

## Core Principles

### 1. Accessibility (WCAG 2.1 AA+)

**Always include:**

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     role="img"
     aria-labelledby="title desc"
     viewBox="0 0 800 600">
  <title id="title">Brief diagram title</title>
  <desc id="desc">Detailed description of diagram content and relationships</desc>
  <!-- diagram content -->
</svg>
```

**Key requirements:**

- Use `role="img"` for meaningful diagrams
- Use `role="graphics-document"` for complex diagrams
- Include both `<title>` and `<desc>` with unique IDs
- Reference IDs via `aria-labelledby="title desc"`
- For decorative diagrams: use `aria-hidden="true"` and `focusable="false"`

### 2. Responsive Design

**viewBox is mandatory:**

```xml
<!-- DO THIS: Scalable and responsive -->
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <!-- content scales automatically -->
</svg>

<!-- NOT THIS: Fixed dimensions -->
<svg width="800" height="600">
  <!-- won't scale properly -->
</svg>
```

**viewBox format:**

- `viewBox="min-x min-y width height"`
- Example: `viewBox="0 0 800 600"` creates 800×600 coordinate system
- Diagram scales proportionally to container
- Maintains aspect ratio automatically

### 3. Coordinate System

**Use consistent units:**

- **Recommended**: User units (no suffix) - `x="100"` not `x="100px"`
- **Avoid**: Print units (inches, cm, pt)
- **Standard**: 1 user unit = 1 pixel at default scale
- **Typical canvas**: 800×600, 1000×800, 1200×900 for diagrams

## Design System & Branding

**Consistency is critical for professional diagrams.** All diagrams should follow a unified design system with consistent colors, typography, spacing, and visual elements.

### Color Palette

**Primary Palette** (Infrastructure & Networking):

```css
/* Primary - Network/Technology */
--primary-blue: #0d6efd;        /* Core network components */
--primary-blue-light: #6ea8fe;  /* Highlights, hover states */
--primary-blue-dark: #0a58ca;   /* Pressed states, emphasis */

/* Neutral Grays - Containers & Backgrounds */
--gray-100: #f8f9fa;   /* Light backgrounds, outer containers */
--gray-200: #e9ecef;   /* Component backgrounds */
--gray-300: #dee2e6;   /* Borders, dividers */
--gray-600: #6c757d;   /* Secondary text, labels */
--gray-800: #343a40;   /* Primary text, strong borders */
--gray-900: #212529;   /* Headings, emphasis text */

/* Semantic Colors - Component Types */
--service-green: #198754;    /* Services, applications */
--service-green-light: #d1e7dd; /* Service backgrounds */

--database-cyan: #0dcaf0;    /* Databases, storage */
--database-cyan-light: #cff4fc; /* Database backgrounds */

--infrastructure-indigo: #6610f2; /* Infrastructure, hosts */
--infrastructure-indigo-light: #e0cffc; /* Infrastructure backgrounds */

--network-yellow: #ffc107;   /* Network connections, mesh */
--network-yellow-light: #fff3cd; /* Network highlights */

/* Status Colors - States & Alerts */
--success-green: #198754;    /* Success, active, healthy */
--warning-yellow: #ffc107;   /* Warning, attention needed */
--danger-red: #dc3545;       /* Error, critical, failed */
--info-blue: #0dcaf0;        /* Information, note */
```

**Color Usage Guidelines:**

- **Primary Blue**: Main actions, primary nodes, core network components
- **Neutral Grays**: Containers, backgrounds, text (ensure 4.5:1 contrast minimum)
- **Semantic Colors**:
  - Green: Services, applications, success states
  - Cyan: Databases, data storage
  - Indigo: Infrastructure, host machines
  - Yellow: Network connections, mesh links
- **Status Colors**: Only for indicating state (success, warning, error)

**Contrast Requirements:**

- Text on background: Minimum 4.5:1 ratio (WCAG AA)
- Large text (18pt+): Minimum 3:1 ratio
- Interactive elements: Minimum 3:1 ratio

### Typography

**Font Stack:**

```css
font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

**Type Scale:**

```css
/* Titles & Headings */
--text-title: 20px;      /* Diagram titles */
--text-subtitle: 16px;   /* Section headers, container labels */

/* Body & Components */
--text-component: 14px;  /* Component names, primary labels */
--text-body: 13px;       /* Descriptive text, notes */
--text-label: 12px;      /* Port labels, annotations */
--text-caption: 11px;    /* Fine print, metadata */

/* Font Weights */
--weight-bold: 600;      /* Titles, headings, emphasis */
--weight-medium: 500;    /* Component names, important labels */
--weight-normal: 400;    /* Body text, descriptions */
```

**Typography Rules:**

- Use `text-anchor="middle"` for centered text in components
- Use `text-anchor="start"` for left-aligned labels
- Keep line length under 50 characters for readability
- Use consistent font weights across diagram types

### Spacing & Sizing

**Grid System:**

```css
/* Base spacing unit: 8px */
--space-xs: 4px;    /* Tight spacing, inline elements */
--space-sm: 8px;    /* Standard padding within components */
--space-md: 16px;   /* Component margins, section spacing */
--space-lg: 24px;   /* Large gaps, major sections */
--space-xl: 32px;   /* Container padding, diagram margins */
--space-xxl: 48px;  /* Major layout separations */
```

**Component Sizing:**

```css
/* Standard component dimensions */
--component-width-sm: 100px;   /* Small components (icons, badges) */
--component-width-md: 140px;   /* Standard components */
--component-width-lg: 200px;   /* Large components, containers */
--component-width-xl: 280px;   /* Major containers, detailed nodes */

--component-height-sm: 60px;   /* Compact components */
--component-height-md: 80px;   /* Standard components */
--component-height-lg: 100px;  /* Tall components */
--component-height-xl: 140px;  /* Major nodes */

/* Minimum spacing between components */
--component-gap: 40px;  /* Minimum distance between sibling components */
--layer-gap: 60px;      /* Distance between hierarchy layers */
```

**Sizing Rules:**

- All spacing should be multiples of 8px (grid system)
- Maintain consistent padding within component types
- Leave minimum 40px between adjacent components
- Use 60px+ for hierarchical separation (parent/child)

### Visual Elements

**Borders & Strokes:**

```css
/* Stroke widths */
--stroke-thin: 1px;      /* Subtle dividers */
--stroke-normal: 2px;    /* Standard component borders */
--stroke-thick: 3px;     /* Container borders, emphasis */
--stroke-connection: 2.5px; /* Connection lines, arrows */

/* Border radius */
--radius-sm: 3px;   /* Small elements, tight curves */
--radius-md: 5px;   /* Standard components */
--radius-lg: 8px;   /* Large containers */

/* Dash patterns */
--dash-standard: "5,5";  /* Standard dashed line */
--dash-sparse: "8,4";    /* Sparse dashed line */
--dash-dense: "3,3";     /* Dense dashed line */
```

**Shadows (Optional):**

Use shadows sparingly for elevated elements:

```xml
<filter id="shadow">
  <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.15"/>
</filter>
```

**Visual Element Rules:**

- Standard components: 2px solid border, 5px radius
- Containers: 3px solid border, 8px radius
- Connection lines: 2.5px solid, arrow markers
- Dashed lines for: wireless, optional, or secondary connections
- No shadows unless element needs visual elevation

### Component Style Definitions

**Standard Component Box:**

```xml
<style>
  .component-standard {
    fill: var(--gray-200);
    stroke: var(--gray-800);
    stroke-width: 2;
    rx: 5;
  }
  .component-text {
    font-family: system-ui, sans-serif;
    font-size: 14px;
    font-weight: 500;
    fill: var(--gray-900);
    text-anchor: middle;
  }
</style>

<rect class="component-standard" x="100" y="100" width="140" height="80"/>
<text class="component-text" x="170" y="145">Component</text>
```

**Container Box:**

```xml
<style>
  .container-box {
    fill: var(--gray-100);
    stroke: var(--gray-800);
    stroke-width: 3;
    rx: 8;
  }
  .container-title {
    font-family: system-ui, sans-serif;
    font-size: 16px;
    font-weight: 600;
    fill: var(--gray-900);
    text-anchor: middle;
  }
</style>
```

**Semantic Component Types:**

```xml
<style>
  /* Service/Application */
  .service {
    fill: var(--service-green-light);
    stroke: var(--service-green);
    stroke-width: 2;
    rx: 5;
  }

  /* Database/Storage */
  .database {
    fill: var(--database-cyan-light);
    stroke: var(--database-cyan);
    stroke-width: 2;
    rx: 5;
  }

  /* Infrastructure/Host */
  .infrastructure {
    fill: var(--infrastructure-indigo-light);
    stroke: var(--infrastructure-indigo);
    stroke-width: 3;
    rx: 8;
  }

  /* Network/Mesh */
  .network {
    fill: var(--network-yellow-light);
    stroke: var(--network-yellow);
    stroke-width: 2;
    rx: 5;
  }
</style>
```

**Connection Styles:**

```xml
<style>
  .connection-primary {
    stroke: var(--gray-800);
    stroke-width: 2.5;
    fill: none;
  }

  .connection-network {
    stroke: var(--network-yellow);
    stroke-width: 2.5;
    fill: none;
  }

  .connection-optional {
    stroke: var(--gray-600);
    stroke-width: 2;
    fill: none;
    stroke-dasharray: 5,5;
  }
</style>
```

### Branding Consistency Checklist

Before publishing any diagram, verify:

- [ ] Colors match defined palette (use CSS variables)
- [ ] Typography uses standard font stack and scale
- [ ] Spacing follows 8px grid system
- [ ] Component sizes match standard dimensions
- [ ] Border radius: 5px (components), 8px (containers)
- [ ] Stroke width: 2px (components), 3px (containers), 2.5px (connections)
- [ ] Text contrast meets WCAG AA (4.5:1 minimum)
- [ ] Semantic colors used correctly (green=service, cyan=database, etc.)
- [ ] Consistent styling within diagram type (all architecture diagrams match)

## Architecture Diagram Best Practices

### Component Representation

**Boxes/Containers:**

```xml
<!-- Standard component box -->
<g id="component-name">
  <rect x="100" y="100" width="120" height="80"
        rx="5"
        fill="#f0f0f0"
        stroke="#333"
        stroke-width="2"/>
  <text x="160" y="145"
        text-anchor="middle"
        font-family="sans-serif"
        font-size="14"
        fill="#333">Component Name</text>
</g>
```

**Key attributes:**

- `rx` for rounded corners (5-10 typical)
- `fill` for background color
- `stroke` for border
- `stroke-width` for border thickness (2-3 typical)
- `text-anchor="middle"` for centered text
- Group related elements with `<g>`

### Connections and Arrows

**Directional arrows:**

```xml
<!-- Define reusable arrowhead -->
<defs>
  <marker id="arrowhead"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto">
    <polygon points="0 0, 10 3, 0 6" fill="#333"/>
  </marker>
</defs>

<!-- Use in lines -->
<line x1="220" y1="140" x2="380" y2="140"
      stroke="#333"
      stroke-width="2"
      marker-end="url(#arrowhead)"/>
```

**Arrow types:**

- **Solid line + arrow**: Direct connection, data flow
- **Dashed line**: Indirect/optional connection
- **Bidirectional**: Use `marker-start` and `marker-end`
- **Label arrows**: Add `<text>` near midpoint

### Grouping and Organization

**Use semantic grouping:**

```xml
<svg viewBox="0 0 1000 800" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Define reusable elements here -->
  </defs>

  <g id="containers">
    <!-- Container boxes -->
  </g>

  <g id="components">
    <!-- Individual components -->
  </g>

  <g id="connections">
    <!-- Arrows and lines -->
  </g>

  <g id="labels">
    <!-- Text labels and annotations -->
  </g>
</svg>
```

## Color and Styling Best Practices

### Color Palette

**Use accessible, professional colors:**

```xml
<!-- Light theme (recommended for technical docs) -->
<style>
  .container { fill: #f8f9fa; stroke: #343a40; }
  .component { fill: #e9ecef; stroke: #495057; }
  .database { fill: #d1ecf1; stroke: #0c5460; }
  .service { fill: #d4edda; stroke: #155724; }
  .network { fill: #fff3cd; stroke: #856404; }

  .connection { stroke: #495057; fill: none; }
  .text-primary { fill: #212529; }
  .text-secondary { fill: #6c757d; }
</style>
```

**Contrast requirements:**

- Minimum 3:1 for large text (18pt+)
- Minimum 4.5:1 for normal text
- Test with WebAIM Contrast Checker

### Typography

```xml
<text font-family="system-ui, -apple-system, sans-serif"
      font-size="14"
      font-weight="600"
      fill="#333">
  Component Label
</text>
```

**Font sizing:**

- **Titles**: 18-24px
- **Component names**: 14-16px
- **Labels/annotations**: 12-14px
- **Small details**: 10-12px (minimum)

## Common Diagram Patterns

### Nested Containers

```xml
<!-- Outer container (e.g., Host Machine) -->
<g id="host">
  <rect x="50" y="50" width="900" height="700"
        rx="8" fill="#f8f9fa" stroke="#343a40" stroke-width="3"/>
  <text x="500" y="80" text-anchor="middle" font-size="18" font-weight="bold">
    Host Machine
  </text>

  <!-- Inner container (e.g., Docker Network) -->
  <g id="docker-network">
    <rect x="100" y="120" width="800" height="600"
          rx="5" fill="#fff" stroke="#6c757d" stroke-width="2"/>
    <text x="500" y="150" text-anchor="middle" font-size="16">
      Docker Compose Network
    </text>

    <!-- Components inside -->
  </g>
</g>
```

### Multi-line Text

```xml
<!-- Use multiple <text> elements with dy offset -->
<text x="160" y="130" text-anchor="middle" font-size="14">
  <tspan x="160" dy="0">Component</tspan>
  <tspan x="160" dy="18">Name</tspan>
</text>
```

### Connection Labels

```xml
<!-- Arrow with label -->
<g id="connection-with-label">
  <line x1="220" y1="140" x2="380" y2="140"
        stroke="#495057" stroke-width="2"
        marker-end="url(#arrowhead)"/>
  <text x="300" y="130"
        text-anchor="middle"
        font-size="12"
        fill="#6c757d">
    Port 3000
  </text>
</g>
```

## Optimization and Performance

### File Size Optimization

**Remove unnecessary attributes:**

```xml
<!-- Verbose -->
<rect x="100.000" y="100.000" width="120.000" height="80.000"/>

<!-- Optimized -->
<rect x="100" y="100" width="120" height="80"/>
```

**Use `<use>` for repeated elements:**

```xml
<defs>
  <g id="server-icon">
    <!-- complex icon definition -->
  </g>
</defs>

<!-- Reuse multiple times -->
<use href="#server-icon" x="100" y="100"/>
<use href="#server-icon" x="300" y="100"/>
<use href="#server-icon" x="500" y="100"/>
```

### CSS vs Inline Styles

**Prefer CSS for maintainability:**

```xml
<svg viewBox="0 0 800 600">
  <style>
    .component-box { fill: #e9ecef; stroke: #495057; stroke-width: 2; }
    .component-text { font-family: sans-serif; font-size: 14px; text-anchor: middle; }
  </style>

  <rect class="component-box" x="100" y="100" width="120" height="80"/>
  <text class="component-text" x="160" y="145">Component</text>
</svg>
```

## Validation and Testing

### Pre-deployment Checklist

- [ ] Valid XML syntax (well-formed)
- [ ] `xmlns="http://www.w3.org/2000/svg"` on `<svg>` element
- [ ] `viewBox` attribute present
- [ ] `role` and `aria-labelledby` for accessibility
- [ ] `<title>` and `<desc>` with descriptive content
- [ ] Adequate color contrast (3:1 minimum)
- [ ] Text readable at all zoom levels
- [ ] No hardcoded width/height on root `<svg>`
- [ ] Proper grouping with `<g>` elements
- [ ] Semantic IDs on important elements

### Testing Tools

**Accessibility:**

- WAVE browser extension
- axe DevTools
- Screen reader testing (NVDA, JAWS, VoiceOver)

**Validation:**

- W3C SVG Validator: https://validator.w3.org/
- Browser DevTools for rendering

**Optimization:**

- SVGO: https://github.com/svg/svgo
- SVGOMG (GUI): https://jakearchibald.github.io/svgomg/

## Common Mistakes to Avoid

❌ **Don't:**

- Use fixed width/height on root `<svg>` element
- Forget `viewBox` attribute
- Mix coordinate units (px, em, %, etc.)
- Use images without alt text / aria labels
- Create overly complex paths when simple shapes work
- Use pure black (#000) or white (#fff) - harsh on eyes
- Forget to test at different zoom levels

✅ **Do:**

- Always use `viewBox` for scalability
- Include accessibility attributes
- Use semantic grouping with `<g>`
- Keep coordinate system consistent
- Add meaningful titles and descriptions
- Test with screen readers
- Use professional, contrasting colors
- Comment complex sections

## Integration with Documentation

### MkDocs Material

```markdown
<!-- Inline SVG in Markdown -->
<figure markdown="span">
  <svg viewBox="0 0 800 600" role="img" aria-labelledby="arch-title arch-desc">
    <title id="arch-title">System Architecture</title>
    <desc id="arch-desc">Diagram showing three-tier architecture...</desc>
    <!-- SVG content -->
  </svg>
  <figcaption>System Architecture Diagram</figcaption>
</figure>
```

### As External File

```markdown
<!-- Reference external SVG -->
![System Architecture](../images/architecture.svg)
```

**File organization:**

- Store in `docs/images/` or `docs/assets/`
- Use descriptive filenames: `docker-architecture.svg`, not `diagram1.svg`
- Include source files if created with tools (e.g., .drawio)

## Tools and Resources

### Recommended Tools

**Code-based:**

- Hand-coded SVG (best control, smallest files)
- D3.js (for data-driven diagrams)
- Snap.svg (modern SVG library)

**Visual editors:**

- draw.io / diagrams.net (free, open source)
- Inkscape (free, powerful)
- Figma (commercial, excellent for UI)

**Optimization:**

- SVGO CLI: `svgo input.svg -o output.svg`
- Prettier (with SVG plugin)

### Reference Documentation

- **W3C SVG Specification**: https://www.w3.org/TR/SVG2/
- **MDN SVG Tutorial**: https://developer.mozilla.org/en-US/docs/Web/SVG
- **Accessible SVGs**: https://css-tricks.com/accessible-svgs/
- **SVG Accessibility (W3C)**: https://www.w3.org/TR/SVG-access/

## Example: Converting ASCII to SVG

**Input (ASCII art):**

```
┌─────────┐      ┌─────────┐
│ Client  │─────→│ Server  │
└─────────┘      └─────────┘
```

**Output (SVG):**

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 400 150"
     role="img"
     aria-labelledby="client-server-title client-server-desc">
  <title id="client-server-title">Client-Server Architecture</title>
  <desc id="client-server-desc">Diagram showing client connecting to server with directional arrow</desc>

  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#495057"/>
    </marker>
  </defs>

  <!-- Client box -->
  <g id="client">
    <rect x="50" y="50" width="100" height="60"
          rx="5" fill="#e9ecef" stroke="#495057" stroke-width="2"/>
    <text x="100" y="85" text-anchor="middle"
          font-family="sans-serif" font-size="14" fill="#212529">
      Client
    </text>
  </g>

  <!-- Connection arrow -->
  <line x1="150" y1="80" x2="240" y2="80"
        stroke="#495057" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Server box -->
  <g id="server">
    <rect x="250" y="50" width="100" height="60"
          rx="5" fill="#e9ecef" stroke="#495057" stroke-width="2"/>
    <text x="300" y="85" text-anchor="middle"
          font-family="sans-serif" font-size="14" fill="#212529">
      Server
    </text>
  </g>
</svg>
```

## Workflow

1. **Analyze ASCII diagram**: Identify components, connections, hierarchy
2. **Plan layout**: Calculate coordinates, spacing, sizing
3. **Create structure**: Define viewBox, add accessibility elements
4. **Add reusables**: Define markers, styles in `<defs>`
5. **Build components**: Create boxes, shapes with proper grouping
6. **Add connections**: Draw lines, arrows with labels
7. **Style**: Apply colors, fonts, spacing
8. **Test**: Validate, check accessibility, test responsive scaling
9. **Optimize**: Remove redundant code, compress if needed
10. **Document**: Add comments for complex sections

---

**Remember**: Good SVG diagrams are accessible, responsive, and maintainable. Prioritize clarity over complexity.
