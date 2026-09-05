---
name: hermes-desktop-theme-authoring
description: Use when styling Hermes Desktop. Create and style themes.
category: hermes
---

# Hermes Desktop Theme & UI Styling Authoring

Standard workflow for creating, registering, styling, and hot-switching custom themes for the Hermes Desktop app using the native `@hermes/plugin-sdk`.

## 1. Plugin Architecture & Placement

Hermes Desktop loads runtime ESM plugins automatically from:
- `$HERMES_HOME/desktop-plugins/<plugin-id>/plugin.js`

Plugins hot-reload within seconds of saving to disk. No compile step or core repo modification is required.

## 2. DesktopTheme Model Structure

A theme is a data object registered to `THEMES_AREA`. Required minimal fields are `name`, `label`, and `colors` (with `background`, `foreground`, `primary`).

```javascript
import { host, PALETTE_AREA, requestTheme, THEMES_AREA } from '@hermes/plugin-sdk'

const THEME_ID = 'custom-dark'

const myTheme = {
  name: THEME_ID,
  label: 'Custom Dark',
  description: 'Clean dark workspace with custom accents',
  colors: {
    background: '#181a1f',
    foreground: '#e2e4e9',
    card: '#1f2228',
    cardForeground: '#e2e4e9',
    muted: '#14161a',
    mutedForeground: '#8a909b',
    popover: '#1f2228',
    popoverForeground: '#e2e4e9',
    primary: '#e5a93c',
    primaryForeground: '#121316',
    secondary: '#252932',
    secondaryForeground: '#d1d5db',
    accent: '#292d37',
    accentForeground: '#ffffff',
    border: '#2a2d35',
    input: '#1e2127',
    ring: '#e5a93c',
    midground: '#e5a93c',
    composerRing: 'rgba(229, 169, 60, 0.4)',
    destructive: '#ef4444',
    destructiveForeground: '#ffffff',
    sidebarBackground: '#131518',
    sidebarBorder: '#202329',
    userBubble: '#20242c',
    userBubbleBorder: '#2a2e37',
  },
  darkColors: { /* mirror or tuned variant */ },
  typography: {
    fontSans: 'Inter, "PingFang SC", sans-serif',
    fontMono: '"JetBrains Mono", "Cascadia Code", Consolas, monospace',
  },
}
```

## 3. Custom CSS Overrides Injection

To modify geometry, floating docks, rounded corners, or custom scrollbars beyond Tailwind CSS tokens, dynamically inject a scoped `<style>` tag into `document.head`:

```javascript
const STYLE_ID = 'custom-theme-overrides'

function injectStyles() {
  if (typeof document === 'undefined') return
  let el = document.getElementById(STYLE_ID)
  if (!el) {
    el = document.createElement('style')
    el.id = STYLE_ID
    document.head.appendChild(el)
  }
  el.textContent = `
    [data-slot='composer-dock'] { padding-bottom: 16px !important; }
    [data-slot='composer-root'] {
      border-radius: 14px !important;
      box-shadow: 0 10px 32px rgba(0, 0, 0, 0.6) !important;
    }
  `
}
```

## 4. Registration & Activation Workflow

```javascript
export default {
  id: 'my-theme-plugin',
  name: 'Custom Theme Plugin',
  register(ctx) {
    // 1. Register palette to theme engine
    ctx.register({
      id: 'theme-entry',
      area: THEMES_AREA,
      data: myTheme,
    })

    // 2. Inject style overrides
    injectStyles()

    // 3. Immediately activate
    try {
      requestTheme(THEME_ID)
    } catch {}

    // 4. Register Ctrl+K Command Palette item
    ctx.register({
      id: 'cmd-activate',
      area: PALETTE_AREA,
      data: {
        id: 'theme.activate',
        label: 'Theme: Switch to Custom Dark',
        keywords: ['theme', 'dark', 'switch'],
        run: () => {
          requestTheme(THEME_ID)
          injectStyles()
          host.notify?.({ kind: 'info', message: 'Theme switched' })
        },
      },
    })
  },
}
```

## 5. Key Invariants & Pitfalls

- **Avoid External UI Wrappers for Styling**: Do not replace Hermes Desktop with third-party web frontends (e.g. `hermes-studio`) merely for aesthetics. Third-party forks drop the `@hermes/plugin-sdk` runtime (breaking desktop plugins like `token-stats`), introduce split-brain SQLite session databases, and add redundant backend bridge layers. Native `@hermes/plugin-sdk` theme plugins provide full visual control with zero capability loss.
- **Module Format**: Plugins must be plain uncompiled ESM (`import`/`export`). Only `@hermes/plugin-sdk` and `react/jsx-runtime` can be imported; do not import npm packages directly.
- **Style Specificity**: Use `!important` or target exact `[data-slot="..."]` attributes to reliably override Tailwind CSS utility layers.
- **Desktop Environment Strict Dark Preference**: The user strictly rejects all daytime/light/bright themes (including cream/sepia parchment, cartoon peach, light blues, wine-red light, and WeChat light) as they cause eye strain and glare in desktop terminal/agent environments. All themes designed for this workspace must adhere to pure dark/night matte palettes (e.g. ZCode Dark, OLED Dark, Palenight, Dracula Mint, JetBrains/VS Code matte).
- **ZCode Agentic IDE Aesthetic Blueprint**: When styling for a modern AI coding workspace (like ZCode):
  1. Palette: Three-tier matte charcoal (`#131518` sidebar, `#181a1f` canvas, `#1f2228` cards), avoiding harsh `#000000` pitch black.
  2. Floating Dock: Apply custom CSS to `[data-slot='composer-root']` giving it `14px` border-radius, `border: 1px solid rgba(255, 255, 255, 0.09)`, and deep ambient elevation `box-shadow: 0 10px 32px -4px rgba(0, 0, 0, 0.6)`.
  3. Micro-Borders: Use `1px solid rgba(255, 255, 255, 0.08)` instead of thick or high-contrast divider lines.
  4. Semantic Accents: Use Amber Gold (`#e5a93c` / `#f59e0b`) for active rings, security badges, and focus outlines; Terminal Green (`#22c55e` / `#10b981`) for diff additions and completed statuses.
  5. De-bubbling: Flatten user messages to compact bordered rectangular cards (`#20242c`) rather than rounded IM chat bubbles.
- **Batch Theme Registration & Deduplication**: When bundling multiple themes within a single desktop plugin (e.g. 18-in-1 theme packs), assign each theme an immutable unique slug in `THEMES_AREA` and register a corresponding `PALETTE_AREA` command with distinct keywords (`['theme', 'switch', '<slug>']`) so users can hot-switch instantly via `Ctrl+K` without traversing Settings menus.
