/**
 * Hermes Desktop Plugin: config-guard-chip
 * 本地配置守卫状态指示器：轮询 /api/plugins/config-guard/result
 * （后端读 gateway:startup hook 写入的检查结果），一切正常时状态栏仅显示
 * 静默绿点，发现配置漂移 / stash 残留 / 技能被误标时显示 🔴 告警 chip，
 * 点开 Popover 看明细与处置建议。
 *
 * 数据链：桌面更新 → 网关重启 → gateway:startup hook（~/.hermes/hooks/config-guard）
 * 跑本地三项检查 → 写 last-result.json → 本插件后端 /result 透传 → 状态栏展示。
 */

import { Badge, Popover, PopoverContent, PopoverTrigger } from '@hermes/plugin-sdk'
import { useEffect, useState } from 'react'
import { jsx, jsxs } from 'react/jsx-runtime'

const ID = 'config-guard-chip'
const POLL_MS = 15_000 // 15s 轮询后端结果

let pluginCtx = null

function toneOf(result) {
  if (!result || !result.exists) return { tone: 'idle', label: '', icon: 'circle-slash' }
  if (result.ok === true) return { tone: 'ok', label: '守卫通过', icon: 'check' }
  if (result.ok === null) return { tone: 'warn', label: '守卫异常', icon: 'alert' }
  return { tone: 'bad', label: `守卫告警 ×${(result.problems || []).length}`, icon: 'error' }
}

function GuardChip() {
  const [result, setResult] = useState(null)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const rest = (pluginCtx && pluginCtx.rest) || null
        if (!rest) return
        const data = await rest('/result')
        if (alive) {
          setResult(data)
          setLoaded(true)
        }
      } catch {
        if (alive) setLoaded(true)
      }
    }
    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      alive = false
      clearInterval(timer)
    }
  }, [])

  const { tone, label } = toneOf(result)
  const color =
    tone === 'ok' ? '#3fb950'
    : tone === 'bad' ? '#f85149'
    : tone === 'warn' ? '#d29922'
    : '#8b949e'

  // 一切正常（ok）时静默：只渲染占位，不占状态栏视觉
  if (loaded && tone === 'idle') return jsx('span', { style: { display: 'none' } })

  return jsxs(Popover, {
    children: [
      jsx(PopoverTrigger, {
        asChild: true,
        children: jsx('button', {
          className: 'inline-flex h-full items-center gap-1 rounded-none px-1.5 text-[0.6875rem] text-(--ui-text-tertiary) transition-colors hover:bg-(--chrome-action-hover) hover:text-foreground',
          title: `本地配置守卫：${label}（${result?.checked_at || '未检查'}）`,
          children: jsxs('span', {
            className: 'inline-flex items-center gap-1',
            children: [
              jsx('span', {
                style: {
                  width: 7, height: 7, borderRadius: 9999,
                  background: color,
                  boxShadow: tone === 'bad' ? `0 0 6px ${color}` : 'none',
                  display: 'inline-block',
                },
              }),
              tone !== 'ok' ? jsx('span', { children: label }) : null,
            ],
          }),
        }),
      }),
      jsx(PopoverContent, {
        align: 'end',
        className: 'w-[26rem] p-3 text-xs',
        children: jsxs('div', {
          className: 'flex flex-col gap-2',
          children: [
            jsxs('div', {
              className: 'flex items-center justify-between',
              children: [
                jsx('div', { className: 'font-medium', children: '本地配置守卫' }),
                jsx(Badge, { variant: 'outline', children: result?.checked_at || '未检查' }),
              ],
            }),
            jsx('div', {
              className: 'text-(--ui-text-tertiary)',
              children: 'Hermes 更新后网关启动时自动检查：拍板配置键 / git stash 残留 / 核心技能 created_by 标记。',
            }),
            jsx('pre', {
              className: 'max-h-72 overflow-auto whitespace-pre-wrap rounded-md bg-(--chrome-action-hover) p-2 leading-relaxed',
              children: result
                ? (result.error
                    ? `⚠ 检查异常：${result.error}`
                    : (result.detail || []).join('\n'))
                : '尚无检查结果（网关启动后 hook 会自动写入）',
            }),
            jsx('div', {
              className: 'text-(--ui-text-tertiary)',
              children: result?.ok === false
                ? '处理完成后重启网关（或下次更新）即自动复检；也可手动跑 watch-capability.cmd。'
                : '配置守卫随每次网关启动自动执行，无需手动操作。',
            }),
          ],
        }),
      }),
    ],
  })
}

export default {
  id: ID,
  name: 'Config Guard Chip',
  register(ctx) {
    pluginCtx = ctx
    ctx.register({
      id: 'chip',
      area: 'statusBar.right',
      order: 9, // token-stats chip (order 10) 左侧
      render: () => jsx(GuardChip, { ctx }),
    })
  },
}
