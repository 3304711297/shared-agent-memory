/**
 * Hermes Desktop Plugin: antigravity-quota
 * 实时监控 Google / Antigravity 官方配额及重置倒计时（5h 重置点 / 每周完全刷新时间）。
 * 已全面升级适配 EasyCLIProxyAPI 架构，通过本地微服务直连 Google 官方配额 API。
 */

import { cn, haptic, host, Tip, useValue } from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'
import { useEffect, useState } from 'react'

const ID = 'token-stats'

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
      return `${days}天 ${remainHours}小时后 (${new Date(isoString).toLocaleDateString([], { month: '2-digit', day: '2-digit' })} ${new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })})`
    }
    if (hours > 0) {
      return `${hours}小时 ${minutes}分钟后 (${new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })})`
    }
    return `${minutes}分钟后 (${new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })})`
  } catch {
    return isoString
  }
}

function AntigravityQuotaChip() {
  const busy = useValue(host.state.busy)

  const [quotaData, setQuotaData] = useState({
    quota5h: 100,
    quotaWeekly: 43,
    reset5h: null,
    resetWeekly: null,
    source: 'Google 官方直连 (EasyCLIProxyAPI)',
    plan: 'Google AI Pro',
    account: 'jimygod114514@gmail.com',
    claude5h: 100,
    claudeWeekly: 100,
  })

  useEffect(() => {
    let timer = null

    const fetchLiveQuota = async () => {
      try {
        const res = await fetch('http://127.0.0.1:18088/quota')
        if (res.ok) {
          const data = await res.json()
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
          }
        }
      } catch (err) {
        // 本地服务短时重试中，保持上次已知数值
      }
    }

    fetchLiveQuota()
    timer = setInterval(fetchLiveQuota, 10000)
    return () => clearInterval(timer)
  }, [])

  const tipLines = [
    `🔋 【Google 官方实时额度看板】`,
    `────────────────────────`,
    `• Gemini 5h 剩余额度: ${quotaData.quota5h}%`,
    `  ⏳ 5h 重置倒计时: ${formatResetTime(quotaData.reset5h)}`,
    ``,
    `• Gemini 本周剩余额度: ${quotaData.quotaWeekly}%`,
    `  ⏳ 本周完全刷新: ${formatResetTime(quotaData.resetWeekly)}`,
    quotaData.claude5h != null ? [
      ``,
      `• 3P (Claude/GPT) 5h: ${quotaData.claude5h}%`,
      `• 3P (Claude/GPT) 周: ${quotaData.claudeWeekly}%`
    ].join('\n') : null,
    `────────────────────────`,
    `• 账号类型: ${quotaData.plan}`,
    `• 授权账号: ${quotaData.account}`,
    `• 数据通道: ${quotaData.source}`,
    `────────────────────────`,
    `💡 提示: 上下文容量、速率及缓存命中率已由 Hermes 原生状态栏托管。`
  ].filter(Boolean).join('\n')

  return jsx(Tip, {
    label: tipLines,
    children: jsxs('button', {
      className: cn(
        'inline-flex h-full items-center gap-1.5 px-2 text-[0.6875rem] font-mono transition-colors select-none',
        'text-(--ui-text-secondary) hover:bg-(--chrome-action-hover) hover:text-(--foreground)',
        busy && 'text-(--ui-accent) animate-pulse'
      ),
      type: 'button',
      onClick: () => {
        haptic?.('tap')
        host.notify({
          kind: 'info',
          message: `Gemini 5h额度: ${quotaData.quota5h}% (重置: ${formatResetTime(quotaData.reset5h)}) | 周额度: ${quotaData.quotaWeekly}% | 账号: ${quotaData.account}`
        })
      },
      children: [
        jsx('span', {
          className: 'text-emerald-500 font-semibold',
          children: `🔋 5h:${quotaData.quota5h}%`
        }),
        jsxs('span', {
          className: 'text-(--ui-text-secondary)',
          children: ['周:', quotaData.quotaWeekly, '%']
        })
      ]
    })
  })
}

export default {
  id: ID,
  name: 'Antigravity Quota Monitor',
  register(ctx) {
    ctx.register({
      id: 'chip',
      area: 'statusBar.right',
      order: 10,
      render: () => jsx(AntigravityQuotaChip, {})
    })
  }
}
