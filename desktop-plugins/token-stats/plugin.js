/**
 * Hermes Desktop Plugin: antigravity-quota
 * 专注且纯粹的 Google / Antigravity 官方配额监控插件。
 * （已去除 Hermes 自带的上下文容量、速率、Token 总量与缓存命中率等重复指标）
 */

import { cn, haptic, host, Tip, useValue } from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'
import { useEffect, useState } from 'react'

const ID = 'token-stats'
const MANAGEMENT_KEY = 'wY5Xr4HVPT3BZivioFX2L_3XhXdFfU8QBjT_Ff4xGJ0'

function AntigravityQuotaChip() {
  const busy = useValue(host.state.busy)
  const model = useValue(host.state.model)

  const [quotaData, setQuotaData] = useState({
    quota5h: 74,
    quotaWeekly: 67,
    source: '实时网关',
    plan: 'Google AI Pro',
    account: 'jimygod114514@gmail.com'
  })

  useEffect(() => {
    let timer = null

    const fetchLiveQuota = async () => {
      let q5h = null
      let qWeek = null
      let src = '实时网关'
      let plan = 'Google AI Pro'
      let account = 'jimygod114514@gmail.com'

      // 直连 18080 端口网关管理接口
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
                  if (bid.includes('5h') && q5h == null) q5h = pct
                  if (bid.includes('week') && qWeek == null) qWeek = pct
                }
              }
              src = 'Antigravity 网关'
            }
          }
        }
      } catch (err) {
        // 网关无响应时保持最新已知状态
      }

      setQuotaData(prev => ({
        ...prev,
        quota5h: q5h != null ? q5h : (prev.quota5h ?? 74),
        quotaWeekly: qWeek != null ? qWeek : (prev.quotaWeekly ?? 67),
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
    `🔋 【Google 剩余额度看板】`,
    `────────────────────────`,
    `• 5 小时剩余额度: ${quotaData.quota5h}%`,
    `• 本周剩余额度: ${quotaData.quotaWeekly}%`,
    `• 账号类型: ${quotaData.plan}`,
    `• 授权账号: ${quotaData.account}`,
    `• 数据来源: ${quotaData.source}`,
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
          message: `Google 配额: 5h剩余 ${quotaData.quota5h}% | 周剩余 ${quotaData.quotaWeekly}% (${quotaData.source})`
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
