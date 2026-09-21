---
name: comfyui-qwen-image-local-bf16
description: 本地 ComfyUI + Qwen-Image-2.1 部署配置、画质优先拍板与量化方案实测否决记录
metadata:
  type: project
---

# 本地 ComfyUI 与 Qwen-Image-2.1 部署（2026-09-21）

## 部署现状

| 项目 | 值 |
|---|---|
| ComfyUI 形态 | 便携版（portable），位于 `D:\ai coding\ComfyUI` |
| 启动方式 | 双击 `run_nvidia_gpu.bat`（黑窗口即服务端，关闭窗口=停止） |
| 服务地址 | `http://127.0.0.1:8188` |
| 版本 | ComfyUI `0.37.0` / 前端 `1.53.6` / 模板 `0.11.66`（三者均等于 required，无需升级） |

## 模型配置（bf16 全精度三件套）

| 角色 | 文件 | 大小 |
|---|---|---|
| 扩散模型 | `models/diffusion_models/qwen_image_2.1_bf16.safetensors` | 14.23 GB |
| 文本编码器 | `models/text_encoders/qwen3vl_8b_bf16.safetensors` | 17.53 GB |
| VAE | `models/vae/qwen_image_2.1_vae_bf16.safetensors` | 676 MB |

来源与构建：扩散模型与文本编码器由 HuggingFace（`Qwen/Qwen-Image-2.1`）分片 safetensors **字节级合并**为单文件；VAE 走 Comfy-Org 官方 repack。

- 扩散模型 297 个张量 key 与上游 `transformer/diffusion_pytorch_model.safetensors.index.json` **完全一致**（未融合的 `img_mlp.gate_layer` + `img_mlp.proj` 布局）。
- 文本编码器 750 个 key 与上游 index.json **完全一致**（`model.language_model.` 前缀 + `model.visual.deepstack_merger_list`），命中 ComfyUI `detect_te_model` 的 `QWEN3VL_8B` 分支。
- VAE 与 Comfy-Org 官方 repack **字节级同哈希**（`sha256 bb21f747…b7c9`）。

**性能实测**：RTX 4070 Laptop 8GB VRAM + 24GB RAM，1024×1024 / 25 步 = **2.76 s/it**（约 73s/张，首跑另有约 8s 模型装载），靠动态 offload 跑满 32GB 权重。

三个工作流存放于 ComfyUI `user/default/workflows/`：文生图、图像编辑、去背景（均标注「本地bf16」，引用上述三件套）。

## 用户拍板：画质优先（2026-09-21）

**明确选择 bf16 全精度，拒绝用量化换速度；已声明「不换量化」，后续不得再提议 GGUF / int8 提速方案。**

**Why**：bf16 是这套模型的无损上限（官方 `comfyui-workflow-templates-json` 三个 Qwen-Image-2.1 模板默认引用的就是这三个文件），任何量化都是向下兼容路径；用户当前优先要画质而非迭代速度。

**How to apply**：涉及本地生图的配置建议一律以「不损失精度」为前置条件；除非用户主动提出提速需求，否则不再主动推销量化方案。

## 量化方案实测否决记录（避免重复调研）

社区 `abenzerps/Qwen-Image-2.1-Uncensored-GGUF` 与官方 `int8_convrot` 两套方案均已实测并否决：

1. **「Uncensored」只是营销标签，不是微调**：该 GGUF 仓库明确声明使用原始上游权重（同一 revision `b3179ad3`），无任何去对齐/微调步骤。它的张量名与形状和本地 bf16 **零差异**（仅 ggml 维度序反转），伴随的文本编码器 750 张量 dtype/shape 与 Comfy-Org 版逐一相同，VAE 与本地**同 sha256**。所谓「无安全过滤」是本地部署的固有属性，非该仓库增益。
2. **K-quant 保 BF16 1D 张量、legacy 量化不保——这才是 Q8_0 崩的真因**：`Q4_K_M/Q5_K_M/Q6_K` 的 65 个 1D 张量（RMSNorm 缩放）全部保留 BF16，而 `Q8_0`/`Q4_0` 把其中 64 个也量化了，导致采样时报 `[136] vs [128]` 形状不匹配（该仓库 README 亦承认 Q8_0 当前不可用）。
3. **GGUF 需第三方节点**：核心 ComfyUI **不含** GGUF 支持（全仓无相关代码），须额外 clone `leejet/ComfyUI-GGUF`；旧 `city96` fork 会报 `Unknown model architecture!`。这些社区 GGUF 的 KV 元数据为 0（`nkv=0`），加载器完全依赖张量命名识别。放置目录 `models/diffusion_models/`，节点 `Unet Loader (GGUF)` 替代 `UNETLoader`。
4. **官方 `int8_convrot` 是更干净的省显存路径（但同样被否决）**：`qwen_image_2.1_int8_convrot`（7.25GB）+ `qwen3vl_8b_int8_convrot`（9.35GB），走 ComfyUI 0.37 原生 `comfy.ops` 量化路径（每层带 `.comfy_quant` 标记 + `weight_scale` 张量，由 `detect_layer_quantization` 识别），**无需任何第三方节点**。8GB 卡上比 bf16 显著省搬运，代价是 int8 有损。
5. 同仓库另有 `qwen3.5_9b_qwen_image_2.1_pe_t2i/i2i.int8_convrot`（9.47GB，含 `linear_attn`，属 Qwen3.5-9B）。**当前官方与上游模板均未引用它们**（模板仍指向 `qwen3vl_8b_*`），属前瞻性文件，暂不适用。

## 通用判据（可迁移）

- **验证社区模型是否为「同一模型换皮/量化」的方法**：用 HTTP `Range` 请求只取远端 safetensors 头部（前 8 字节小端给出 header 长度，再取 `bytes=8-(7+n)`），比对张量名+dtype+shape，必要时比对整文件 sha256——**几 KB 的请求即可定论，不必下载数十 GB**。
- **GGUF 的每张量 GGML 类型可同样从头部读出**：版本 3 格式为 magic(4) + version(4) + tensor_count(8) + kv_count(8)，随后是 KV 区与张量信息表；据此可判定哪些张量被量化、哪些保 BF16，从而预判加载器兼容性。
- **换 VAE 是最容易真掉画质的操作**：第三方「优化版」VAE 常为重编码产物，除非哈希与官方 repack 一致，否则不要替换。
