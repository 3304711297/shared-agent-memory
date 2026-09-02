---
name: verify-community-tweak-claims
description: User expects web-based reliability verification of forum/blog tweak
  posts before integrating them into the tweak script
metadata:
  node_type: memory
  type: feedback
  originSessionId: sess_7c83468f-a371-4eb2-8a85-9a75950ca84c
---

When the user shares a community post (forum/blog) of Windows tweaks and asks to 查漏补缺 (fill gaps in the script), they explicitly want its reliability verified first ("你需要检索他的可靠性"), not blind integration.

**Why:** The repo ships risky system tweaks; wrong registry keys or stale advice would propagate to users. In the MPO session (2026-08-16), verification caught nuances: one key (DisableMPO) reportedly dead on Win11 24H2/25H2, one "choose one, never both" constraint, and one claim ("OverlayMinFPS better than disabling MPO") only true for a specific scenario.

**How to apply:** Web-search each registry key against authoritative sources (vendor forums like NVIDIA's, community fix repos like [[mpo-tweak-reference]]'s MPO-GPU-FIX, TechPowerUp/Reddit reports); present a per-item verdict table; then implement only verified parts following repo conventions (new menu Part N with sub-options, script header comment, README menu table, OPTIMIZATION-DETAILS.md section).
