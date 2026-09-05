import { host, PALETTE_AREA, requestTheme, THEMES_AREA } from '@hermes/plugin-sdk'

const THEME_ID = 'my-theme'
const STYLE_ID = 'my-theme-styles'

const themeData = {
  name: THEME_ID,
  label: 'My Custom Theme',
  description: 'Custom theme for Hermes Desktop',
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
  typography: {
    fontSans: 'Inter, "PingFang SC", sans-serif',
    fontMono: '"JetBrains Mono", Consolas, monospace',
  },
}

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

export default {
  id: 'custom-theme-plugin',
  name: 'Custom Theme Plugin',
  register(ctx) {
    ctx.register({
      id: 'theme',
      area: THEMES_AREA,
      data: themeData,
    })
    injectStyles()
    try { requestTheme(THEME_ID) } catch {}
    ctx.register({
      id: 'cmd',
      area: PALETTE_AREA,
      data: {
        id: 'theme.switch',
        label: 'Theme: Switch Theme',
        keywords: ['theme', 'switch'],
        run: () => {
          requestTheme(THEME_ID)
          injectStyles()
          host.notify?.({ kind: 'info', message: 'Theme applied' })
        },
      },
    })
  },
}
