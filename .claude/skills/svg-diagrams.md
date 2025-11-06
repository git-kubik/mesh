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
