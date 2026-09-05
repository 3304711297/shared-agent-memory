/**
 * Hermes Desktop Plugin: antigravity-quota
 * 现代化极简奢华 UI 看板：实时监控 Google / Antigravity 官方配额及精确重置倒计时。
 * 遵循 Hermes 设计规范与现代前端美学标准，彻底消除锯齿文本与生硬折行。
 * 支持手动强制穿透刷新（带高响应动画、完成反馈与精确时间戳）。
 */

import {
  cn,
  haptic,
  host,
  Popover,
  PopoverContent,
  PopoverTrigger,
  Separator,
  Tip,
  useValue,
} from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'
import { useEffect, useState } from 'react'

const ID = 'token-stats'

// Plugin context captured at register() — the door to ctx.rest (the namespace-
// scoped REST path to the token-stats backend router inside the Hermes process).
let pluginCtx = null

function formatResetTime(isoString) {
  if (!isoString) return '--'
  try {
    const target = new Date(isoString).getTime()
    const now = Date.now()
    const diff = target - now
    if (diff <= 0) return '即将刷新'

    const totalMinutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(totalMinutes / 60)
    const minutes = totalMinutes % 60
    const days = Math.floor(hours / 24)
    const remainHours = hours % 24

    if (days > 0) {
      const dt = new Date(isoString)
      const m = String(dt.getMonth() + 1).padStart(2, '0')
      const d = String(dt.getDate()).padStart(2, '0')
      const hm = dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      return `${days}天 ${remainHours}小时后 (${m}/${d} ${hm})`
    }
    if (hours > 0) {
      const hm = new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      return `${hours}小时 ${minutes}分钟后 (${hm})`
    }
    const hm = new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
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

function AntigravityQuotaChip({ ctx }) {
  const busy = useValue(host.state.busy)
  const [open, setOpen] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [justUpdated, setJustUpdated] = useState(false)
  const [lastSyncTime, setLastSyncTime] = useState('')

  const [quotaData, setQuotaData] = useState({
    quota5h: 100,
    quotaWeekly: 43,
    reset5h: null,
    resetWeekly: null,
    source: 'Google 官方直连',
    plan: 'Google AI Pro',
    account: 'jimygod114514@gmail.com',
    claude5h: 100,
    claudeWeekly: 100,
  })

  const fetchLiveQuota = async (isManual = false) => {
    try {
      setRefreshing(true)
      const path = isManual ? '/quota?force=1' : '/quota'
      const rest = (ctx && ctx.rest) || (pluginCtx && pluginCtx.rest)
      if (!rest) throw new Error('plugin context unavailable')
      const data = await rest.call(ctx || pluginCtx, path)
      if (data && data.status === 'ok') {
        setQuotaData({
          quota5h: data.quota5h != null ? Math.round(data.quota5h) : 100,
          quotaWeekly: data.quotaWeekly != null ? Math.round(data.quotaWeekly) : 100,
          reset5h: data.reset5h,
          resetWeekly: data.resetWeekly,
          source: data.source || 'Google 官方直连 (EasyCLIProxyAPI)',
          plan: data.plan || 'Google AI Pro',
          account: data.account || 'jimygod114514@gmail.com',
          claude5h: data.claudeQuota5h != null ? Math.round(data.claudeQuota5h) : 100,
          claudeWeekly: data.claudeQuotaWeekly != null ? Math.round(data.claudeQuotaWeekly) : 100,
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
            message: `✅ Google 官方配额已同步 (同步于 ${syncTime})`,
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
              // 5h 维度
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
              // 维度分隔符
              jsx('span', {
                className: 'text-[10px] text-white/15 select-none font-mono mx-0.5',
                children: '·',
              }),
              // 周 维度
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
          'w-84 p-4 rounded-xl border border-(--ui-stroke-secondary) bg-(--ui-bg-elevated) shadow-2xl backdrop-blur-xl',
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
                    children: 'Google 官方配额看板',
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
                        title: '点击强制向 Google 官方拉取最新配额',
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

          // 账号信息卡
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
                      jsx('span', {
                        className: 'font-mono text-zinc-300',
                        children: formatResetTime(quotaData.reset5h),
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
                      jsx('span', {
                        className: 'font-mono text-zinc-300',
                        children: formatResetTime(quotaData.resetWeekly),
                      }),
                    ],
                  }),
                ],
              }),

              // 第三方模型池 (Claude / GPT)
              quotaData.claude5h != null &&
                jsxs('div', {
                  className:
                    'mt-1 p-2 rounded-lg bg-white/5 border border-white/5 flex items-center justify-between text-[0.6875rem]',
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
                          children: ['5h:', quotaData.claude5h, '%'],
                        }),
                        jsx('span', { className: 'text-white/20', children: '|' }),
                        jsxs('span', {
                          className: 'text-emerald-400',
                          children: ['周:', quotaData.claudeWeekly, '%'],
                        }),
                      ],
                    }),
                  ],
                }),
            ],
          }),

          jsx(Separator, { className: 'bg-white/5' }),

          // 底部提示
          jsx('div', {
            className: 'text-[0.625rem] text-(--ui-text-tertiary) leading-tight',
            children: '💡 提示：会话上下文容量、生成速率与缓存命中率已由 Hermes 原生状态栏托管。',
          }),
        ],
      }),
    ],
  })
}

export default {
  id: ID,
  name: 'Antigravity Quota Monitor',
  register(ctx) {
    pluginCtx = ctx
    ctx.register({
      id: 'chip',
      area: 'statusBar.right',
      order: 10,
      render: () => jsx(AntigravityQuotaChip, { ctx }),
    })
  },
}
