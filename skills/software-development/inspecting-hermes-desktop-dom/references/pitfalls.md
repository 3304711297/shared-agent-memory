## Pitfalls

- **Never kill the user's dev server or app to "free" anything.** A mid-serve
  kill nukes Chromium's socket pool, and the resulting `ERR_NETWORK_CHANGED`
  gets blamed on whatever you just changed.
- **A throwaway `HERMES_HOME` has no backend.** The app logs `ECONNREFUSED` for
  `hermes:api` and may exit on its own. The renderer still mounts and the DOM is
  readable — read promptly, and don't mistake a self-exited probe for a broken
  port. Chromium logs `DevTools listening on ws://127.0.0.1:<port>/…` when it
  binds; that line is the proof the port opened.
- **Poll, don't probe once.** A just-launched app needs a second or two before
  the port answers.
- **Never dump the whole DOM.** The desktop renders hundreds of nodes and
  `outerHTML` will bury your context. Project down to a small JSON object inside
  the evaluated expression.
- **Pass `match` to `CDP.connect`.** Without it you may attach to the pet
  overlay, quick-entry window, or a devtools target instead of the main window.
- **`cdp.eval` returns the value; raw `Runtime.evaluate` double-nests it**
  (`.result.result.value`). Use the wrapper.
- **`import.meta.env.DEV` is `true` under `vite dev`** in this repo. The note in
  `apps/desktop/scripts/profile-typing-lag.md` claiming otherwise is stale.
