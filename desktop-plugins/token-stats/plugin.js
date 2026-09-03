/**
 * Hermes Desktop Plugin: token-stats
 * 全独立双模监控：
 * 1. 启动 Antigravity 时：自动直读网关数据；
 * 2. 未启动 Antigravity 时：通过直连引擎（fetch_quota.py）直接解密本地 Google OAuth 凭据向 Google 官方查询 5h/周实时额度！
 */

import { cn, haptic, host, Tip, useValue } from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'
import { useEffect, useState } from 'react'

const ID = 'token-stats'

function formatNum(num) {
  if (num == null || isNaN(num)) return '0'
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M'
  if (num >= 1_000) return (num / 1_000).toFixed(1) + 'k'
  return String(num)
}

function TokenStatsChip() {
  const usage = useValue(host.state.focusedUsage)
  const busy = useValue(host.state.busy)
  const model = useValue(host.state.model)

  const calls = usage?.calls ?? 0
  const sessionInput = usage?.input ?? 0
  const sessionOutput = usage?.output ?? 0
  const sessionTotal = usage?.total ?? (sessionInput + sessionOutput)
  const contextUsed = usage?.context_used ?? null
  const contextMax = usage?.context_max ?? null
  const contextPct = usage?.context_percent != null ? Math.round(usage.context_percent) : null
  const hermesTps = usage?.avg_tps ? Math.round(usage.avg_tps) : null

  // 额度与度量状态
  const [quotaData, setQuotaData] = useState({
    quota5h: null,
    quotaWeekly: null,
    recentOutput: null,
    recentSpeed: null,
    recentReasoning: null,
    source: '直连官方',
    plan: 'Google AI Pro',
    account: ''
  })

  useEffect(() => {
    let timer = null

    const fetchAllData = async () => {
      let q5h = null
      let qWeek = null
      let src = '直连官方'
      let plan = 'Google AI Pro'
      let account = ''
      let recentOut = null
      let recentSpd = null
      let recentRsn = 0

      // 1. 尝试读 Antigravity 网关缓存
      const res = await host.request('system.read_file', {
        path: 'C:/Users/VOS-User/AppData/Local/ZCodeAntigravity/quota-cache.json'
      }).catch(() => null)

      const metricsRes = await host.request('system.read_file', {
        path: 'C:/Users/VOS-User/AppData/Local/ZCodeAntigravity/usage-metrics.json'
      }).catch(() => null)

      if (res && res.content) {
        try {
          const quota = JSON.parse(res.content)
          const acc = quota?.accounts?.[0]
          const geminiGroup = acc?.groups?.find(g => g.name.includes('Gemini'))
          const b5h = geminiGroup?.buckets?.find(b => b.window === '5h')
          const bWeekly = geminiGroup?.buckets?.find(b => b.window === 'weekly')

          if (b5h?.remainingPercent != null) q5h = Math.round(b5h.remainingPercent)
          if (bWeekly?.remainingPercent != null) qWeek = Math.round(bWeekly.remainingPercent)
          if (acc?.plan) plan = acc.plan
          if (acc?.account) account = acc.account
          src = 'Antigravity 网关'
        } catch (e) {}
      }

      // 2. 如果 Antigravity 未启动或无缓存，读取直连缓存 direct-quota.json
      if (q5h == null) {
        const directRes = await host.request('system.read_file', {
          path: 'C:/Users/VOS-User/AppData/Local/hermes/desktop-plugins/token-stats/direct-quota.json'
        }).catch(() => null)

        if (directRes && directRes.content) {
          try {
            const dq = JSON.parse(directRes.content)
            if (dq?.quota5h != null) q5h = Math.round(dq.quota5h)
            if (dq?.quotaWeekly != null) qWeek = Math.round(dq.quotaWeekly)
            if (dq?.plan) plan = dq.plan
            if (dq?.account) account = dq.account
            src = 'Google 官方直连 (独立无须启动软件)'
          } catch (e) {}
        }
      }

      if (metricsRes && metricsRes.content) {
        try {
          const metrics = JSON.parse(metricsRes.content)
          const samples = metrics?.samples || []
          if (samples.length > 0) {
            const last = samples[samples.length - 1]
            recentOut = last?.outputTokens ?? null
            recentSpd = last?.outputTokensPerSecond ? Math.round(last.outputTokensPerSecond) : null
            recentRsn = last?.reasoningTokens ?? 0
          }
        } catch (e) {}
      }

      setQuotaData({
        quota5h: q5h,
        quotaWeekly: qWeek,
        recentOutput: recentOut,
        recentSpeed: recentSpd,
        recentReasoning: recentRsn,
        source: src,
        plan,
        account
      })
    }

    fetchAllData()
    timer = setInterval(fetchAllData, 4000)
    return () => clearInterval(timer)
  }, [])

  const displayOutput = quotaData.recentOutput != null ? quotaData.recentOutput : (sessionOutput > 0 ? sessionOutput : null)
  const displaySpeed = quotaData.recentSpeed != null ? quotaData.recentSpeed : hermesTps

  const tipLines = [
    `📊 【${model || 'Gemini 3.7 Flash'}】实时监控看板`,
    `────────────────────────`,
    `🔋 【Google 剩余额度】 (${quotaData.source})`,
    quotaData.quota5h != null ? `  • 5 小时剩余额度: ${quotaData.quota5h}%` : `  • 5 小时剩余额度: 监控中`,
    quotaData.quotaWeekly != null ? `  • 本周剩余额度: ${quotaData.quotaWeekly}%` : `  • 本周剩余额度: 监控中`,
    quotaData.plan ? `  • 账号类型: ${quotaData.plan} (${quotaData.account || '已授权'})` : null,
    `────────────────────────`,
    `⚡ 【当轮请求 (Last Turn)】`,
    displayOutput != null ? `  • 最近输出 (Recent Output): ${displayOutput} tok` : null,
    quotaData.recentReasoning ? `  • 思考推理 (Reasoning): ${quotaData.recentReasoning} tok` : null,
    displaySpeed ? `  • 有效吞吐 (Throughput): ~${displaySpeed} tok/s` : null,
    contextUsed != null ? `  • 当轮上下文 (Prompt): ${contextUsed.toLocaleString()} tok` : null,
    `────────────────────────`,
    `📦 【会话累计 (Session Total)】`,
    `  • 累计输入: ${sessionInput.toLocaleString()} tok`,
    `  • 累计输出: ${sessionOutput.toLocaleString()} tok`,
    `  • 累计总计: ${sessionTotal.toLocaleString()} tok`,
    contextMax != null ? `  • 上下文窗口: ${contextUsed ? contextUsed.toLocaleString() : 0} / ${formatNum(contextMax)} (${contextPct || 0}%)` : null,
    `  • 交互轮次: ${calls} 次`
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
          message: `Google 5h额度: ${quotaData.quota5h ?? '--'}% | 周额度: ${quotaData.quotaWeekly ?? '--'}% (${quotaData.source})`
        })
      },
      children: [
        jsx('span', {
          className: 'text-emerald-500 font-semibold',
          children: quotaData.quota5h != null ? `🔋${quotaData.quota5h}%` : '🔋'
        }),
        jsxs('span', {
          className: 'flex items-center gap-1.5',
          children: [
            displayOutput != null ? jsxs('span', {
              className: 'font-semibold text-(--foreground)',
              children: [
                jsx('span', { className: 'text-(--ui-text-tertiary) font-normal mr-0.5', children: 'Out:' }),
                displayOutput,
                't'
              ]
            }) : null,
            displaySpeed ? jsxs('span', {
              className: 'text-(--ui-accent) font-semibold',
              children: [displaySpeed, 't/s']
            }) : null,
            quotaData.quotaWeekly != null ? jsxs('span', {
              className: 'text-(--ui-text-quaternary)',
              children: ['[W:', quotaData.quotaWeekly, '%]']
            }) : null
          ]
        })
      ]
    })
  })
}

export default {
  id: ID,
  name: 'Token & Google Quota Stats',
  register(ctx) {
    ctx.register({
      id: 'chip',
      area: 'statusBar.right',
      order: 10,
      render: () => jsx(TokenStatsChip, {})
    })
  }
}
