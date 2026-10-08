---
name: windows-11-feature-staging-and-featuredeck
description: Internal mechanics of Windows 11 Feature Staging, ViVeTool architecture, and FeatureDeck bugfix
metadata:
  node_type: memory
  type: topic
---

# Windows 11 Feature Staging & FeatureDeck Internals

## 1. Dual Store Architecture in Windows Feature Staging

Windows 10/11 controls experimental and A/B tested features via Feature Staging (Velocity):

1. **Runtime Store**:
   - In-memory feature table accessed via `ntdll.dll!RtlSetFeatureConfigurations`.
   - Modifies active execution behavior immediately without requiring a reboot (for features that support dynamic reload).
2. **Boot Store**:
   - Persisted in Windows Registry under `HKLM\SYSTEM\CurrentControlSet\Control\FeatureManagement\Overrides\<Priority>\<ObfuscatedFeatureId>`.
   - Applied during early boot initialization by `winload` and the kernel.
   - Changes require setting the Boot Pending flag via `RtlSetSystemBootStatus(17, ...)` (`RtlBsdItemFeatureConfigurationState`). If `RtlSetSystemBootStatus` returns `0xC0000034` (`STATUS_OBJECT_NAME_NOT_FOUND`), `RtlCreateBootStatusDataFile(NULL)` must be called first to initialize `BootStat.dat`.

## 2. Priority Hierarchy & Immutable Baseline Guard

- Priorities range from `ImageDefault (0)`, `EKB (1)`, `Service (4)`, `User (8)`, `Security (9)` to `ImageOverride (15)`.
- System image baselines (`ImageDefault`, `ImageOverride`) are immutable and protected by the kernel: calling `RtlSetFeatureConfigurations` with `ResetState` on them fails.
- **User Override Invariant**: Users cannot alter the `ImageDefault` baseline itself, but CAN place an override under `Priority = User (8)` (`EnabledState = 2`) to supercede the image default.

## 3. FeatureDeck Bug & PR #1 Fix

- **Problem in FeatureDeck v0.1.0**: The UI marked all `ImageDefault` rows as `CanEdit = false`, disabling inline/batch enable buttons and showing the modal "选中的条目由系统镜像管理，不允许修改".
- **Root Cause**: Conflated "cannot reset system baseline" (`CanReset = !IsImmutable`) with "cannot write user override" (`CanToggle = true`).
- **Fix (PR #1)**: Decoupled `CanToggle` and `CanReset`. Allow writing User priority overrides for any feature while preserving the read-only guard during reset operations.

## 4. Windows 11 26H2 (Build 26300) Feature Findings

- **Master Bundle (`61161244`) Cascaded Activation**:
  Enabling `61161244` automatically promotes sub-features in the system table:
  - `59213768`: Taskbar positioning (Top / Left / Right / Bottom)
  - `61090762`: Small taskbar buttons
  - `59728252`: Modern fluid boot/login animation
- **Gated Features Verified in Build 26300**:
  - `60911173`: Native "Feature Flags" page under Windows Settings (Windows Update > Windows Insider Program).
  - `61465695`: File Explorer middle-click folder background tab open.
  - `60813048`: Modern context menu customization settings.
