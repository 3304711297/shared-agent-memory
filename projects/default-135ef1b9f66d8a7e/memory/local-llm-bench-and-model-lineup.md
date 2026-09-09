---
name: local-llm-bench-and-model-lineup
description: 2026-09-09 本地三模型横评闭环(测试基建+结论+模型库定案)与嵌入模型备选研究备忘
metadata:
  type: project
---

# 本地 LLM 横评与模型库定案 (2026-09-09)

**Why:** 用户要求对新下的 MiniCPM5-2B 与存量聊天模型做质量+速度横评,并用数据决定去留;测试基建已沉淀可复用。

## 测试基建(可复用)

- 位置:`D:\HermesRuntimes\llamacpp\`(llama.cpp b10679 CUDA 13),`bench.py` = 可复用横评脚本(起服务→探活→8题→JSON),原始数据在 `results\`(3 JSON + REPORT.md)
- 统一参数:ctx 8192 全显存、-ngl 99、flash-attn on、KV q8_0、batch 2048、temp 0.2
- **坑:llama.cpp `/health` 只收 GET,POST 探活会静默挂到超时**(当日首个"没反应"假故障根因);识别加载了哪个模型用 GET `/props` 的 `model_alias`

## 横评结论(8 题:数学×2/逻辑×2/幻觉陷阱/翻译/代码概念/exec 实测代码)

| 模型 | 得分 | 速度 | 显存 |
|---|---|---|---|
| MiniCPM5-2B (Q4, 1.6GB) | 8/8 | 130.6 tok/s | 2.3GB |
| Qwen3.5-9B (Q4, 5.7GB) | 8/8 | 42.1 tok/s | 6.1GB |
| DeepSeek-R1-Distill-7B | 7/8 | 51.3 tok/s | 5.5GB |

- **MiniCPM5-2B = 本地常驻性价比首选**(同分但快 3 倍);Q​wen3.5-9B = 质量天花板(幻觉题唯一正确指出《阿Q正传》在《呐喊》),慢且啰嗦
- Q​wen preset 的 ffn override-tensor=CPU 方案仅 64k 长上下文才需要,8k 全显存可行

## 模型库定案(已执行)

- **DeepSeek-R1-7B 已删**(09-09 用户确认):同题两轮不稳(数列 56→42)、幻觉题答案对但推理事实错、思考 token 拖速度、输出被 LaTeX 污染;preset.ini 段落同步清除
- `D:\HermesModels` 现存:bge-m3-Q8_0(OpenViking 嵌入专用)+ MiniCPM5-2B + Qwen3.5-9B(聊天)

## 嵌入模型备选备忘(搁置,重建索引时启用)

- **bge-m3 只服务 OpenViking**,与聊天模型无关;`openviking_lazy_gateway.py` 起它于 18082(嵌入),`ov.conf` dimension=1024
- **jina-embeddings-v5-text-nano**(2026-02 发布):239M,蒸馏自 Qwen3-Embedding-4B,MTEB 多语 65.5 超 bge-m3 约 6 分,Q8 仅 222MB。**不迁移的三个理由**:768 维≠1024 维(换=全库重嵌入)、任务分家(4 个独立 GGUF 需各自任务前缀,OpenAI 兼容裸调用吃不到)、CC-BY-NC 禁商用
- 未来重建索引时与 **Qwen3-Embedding-0.6B**(1024 维免改配置,MTEB 64.33)一并实测;当前召回无痛点不动
