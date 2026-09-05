/**
 * Hermes Desktop Plugin: im-themes (Telegram 社交经典主题套系)
 *
 * 移植自 Telegram 经典社交主题包：
 * 1. qq-classic: Such QQ (QQ 经典天蓝与蓝白气泡)
 * 2. wechat-light: 小而美 8.0 (微信官方日间浅灰底 + 嫩绿发信气泡)
 * 3. wechat-dark: 小而美 8.0 暗黑模式 (微信夜间1 深灰底 + 暗绿发信气泡)
 * 4. wechatify-dark: WeChatify Dark (微信夜间2 AMOLED 极黑底 + 沉浸深翠绿)
 *
 * 每一个主题均注册至 THEMES_AREA，并在 Ctrl+K 命令面板中支持一键极速切换。
 */

import { host, PALETTE_AREA, requestTheme, THEMES_AREA } from '@hermes/plugin-sdk'

// ==================== 1. Such QQ (QQ 经典风格) ====================

const qqTheme = {
  name: 'qq-classic',
  label: 'QQ 经典 (Such QQ)',
  description: 'Classic Tencent QQ blue theme with clean chat cards and sky-blue bubbles',
  colors: {
    background: '#f2f4f7',
    foreground: '#1f2329',
    card: '#ffffff',
    cardForeground: '#1f2329',
    muted: '#e8ebf0',
    mutedForeground: '#8a919e',
    popover: '#ffffff',
    popoverForeground: '#1f2329',
    primary: '#0099ff', // QQ 经典天蓝
    primaryForeground: '#ffffff',
    secondary: '#e6f4ff',
    secondaryForeground: '#0077cc',
    accent: '#e6f4ff',
    accentForeground: '#0077cc',
    border: '#dce1e8',
    input: '#ffffff',
    ring: '#0099ff',
    midground: '#0099ff',
    composerRing: '#0099ff',
    destructive: '#ef4444',
    destructiveForeground: '#ffffff',
    sidebarBackground: '#ffffff',
    sidebarBorder: '#e5e8ec',
    userBubble: '#12b7f5', // QQ 标志性蓝气泡
    userBubbleBorder: '#0ea5e9',
  },
  darkColors: {
    background: '#18191c',
    foreground: '#e1e4ea',
    card: '#222429',
    cardForeground: '#e1e4ea',
    muted: '#1e2025',
    mutedForeground: '#7a8190',
    popover: '#222429',
    popoverForeground: '#e1e4ea',
    primary: '#12b7f5',
    primaryForeground: '#ffffff',
    secondary: '#1c2b38',
    secondaryForeground: '#38bdf8',
    accent: '#233647',
    accentForeground: '#38bdf8',
    border: '#282b32',
    input: '#1e2025',
    ring: '#12b7f5',
    midground: '#12b7f5',
    composerRing: 'rgba(18, 183, 245, 0.45)',
    destructive: '#ef4444',
    destructiveForeground: '#ffffff',
    sidebarBackground: '#131416',
    sidebarBorder: '#24262b',
    userBubble: '#007acc',
    userBubbleBorder: '#0099ff',
  },
  typography: {
    fontSans: 'Inter, "PingFang SC", "Segoe UI Variable Text", "Microsoft YaHei", sans-serif',
    fontMono: '"JetBrains Mono", "Cascadia Code", Consolas, monospace',
  },
}

// ==================== 2. 小而美 8.0 (微信日间版) ====================

const wechatLightTheme = {
  name: 'wechat-light',
  label: '微信日间 (小而美 8.0)',
  description: 'Official WeChat 8.0 light theme with signature green bubbles and neutral grey canvas',
  colors: {
    background: '#ededed', // 微信聊天背景浅灰
    foreground: '#191919',
    card: '#ffffff', // 微信白底收信气泡
    cardForeground: '#191919',
    muted: '#dfdfdf',
    mutedForeground: '#7d7d7d',
    popover: '#ffffff',
    popoverForeground: '#191919',
    primary: '#07c160', // 微信品牌绿
    primaryForeground: '#ffffff',
    secondary: '#e1f6eb',
    secondaryForeground: '#059648',
    accent: '#e6faef',
    accentForeground: '#07c160',
    border: '#dcdcdc',
    input: '#ffffff',
    ring: '#07c160',
    midground: '#07c160',
    composerRing: '#07c160',
    destructive: '#fa5151',
    destructiveForeground: '#ffffff',
    sidebarBackground: '#e8e8e8',
    sidebarBorder: '#d9d9d9',
    userBubble: '#95ec69', // 微信标志性嫩绿发信气泡
    userBubbleBorder: '#86d45e',
  },
  typography: {
    fontSans: 'Inter, "PingFang SC", "Segoe UI Variable Text", "Microsoft YaHei", sans-serif',
    fontMono: '"JetBrains Mono", "Cascadia Code", Consolas, monospace',
  },
}

// ==================== 3. 小而美 8.0 暗黑模式 (微信夜间1) ====================

const wechatDarkColors = {
  background: '#191919', // 微信暗黑模式主底色
  foreground: '#e1e1e1',
  card: '#2c2c2c', // 微信暗黑收信灰气泡
  cardForeground: '#e1e1e1',
  muted: '#222222',
  mutedForeground: '#777777',
  popover: '#2c2c2c',
  popoverForeground: '#e1e1e1',
  primary: '#28b461', // 微信深色绿
  primaryForeground: '#ffffff',
  secondary: '#1b3524',
  secondaryForeground: '#28b461',
  accent: '#243f2d',
  accentForeground: '#34d399',
  border: '#2e2e2e',
  input: '#222222',
  ring: '#28b461',
  midground: '#28b461',
  composerRing: 'rgba(40, 180, 97, 0.4)',
  destructive: '#fa5151',
  destructiveForeground: '#ffffff',
  sidebarBackground: '#131313',
  sidebarBorder: '#262626',
  userBubble: '#28b461', // 微信暗黑发信绿气泡
  userBubbleBorder: '#239b54',
}

const wechatDarkTheme = {
  name: 'wechat-dark',
  label: '微信夜间 1 (小而美 8.0 暗黑模式)',
  description: 'Official WeChat 8.0 dark mode with matte dark grey surfaces and deep emerald accents',
  colors: wechatDarkColors,
  darkColors: wechatDarkColors,
  typography: {
    fontSans: 'Inter, "PingFang SC", "Segoe UI Variable Text", "Microsoft YaHei", sans-serif',
    fontMono: '"JetBrains Mono", "Cascadia Code", Consolas, monospace',
  },
}

// ==================== 4. WeChatify Dark (微信夜间2 OLED 极黑) ====================

const wechatifyDarkColors = {
  background: '#0d0d0e', // 纯黑 OLED 极暗夜景
  foreground: '#ececec',
  card: '#18181b', // 深墨微发光卡片
  cardForeground: '#ececec',
  muted: '#141416',
  mutedForeground: '#71717a',
  popover: '#18181b',
  popoverForeground: '#ececec',
  primary: '#22c55e', // 翠绿点缀
  primaryForeground: '#ffffff',
  secondary: '#14331d',
  secondaryForeground: '#4ade80',
  accent: '#1c3d25',
  accentForeground: '#86efac',
  border: '#222226',
  input: '#161618',
  ring: '#22c55e',
  midground: '#22c55e',
  composerRing: 'rgba(34, 197, 94, 0.45)',
  destructive: '#ef4444',
  destructiveForeground: '#ffffff',
  sidebarBackground: '#080809',
  sidebarBorder: '#1a1a1d',
  userBubble: '#1a6e38', // WeChatify 特制深翠绿发信气泡
  userBubbleBorder: '#22c55e',
}

const wechatifyDarkTheme = {
  name: 'wechatify-dark',
  label: '微信夜间 2 (WeChatify Dark OLED)',
  description: 'WeChatify pure-black OLED optimized theme with high-contrast emerald glow',
  colors: wechatifyDarkColors,
  darkColors: wechatifyDarkColors,
  typography: {
    fontSans: 'Inter, "PingFang SC", "Segoe UI Variable Text", "Microsoft YaHei", sans-serif',
    fontMono: '"JetBrains Mono", "Cascadia Code", Consolas, monospace',
  },
}

// ==================== 插件注册入口 ====================

export default {
  id: 'im-themes',
  name: 'IM Classic Themes (QQ & WeChat)',
  register(ctx) {
    const themes = [
      { id: 'qq', theme: qqTheme, title: 'QQ 经典 (Such QQ)' },
      { id: 'wechat-light', theme: wechatLightTheme, title: '微信日间 (小而美 8.0)' },
      { id: 'wechat-dark', theme: wechatDarkTheme, title: '微信夜间 1 (小而美 8.0 暗黑模式)' },
      { id: 'wechatify-dark', theme: wechatifyDarkTheme, title: '微信夜间 2 (WeChatify Dark OLED)' },
    ]

    // 1. 注册 4 个主题至 Hermes 原生主题池
    for (const item of themes) {
      ctx.register({
        id: `theme-${item.id}`,
        area: THEMES_AREA,
        data: item.theme,
      })

      // 2. 在 Ctrl+K 命令面板中注册快速切换指令
      ctx.register({
        id: `palette-switch-${item.id}`,
        area: PALETTE_AREA,
        data: {
          id: `theme.switch.${item.id}`,
          label: `Theme: 切换到 ${item.title}`,
          keywords: ['theme', 'qq', 'wechat', item.id, 'im'],
          run: () => {
            requestTheme(item.theme.name)
            host.notify?.({
              kind: 'info',
              message: `🎨 已切换到「${item.title}」`,
            })
          },
        },
      })
    }
  },
}
