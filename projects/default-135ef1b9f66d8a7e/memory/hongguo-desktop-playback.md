# 红果桌面版（hongguo-desktop-companion）播放失败排障

应用由渠道有数维护的第三方客户端：`waligoraamodio288-rgb/hongguo-desktop-releases`（公开分发/反馈仓库，不含源码）。
结构：Tauri 外壳 + `backend/` Python FastAPI + Java `unidbg-sign.jar` 签名服务 + V5 路径（unicorn 模拟 `libmetasec_ml.so`）。
本机安装目录：D 盘自定义目录（下文记为 `<安装目录>`）；数据目录：`%APPDATA%\cn.guoban.desktop-companion`；当前版本 1.0.27（2026-11-13 发布）。

## 症状与证据文件

「播放中断，请重试当前集」、计时停在 00:00、画质列表暂不可用。先读这 5 个诊断文件再判断，不要猜：

| 文件 | 判读 |
|---|---|
| `playback-v5-diagnostic.json` | `errorType:SdkAssetsError` = SDK 素材问题；`sdkExchanges:0` = 会话根本没开始 |
| `playback-fresh-diagnostic.json` | `v5-model-unavailable` + `batchAttempts:0` = 匿名批处理从未执行 |
| `playback-input-diagnostic.json` | `reason:upstream-empty` + `upstreamStatus:200` + `upstreamBodyBytes:0` = 上游空 200 |
| `player-route-state.json` | `counts` 里 account/public/spare 各失败次数 |
| `diagnostics/lifecycle.jsonl` | `version` 字段核对版本、PID、启动退出时间 |

## 两个独立根因

1. **上游取流空响应（服务端，本地不可修）**：`POST https://api5-normal-lq.fqnovel.com/novel/player/multi_video_model/player/v1` 对登录态、游客态、甚至空 body 均返回 `HTTP 200` + `0 字节`；无签名头 curl 直连同样 200/0。已有 issue #1161 记录。
2. **SDK 素材下载被 CDN 302 拒绝（客户端 bug，可本地绕过）**：
   `backend/phone-account-protocol/phone_sdk_assets_v5.py::_download()` 写死 `allow_redirects=False`，且要求响应必须是 `206` 且 `Content-Range` 精确匹配。而 `lf9-apk.ugapk.cn` 的 APK 现在先回 `302` 跳到 `<随机子域>.jspcdn.cn:20443`，于是必然 `SdkAssetsError('sdk-material-range-unavailable')` → `SpareError('v5-model-unavailable')`。
   又因 `desktop_fresh_playback.read()` 只把 `empty-response / invalid-model / registration-outcome-unknown` 当可回退原因，`v5-model-unavailable` 直接上抛，`batchAttempts` 恒为 0 —— 表现为「所有剧集都播不了」，很像上游整体挂掉，其实是备用路径本地就断了。

## 修复：手工装入已校验素材（不改程序、不需重启）

目标目录 `%APPDATA%\cn.guoban.desktop-companion\playback-sdk\74332\`（目录为空 = 从未下载成功）。
用安装目录自带 python（`<安装目录>\backend\python\python.exe -I -B`，系统 python 缺依赖），只改重定向策略：

```python
import sys, requests
sys.path.insert(0, r'<安装目录>\backend')
sys.path.insert(0, r'<安装目录>\backend\phone-account-protocol')
import phone_sdk_assets_v5 as A

class Follow(requests.Session):          # 唯一改动：跟随 CDN 302
    def send(self, request, **kw):
        kw['allow_redirects'] = True
        return super().send(request, **kw)

A.load_assets(r'%APPDATA%\cn.guoban.desktop-companion\playback-sdk\74332',
              allow_download=True, client_factory=Follow)
```

- 模块内部仍校验 `206` + `Content-Range` + sha256，摘要对上才落盘，302 只是 CDN 调度层，不降低安全性。
- 期望产物：`libmetasec_ml.so` 4501136 B / `c6831ab265a0cb76dacfa3b7041e9ea0f706490106a74e12f39058671cc14fe3`；`sdk-app-config.encoded` 304 B / `584a01183f1e6783326bff49d4f1319f33fcce678afb93ca0dc8b60a56b65855`。
- 装完不必重启：`Reader.assets` 失败时保持 None，下次播放会重新 `load_assets` 并命中磁盘缓存。播放器点「重试」即可。
- 成功标志：`playback-v5-diagnostic.json` → `state:ready` + `tracks>0`；`playback-input-diagnostic.json` 出现 `descriptor-resolved` → `prepared` → `ready`。
- 实测（2026-11-14，1.0.27，Win11 26300）：修复后 00:00→01:40 连续播放，历史写入第 97 集；此时 `player-route-state.json` 仍是 `public-empty / account-failed`，即播放完全由 V5 路径提供。

## 排障要点

- 后端禁用代理：启动时 pop 掉所有 proxy 环境变量且 `trust_env=False`，别用「加代理」思路排查，直接 curl 对比。
- 老板键隐藏窗口后截图只有 16x16：仍可用 `computer_use` 的 AX 树 + element 索引后台点击（UIA Invoke 对屏外/隐藏窗口有效），不必强推前台。
- 本次已提交 issue：#1422（SDK 素材 302），引用 #1161（空 200）。仓库 issue 约 1300 条未关，多为「无法播放」重复反馈。
