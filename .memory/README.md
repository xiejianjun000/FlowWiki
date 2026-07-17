# A-MEM 卡片库

## 概述

A-MEM（Agent Memory）是 FlowWiki 的记忆层，采用 Zettelkasten 卡片笔记法，存储 Agent 的学习和反思内容。

## 目录结构

```
.memory/
├── cards/            # Zettelkasten 卡片
│   ├── {date}-{id}.md
│   └── ...
├── ace/              # ACE 反思记录
│   ├── {date}-{id}.md
│   └── ...
└── README.md         # 本文件
```

## 卡片格式

### Zettelkasten 卡片

```markdown
---
id: {UUID}
date: {ISO 8601}
tags: [tag1, tag2, tag3]
source: {来源}
related: [{card_id}, {card_id}]
---

# 卡片标题

## 核心内容

{内容}

## 关联知识

- [{知识1}](../wiki/{path})
- [{知识2}](../wiki/{path})

## 原始证据

- [{证据1}](../raw/{path})
```

### ACE 反思记录

```markdown
---
id: {UUID}
date: {ISO 8601}
stage: generator|reflector|curator
status: pending|approved|rejected
---

# ACE 反思记录

## Generator 输出

{Generator 生成的内容}

## Reflector 审查

{审查结果和修改建议}

## Curator 决策

{最终决策：存入/不存入/修改后存入}

## 最终版本

{如果批准，存入 wiki 的最终版本}
```

## 卡片生命周期

1. **创建**：Agent 生成新回答或新知识时创建卡片
2. **关联**：自动关联相关卡片和 wiki 页面
3. **更新**：随着知识增长，卡片内容持续更新
4. **归档**：过时或冗余的卡片自动归档
5. **删除**：确认为错误的卡片可被删除

## 卡片管理

- **自动生成**：每次回答后自动生成卡片
- **自动关联**：基于内容相似度自动关联
- **自动去重**：避免重复卡片
- **定期清理**：过期卡片自动归档

## 查询方式

- 按标签查询
- 按日期查询
- 按内容搜索
- 按关联查询