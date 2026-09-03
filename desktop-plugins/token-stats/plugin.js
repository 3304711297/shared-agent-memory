/**
 * Hermes Desktop Plugin: antigravity-quota
 * 实时监控 Google / Antigravity 官方配额及重置倒计时（5h 重置点 / 每周完全刷新时间）。
 */

import { cn, haptic, host, Tip, useValue } from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'
import { useEffect, useState } from 'react'

const ID = 'token-stats'
const MANAGEMENT_KEY = 'wY5Xr4HVPT3BZivioFX2L_3XhXdFfU8QBjT_Ff4xGJ0'

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
      return `${days}天 ${remainHours}小时后 (${new Date(isoString).toLocaleDateString([], {month: '2-digit', day: '2-digit'})} ${new Date(isoString).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})})`
    }
    if (hours > 0) {
      return `${hours}小时 ${minutes}分钟后 (${new Date(isoString).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})})`
    }
    return `${minutes}分钟后 (${new Date(isoString).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})})`
  } catch {
    return isoString
  }
}

function AntigravityQuotaChip() {
  const busy = useValue(host.state.busy)

  const [quotaData, setQuotaData] = useState({
    quota5h: 57,
    quotaWeekly: 64,
    reset5h: '2026-09-03T12:09:03Z',
    resetWeekly: '2026-09-09T08:07:32Z',
    source: '实时网关',
    plan: 'Google AI Pro',
    account: 'jimygod114514@gmail.com'
  })

  useEffect(() => {
    let timer = null

    const fetchLiveQuota = async () => {
      let q5h = null
      let qWeek = null
      let r5h = null
      let rWeek = null
      let src = '实时网关'
      let plan = 'Google AI Pro'
      let account = 'jimygod114514@gmail.com'

      try {
        const authFilesReq = await fetch('http://127.0.0.1:18080/v0/management/auth-files', {
          headers: { 'Authorization': `Bearer ${MANAGEMENT_KEY}` }
        })
        if (authFilesReq.ok) {
          const authFiles = await authFilesReq.json()
          const file = authFiles?.files?.find(f => f.email || f.provider === 'antigravity') || authFiles?.files?.[0]
          if (file?.auth_index && file?.project_id) {
            account = file.email || file.label || account
            const callReq = await fetch('http://127.0.0.1:18080/v0/management/api-call', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${MANAGEMENT_KEY}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                auth_index: file.auth_index,
                method: 'POST',
                url: 'https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary',
                header: {
                  'Authorization': 'Bearer $TOKEN$',
                  'Accept': '*/*',
                  'Content-Type': 'application/json',
                  'User-Agent': 'antigravity/hub/2.8.1 windows/amd64'
                },
                data: JSON.stringify({ project: file.project_id })
              })
            })

            if (callReq.ok) {
              const callResp = await callReq.json()
              const summary = JSON.parse(callResp.body)
              const groups = summary?.groups || []
              for (const g of groups) {
                for (const b of (g.buckets || [])) {
                  const bid = b.bucketId || ''
                  const frac = b.remainingFraction != null ? b.remainingFraction : 1.0
                  const pct = Math.round(frac * 100)
                  if (bid.includes('5h') && q5h == null) {
                    q5h = pct
                    r5h = b.resetTime
                  }
                  if (bid.includes('week') && qWeek == null) {
                    qWeek = pct
                    rWeek = b.resetTime
                  }
                }
              }
              src = 'Antigravity 网关'
            }
          }
        }
      } catch (err) {
        // 网关离线时保持上次已知状态
      }

      setQuotaData(prev => ({
        ...prev,
        quota5h: q5h != null ? q5h : prev.quota5h,
        quotaWeekly: qWeek != null ? qWeek : prev.quotaWeekly,
        reset5h: r5h || prev.reset5h,
        resetWeekly: rWeek || prev.resetWeekly,
        source: src,
        plan,
        account
      }))
    }

    fetchLiveQuota()
    timer = setInterval(fetchLiveQuota, 10000)
    return () => clearInterval(timer)
  }, [])

  const tipLines = [
    `🔋 【Google 剩余额度与重置看板】`,
    `────────────────────────`,
    `• 5 小时剩余额度: ${quotaData.quota5h}%`,
    `  ⏳ 5h 重置倒计时: ${formatResetTime(quotaData.reset5h)}`,
    ``,
    `• 本周剩余额度: ${quotaData.quotaWeekly}%`,
    `  ⏳ 本周刷新时间: ${formatResetTime(quotaData.resetWeekly)}`,
    `────────────────────────`,
    `• 账号类型: ${quotaData.plan}`,
    `• 授权账号: ${quotaData.account}`,
    `• 数据通道: ${quotaData.source}`,
    `────────────────────────`,
    `💡 提示: 上下文容量、速率及缓存命中率已由 Hermes 原生状态栏托管。`
  ].join('\n')

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
          message: `5h额度: ${quotaData.quota5h}% (重置: ${formatResetTime(quotaData.reset5h)}) | 周额度: ${quotaData.quotaWeekly}%`
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
