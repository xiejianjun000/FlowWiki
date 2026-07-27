---
name: wiki-update
description: 将当前项目的知识同步到 FlowWiki 知识库。在任何项目中调用此 skill，AI 将提取当前项目的有价值知识、写入 FlowWiki 的 raw/inbox/ 或直接编译到 wiki/。触发词：更新知识库、同步知识、wiki-update、记录到 FlowWiki、把这段存到知识库。
license: MIT
metadata:
  version: "1.0.0"
  author: FlowWiki
  type: global-skill
  requires: ["~/.flowwiki/config"]
---

# wiki-update —— 全局知识同步

## 概述

此 skill 允许你在**任意项目**中将知识同步到 FlowWiki 知识库，使跨项目知识复利成为现实。不需要切换到 FlowWiki 工作区，在当前项目即可写入。

## 前置条件

确保 `~/.flowwiki/config` 文件存在，内容为：

```yaml
flowwiki_root: /path/to/FlowWiki
```

若文件不存在，运行 `bash /path/to/FlowWiki/_scripts/setup.sh` 初始化。

## 工作流

### 1. 读取配置

从 `~/.flowwiki/config` 获取 FlowWiki 根目录路径 `FLOWWIKI_ROOT`。

### 2. 分析当前项目的知识

回顾当前对话或项目内容，识别有价值的知识点：
- 技术决策及其理由
- 踩过的坑和解决方案
- 新学到的概念或模式
- 值得复用的代码片段或配置

### 3. 判断写入路径

```
有价值的内容
├─ 成熟、结构化、可独立成篇 → 直接写入 ${FLOWWIKI_ROOT}/wiki/
│  (需要经过 ACE 反思循环)
├─ 临时发现、待验证、片段化 → 写入 ${FLOWWIKI_ROOT}/raw/inbox/
│  (标记 confidence=pending，等待后续正式 ingest)
└─ 不确定价值 → 写入 ${FLOWWIKI_ROOT}/raw/inbox/
   (标记 confidence=low，附上简短说明让人类策展)
```

### 4. wiki/ 写入（需 ACE 审查）

如果当前知识成熟且结构化，可直接编译到 FlowWiki 的 wiki/ 层：

1. **确定写入位置**：
   - 概念/模式 → `wiki/concepts/<slug>.md`
   - 操作流程/踩坑 → `wiki/playbooks/<slug>.md`
   - 对比分析 → `wiki/comparisons/<slug>.md`
   - 工具/项目介绍 → `wiki/entities/<slug>.md`

2. **写入前自检（ACE 快速版）**：
   - frontmatter 含 `sources`（标注来源项目）
   - 含 `## 摘要` 段且非空
   - 含 `## 原文指针` 段（指向当前项目的相关文件或对话记录）
   - 无大段原文搬运（单段不超过 500 字）

3. **写入文件**

4. **更新索引**：
   - 更新 `${FLOWWIKI_ROOT}/wiki/index.md`
   - 追加 `${FLOWWIKI_ROOT}/wiki/log.md`

5. **Git 提交**（建议）：
   ```bash
   cd ${FLOWWIKI_ROOT} && git add -A && git commit -m "feat(wiki-update): <主题> @ <来源项目>"
   ```

### 5. raw/inbox/ 暂存（快速模式）

如果知识是临时发现或尚待验证：

1. 创建文件：`${FLOWWIKI_ROOT}/raw/inbox/YYYY-MM-DD-<slug>.md`
2. 格式：
   ```markdown
   ---
   title: "<主题>"
   type: inbox
   confidence: pending
   source_project: "<当前项目名>"
   created: YYYY-MM-DD
   tags: []
   ---

   # <主题>

   ## 原始内容
   <保存的知识片段>

   ## 上下文
   - 来源项目：<当前项目路径>
   - 记录原因：<为什么值得保存>
   - 建议处理：<建议的 wiki 目录>
   ```

## 约束

- 写入 wiki/ 的内容必须经过 ACE 自检（摘要 + 原文指针 + 不大段搬运）
- raw/inbox/ 中的内容标记 `confidence=pending` 或 `confidence=low`，等待人类策展或正式 ingest
- 不覆盖 FlowWiki 中已有的页面，以合并/补充为主
- 保留来源项目信息，便于跨项目知识追溯
- 敏感信息（密钥、密码）绝不写入

## 示例

用户: "把刚才那个 Redis 连接池配置的坑记录下来"

流程: 分析对话中的 Redis 连接池知识 → 创建 `raw/inbox/2026-07-20-redis-connection-pool-pitfall.md` → 标记 confidence=pending → 告知用户已暂存
