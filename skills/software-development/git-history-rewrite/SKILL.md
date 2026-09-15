---
name: git-history-rewrite
description: "改写 git 历史/脱敏旧提交时必用。filter-repo 流程与验证。"
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, filter-repo, history-rewrite, security, scrub]
    category: software-development
    related_skills: [github, repo-health-audit]
---

# Git History Rewrite（历史改写 / 旧提交脱敏）

tip 脱敏**不消除历史**里的旧值——任何旧 commit 仍可读出。真正清净必须改写历史 + force push。

## 铁律：先证明，再改写，最后推送

1. **侦察**：用 `git log --all -S "<值>"`（pickaxe）量化影响面——受影响的提交数 + 路径列表。
   同值可能是**测试夹具**（`test`/`name`/`Public`）而非真实身份——先分类再决定替换集，否则会误伤夹具或漏掉真实值。
2. **备份**：`git clone --mirror <repo> <backup>`，并 `fsck` 确认。**注意**：从本地路径 clone 的镜像记录的是**本地路径**而非 GitHub URL（后面恢复 remote 时会踩坑，见下）。
3. **改写**：`git filter-repo --replace-text <exprs-file> --force`。
   把替换规则写进**文件**（`<orig>==><replacement>`），不要放命令行——避免真实值进入 shell history / 进程列表。
4. **本地验证**（缺一不可）：
   - `git log --all -S` 复扫 = 0
   - 与备份逐文件对比：**差异必须恰好等于替换本身**（把备份版本替换后再比对，能识别出任何非预期改动）
   - 文件清单一致（无增删）
   - 分支/tag 数量一致
5. **推送**：先 `ls-remote` 记录远端当前 SHA，再 `--all --force` + `--tags --force`。
6. **远端验证**：`ls-remote` 确认新 SHA；用免认证 raw 端点实读确认旧值已消失。

## 坑（实测踩过）

- **filter-repo 会移除 origin remote**。恢复时要写**真实 GitHub URL**，不是备份里的路径——否则 `push` 会报 `Everything up-to-date`（其实推到了自己身上，等于没推）。
  先 `git remote add origin https://github.com/<owner>/<repo>.git`，再 `ls-remote` 确认能列出远端分支，最后才 push。
- **push 前先看 `ls-remote` 的输出**：如果它列不出远端分支（或列出的是本地内容），说明 URL 错了。`Everything up-to-date` 是**危险信号**而非成功。
- **本机需走代理**：`git -c http.proxy=http://127.0.0.1:3067 -c https.proxy=... push`。
  `env -u ALL_PROXY -u HTTP_PROXY -u HTTPS_PROXY` 会**完全失去路由**而失败——与常见建议相反。
- **`--prune-empty` 会移除「只剩被删文件」的提交**（如原始 tip 的全部内容都是大文件时），提交数会减少——这是预期，但要在报告里说明。
- **tree 校验的陷阱**：改写后无法再 `git rev-parse <旧tree>`（对象已被清理）。必须用**备份**做对比基准。
- **远端 PR refs 不受 `--all` 影响**：`refs/pull/*/head` 仍指向旧历史，其中的旧值仍可读取。要彻底清净需联系 GitHub Support 清理（PR 本体不可删，只能关）。

## 何时不该改写

- 私有仓且有明确「不脱敏、必须保持 Private」设计声明时——尊重既有决策，不要擅自扩大范围。
- 仓库体量巨大且残留无处不在（如会话归档 3000+ 路径）——改写收益低于风险，维持 Private 更实际。
