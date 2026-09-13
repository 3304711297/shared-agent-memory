## The port

Open on `127.0.0.1:9222` for any dev-server run. Closed in exactly two cases
(`apps/desktop/electron/dev-cdp.ts`):

- **packaged builds** — always, and no environment value overrides it;
- **no `HERMES_DESKTOP_DEV_SERVER`** — an unpackaged `electron .` against
  `dist/` is how the packaged app gets smoke tested, so it behaves like one.

`HERMES_DESKTOP_CDP_PORT` moves the port (`=9333`) or disables it (`=off`).

Check before doing anything else:

```bash
curl -s --max-time 3 http://127.0.0.1:${HERMES_DESKTOP_CDP_PORT:-9222}/json/version
```

Empty → no port. Do not guess another port silently.

**Never relaunch the user's app to get a port.** That destroys their session and
their state. Launch your own isolated instance instead (below).

## Reading the DOM

`apps/desktop/scripts/eval.mjs` is the one-liner:

```bash
cd apps/desktop
node scripts/eval.mjs "document.querySelectorAll('[data-slot]').length"
```

For multi-step work use the shared client — it has target discovery and
promise-aware eval:

```js
import { CDP, SELECTORS } from './scripts/perf/lib/cdp.mjs'

const cdp = await CDP.connect({ port: 9222, match: '5174' })
const out = await cdp.eval(`JSON.stringify({
  radius: getComputedStyle(document.documentElement).getPropertyValue('--radius-scalar').trim(),
  composer: !!document.querySelector('[data-slot="composer-rich-input"]')
})`)
cdp.close()
```

`SELECTORS` in `scripts/perf/lib/cdp.mjs` holds the stable `data-slot` hooks
(composer, thread viewport, assistant message, turn pair, profile rail). Prefer
them over inventing a `querySelector` — they are updated as a unit when
components move.
