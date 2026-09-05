/**
 * Hermes Desktop Plugin: token-stats (Antigravity & Gateway Quota Monitor)
 * 现代化极简奢华 UI 看板：实时监控 Google / Antigravity 官方配额及本地 WorkBuddy 网关状态。
 * 支持右下角状态栏 Chip、点击 Popover、左侧导航栏 Pulse 入口及 /quota 独立全景看板页面。
 * 基于 ctx.storage 实现偏好持久化（相对倒计时 / 绝对时刻）。
 */

import {
  cn,
  haptic,
  host,
  PALETTE_AREA,
  Popover,
  PopoverContent,
  PopoverTrigger,
  ROUTES_AREA,
  Separator,
  SIDEBAR_NAV_AREA,
  Tip,
  useValue,
} from '@hermes/plugin-sdk'
import { useEffect, useState } from 'react'
import { jsx, jsxs } from 'react/jsx-runtime'

const ID = 'token-stats'
const STORAGE_KEY_FORMAT = 'quota_reset_format' // 'relative' | 'absolute'

let pluginCtx = null

function formatResetTime(isoString, formatMode = 'relative') {
  if (!isoString) return '--'
  try {
    const target = new Date(isoString).getTime()
    const now = Date.now()
    const diff = target - now
    if (diff <= 0) return '即将刷新'

    const dt = new Date(isoString)
    const m = String(dt.getMonth() + 1).padStart(2, '0')
    const d = String(dt.getDate()).padStart(2, '0')
    const hm = dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

    if (formatMode === 'absolute') {
      return `${m}/${d} ${hm}`
    }

    const totalMinutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(totalMinutes / 60)
    const minutes = totalMinutes % 60
    const days = Math.floor(hours / 24)
    const remainHours = hours % 24

    if (days > 0) {
      return `${days}天 ${remainHours}小时后 (${m}/${d} ${hm})`
    }
    if (hours > 0) {
      return `${hours}小时 ${minutes}分钟后 (${hm})`
    }
    return `${minutes}分钟后 (${hm})`
  } catch {
    return isoString
  }
}

function getProgressColor(pct) {
  if (pct >= 40) return 'bg-emerald-500'
  if (pct >= 15) return 'bg-amber-500'
  return 'bg-rose-500'
}

function getTextColor(pct) {
  if (pct >= 40) return 'text-emerald-400'
  if (pct >= 15) return 'text-amber-400'
  return 'text-rose-400'
}

// ==================== 状态栏 Chip 组件 ====================

function AntigravityQuotaChip({ ctx }) {
  const busy = useValue(host.state.busy)
  const [open, setOpen] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [justUpdated, setJustUpdated] = useState(false)
  const [lastSyncTime, setLastSyncTime] = useState('')
  const [formatMode, setFormatMode] = useState(() => {
    try {
      return (ctx && ctx.storage && ctx.storage.get(STORAGE_KEY_FORMAT)) || 'relative'
    } catch {
      return 'relative'
    }
  })

  const [quotaData, setQuotaData] = useState({
    quota5h: 100,
    quotaWeekly: 100,
    reset5h: null,
    resetWeekly: null,
    source: 'Google 官方直连',
    plan: 'Google AI Pro',
    account: '...',
    claude5h: 100,
    claudeWeekly: 100,
    workbuddy: { status: 'offline', statusLabel: '未启动' },
  })

  const toggleFormat = (e) => {
    if (e) e.stopPropagation()
    const next = formatMode === 'relative' ? 'absolute' : 'relative'
    setFormatMode(next)
    try {
      if (ctx && ctx.storage) ctx.storage.set(STORAGE_KEY_FORMAT, next)
    } catch {}
    haptic?.('tap')
  }

  const fetchLiveQuota = async (isManual = false) => {
    try {
      setRefreshing(true)
      const path = isManual ? '/quota?force=1' : '/quota'
      const rest = (ctx && ctx.rest) || (pluginCtx && pluginCtx.rest)
      if (!rest) throw new Error('plugin context unavailable')
      const data = await rest.call(ctx || pluginCtx, path)
      if (data && data.status === 'ok') {
        setQuotaData({
          quota5h: data.quota5h != null ? Math.round(data.quota5h * 10) / 10 : 100,
          quotaWeekly: data.quotaWeekly != null ? Math.round(data.quotaWeekly * 10) / 10 : 100,
          reset5h: data.reset5h,
          resetWeekly: data.resetWeekly,
          source: data.source || 'Google 官方直连 (EasyCLIProxyAPI)',
          plan: data.plan || 'Google AI Pro',
          account: data.account || '...',
          claude5h: data.claudeQuota5h != null ? Math.round(data.claudeQuota5h) : 100,
          claudeWeekly: data.claudeQuotaWeekly != null ? Math.round(data.claudeQuotaWeekly) : 100,
          workbuddy: data.workbuddy || { status: 'offline', statusLabel: '未启动' },
        })
        const syncTime =
          data.updatedAtLocal ||
          new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        setLastSyncTime(syncTime)

        if (isManual) {
          setJustUpdated(true)
          haptic?.('success') || haptic?.('tap')
          host.notify({
            kind: 'info',
            message: `✅ 配额与网关状态已同步 (${syncTime})`,
          })
          setTimeout(() => setJustUpdated(false), 2400)
        }
      }
    } catch {
      if (isManual) {
        host.notify({
          kind: 'error',
          message: '刷新配额失败：Hermes 内置配额服务未响应',
        })
      }
    } finally {
      setTimeout(() => setRefreshing(false), 500)
    }
  }

  useEffect(() => {
    fetchLiveQuota()
    const timer = setInterval(() => fetchLiveQuota(false), 10000)
    return () => clearInterval(timer)
  }, [])

  return jsxs(Popover, {
    open,
    onOpenChange: setOpen,
    children: [
      jsx(Tip, {
        label: `Google 官方配额 · 5h: ${quotaData.quota5h}% | 周: ${quotaData.quotaWeekly}% (点击展开)`,
        children: jsx(PopoverTrigger, {
          asChild: true,
          children: jsxs('button', {
            className: cn(
              'inline-flex h-full items-center gap-1.5 px-2 text-[0.6875rem] font-mono transition-colors select-none cursor-pointer',
              'text-(--ui-text-secondary) hover:bg-(--chrome-action-hover) hover:text-(--foreground)',
              busy && 'text-(--ui-accent) animate-pulse',
              open && 'bg-(--chrome-action-hover) text-(--foreground)'
            ),
            type: 'button',
            onClick: () => haptic?.('tap'),
            children: [
              jsx('span', {
                className: 'text-[0.75rem] mr-0.5 select-none leading-none',
                children: '🔋',
              }),
              jsxs('span', {
                className: 'inline-flex items-baseline gap-0.5',
                children: [
                  jsx('span', {
                    className: 'text-[10px] font-sans font-medium text-(--ui-text-secondary)',
                    children: '5h',
                  }),
                  jsx('span', {
                    className: 'text-[10px] text-(--ui-text-quaternary) font-mono',
                    children: ':',
                  }),
                  jsxs('span', {
                    className: cn('font-mono font-bold tracking-tight', getTextColor(quotaData.quota5h)),
                    children: [quotaData.quota5h, '%'],
                  }),
                ],
              }),
              jsx('span', {
                className: 'text-[10px] text-white/15 select-none font-mono mx-0.5',
                children: '·',
              }),
              jsxs('span', {
                className: 'inline-flex items-baseline gap-0.5',
                children: [
                  jsx('span', {
                    className: 'text-[10px] font-sans font-medium text-(--ui-text-secondary)',
                    children: '周',
                  }),
                  jsx('span', {
                    className: 'text-[10px] text-(--ui-text-quaternary) font-mono',
                    children: ':',
                  }),
                  jsxs('span', {
                    className: cn('font-mono font-bold tracking-tight', getTextColor(quotaData.quotaWeekly)),
                    children: [quotaData.quotaWeekly, '%'],
                  }),
                ],
              }),
            ],
          }),
        }),
      }),

      jsxs(PopoverContent, {
        align: 'end',
        side: 'top',
        sideOffset: 8,
        className: cn(
          'w-88 p-4 rounded-xl border border-(--ui-stroke-secondary) bg-(--ui-bg-elevated) shadow-2xl backdrop-blur-xl',
          'text-(--foreground) font-sans select-none flex flex-col gap-3.5 z-50'
        ),
        children: [
          // 标题行
          jsxs('div', {
            className: 'flex items-center justify-between',
            children: [
              jsxs('div', {
                className: 'flex items-center gap-2',
                children: [
                  jsx('div', {
                    className:
                      'w-2 h-2 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50 animate-pulse',
                  }),
                  jsx('span', {
                    className: 'text-xs font-semibold tracking-wide text-(--ui-text-primary)',
                    children: '模型配额与网关监控',
                  }),
                ],
              }),
              jsxs('div', {
                className: 'flex items-center gap-1.5',
                children: [
                  jsx('span', {
                    className:
                      'px-1.5 py-0.5 text-[0.625rem] font-medium rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
                    children: 'Pro 订阅',
                  }),
                  justUpdated
                    ? jsxs('span', {
                        className:
                          'px-1.5 py-0.5 text-[0.625rem] font-medium rounded-md bg-emerald-500/20 text-emerald-300 flex items-center gap-1 transition-all',
                        children: [
                          jsx('svg', {
                            className: 'w-2.5 h-2.5',
                            fill: 'none',
                            viewBox: '0 0 24 24',
                            stroke: 'currentColor',
                            strokeWidth: 3,
                            children: jsx('path', {
                              strokeLinecap: 'round',
                              strokeLinejoin: 'round',
                              d: 'M5 13l4 4L19 7',
                            }),
                          }),
                          '已刷新',
                        ],
                      })
                    : jsx('button', {
                        type: 'button',
                        disabled: refreshing,
                        onClick: (e) => {
                          e.stopPropagation()
                          haptic?.('tap')
                          fetchLiveQuota(true)
                        },
                        title: '点击强制向官方拉取最新配额',
                        className: cn(
                          'p-1.5 text-(--ui-text-tertiary) hover:text-(--foreground) rounded-md transition-all',
                          'hover:bg-(--chrome-action-hover) active:scale-90 cursor-pointer flex items-center justify-center',
                          refreshing && 'opacity-75 cursor-wait'
                        ),
                        children: jsx('svg', {
                          className: cn(
                            'w-3.5 h-3.5 transition-transform duration-300',
                            refreshing && 'animate-spin text-emerald-400'
                          ),
                          fill: 'none',
                          viewBox: '0 0 24 24',
                          stroke: 'currentColor',
                          strokeWidth: 2,
                          children: jsx('path', {
                            strokeLinecap: 'round',
                            strokeLinejoin: 'round',
                            d: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15',
                          }),
                        }),
                      }),
                ],
              }),
            ],
          }),

          // 账号与直连状态卡
          jsxs('div', {
            className:
              'px-2.5 py-1.5 rounded-lg bg-black/20 border border-white/5 flex items-center justify-between text-[0.6875rem]',
            children: [
              jsx('span', {
                className: 'text-(--ui-text-tertiary) truncate max-w-44 font-mono text-[11px]',
                children: quotaData.account,
              }),
              jsxs('div', {
                className: 'flex items-center gap-1.5 text-[0.625rem]',
                children: [
                  jsx('span', {
                    className: 'text-emerald-400/90 font-mono',
                    children: '● EasyCLIProxy 直连',
                  }),
                  lastSyncTime &&
                    jsxs('span', {
                      className: 'text-(--ui-text-quaternary) font-mono',
                      children: ['(', lastSyncTime, ')'],
                    }),
                ],
              }),
            ],
          }),

          // 配额核心指标区
          jsxs('div', {
            className: 'flex flex-col gap-3 py-1',
            children: [
              // 5 小时额度条
              jsxs('div', {
                className: 'flex flex-col gap-1.5',
                children: [
                  jsxs('div', {
                    className: 'flex items-center justify-between text-xs',
                    children: [
                      jsx('span', {
                        className: 'text-(--ui-text-secondary) font-medium',
                        children: 'Gemini 5h 滚动额度',
                      }),
                      jsxs('span', {
                        className: cn('font-mono font-semibold', getTextColor(quotaData.quota5h)),
                        children: [quotaData.quota5h, '%'],
                      }),
                    ],
                  }),
                  jsx('div', {
                    className: 'h-1.5 w-full rounded-full bg-white/10 overflow-hidden',
                    children: jsx('div', {
                      className: cn(
                        'h-full rounded-full transition-all duration-500',
                        getProgressColor(quotaData.quota5h)
                      ),
                      style: { width: `${Math.min(100, Math.max(0, quotaData.quota5h))}%` },
                    }),
                  }),
                  jsxs('div', {
                    className: 'flex items-center justify-between text-[0.6875rem] text-(--ui-text-tertiary)',
                    children: [
                      jsx('span', { children: '⏳ 重置倒计时' }),
                      jsx('button', {
                        type: 'button',
                        onClick: toggleFormat,
                        title: '点击切换 相对/绝对 显示格式',
                        className: 'font-mono text-zinc-300 hover:text-white cursor-pointer transition-colors',
                        children: formatResetTime(quotaData.reset5h, formatMode),
                      }),
                    ],
                  }),
                ],
              }),

              jsx(Separator, { className: 'bg-white/5 my-0.5' }),

              // 周额度条
              jsxs('div', {
                className: 'flex flex-col gap-1.5',
                children: [
                  jsxs('div', {
                    className: 'flex items-center justify-between text-xs',
                    children: [
                      jsx('span', {
                        className: 'text-(--ui-text-secondary) font-medium',
                        children: 'Gemini 本周总配额',
                      }),
                      jsxs('span', {
                        className: cn('font-mono font-semibold', getTextColor(quotaData.quotaWeekly)),
                        children: [quotaData.quotaWeekly, '%'],
                      }),
                    ],
                  }),
                  jsx('div', {
                    className: 'h-1.5 w-full rounded-full bg-white/10 overflow-hidden',
                    children: jsx('div', {
                      className: cn(
                        'h-full rounded-full transition-all duration-500',
                        getProgressColor(quotaData.quotaWeekly)
                      ),
                      style: { width: `${Math.min(100, Math.max(0, quotaData.quotaWeekly))}%` },
                    }),
                  }),
                  jsxs('div', {
                    className: 'flex items-center justify-between text-[0.6875rem] text-(--ui-text-tertiary)',
                    children: [
                      jsx('span', { children: '⏳ 完全刷新' }),
                      jsx('button', {
                        type: 'button',
                        onClick: toggleFormat,
                        title: '点击切换 相对/绝对 显示格式',
                        className: 'font-mono text-zinc-300 hover:text-white cursor-pointer transition-colors',
                        children: formatResetTime(quotaData.resetWeekly, formatMode),
                      }),
                    ],
                  }),
                ],
              }),

              // 3P 协同池 (Claude / GPT)
              quotaData.claude5h != null &&
                jsxs('div', {
                  className:
                    'mt-0.5 p-2 rounded-lg bg-white/5 border border-white/5 flex items-center justify-between text-[0.6875rem]',
                  children: [
                    jsx('span', {
                      className: 'text-(--ui-text-secondary)',
                      children: '3P (Claude/GPT) 协同池',
                    }),
                    jsxs('div', {
                      className: 'flex items-center gap-2 font-mono',
                      children: [
                        jsxs('span', {
                          className: 'text-emerald-400',
                          children: ['5h: ', quotaData.claude5h, '%'],
                        }),
                        jsx('span', { className: 'text-white/20', children: '|' }),
                        jsxs('span', {
                          className: 'text-emerald-400',
                          children: ['周: ', quotaData.claudeWeekly, '%'],
                        }),
                      ],
                    }),
                  ],
                }),

              // WorkBuddy 网关探测简卡（含账号与积分）
              jsxs('div', {
                className: 'p-2.5 rounded-lg bg-black/25 border border-white/5 flex flex-col gap-1.5 text-[0.6875rem]',
                children: [
                  // 第一行：状态与名称
                  jsxs('div', {
                    className: 'flex items-center justify-between',
                    children: [
                      jsxs('div', {
                        className: 'flex items-center gap-1.5',
                        children: [
                          jsx('span', {
                            className: cn(
                              'w-1.5 h-1.5 rounded-full',
                              quotaData.workbuddy.status === 'online' ? 'bg-emerald-400' : 'bg-zinc-500'
                            ),
                          }),
                          jsx('span', {
                            className: 'text-(--ui-text-secondary)',
                            children: 'WorkBuddy (8787)',
                          }),
                        ],
                      }),
                      jsx('span', {
                        className: cn(
                          'font-mono text-[10px] px-1.5 py-0.5 rounded',
                          quotaData.workbuddy.status === 'online'
                            ? 'bg-emerald-500/15 text-emerald-300'
                            : 'bg-zinc-800 text-zinc-400'
                        ),
                        children: quotaData.workbuddy.statusLabel || '待机中',
                      }),
                    ],
                  }),

                  // 第二行：账号与积分（在线且有数据时显示）
                  quotaData.workbuddy.status === 'online' &&
                    quotaData.workbuddy.usage &&
                    jsxs('div', {
                      className: 'flex flex-col gap-1 pt-0.5',
                      children: [
                        // 账号昵称 + 积分余量
                        jsxs('div', {
                          className: 'flex items-center justify-between',
                          children: [
                            jsxs('span', {
                              className: 'text-(--ui-text-tertiary)',
                              children: [
                                '👤 ',
                                quotaData.workbuddy.usage.nickname || '—',
                                quotaData.workbuddy.usage.isPaidUser ? '' : ' (免费版)',
                              ],
                            }),
                            jsxs('span', {
                              className: cn(
                                'font-mono font-bold tracking-tight',
                                getTextColor(quotaData.workbuddy.usage.remainPercent)
                              ),
                              children: [
                                Math.round(quotaData.workbuddy.usage.remain),
                                ' / ',
                                Math.round(quotaData.workbuddy.usage.total),
                                ' credits',
                              ],
                            }),
                          ],
                        }),

                        // 积分进度条
                        jsx('div', {
                          className: 'h-1 w-full rounded-full bg-white/10 overflow-hidden',
                          children: jsx('div', {
                            className: cn(
                              'h-full rounded-full transition-all duration-500',
                              getProgressColor(quotaData.workbuddy.usage.remainPercent)
                            ),
                            style: {
                              width: `${Math.min(100, Math.max(0, quotaData.workbuddy.usage.remainPercent))}%`,
                            },
                          }),
                        }),
                      ],
                    }),

                  // 积分查询失败提示
                  quotaData.workbuddy.status === 'online' &&
                    quotaData.workbuddy.usageError &&
                    jsx('div', {
                      className: 'text-[0.625rem] text-amber-400/80 pt-0.5',
                      children: `⚠️ ${quotaData.workbuddy.usageError}`,
                    }),
                ],
              }),
            ],
          }),

          jsx(Separator, { className: 'bg-white/5' }),

          // 底部导航直达按钮
          jsxs('div', {
            className: 'flex items-center justify-between pt-0.5',
            children: [
              jsx('button', {
                type: 'button',
                onClick: toggleFormat,
                className: 'text-[0.625rem] text-(--ui-text-tertiary) hover:text-(--foreground) transition-colors cursor-pointer',
                children: `时间格式: ${formatMode === 'relative' ? '倒计时' : '绝对时刻'}`,
              }),
              jsxs('button', {
                type: 'button',
                onClick: () => {
                  setOpen(false)
                  haptic?.('tap')
                  host.navigate('/quota')
                },
                className:
                  'inline-flex items-center gap-1 text-[0.6875rem] font-medium text-emerald-400 hover:text-emerald-300 transition-colors cursor-pointer',
                children: [
                  '全景看板',
                  jsx('span', { className: 'text-[0.75rem]', children: '➔' }),
                ],
              }),
            ],
          }),
        ],
      }),
    ],
  })
}

// ==================== 侧边栏独立全景看板页面 ====================

function QuotaPage({ ctx }) {
  const [refreshing, setRefreshing] = useState(false)
  const [lastSyncTime, setLastSyncTime] = useState('')
  const [formatMode, setFormatMode] = useState(() => {
    try {
      return (ctx && ctx.storage && ctx.storage.get(STORAGE_KEY_FORMAT)) || 'relative'
    } catch {
      return 'relative'
    }
  })

  const [data, setData] = useState({
    quota5h: 100,
    quotaWeekly: 100,
    reset5h: null,
    resetWeekly: null,
    source: 'Google 官方直连 (EasyCLIProxyAPI)',
    plan: 'Google AI Pro',
    account: '...',
    claude5h: 100,
    claudeWeekly: 100,
    workbuddy: { status: 'offline', statusLabel: '未启动', note: '本地反代服务待机中 (端口 8787)' },
  })

  const toggleFormat = () => {
    const next = formatMode === 'relative' ? 'absolute' : 'relative'
    setFormatMode(next)
    try {
      if (ctx && ctx.storage) ctx.storage.set(STORAGE_KEY_FORMAT, next)
    } catch {}
    haptic?.('tap')
  }

  const loadData = async (isManual = false) => {
    try {
      setRefreshing(true)
      const path = isManual ? '/quota?force=1' : '/quota'
      const rest = (ctx && ctx.rest) || (pluginCtx && pluginCtx.rest)
      if (!rest) return
      const res = await rest.call(ctx || pluginCtx, path)
      if (res && res.status === 'ok') {
        setData({
          quota5h: res.quota5h != null ? Math.round(res.quota5h * 10) / 10 : 100,
          quotaWeekly: res.quotaWeekly != null ? Math.round(res.quotaWeekly * 10) / 10 : 100,
          reset5h: res.reset5h,
          resetWeekly: res.resetWeekly,
          source: res.source || 'Google 官方直连 (EasyCLIProxyAPI)',
          plan: res.plan || 'Google AI Pro',
          account: res.account || '...',
          claude5h: res.claudeQuota5h != null ? Math.round(res.claudeQuota5h) : 100,
          claudeWeekly: res.claudeQuotaWeekly != null ? Math.round(res.claudeQuotaWeekly) : 100,
          workbuddy: res.workbuddy || { status: 'offline', statusLabel: '未启动', note: '本地反代服务待机中' },
        })
        const sync =
          res.updatedAtLocal ||
          new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        setLastSyncTime(sync)
        if (isManual) {
          haptic?.('success') || haptic?.('tap')
          host.notify({
            kind: 'info',
            message: `✅ 模型配额已强制同步 (${sync})`,
          })
        }
      }
    } catch {
      if (isManual) {
        host.notify({ kind: 'error', message: '获取配额失败，请确认 Hermes 后端服务正常' })
      }
    } finally {
      setTimeout(() => setRefreshing(false), 500)
    }
  }

  useEffect(() => {
    loadData()
    const timer = setInterval(() => loadData(false), 15000)
    return () => clearInterval(timer)
  }, [])

  return jsxs('div', {
    className: 'h-full overflow-y-auto p-6 md:p-8 flex flex-col gap-6 max-w-5xl mx-auto text-(--foreground) font-sans select-none',
    children: [
      // 头部
      jsxs('div', {
        className: 'flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-5',
        children: [
          jsxs('div', {
            className: 'flex flex-col gap-1',
            children: [
              jsxs('div', {
                className: 'flex items-center gap-2.5',
                children: [
                  jsx('span', { className: 'text-2xl', children: '⚡' }),
                  jsx('h1', {
                    className: 'text-xl font-bold tracking-tight text-(--foreground)',
                    children: '模型配额与网关监控',
                  }),
                  jsx('span', {
                    className: 'px-2 py-0.5 text-xs font-mono rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
                    children: 'Live Quota',
                  }),
                ],
              }),
              jsx('p', {
                className: 'text-xs text-(--ui-text-secondary)',
                children: '实时监控 Google / Antigravity 官方高阶额度池与本地 WorkBuddy 推理网关状态',
              }),
            ],
          }),

          // 右侧操作
          jsxs('div', {
            className: 'flex items-center gap-3',
            children: [
              lastSyncTime &&
                jsxs('span', {
                  className: 'text-xs font-mono text-(--ui-text-tertiary)',
                  children: ['同步时间: ', lastSyncTime],
                }),
              jsxs('button', {
                type: 'button',
                disabled: refreshing,
                onClick: () => loadData(true),
                className: cn(
                  'px-3.5 py-1.5 rounded-lg bg-(--ui-bg-elevated) hover:bg-(--chrome-action-hover) border border-(--ui-stroke-secondary)',
                  'text-xs font-medium text-(--foreground) transition-all flex items-center gap-2 cursor-pointer active:scale-95 shadow-sm',
                  refreshing && 'opacity-60 cursor-wait'
                ),
                children: [
                  jsx('svg', {
                    className: cn('w-3.5 h-3.5 text-emerald-400', refreshing && 'animate-spin'),
                    fill: 'none',
                    viewBox: '0 0 24 24',
                    stroke: 'currentColor',
                    strokeWidth: 2,
                    children: jsx('path', {
                      strokeLinecap: 'round',
                      strokeLinejoin: 'round',
                      d: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15',
                    }),
                  }),
                  '立即刷新',
                ],
              }),
            ],
          }),
        ],
      }),

      // 主卡片 1：Google AI Pro (Antigravity 官方凭据通道)
      jsxs('div', {
        className: 'rounded-2xl border border-(--ui-stroke-secondary) bg-(--ui-bg-elevated) p-6 shadow-xl flex flex-col gap-5',
        children: [
          // 卡片头
          jsxs('div', {
            className: 'flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/5 pb-4',
            children: [
              jsxs('div', {
                className: 'flex items-center gap-3',
                children: [
                  jsx('div', {
                    className: 'w-8 h-8 rounded-xl bg-gradient-to-br from-blue-500/20 to-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-base',
                    children: '✨',
                  }),
                  jsxs('div', {
                    children: [
                      jsxs('div', {
                        className: 'flex items-center gap-2',
                        children: [
                          jsx('h2', {
                            className: 'text-sm font-semibold text-(--foreground)',
                            children: 'Google AI (Antigravity 官方直连)',
                          }),
                          jsx('span', {
                            className: 'px-2 py-0.5 text-[10px] font-mono font-medium rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/20',
                            children: data.plan,
                          }),
                        ],
                      }),
                      jsx('p', {
                        className: 'text-xs font-mono text-(--ui-text-tertiary)',
                        children: data.account,
                      }),
                    ],
                  }),
                ],
              }),
              jsxs('div', {
                className: 'flex items-center gap-2 text-xs font-mono text-(--ui-text-secondary)',
                children: [
                  jsx('span', { className: 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse' }),
                  'EasyCLIProxyAPI 官方核心 (18080)',
                ],
              }),
            ],
          }),

          // 核心两列指标：5h 与 每周总配额
          jsxs('div', {
            className: 'grid grid-cols-1 md:grid-cols-2 gap-4',
            children: [
              // 5 小时卡
              jsxs('div', {
                className: 'p-4 rounded-xl bg-black/20 border border-white/5 flex flex-col gap-3',
                children: [
                  jsxs('div', {
                    className: 'flex items-center justify-between',
                    children: [
                      jsx('span', { className: 'text-xs text-(--ui-text-secondary) font-medium', children: 'Gemini 5h 滚动额度' }),
                      jsxs('span', {
                        className: cn('font-mono text-2xl font-bold tracking-tight', getTextColor(data.quota5h)),
                        children: [data.quota5h, '%'],
                      }),
                    ],
                  }),
                  jsx('div', {
                    className: 'h-2 w-full rounded-full bg-white/10 overflow-hidden',
                    children: jsx('div', {
                      className: cn('h-full rounded-full transition-all duration-500', getProgressColor(data.quota5h)),
                      style: { width: `${Math.min(100, Math.max(0, data.quota5h))}%` },
                    }),
                  }),
                  jsxs('div', {
                    className: 'flex items-center justify-between text-xs text-(--ui-text-tertiary)',
                    children: [
                      jsx('span', { children: '⏳ 重置时间' }),
                      jsx('button', {
                        type: 'button',
                        onClick: toggleFormat,
                        className: 'font-mono text-zinc-300 hover:text-white transition-colors cursor-pointer',
                        title: '点击切换 相对倒计时 / 绝对具体时刻',
                        children: formatResetTime(data.reset5h, formatMode),
                      }),
                    ],
                  }),
                ],
              }),

              // 每周总配额卡
              jsxs('div', {
                className: 'p-4 rounded-xl bg-black/20 border border-white/5 flex flex-col gap-3',
                children: [
                  jsxs('div', {
                    className: 'flex items-center justify-between',
                    children: [
                      jsx('span', { className: 'text-xs text-(--ui-text-secondary) font-medium', children: 'Gemini 每周总配额' }),
                      jsxs('span', {
                        className: cn('font-mono text-2xl font-bold tracking-tight', getTextColor(data.quotaWeekly)),
                        children: [data.quotaWeekly, '%'],
                      }),
                    ],
                  }),
                  jsx('div', {
                    className: 'h-2 w-full rounded-full bg-white/10 overflow-hidden',
                    children: jsx('div', {
                      className: cn('h-full rounded-full transition-all duration-500', getProgressColor(data.quotaWeekly)),
                      style: { width: `${Math.min(100, Math.max(0, data.quotaWeekly))}%` },
                    }),
                  }),
                  jsxs('div', {
                    className: 'flex items-center justify-between text-xs text-(--ui-text-tertiary)',
                    children: [
                      jsx('span', { children: '⏳ 周期完全刷新' }),
                      jsx('button', {
                        type: 'button',
                        onClick: toggleFormat,
                        className: 'font-mono text-zinc-300 hover:text-white transition-colors cursor-pointer',
                        title: '点击切换 相对倒计时 / 绝对具体时刻',
                        children: formatResetTime(data.resetWeekly, formatMode),
                      }),
                    ],
                  }),
                ],
              }),
            ],
          }),

          // 3P 协同模型池
          data.claude5h != null &&
            jsxs('div', {
              className: 'p-3 rounded-xl bg-white/5 border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs',
              children: [
                jsxs('div', {
                  className: 'flex items-center gap-2',
                  children: [
                    jsx('span', { className: 'text-(--ui-text-secondary) font-medium', children: '3P (Claude/GPT) 协同通道' }),
                    jsx('span', { className: 'text-[10px] text-(--ui-text-tertiary)', children: '(按 Pro 订阅共享配额)' }),
                  ],
                }),
                jsxs('div', {
                  className: 'flex items-center gap-3 font-mono font-medium',
                  children: [
                    jsxs('span', { className: 'text-emerald-400', children: ['5h 额度: ', data.claude5h, '%'] }),
                    jsx('span', { className: 'text-white/20', children: '|' }),
                    jsxs('span', { className: 'text-emerald-400', children: ['周额度: ', data.claudeWeekly, '%'] }),
                  ],
                }),
              ],
            }),
        ],
      }),

      // 主卡片 2：WorkBuddy (codebuddy2openai 本地网关)
      jsxs('div', {
        className: 'rounded-2xl border border-(--ui-stroke-secondary) bg-(--ui-bg-elevated) p-6 shadow-xl flex flex-col gap-4',
        children: [
          jsxs('div', {
            className: 'flex flex-col sm:flex-row sm:items-center justify-between gap-2',
            children: [
              jsxs('div', {
                className: 'flex items-center gap-3',
                children: [
                  jsx('div', {
                    className: 'w-8 h-8 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-base',
                    children: '🤖',
                  }),
                  jsxs('div', {
                    children: [
                      jsx('h2', {
                        className: 'text-sm font-semibold text-(--foreground)',
                        children: 'WorkBuddy (codebuddy2openai 本地反代)',
                      }),
                      jsx('p', {
                        className: 'text-xs font-mono text-(--ui-text-tertiary)',
                        children: data.workbuddy.endpoint || 'http://127.0.0.1:8787/v1',
                      }),
                    ],
                  }),
                ],
              }),

              jsxs('div', {
                className: 'flex items-center gap-2',
                children: [
                  jsx('span', {
                    className: cn(
                      'px-2.5 py-1 text-xs font-mono font-semibold rounded-lg border',
                      data.workbuddy.status === 'online'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : 'bg-zinc-800 text-zinc-400 border-white/5'
                    ),
                    children: data.workbuddy.statusLabel || '未启动',
                  }),
                ],
              }),
            ],
          }),

          // 积分概览行（在线且数据可得时显示）
          data.workbuddy.status === 'online' &&
            data.workbuddy.usage &&
            jsxs('div', {
              className: 'p-4 rounded-xl bg-black/20 border border-white/5 flex flex-col gap-3',
              children: [
                // 账号与余量
                jsxs('div', {
                  className: 'flex items-center justify-between',
                  children: [
                    jsxs('span', {
                      className: 'text-xs text-(--ui-text-secondary)',
                      children: [
                        '👤 当前账号: ',
                        jsx('span', { className: 'font-mono text-(--foreground)', children: data.workbuddy.usage.nickname || '—' }),
                        jsx('span', {
                          className: 'ml-1.5 px-1.5 py-0.5 text-[10px] rounded bg-white/5 text-(--ui-text-tertiary)',
                          children: data.workbuddy.usage.isPaidUser ? '付费版' : '免费版',
                        }),
                      ],
                    }),
                    jsxs('span', {
                      className: cn('font-mono text-lg font-bold tracking-tight', getTextColor(data.workbuddy.usage.remainPercent)),
                      children: [
                        data.workbuddy.usage.remain != null ? data.workbuddy.usage.remain.toFixed(1) : '—',
                        jsx('span', { className: 'text-xs text-(--ui-text-tertiary) font-normal', children: ' / ' }),
                        Math.round(data.workbuddy.usage.total || 0),
                        ' credits',
                      ],
                    }),
                  ],
                }),

                // 进度条
                jsx('div', {
                  className: 'h-2 w-full rounded-full bg-white/10 overflow-hidden',
                  children: jsx('div', {
                    className: cn('h-full rounded-full transition-all duration-500', getProgressColor(data.workbuddy.usage.remainPercent)),
                    style: { width: `${Math.min(100, Math.max(0, data.workbuddy.usage.remainPercent || 0))}%` },
                  }),
                }),

                // 积分包明细
                (data.workbuddy.usage.packages || []).length > 0 &&
                  jsxs('div', {
                    className: 'flex flex-col gap-1 pt-1 border-t border-white/5',
                    children: [
                      jsx('span', { className: 'text-[10px] text-(--ui-text-tertiary) pt-1', children: '积分包明细' }),
                      ...data.workbuddy.usage.packages.map((p, i) =>
                        jsxs('div', {
                          className: 'flex items-center justify-between text-[11px] font-mono',
                          children: [
                            jsx('span', { className: 'text-(--ui-text-tertiary)', children: `包 #${i + 1} (…${String(p.code || '').slice(-6)})` }),
                            jsxs('span', {
                              className: cn(
                                getTextColor(p.total > 0 ? (p.remain / p.total) * 100 : 0)
                              ),
                              children: [
                                (p.remain || 0).toFixed(0),
                                ' / ',
                                (p.total || 0).toFixed(0),
                                ` ${p.unit || 'credits'}`,
                              ],
                            }),
                          ],
                        }, i)
                      ),
                    ],
                  }),
              ],
            }),

          jsxs('div', {
            className: 'px-4 py-3 rounded-xl bg-black/20 border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs',
            children: [
              jsx('span', {
                className: 'text-(--ui-text-secondary)',
                children: data.workbuddy.note || '本地反代服务待机中 (端口 8787)',
              }),
              jsx('span', {
                className: 'text-[11px] text-(--ui-text-tertiary) font-mono',
                children: 'Tauri v2 架构 · 28 官方模型矩阵 · 纯净倍率',
              }),
            ],
          }),
        ],
      }),

      // 主卡片 3：显示偏好与架构规范
      jsxs('div', {
        className: 'rounded-2xl border border-(--ui-stroke-secondary) bg-(--ui-bg-elevated) p-6 shadow-xl flex flex-col gap-4',
        children: [
          jsx('h3', { className: 'text-sm font-semibold text-(--foreground)', children: '⚙️ 偏好与系统架构' }),
          jsxs('div', {
            className: 'grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs',
            children: [
              jsxs('div', {
                className: 'p-3.5 rounded-xl bg-black/20 border border-white/5 flex items-center justify-between',
                children: [
                  jsxs('div', {
                    className: 'flex flex-col gap-0.5',
                    children: [
                      jsx('span', { className: 'text-(--foreground) font-medium', children: '倒计时时间格式' }),
                      jsx('span', { className: 'text-[11px] text-(--ui-text-tertiary)', children: '控制所有重置时间以相对倒计时或绝对时刻展示' }),
                    ],
                  }),
                  jsx('button', {
                    type: 'button',
                    onClick: toggleFormat,
                    className: 'px-2.5 py-1 rounded bg-white/10 hover:bg-white/15 text-xs font-mono text-emerald-400 cursor-pointer transition-colors',
                    children: formatMode === 'relative' ? '相对倒计时' : '绝对时刻',
                  }),
                ],
              }),

              jsxs('div', {
                className: 'p-3.5 rounded-xl bg-black/20 border border-white/5 flex items-center justify-between',
                children: [
                  jsxs('div', {
                    className: 'flex flex-col gap-0.5',
                    children: [
                      jsx('span', { className: 'text-(--foreground) font-medium', children: '架构模式' }),
                      jsx('span', { className: 'text-[11px] text-(--ui-text-tertiary)', children: 'FastAPI 内置用户插件路由 (/api/plugins/token-stats)' }),
                    ],
                  }),
                  jsx('span', {
                    className: 'px-2 py-0.5 rounded bg-emerald-500/10 text-[11px] font-mono text-emerald-400 border border-emerald-500/20',
                    children: '零进程派生',
                  }),
                ],
              }),
            ],
          }),
          jsx('p', {
            className: 'text-[11px] text-(--ui-text-tertiary) leading-relaxed',
            children: '💡 提示：本插件采用 Hermes 官方内嵌插件体系，随 Hermes 桌面端后端自动启闭，不依赖外部 18088 独立微服务与计划任务。会话 Token 速率与上下文容量由 Hermes 原生状态栏托管。可在终端任意会话中输入 /quota 查看实时配额报告。',
          }),
        ],
      }),
    ],
  })
}

// ==================== 插件注册入口 ====================

export default {
  id: ID,
  name: 'Antigravity Quota Monitor',
  register(ctx) {
    pluginCtx = ctx

    // 1. 状态栏右侧 Chip
    ctx.register({
      id: 'chip',
      area: 'statusBar.right',
      order: 10,
      render: () => jsx(AntigravityQuotaChip, { ctx }),
    })

    // 2. 独立配额看板路由页面 (/quota)
    ctx.register({
      id: 'page',
      area: ROUTES_AREA,
      data: { path: '/quota' },
      render: () => jsx(QuotaPage, { ctx }),
    })

    // 3. 左侧导航栏 Pulse 入口
    ctx.register({
      id: 'nav',
      area: SIDEBAR_NAV_AREA,
      order: 80,
      data: {
        path: '/quota',
        label: '配额',
        codicon: 'pulse',
      },
    })

    // 4. 命令面板 (Cmd/Ctrl + K)
    ctx.register({
      id: 'open',
      area: PALETTE_AREA,
      data: {
        id: 'quota.open',
        label: 'Quota: 查看模型配额看板',
        keywords: ['quota', 'tokens', 'antigravity', 'gemini', 'workbuddy'],
        run: () => host.navigate('/quota'),
      },
    })
  },
}
