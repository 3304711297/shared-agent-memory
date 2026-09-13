## Page content is a separate toolset

`computer_use` is desktop-only: it does not expose a typed route for browser
page content (no `cua_browser_*` actions). For reading or acting on a page's
DOM — navigation, clicking a link by text, typed input into a form field —
use the separate `browser_navigate`/`browser_click`/`browser_type`/`browser_snapshot`
tools (or `browser_exec` when the Browser Use CLI backend is active); their
own schemas document the current contract. Reserve `computer_use` for browser
*chrome* (the address bar, permission prompts, extension popups, native
dialogs) and anything else on screen that isn't page content.

### Key shortcuts vary per platform

Use the host's idiomatic modifier:

| Common action | macOS | Windows / Linux |
|---|---|---|
| Save | `cmd+s` | `ctrl+s` |
| New tab | `cmd+t` | `ctrl+t` |
| Close tab / window | `cmd+w` | `ctrl+w` |
| Copy / paste | `cmd+c` / `cmd+v` | `ctrl+c` / `ctrl+v` |
| Address bar | `cmd+l` | `ctrl+l` |
| App switcher | `cmd+tab` | `alt+tab` |

When in doubt, capture and look for menu hints, or ask the user which
shortcut to use.

## Background rules (the whole point)

1. **Never `raise_window=True`** unless the user explicitly asked you
   to bring a window to front. Input routing works without raising.
2. **Scope captures to an app** (`app="Chrome"`) — less noisy, fewer
   elements, doesn't leak other windows the user has open.
3. **Don't switch virtual desktops / Spaces.** cua-driver drives
   elements on any virtual desktop / Space regardless of which one is
   visible.
4. **The user can be on the same machine.** They might be typing in
   another window. Don't grab focus. Don't pop modals to the front.

## Drag & drop

Prefer element indices:

```
computer_use(action="drag", from_element=3, to_element=17)
```

For a rubber-band selection on empty canvas, use coordinates:

```
computer_use(action="drag",
             from_coordinate=[100, 200],
             to_coordinate=[400, 500])
```

## Scroll

Scroll the viewport under an element (most common):

```
computer_use(action="scroll", direction="down", amount=5, element=12)
```

Or at a specific point:

```
computer_use(action="scroll", direction="down", amount=3, coordinate=[500, 400])
```

## Managing what's focused

`list_apps` returns running apps with bundle IDs / process names, PIDs,
and window counts. `focus_app` routes input to an app without raising
it. You rarely need to focus explicitly — passing `app=...` to
`capture` / `click` / `type` will target that app's frontmost window
automatically.
