---
name: local-llm-ops
description: "本地跑模型/GGUF/显存不够时必用。本地模型选型与 llama.cpp 运维。Use when selecting, benchmarking, or serving local GGUF models."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [local-llm, llama.cpp, gguf, vram, quantization, speculative-decoding, benchmarking]
    category: devops
    related_skills: [local-proxy-client-diagnostics, hermes-auxiliary-models]
---

# Local LLM Ops — llama.cpp / GGUF

在本地用 llama.cpp 跑 GGUF 模型：选型核对、显存预算、量化取舍、投机解码调优、横评复现。
覆盖"模型该不该换"与"换了怎么跑得更快"，不覆盖云端 API 模型接入（那是 `hermes-auxiliary-models`）。

## 核心原则

**先查字节数，再谈版本号。** 上游仓库的 `lastModified` 经常只反映 README 改动，权重本身没变；
用 HF API 比对**文件字节数**才能判断本机模型是否真的过期。同理，"发布了新版本"≠"值得升级"——
必须过下面三条筛子。

**加速取决于接受率，不取决于开关。** 投机解码不是"打开就快"：草稿被接受才省时间，
被拒绝时反而比不用更慢（实测 0.6x）。见 Pitfalls。

## When to Use

- 本地模型选型："有没有更好/更新的版本"、"这个新模型值不值得换"
- 本地服务运维：llama-server 启动参数、显存预算、上下文长度取舍
- 速度优化：投机解码、量化选择、offload 策略
- 本地横评：同口径对比多个模型

**Don't use for:** 云端/API 模型接入 → `hermes-auxiliary-models`；代理客户端排查 → `local-proxy-client-diagnostics`。

## Prerequisites

- llama.cpp 二进制（本机 `%LOCALAPPDATA%` 外的独立目录，含 `llama-server.exe`）
- GGUF 模型文件
- `curl`（查 HF API）、Python 3（跑横评脚本）

## 升级决策三筛（顺序执行，任一不过即不换）

1. **上游真的变了吗？** 查 HF API 的文件字节数与 `lastCommit`，不要只看 `lastModified`：
   ```bash
   curl -fsS -A 'Mozilla/5.0' \
     'https://huggingface.co/api/models/<owner>/<repo>?blobs=true' \
     | python -c "import json,sys; [print(s['rfilename'], s.get('size')) for s in json.load(sys.stdin)['siblings'] if s.get('size')]"
   ```
   与 `read_file` 得到的本机文件字节数逐一比对。**字节数相同 = 权重未变，不必重下。**

2. **新候选强过现有基线吗？** 用独立榜单（Artificial Analysis 等）+ 同口径实测。同尺寸档位的
   分数差距若在 3 分以内，通常不足以抵消语言能力/生态风险。

3. **工具链支持吗？** 榜单分数高但 llama.cpp 上游无架构支持 = 不可用。必查：
   ```bash
   curl -fsS 'https://api.github.com/search/issues?q=repo:ggml-org/llama.cpp+<arch>+in:title&sort=created&order=desc&per_page=10'
   ```
   只看有没有**已合并的 PR**。issue 挂着、PR 只有 fork 分支的一律视为不支持（模型卡里的
   "PR in progress" 可能长期不动）。

## Quick Reference

```bash
# 版本/能力自检
<llama-server> --version
<llama-server> --help | grep -iE 'spec-type|draft|preset'   # 支持的投机解码类型

# 单模型起服务（按需，勿常驻）
<llama-server> -m <model.gguf> -ngl 99 -fa on -c 8192 --port <port> --host 127.0.0.1

# 带草稿模型的投机解码
<llama-server> -m <target.gguf> -md <draft.gguf> \
  --spec-type draft-<name> --spec-draft-n-max 3 -ngl 99 -ngld 99 -fa on -c 8192

# 探活（/health 只接受 GET；/props 可见实际加载参数）
curl -fsS http://127.0.0.1:<port>/health
curl -fsS http://127.0.0.1:<port>/props
```

## Procedure

### 1. 盘点本机现状
列出模型文件（字节数+日期）与运行时版本，确认服务是否在跑。完成判据：拿到每个模型的字节数，
且知道哪些端口有监听、哪个 PID 持有。

### 2. 核对上游（走"升级决策三筛"）
完成判据：每个模型都有一个明确结论——"权重未变，无需动作" / "有新版本，待评估" /
"新版本装不下 / 工具链不支持"。

### 3. 显存预算
```
权重 = GGUF 文件字节数
KV 缓存 ≈ 2(K+V) × 层数 × KV头数 × head_dim × 2字节 × 上下文token数
```
Q4_K_M 的 9B 级模型约 5.3–5.8 GiB；2B 级约 1.5 GiB。8 GB 卡上留 1–1.5 GiB 给显示与计算缓冲。
长上下文用 `--cache-type-k q8_0 --cache-type-v q8_0` 压 KV。完成判据：权重 + KV + 缓冲 < 显存上限。

### 4. 起服务并实测（不要只看榜单）
用 `--port` 起临时实例（推荐 19300 段，避开生产端口），跑横评，**测完立刻 kill**。
完成判据：拿到本机实测 tok/s 与质量分，而非引用他人数据。

### 5. 投机解码调优（可选，见 Pitfalls）
先测**无草稿基线**，再测开草稿，按场景对比。完成判据：有一组同 prompt、同参数的对照数字。

## Pitfalls

- **推理型模型的 `content` 可能为空。** 部分模型（如蒸馏 CoT 类）把 token 全烧在隐藏推理里，`content` 返回空字符串而 `usage.completion_tokens` 照常计数。**评测时必须只对 `content` 断言**——若把 `reasoning_content` 并入检查，会把"用户什么都没收到"误判成通过。同时把 `max_tokens` 放到足够大（实测 800 会截断，需 3000+），否则测的是预算而不是能力。
- **投机解码可能变慢。** 加速倍数＝草稿接受率的函数，与内容类型强相关：结构化输出
  （代码/说明文）接受率高（实测 1.3–2.6x），自由创作类接受率低（实测 **0.56–0.61x，反而更慢**）。
  `--spec-draft-n-max` 调小（7 → 3）能牺牲上限换稳定：低接受率场景从 0.61x 回升到 0.83x，
  其余场景仍保持 1.3–1.4x。**先测再定，别照抄模型卡推荐值。**
- **草稿模型不能替代目标模型。** 草稿是独立的小模型（约 0.6 GB），必须与目标模型**配对加载**
  （`-m` + `-md`）。删掉目标模型只留草稿 = 服务起不来。
- **`lastModified` 会骗人。** 上游批量刷 README 会让一排仓库看起来"刚更新"，权重其实没动。
  只信 `tree` API 里 `.gguf`/`.safetensors` 的 `lastCommit` 与字节数。
- **`--spec-type` 是较新参数。** 老版本 llama.cpp 没有；先 `--help | grep spec-type` 确认。
  启动日志里的 `E ... failed to initialize the context: ... (this warning is normal during memory fitting)`
  是**良性**的自动显存 fitting 提示，后面出现 `model loaded` / `listening on` 即正常。
- **`/health` 只接受 GET。** POST 会报错，别误判为服务挂了。
- **测试实例必须回收。** 每次起服务后确认监听端口与 PID，测完 kill 并复查端口已释放；
  显存不释放会污染后续所有测量。
- **别删旧模型腾空间前先问。** 目标模型与草稿是配对关系；且"旧模型"往往仍是回退选项。

## 嵌入模型替换（RAG 索引重建）

替 RAG 系统的嵌入模型与换对话模型完全不同：**旧向量与新向量不在同一语义空间，必须全量重建**。
维度相同也不意味着可以混用——查询用新模型编码、文档是旧模型编码，相似度就是噪声。

### 选型要扩样本

小样本会给出相反结论。实测教训：8 条语料时候选 A 领先，5 组干扰题时换成 B 领先，
扩到 10 组后才稳定（A 8/10 vs B 6/10）。**同一结论要在 ≥10 组、含语义近邻干扰项的
数据集上复现才可信**，否则报的是抽样噪声。

### OpenAI 兼容嵌入服务探活

```bash
curl -fsS http://127.0.0.1:<port>/v1/embeddings \
  -H 'Content-Type: application/json' \
  -d '{"input":["测试文本"],"model":"x"}'
```
服务端 `--pooling last` 是多数 LLM-based 嵌入模型的正确池化方式（Qwen/Octen 系）。

### 注册表校验（RAG/向量库系统）

这类系统把嵌入元数据（provider/model/dimension）写进向量集合的描述里，启动时比对；
**模型名不一致会直接拒绝启动**（`EmbeddingRebuildRequiredError`）。两条路：

| 做法 | 适用 | 风险 |
|---|---|---|
| `embedding.allow_metadata_override=true` | 仅维度相同 | 保留旧向量 → **语义空间错配，检索退化为噪声**。只在确认向量本来就该保留时用 |
| 清空集合重建（推荐） | 任何情况 | 需重跑全部 embed；先备份 |

重建流程：停服务 → 备份并**移走**（不是删）索引目录 → 启动服务（自动新建集合）→
跑系统自带的 reindex 命令 → 轮询队列直到消化完。

**长任务 CLI 会先报超时，但服务端继续跑**——不要因客户端超时以为失败而重发；
用系统状态命令看队列（pending/running/errors）与向量计数。

## 桌面端托管运行时（hermes desktop “本地模型”面板）

当模型由 Hermes 桌面端托管时，**不要手写它的配置文件** —— 与托管层抢方向盘必然被覆盖或误判。
先弄清托管层的三条规则：

### 1. 模型发现靠“目录扫描”，无需注册

托管层启动时扫描模型目录（本机 `%LOCALAPPDATA%\hermes\models`，可 junction 到其他盘）下的
`*.gguf`，**新增文件即被发现**，不需要往任何清单里登记。分割模型（`-00001-of-0000N`）只在全部
分片齐备时才算一个模型。

### 2. 资产文件必须放 `models/assets/` 子目录，且靠**文件名前缀**区分

mmproj 投影器与投机解码草稿模型不是可服务的模型。判定靠文件名开头：
`mmproj`、`dspark`、或名字含 `draft` → 资产；其余 `.gguf` → 当成聊天模型列出来。

**踩坑**：把草稿命名为 `MiniCPM5-2.6B-DSpark.gguf` 放在模型目录根下，会被当成一个可加载的聊天
模型（前缀不是 `dspark`，是中缀）。正确做法：放进 `models/assets/` 并改成 `dspark-*.gguf`。
验证方法：起 router 看 `GET /v1/models` 里有没有它——出现了就是放错了。

### 3. 启动参数、上下文窗口都由托管层自动生成，且窗口只能升不能降

预设 INI（`runtimes/llamacpp/presets.ini`）由代码根据模型的 GGUF 头和硬件预算**整份重写**，
手写的条目会在下次启动时消失。它从模型头读取真实参数（层数、KV 维度、词表），据此算显存占用并
决定启动标志。

**反直觉约束：上下文窗口不可手动调小。** 策略里有硬地板（64K）与“只能往上增长”的判定——
覆盖文件 `window_overrides.json` 只接受比当前值**更大**的目标。试图改小不会报错，但也不生效。

因此推理：**小显存跑大模型时，“调小窗口换全 GPU 速度”这条路是不通的。** 只能改走：
换更小的模型、接受 CPU offload 的降速、或绕过托管层自起实例。判定是否被 offload：生成的
预设里出现 `override-tensor=...=CPU` 即 FFN 层已卸到 CPU。

**降速幅度实测**（9B Q4 在 8GB 卡上）：全 GPU 约 43 tok/s，托管层默认配置（大窗口 +
FFN 卸到 CPU）约 20 tok/s，差约 2.2 倍。这是硬件约束下的设计取舍，不是配置错误。

### 4. 引擎更新（bump llama.cpp build）走面板按钮，别手工替换二进制

面板“引擎有可用更新”的判定 = 启用中、有已装 tag、且**配置 tag 不在已装列表**里
（`configured_tag not in have`）；配置 tag 来自 `config.yaml` 的 `local_runtime.tag`，未写时用发布 pin
（`config_defaults.py` 的 `DEFAULT_CONFIG["local_runtime"]["tag"]`）。

点“更新引擎”→ `POST /api/local-models/runtime/install`：解析资产 → 下载 → sha256（无 pin 时 TOFU
记录）→ 解压 → `--version` 验证 build 号 → 写 manifest → **重启托管 server 到新构建** → prune 只留 N-1。

- **下载走 Python `urllib`，读 `HTTPS_PROXY`/`HTTP_PROXY` 环境变量**——调试期先用
  `curl -r 0-50 -L`（GET 带 range；HEAD 可能被拒）确认 GitHub release 链路可达。
- 下载量：Win CUDA = runtime zip + cudart zip（b10964 实测约 143 MB + 373 MB）；
  `downloads/` 里已存在的同名资产（cudart 文件名不含 tag）会跳过，失败重试只补缺的那个（.part 会被清）。
- **手工替换二进制行不通**：托管层按 manifest 判定“已装”并整份重生成 presets，绕过只会让状态与磁盘失配。
- **更新会重启托管 server**（这次点击即授权）——正在跑的本地模型会重载一次；独立自起的实例
  （如嵌入服务）不归托管层管，不受影响。
- N-1 保留：连跳两个 build 后更早的 tag 目录会被 `prune_old_tags` 删；从被删目录启动的**运行中**进程
  在 Windows 上因文件锁让删除静默失败（`ignore_errors=True`），目录残留而非崩溃。

## Verification

```bash
# 0) 评测脚本的自检：确认只断言 content，且 finish_reason 不是 length
python -c "import json; r=json.load(open('result.json')); print('空答案数:', sum(1 for x in r if not x.get('content')))"
# 1) 服务确实在跑（GET，非 POST）
curl -fsS http://127.0.0.1:<port>/health

# 2) 加载的是你以为的模型与参数
curl -fsS http://127.0.0.1:<port>/props | head -c 400

# 3) 测完确认端口释放、无残留进程
netstat -ano | grep -E ':(<port1>|<port2>)\b'
```

**反例信号**：报告里只有"启用了投机解码"而没有对照 tok/s 数字；或声称"上游有更新"却只引用了
`lastModified` 日期；或推荐了一个 llama.cpp 无法加载的架构。
