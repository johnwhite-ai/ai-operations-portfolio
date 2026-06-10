# Portfolio Design System

The single source of truth for the visual identity of this portfolio. Every README, diagram, SHOWCASE PDF, and the future hosted site inherits from these tokens. Derived from a Swiss/minimalist design system tuned for a professional technical portfolio.

## Principles

1. **Content first.** The work speaks; design gets out of the way.
2. **Restraint.** Navy plus one accent. No decorative gradients, no emoji as structural icons.
3. **Consistency.** Every asset uses the same tokens, so the whole portfolio reads as one product.
4. **Two-layer depth.** Digestible at a glance for a busy hiring manager; full detail underneath for those who dig.

## Color Tokens

| Token | Hex | Use |
|---|---|---|
| `ink` | `#0f172a` | Primary text, darkest surfaces (slate-900) |
| `navy` | `#1e293b` | Headers, primary brand surface (slate-800) |
| `navy-600` | `#334155` | Secondary surfaces (slate-700) |
| `accent` | `#2563eb` | Single accent — links, emphasis, primary CTA (blue-600) |
| `accent-soft` | `#dbeafe` | Accent backgrounds, fills (blue-100) |
| `success` | `#15803d` | "Live" status, confirmed (green-700) |
| `line` | `#e2e8f0` | Borders, dividers, gridlines (slate-200) |
| `muted` | `#64748b` | Secondary text, captions (slate-500) |
| `surface` | `#f8fafc` | Page background tint (slate-50) |
| `white` | `#ffffff` | Cards, base background |

Contrast: ink-on-white = 16:1, navy-on-white = 13:1, accent-on-white = 5.2:1 — all pass WCAG AA.

## Typography

- **Headings:** Space Grotesk (or system geometric sans). Weights 600–700.
- **Body:** Inter (or system sans). Weight 400; 500 for labels.
- **Mono:** for code and data — system monospace.
- **Scale (1.25 major third):** 12 · 14 · 16 · 20 · 25 · 31 · 39
- **Line height:** 1.5 body, 1.2 headings.

## Spacing

8pt grid. Steps: 4 · 8 · 16 · 24 · 32 · 48 · 64. Section spacing tiers: 16 (tight) · 24 (default) · 48 (section break).

## Effects

- Border radius: 8px (cards), 12px (large panels).
- Shadows: subtle elevation only (`0 1px 3px rgba(15,23,42,.08)`), never decorative.
- Borders: 1px `line`.

## Markdown / README Conventions

- **No emoji as section icons.** Use clean text headers. A single small status pill (e.g. `Live`) is allowed inline.
- **Badges:** shields.io, flat-square style, navy/accent palette only.
- **Diagrams:** navy boxes, accent arrows, `line` gridlines, Space-Grotesk-style bold labels, white background, generous padding.
- **PDFs:** navy headers with a 2px rule, accent sub-rules, stat cards in navy, captions in muted, footer in muted.
- **Every project folder:** `README.md` (user manual w/ visuals) + `SHOWCASE.pdf` (1–2 page case study) + `architecture-diagram.png` + `code/`.

## Diagram color constants (for the asset scripts)

```
INK     = "#0f172a"
NAVY    = "#1e293b"
ACCENT  = "#2563eb"
ACCENTS = "#dbeafe"
SUCCESS = "#15803d"
LINE    = "#e2e8f0"
MUTED   = "#64748b"
SURFACE = "#f8fafc"
WHITE   = "#ffffff"
```

*This file is the contract. When in doubt, an asset should match DESIGN.md, not improvise.*
