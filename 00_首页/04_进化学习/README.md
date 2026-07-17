# 04_进化学习

## 概述

FlowWiki 的知识复利引擎：ACE 反思循环 + A-MEM 卡片记忆，让知识库"越用越懂"。

## 内容

### ACE 反思循环

每次 ingest/query 都经过 Generator → Reflector → Curator 三 agent 制约：

- **Generator**：生成摘要/回答
- **Reflector**：批判找矛盾/幻觉/过时
- **Curator**：决策入 wiki / 标"待核" / 触发矛盾追踪

ACE 记录存档：`.memory/ace/`

### A-MEM 卡片记忆

Zettelkasten 格式的跨会话记忆卡片：

- **ZK 卡片**（`.memory/zettelkasten/`）：每个 raw 入库时生成，记录关键论点和关联
- **情景记忆**（`.memory/episodic/`）：每次 query 答案回存，标注复利价值
- **矛盾追踪**（`.memory/conflict/`）：新旧说法冲突的显式追踪

### 知识复利记录

```dataview
TABLE date, status, stage
FROM ".memory/ace"
SORT date DESC
LIMIT 10
```

### Skill 升级追踪

高频任务（≥3 次）自动从 Prompt 升级为 Skill：

- 升级候选追踪：`70_Prompt库/` 中的频率标注
- 已升级 Skill：`.agents/skills/` + `.claude/skills/`

## 导航

- [采集记录](../05_采集记录/README.md) — 入仓审计
- [系统运维](../06_系统运维/README.md) — 健康度监控
- [A-MEM README](../../.memory/README.md) — 卡片格式规范
