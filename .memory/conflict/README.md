# 矛盾追踪库

## 概述

Conflict Tracking 是 FlowWiki 防止"错误知识永久化"的关键机制。当新入库的资料与现有 wiki 知识矛盾时，不静默覆盖，而是显式记录矛盾，等待人工裁决。

## 目录结构

```
.memory/conflict/
├── <topic>.md           # 每个矛盾主题一个文件
└── README.md            # 本文件
```

## 矛盾记录格式

```markdown
---
id: CF-<topic>
created: 2026-07-17
status: open | resolved | auto-overridden
severity: high | medium | low
---

# 矛盾：<topic>

## 旧说法

- 来源：[[wiki/concepts/old-view]]
- 溯源：[[raw/old-source]]
- confidence: <level>

## 新说法

- 来源：[[wiki/concepts/new-view]]
- 溯源：[[raw/new-source]]
- confidence: <level>

## 矛盾点

<具体描述哪些论断冲突>

## 状态

- [ ] 待人工裁决
- [ ] 已解决（保留旧说法 / 保留新说法 / 合并）
- [ ] 自动覆盖（条件：新 source 权威 + confidence=high + Reflector 确认）

## 决议时间

YYYY-MM-DD

## 决议记录

<裁决理由和最终选择>
```

## 触发条件

ACE Reflector 在审查时发现以下情况之一即触发矛盾追踪：

1. **事实矛盾**：新旧说法对同一事实给出不同结论
2. **数值矛盾**：同一指标的限值/标准不同
3. **法规更新**：旧法规被新法规替代但 wiki 未更新
4. **标准修订**：旧标准被新标准修订但 wiki 未更新

## 解决流程

```
Reflector 发现矛盾
    ↓
写入 .memory/conflict/<topic>.md（status: open）
    ↓
Curator 判断是否可自动覆盖
    ├─ 是（新 source 权威 + confidence=high）→ 自动覆盖 + 标记 auto-overridden
    └─ 否 → status: open，等待人工裁决
        ↓
    人类裁决 → 更新 wiki + 关闭矛盾（status: resolved）
```

## 查询

- 未解决矛盾：`grep -r "status: open" .memory/conflict/`
- 按严重程度：`grep -r "severity: high" .memory/conflict/`
