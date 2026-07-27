---
name: wiki-query
description: 从 FlowWiki 知识库中查询知识。在任何项目中调用此 skill，AI 将搜索 FlowWiki 的 wiki/ 层，返回结构化回答（带溯源）。触发词：查询、搜索、wiki、知识库、FlowWiki、问一下知识库。
license: MIT
metadata:
  version: "1.0.0"
  author: FlowWiki
  type: global-skill
  requires: ["~/.flowwiki/config"]
---

# wiki-query —— 全局知识查询

## 概述

此 skill 允许你在**任意项目**中查询 FlowWiki 知识库，无需切换到 FlowWiki 工作区。

## 前置条件

确保 `~/.flowwiki/config` 文件存在，内容为：

```yaml
flowwiki_root: /path/to/FlowWiki
```

若文件不存在，运行 `bash /path/to/FlowWiki/_scripts/setup.sh` 初始化。

## 工作流

### 1. 读取配置

从 `~/.flowwiki/config` 获取 FlowWiki 根目录路径 `FLOWWIKI_ROOT`。

### 2. 加载索引

读取 `${FLOWWIKI_ROOT}/wiki/index.md` —— 这是整个知识库的目录，包含每个页面的链接和一行摘要。

### 3. 定位相关页面

根据用户查询的关键词，在 index.md 中匹配相关页面，确定 3-8 个最相关页面。

### 4. 读取页面内容

读取定位到的 wiki 页面全文。如有需要，可递归追踪页面内的 `[[wikilink]]` 引用。

### 5. 合成回答

基于读取的内容合成回答。输出格式：

```markdown
**查询**: {用户问题}

**回答**: {基于 wiki 内容合成的答案}

**依据**:
- [[wiki/页面名]]: {关键引用}
- {法条号}: {相关条文}

**置信度**: high / medium / low
```

## 约束

- 所有回答必须引用 wiki/ 页面（`[[wikilink]]`），可追溯到 raw/ 原始证据
- 不确定时明确告知，不编造答案
- 若查询涉及执法领域，使用专业术语（案卷评查、程序合法性等）
- 回答不超过 500 字（除非用户要求详细展开）
- 若查询的领域 FlowWiki 中无相关内容，建议用户执行 `wiki-update` 来扩充知识库

## 示例

用户: "行政处罚的程序合法性要点有哪些？"

流程: 读 index.md → 定位 wiki/playbooks/administrative-penalty.md → 读全文 → 合成答案 → 引用法条号
