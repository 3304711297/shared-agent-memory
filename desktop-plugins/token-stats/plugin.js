/**
 * Hermes Desktop Plugin: token-stats
 * 智能区分【单轮即时 Token/速率】与【整场会话累计】，对齐 Antigravity 网关统计口径。
 */

import { cn, haptic, host, Tip, useValue } from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'
import { useEffect, useRef, useState } from 'react'

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
  const tps = usage?.avg_tps ? Math.round(usage.avg_tps) : null
  const cacheHit = usage?.cache_hit_pct != null ? Math.round(usage.cache_hit_pct) : null

  // 跟踪单轮增量 (Last Turn Output)
  const prevOutputRef = useRef(sessionOutput)
  const prevCallsRef = useRef(calls)
  const [lastTurnOutput, setLastTurnOutput] = useState(0)

  useEffect(() => {
    if (calls > prevCallsRef.current) {
      const delta = Math.max(0, sessionOutput - prevOutputRef.current)
      if (delta > 0) {
        setLastTurnOutput(delta)
      }
      prevOutputRef.current = sessionOutput
      prevCallsRef.current = calls
    } else if (calls === 0 || sessionOutput < prevOutputRef.current) {
      prevOutputRef.current = sessionOutput
      prevCallsRef.current = calls
      setLastTurnOutput(0)
    }
  }, [calls, sessionOutput])

  const displayTurnOutput = lastTurnOutput > 0 ? lastTurnOutput : (calls === 1 ? sessionOutput : null)

  const tipLines = [
    `📊 【${model || 'Gemini 3.7 Flash'}】用量统计`,
    `────────────────────────`,
    `⚡ 【当前单轮 (Last Turn)】`,
    displayTurnOutput != null ? `  • 本轮输出 (Recent Output): ${displayTurnOutput.toLocaleString()} tok` : null,
    contextUsed != null ? `  • 本轮输入上下文 (Prompt): ${contextUsed.toLocaleString()} tok` : null,
    tps ? `  • 推理速率 (Throughput): ~${tps} tok/s` : null,
    `────────────────────────`,
    `📦 【会话累计 (Session Total)】`,
    `  • 累计输入: ${sessionInput.toLocaleString()} tok`,
    `  • 累计输出: ${sessionOutput.toLocaleString()} tok`,
    `  • 累计总计: ${sessionTotal.toLocaleString()} tok`,
    contextMax != null ? `  • 上下文窗口: ${contextUsed ? contextUsed.toLocaleString() : 0} / ${formatNum(contextMax)} (${contextPct || 0}%)` : null,
    cacheHit != null ? `  • 提示词缓存命中率: ${cacheHit}%` : null,
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
          message: displayTurnOutput
            ? `当轮输出: ${displayTurnOutput} tok | 速率: ~${tps || 0} tok/s | 累计: ${formatNum(sessionTotal)} tok`
            : `会话总计: ${formatNum(sessionTotal)} tok | 轮次: ${calls}`
        })
      },
      children: [
        jsx('span', {
          className: 'opacity-80',
          children: '⚡'
        }),
        jsxs('span', {
          className: 'flex items-center gap-1.5',
          children: [
            // 当轮输出优先显示（类似 Antigravity 的 Recent Output）
            displayTurnOutput != null ? jsxs('span', {
              className: 'font-semibold text-(--foreground)',
              children: [
                jsx('span', { className: 'text-(--ui-text-tertiary) font-normal mr-0.5', children: 'Turn:' }),
                displayTurnOutput,
                ' tok'
              ]
            }) : null,
            // 吞吐速率
            tps ? jsxs('span', {
              className: 'text-(--ui-accent) font-semibold',
              children: [tps, ' t/s']
            }) : null,
            // 上下文占用
            contextUsed != null ? jsxs('span', {
              className: 'text-(--ui-text-quaternary)',
              children: ['[Ctx: ', formatNum(contextUsed), ']']
            }) : null
          ]
        })
      ]
    })
  })
}

export default {
  id: ID,
  name: 'Token & Usage Stats',
  register(ctx) {
    ctx.register({
      id: 'chip',
      area: 'statusBar.right',
      order: 10,
      render: () => jsx(TokenStatsChip, {})
    })
  }
}
