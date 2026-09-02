# ZCode Agent 私有记忆库 (Personal Memories Backup) 🧠

本仓库用于持久化备份 **ZCode Agent** 的所有本地记忆文件（`~/.zcode/cli/memories/`），包含跨会话累积的系统环境配置、工程契约、项目审计发现、踩坑记录及偏好设置。

> 🔒 **私有仓库声明**：此仓库设为 Private（仅自己可见），防止个人环境配置、记忆细节与私有工程习惯外泄。

---

## 📂 目录结构与记忆范围

```text
memories/
├── README.md               # 备份说明与恢复指南
├── .gitignore
├── backup-memories.cmd     # Windows 一键增量备份脚本
└── projects/
    ├── default-*/          # 全局/默认工作区记忆（系统环境、CI契约、通用偏好）
    ├── tweak-*/            # tweakbyjie 专属工程细节与 BCD/MPO/Defender 踩坑记忆
    ├── youshouldknow-*/    # YouShouldKnow 知识库规范与联动记忆
    └── omp-*/              # 历史工作区记忆
```

---

## 🔄 更换电脑 / 重装系统恢复指南

重装系统或切换新设备后，只需两步即可 100% 恢复所有记忆：

```powershell
# 1. 确保安装了 Git 并完成 GitHub 登录
# 2. 将本私有仓库直接克隆到 ZCode 记忆目录：
git clone https://github.com/3304711297/zcode-memories.git "$HOME\.zcode\cli\memories"
```

恢复完成后，重新打开 ZCode 客户端，Agent 将立即自动读取全部历史记忆与项目上下文！

---

## ⚡ 日常备份方式

在任何需要备份最新记忆的时刻，只需在终端运行：

```powershell
cd "$HOME\.zcode\cli\memories"
git add .
git commit -m "backup: 同步最新 ZCode 记忆文件"
git push
```
