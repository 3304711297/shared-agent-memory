/**
 * Hermes Desktop Plugin: token-stats
 * 实时监控当前会话的输入/输出 Token、上下文用量、平均速率 (t/s) 及 API 统计。
 */

import { cn, haptic, host, Tip, useValue } from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'

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

  const input = usage?.input ?? 0
  const output = usage?.output ?? 0
  const total = usage?.total ?? (input + output)
  const calls = usage?.calls ?? 0
  const tps = usage?.avg_tps ? Math.round(usage.avg_tps) : null
  const contextUsed = usage?.context_used ?? null
  const contextMax = usage?.context_max ?? null
  const contextPct = usage?.context_percent != null ? Math.round(usage.context_percent) : null
  const cacheHit = usage?.cache_hit_pct != null ? Math.round(usage.cache_hit_pct) : null

  const tipText = [
    `📊 会话 Token 统计 [${model || '默认模型'}]`,
    `📥 输入 (Prompt): ${input.toLocaleString()} tokens`,
    `📤 输出 (Completion): ${output.toLocaleString()} tokens`,
    `🔄 总计 (Total): ${total.toLocaleString()} tokens`,
    contextUsed != null && contextMax != null ? `🧠 上下文用量: ${contextUsed.toLocaleString()} / ${contextMax.toLocaleString()} (${contextPct}%)` : null,
    tps ? `⚡ 响应速率: ~${tps} tokens/s` : null,
    cacheHit ? `⚡ 提示词缓存命中: ${cacheHit}%` : null,
    `📞 交互轮次 (API Calls): ${calls} 次`
  ].filter(Boolean).join('\n')

  return jsx(Tip, {
    label: tipText,
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
          message: `当前会话: 输入 ${input.toLocaleString()} | 输出 ${output.toLocaleString()} | 总计 ${total.toLocaleString()} tokens${tps ? ` | ~${tps} t/s` : ''}`
        })
      },
      children: [
        jsx('span', {
          className: 'opacity-70',
          children: '🪙'
        }),
        jsxs('span', {
          className: 'flex items-center gap-1',
          children: [
            jsx('span', { className: 'text-(--ui-text-tertiary)', children: 'In:' }),
            jsx('span', { className: 'font-semibold', children: formatNum(input) }),
            jsx('span', { className: 'text-(--ui-text-tertiary)', children: 'Out:' }),
            jsx('span', { className: 'font-semibold', children: formatNum(output) }),
            tps ? jsxs('span', {
              className: 'text-(--ui-accent) ml-0.5',
              children: [tps, 't/s']
            }) : null,
            contextPct != null ? jsxs('span', {
              className: 'text-(--ui-text-quaternary) ml-0.5',
              children: ['(', contextPct, '%)']
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
