/**
 * Hermes Desktop Plugin: zcode-theme
 *
 * 1:1 复刻 ZCode 现代化 Agentic IDE 视觉美学：
 * - 哑光深炭三层背景（#131518 侧栏 / #181a1f 主工作区 / #1f2228 卡片）
 * - 极细微描边（rgba(255,255,255,0.08)）与精致内敛光影
 * - 琥珀金（#e5a93c）专业安全/权限状态高亮 + 终端绿强调
 * - 悬浮式底栏卡片（Floating Dock Input）与去气泡化流式卡片质感
 * - 双字体系统：现代无衬线正文 + JetBrains Mono / Cascadia Code 极客等宽代码
 */

import { host, PALETTE_AREA, requestTheme, THEMES_AREA } from '@hermes/plugin-sdk'

const THEME_ID = 'zcode-dark'
const STYLE_ID = 'zcode-desktop-overrides'

// ==================== ZCode 核心调色板 ====================

const zcodeDarkColors = {
  // 主画布：哑光石墨炭黑，不刺眼、高沉浸
  background: '#181a1f',
  foreground: '#e2e4e9',

  // 卡片与提升层容器
  card: '#1f2228',
  cardForeground: '#e2e4e9',

  // 弱化区与沉淀底色
  muted: '#14161a',
  mutedForeground: '#8a909b',

  // 浮动菜单与弹窗
  popover: '#1f2228',
  popoverForeground: '#e2e4e9',

  // 核心品牌色：ZCode 标志性琥珀金（Amber Gold）
  primary: '#e5a93c',
  primaryForeground: '#121316',

  // 次级胶囊与操作底色
  secondary: '#252932',
  secondaryForeground: '#d1d5db',

  // 悬停与高亮项
  accent: '#292d37',
  accentForeground: '#ffffff',

  // 极细微描边 (Subtle 1px Borders)
  border: '#2a2d35',
  input: '#1e2127',

  // 聚焦环与描边光晕
  ring: '#e5a93c',
  midground: '#e5a93c',
  midgroundForeground: '#121316',
  composerRing: 'rgba(229, 169, 60, 0.4)',

  // 警告与危险色
  destructive: '#ef4444',
  destructiveForeground: '#ffffff',

  // 侧边栏：比主区域更深沉的冷炭色，形成前后纵深
  sidebarBackground: '#131518',
  sidebarBorder: '#202329',

  // 用户消息卡片：扁平暗灰，拒绝大块气泡
  userBubble: '#20242c',
  userBubbleBorder: '#2a2e37',
}

const zcodeTheme = {
  name: THEME_ID,
  label: 'ZCode Dark (Agentic IDE)',
  description: 'ZCode-inspired matte charcoal workspace with amber gold accents and floating dock input',
  colors: zcodeDarkColors,
  darkColors: zcodeDarkColors,
  typography: {
    fontSans: 'Inter, "PingFang SC", "Segoe UI Variable Text", "Microsoft YaHei", -apple-system, sans-serif',
    fontMono: '"JetBrains Mono", "Cascadia Code", "Fira Code", Consolas, monospace',
  },
  darkTerminal: {
    foreground: '#e2e4e9',
    cursor: '#e5a93c',
    selectionBackground: 'rgba(229, 169, 60, 0.25)',
    black: '#181a1f',
    red: '#f87171',
    green: '#34d399',
    yellow: '#fbbf24',
    blue: '#60a5fa',
    magenta: '#c084fc',
    cyan: '#38bdf8',
    white: '#f3f4f6',
    brightBlack: '#4b5563',
    brightRed: '#ef4444',
    brightGreen: '#10b981',
    brightYellow: '#f59e0b',
    brightBlue: '#3b82f6',
    brightMagenta: '#a855f7',
    brightCyan: '#06b6d4',
    brightWhite: '#ffffff',
  },
}

// ==================== ZCode 视觉微调样式表 ====================

const zcodeCustomCSS = `
/* [ZCode Theme] 悬浮底栏输入框 (Floating Dock Input) */
[data-slot='composer-dock'] {
  padding-bottom: 16px !important;
}

[data-slot='composer-root'] {
  border-radius: 14px !important;
  background: #1f2228 !important;
  border: 1px solid rgba(255, 255, 255, 0.09) !important;
  box-shadow: 0 10px 32px -4px rgba(0, 0, 0, 0.6), 0 0 1px rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(20px) !important;
  transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

[data-slot='composer-root']:focus-within {
  border-color: rgba(229, 169, 60, 0.45) !important;
  box-shadow: 0 12px 36px -4px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(229, 169, 60, 0.25) !important;
}

[data-slot='composer-rich-input'] {
  font-family: Inter, "PingFang SC", "Segoe UI Variable Text", "Microsoft YaHei", sans-serif !important;
  font-size: 0.875rem !important;
  line-height: 1.55 !important;
  color: #e2e4e9 !important;
}

/* [ZCode Theme] 用户提问卡片：扁平克制，去气泡化 */
[data-slot='aui_user-message-root'] {
  background: #20242c !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 12px !important;
  padding: 10px 15px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
  max-width: 92% !important;
}

/* [ZCode Theme] Agent 助手回复正文排版 */
[data-slot='aui_assistant-message-content'] {
  font-size: 0.875rem !important;
  line-height: 1.68 !important;
  color: #e2e4e9 !important;
}

/* [ZCode Theme] 代码卡片与行内代码：等宽对齐与深色暗仓 */
[data-slot='code-card'], .aui-md pre {
  background: #14161b !important;
  border: 1px solid rgba(255, 255, 255, 0.07) !important;
  border-radius: 10px !important;
  font-family: "JetBrains Mono", "Cascadia Code", Consolas, monospace !important;
}

.aui-md :where(:not(pre) > code) {
  background: #22262e !important;
  color: #f59e0b !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 4px !important;
  padding: 2px 5px !important;
  font-size: 0.8125rem !important;
  font-family: "JetBrains Mono", "Cascadia Code", Consolas, monospace !important;
}

/* [ZCode Theme] 侧边栏：深色石墨质感与细分割线 */
[data-slot='sidebar-wrapper'] {
  background: #131518 !important;
  border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
}

/* [ZCode Theme] 极简现代细微滚动条 */
::-webkit-scrollbar {
  width: 5px !important;
  height: 5px !important;
}
::-webkit-scrollbar-track {
  background: transparent !important;
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12) !important;
  border-radius: 3px !important;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.22) !important;
}
`

function injectCustomStyles() {
  if (typeof document === 'undefined') return
  let styleEl = document.getElementById(STYLE_ID)
  if (!styleEl) {
    styleEl = document.createElement('style')
    styleEl.id = STYLE_ID
    document.head.appendChild(styleEl)
  }
  styleEl.textContent = zcodeCustomCSS
}

// ==================== 插件注册入口 ====================

export default {
  id: 'zcode-theme',
  name: 'ZCode Dark Theme',
  register(ctx) {
    // 1. 注册桌面端原生主题
    ctx.register({
      id: 'theme-zcode',
      area: THEMES_AREA,
      data: zcodeTheme,
    })

    // 2. 注入 ZCode 视觉精调 CSS 样式
    injectCustomStyles()

    // 3. 立即自动激活 ZCode 主题
    try {
      requestTheme(THEME_ID)
    } catch {
      // 容错捕获
    }

    // 4. 在 Ctrl/Cmd+K 命令面板中增加切换选项
    ctx.register({
      id: 'cmd-activate',
      area: PALETTE_AREA,
      data: {
        id: 'theme.zcode',
        label: 'Theme: 切换到 ZCode Dark (Agentic IDE)',
        keywords: ['theme', 'zcode', 'dark', 'ide', 'amber'],
        run: () => {
          requestTheme(THEME_ID)
          injectCustomStyles()
          host.notify?.({
            kind: 'info',
            message: '🎨 已切换至 ZCode Dark 沉浸式编程工作台主题',
          })
        },
      },
    })
  },
}
