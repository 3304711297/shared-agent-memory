---
name: user-machine-tweak-state
description: The user runs their own tweak scripts on this machine; MPO state
  observed 2026-08-16
metadata:
  node_type: memory
  type: project
  originSessionId: sess_7c83468f-a371-4eb2-8a85-9a75950ca84c
---

The user dogfoods the tweak repo's scripts on this same machine (the working dir PC). As of 2026-08-16, a read-only registry check showed: `DisableMPO=1` and `OverlayTestMode=5` set (i.e., script option 1 previously applied, MPO disabled via scheme A), `DisableOverlays` and `OverlayMinFPS` unset.

Relevant when the user reports display issues (flicker/stutter): MPO is currently disabled on this machine — option 10 → 4 restores, 10 → 3 switches to the G-Sync video-stutter fix. Machine state can change as the user runs more options; re-check before assuming.
