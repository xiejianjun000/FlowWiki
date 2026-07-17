# Zettelkasten 卡片库

## 概述

Zettelkasten（卡片盒）是 FlowWiki 的跨会话长期记忆层。每个 raw 文件入库时，AI 生成一张 ZK 卡片，记录关键论点、关联知识和原始证据。

## 目录结构

```
.memory/zettelkasten/
├── YYYY-MM-DD-NNN.md    # 每张卡片一个文件
└── README.md            # 本文件
```

## 卡片格式

```markdown
---
id: ZK-YYYY-MM-DD-NNN
date: 2026-07-17
tags: [flow-wiki, <topic>]
source: raw/<path>
related: [ZK-YYYY-MM-DD-NNN, ...]
confidence: high | medium | low
---

# 卡片标题

> 一句话主旨

## 关键论点

- 论点 1
- 论点 2

## 关联知识

- [[wiki/concepts/xxx]]
- [[ZK-YYYY-MM-DD-NNN]]

## 原始证据

- [[raw/xxx]]
```

## 生命周期

1. **创建**：ingest 时由 Generator 生成，ACE Curator 批准后写入
2. **关联**：自动匹配内容相似的已有卡片，写入 `related` 字段
3. **更新**：知识增长时追加新论点，不覆盖旧内容
4. **归档**：30 天后 AI 蒸馏到 `wiki/meta/`，旧卡片移入 `archive/`
5. **删除**：确认为错误的卡片可删除（需 ACE 批准）

## 查询方式

- 按标签：`grep -r "tags:.*<tag>" .memory/zettelkasten/`
- 按日期：文件名前缀 `YYYY-MM-DD`
- 按内容：全文搜索
- 按关联：`related` 字段中的卡片 ID
