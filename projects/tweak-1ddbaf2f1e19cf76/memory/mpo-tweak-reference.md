---
name: mpo-tweak-reference
description: Verified reliability verdicts and sources for MPO/Overlay registry
  keys (OverlayTestMode, DisableMPO, DisableOverlays, OverlayMinFPS)
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_7c83468f-a371-4eb2-8a85-9a75950ca84c
---

MPO registry keys verified 2026-08-16 (implemented as script option 10 / Part 10, three mutually exclusive schemes + restore):

- `OverlayTestMode=5` (HKLM\SOFTWARE\Microsoft\Windows\Dwm) — DWM-layer disable, most common, still effective on Win11 25H2 ("dead" rumor refuted by MPO-GPU-FIX).
- `DisableMPO=1` (HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers) — older driver-layer disable, reportedly no longer works on Win11 24H2/25H2 per 2025 community reports.
- `DisableOverlays=1` (same GraphicsDrivers path) — most thorough last-resort disable; can break some DX12 games (Cyberpunk, Warzone); mutually exclusive with OverlayTestMode and OverlayMinFPS.
- `OverlayMinFPS=0` (Dwm) — does NOT disable MPO; forces hardware overlay to stay promoted at low FPS, fixing G-Sync/FreeSync fullscreen video stutter (appears in NVIDIA's official RTX 5000 forum fix thread).
- Verification: dxdiag → Save All Information → search "MPO" in txt; disabled = entries gone or MaxPlanes 0; active = "MPO MaxPlanes: 4".

Sources: https://github.com/RedDot-3ND7355/MPO-GPU-FIX (primary community fix repo), https://www.nvidia.com/en-us/geforce/forums/game-ready-drivers/13/573244/mega-thread-for-black-screenfreezing-for-5000-seri/ , https://dnpu.com/853.html (covers only OverlayTestMode+DisableMPO), TechPowerUp "Disabling MPO in 2025". See also [[verify-community-tweak-claims]].
