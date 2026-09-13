## The question this is best at: which rule won?

Editing every call site because a style "isn't applying" is the classic waste.
Read the real node first:

```js
const el = document.querySelector('[data-slot="aui_assistant-message-root"] a')
JSON.stringify({
  ownClasses: el.className,
  weight: getComputedStyle(el).fontWeight,
  parents: (() => {
    const out = []
    let n = el
    while ((n = n.parentElement) && out.length < 6) out.push(n.className)
    return out
  })()
})
```

If the node carries no class of its own, the value is **inherited** — sweeping
call sites will not fix it, and you need the ancestor rule. A plugin stylesheet
(e.g. `@tailwindcss/typography`'s `prose a { font-weight: 500 }`) routinely beats
a utility class; override on the shared class, not at each usage.

## Your own isolated instance

When there is no port, or you must not disturb the user's window:

```bash
cd apps/desktop
HERMES_HOME=/tmp/cdp-probe-home \
HERMES_DESKTOP_DEV_SERVER=http://127.0.0.1:5174 \
HERMES_DESKTOP_CDP_PORT=9333 \
  npx electron . --user-data-dir=/tmp/cdp-probe-userdata
```

The separate `--user-data-dir` dodges Electron's single-instance lock, so it
cannot collide with a running `hgui`; the separate `HERMES_HOME` keeps it away
from real sessions. Pick a port other than 9222 for the same reason. Run it in
the background and kill it when done.

`npm run perf:serve` does the same with a temp `HERMES_HOME` baked in, if you
also want the perf harness.
