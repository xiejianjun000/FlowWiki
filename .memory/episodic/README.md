# 情景记忆库

## 概述

Episodic Memory 记录每次用户查询的问答过程，实现跨会话的"经验积累"。每次 query 的答案回存到这里，AI 下次遇到类似问题时可以直接复用。

## 目录结构

```
.memory/episodic/
├── YYYY-MM-DD-NNN.md    # 每次查询一条记录
└── README.md            # 本文件
```

## 记录格式

```markdown
---
id: EP-YYYY-MM-DD-NNN
date: 2026-07-17
query_type: concept | playbook | comparison | research
industry: <industry_slug>
reuse_count: 0
skill_candidate: false
---

# Episodic-YYYY-MM-DD-NNN

## 问题

<用户原始问题>

## 答案

<AI 整合答案>

## 引用

- [[wiki/concepts/xxx]]
- [[wiki/playbooks/yyy]]
- [[raw/zzz]]

## 复利价值

- 是否值得提取为 playbook？是 / 否
- 是否值得抽象为 skill？是 / 否
- 同类问题出现次数：N（≥3 触发升级检查）
```

## 生命周期

1. **创建**：每次 query 完成后自动生成
2. **复用**：AI 遇到类似问题时先查 episodic，命中则直接引用
3. **升级**：`reuse_count >= 3` 且流程可标准化 → 升级为 skill
4. **归档**：90 天后未再被引用的记录移入 `archive/`

## 与 Skill 升级的关系

```
episodic 记录 → reuse_count >= 3 → 触发升级检查
    ↓
流程可标准化？
    ├─ 是 → 生成 .agents/skills/<name>/SKILL.md
    └─ 否 → 保持 episodic 记录
```
