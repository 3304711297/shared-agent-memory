/**
 * Hermes Desktop Plugin: token-stats
 * 智能监控当前会话 Token 用量、实时生成速率，并与 ZCode Antigravity 额度系统直连同步（5h 额度 / 周额度 / 单轮输出 / 真实速率）。
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

  // Antigravity 实时额度与度量状态
  const [antigravityData, setAntigravityData] = useState({
    quota5h: null,
    quotaWeekly: null,
    recentOutput: null,
    recentSpeed: null,
    recentReasoning: null,
    lastUpdate: null,
    plan: 'Google AI Pro',
    account: ''
  })

  // 定时从本地 Antigravity 缓存文件拉取最新额度与度量
  useEffect(() => {
    let timer = null

    const fetchAntigravityStats = async () => {
      try {
        const res = await host.request('system.read_file', {
          path: 'C:/Users/VOS-User/AppData/Local/ZCodeAntigravity/quota-cache.json'
        }).catch(() => null)

        const metricsRes = await host.request('system.read_file', {
          path: 'C:/Users/VOS-User/AppData/Local/ZCodeAntigravity/usage-metrics.json'
        }).catch(() => null)

        let quotaInfo = {}
        if (res && res.content) {
          const quota = JSON.parse(res.content)
          const acc = quota?.accounts?.[0]
          const geminiGroup = acc?.groups?.find(g => g.name.includes('Gemini'))
          const b5h = geminiGroup?.buckets?.find(b => b.window === '5h')
          const bWeekly = geminiGroup?.buckets?.find(b => b.window === 'weekly')

          quotaInfo = {
            quota5h: b5h?.remainingPercent != null ? Math.round(b5h.remainingPercent) : null,
            quotaWeekly: bWeekly?.remainingPercent != null ? Math.round(bWeekly.remainingPercent) : null,
            plan: acc?.plan || 'Google AI Pro',
            account: acc?.account || ''
          }
        }

        let metricsInfo = {}
        if (metricsRes && metricsRes.content) {
          const metrics = JSON.parse(metricsRes.content)
          const samples = metrics?.samples || []
          if (samples.length > 0) {
            const last = samples[samples.length - 1]
            metricsInfo = {
              recentOutput: last?.outputTokens ?? null,
              recentSpeed: last?.outputTokensPerSecond ? Math.round(last.outputTokensPerSecond) : null,
              recentReasoning: last?.reasoningTokens ?? 0,
              lastUpdate: last?.timestamp ? new Date(last.timestamp).toLocaleTimeString() : null
            }
          }
        }

        setAntigravityData(prev => ({
          ...prev,
          ...quotaInfo,
          ...metricsInfo
        }))
      } catch (e) {
        // 容错降级
      }
    }

    fetchAntigravityStats()
    timer = setInterval(fetchAntigravityStats, 5000) // 每 5 秒轮询一次 Antigravity 本地数据
    return () => clearInterval(timer)
  }, [])

  const displayOutput = antigravityData.recentOutput != null ? antigravityData.recentOutput : (sessionOutput > 0 ? sessionOutput : null)
  const displaySpeed = antigravityData.recentSpeed != null ? antigravityData.recentSpeed : hermesTps

  const tipLines = [
    `📊 【${model || 'Gemini 3.7 Flash'}】实时监控看板`,
    `────────────────────────`,
    `🔋 【Antigravity 剩余额度】`,
    antigravityData.quota5h != null ? `  • 5 小时剩余额度: ${antigravityData.quota5h}%` : `  • 5 小时剩余额度: 监控中`,
    antigravityData.quotaWeekly != null ? `  • 本周剩余额度: ${antigravityData.quotaWeekly}%` : `  • 本周剩余额度: 监控中`,
    antigravityData.plan ? `  • 账号类型: ${antigravityData.plan} (${antigravityData.account || '已连接'})` : null,
    `────────────────────────`,
    `⚡ 【当轮请求 (Last Turn)】`,
    displayOutput != null ? `  • 最近输出 (Recent Output): ${displayOutput} tok` : null,
    antigravityData.recentReasoning ? `  • 思考推理 (Reasoning): ${antigravityData.recentReasoning} tok` : null,
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
          message: `Antigravity 5h额度: ${antigravityData.quota5h ?? '--'}% | 周额度: ${antigravityData.quotaWeekly ?? '--'}% | 当轮输出: ${displayOutput ?? '--'} tok | 速率: ~${displaySpeed ?? '--'} tok/s`
        })
      },
      children: [
        // 额度电池指示
        jsx('span', {
          className: 'text-emerald-500 font-semibold',
          children: antigravityData.quota5h != null ? `🔋${antigravityData.quota5h}%` : '🔋'
        }),
        jsxs('span', {
          className: 'flex items-center gap-1.5',
          children: [
            // 当轮输出
            displayOutput != null ? jsxs('span', {
              className: 'font-semibold text-(--foreground)',
              children: [
                jsx('span', { className: 'text-(--ui-text-tertiary) font-normal mr-0.5', children: 'Out:' }),
                displayOutput,
                't'
              ]
            }) : null,
            // 实时速率
            displaySpeed ? jsxs('span', {
              className: 'text-(--ui-accent) font-semibold',
              children: [displaySpeed, 't/s']
            }) : null,
            // 周额度小标
            antigravityData.quotaWeekly != null ? jsxs('span', {
              className: 'text-(--ui-text-quaternary)',
              children: ['[W:', antigravityData.quotaWeekly, '%]']
            }) : null
          ]
        })
      ]
    })
  })
}

export default {
  id: ID,
  name: 'Token & Antigravity Stats',
  register(ctx) {
    ctx.register({
      id: 'chip',
      area: 'statusBar.right',
      order: 10,
      render: () => jsx(TokenStatsChip, {})
    })
  }
}
