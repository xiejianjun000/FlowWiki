---
标题: FlowWiki 架构设计（知识库级别）
layer: 10-元文档
type: spec
触发词: ["架构", "设计", "flowwiki", "7层"]
适用场景: 理解本库的架构设计与关键决策
风险等级: 🟡
version: 1.0
status: 现行
tags: [10-元文档, 🟡常规, spec, 现行]
confidence: high
sources: []
---

# FlowWiki 架构设计 — 执法督察评查知识库

> 基于 FlowWiki 7 层架构。关联文档：requirements.md / structure.md / tasks.md

## 7 层总览

```
L7 场景层      执法督察评查（enforcement-review）
L6 多Agent层   CLAUDE.md / AGENTS.md / CODEX.md
L5 Skill化层   .agents/skills/ + .claude/skills/（4操作+8行业）
L4 记忆层      .memory/（zettelkasten / episodic / conflict / ace / gaps / ops）
L3 变更治理    spec/ + openspec/changes/
L2 检索增强    config.toml（BM25→nano-graphrag→LightRAG）
L1 知识编译    raw/ + wiki/ + 首页/
```

## 关键设计决策

### 决策 1：物理分离
- raw/ 只读，LLM 不修改原始资料
- wiki/ LLM 编译，人类不直接编辑
- 首页/ 人类入口，LLM 编译 + 人类策展

### 决策 2：双索引
- 机器索引：wiki/index.md（紧凑，AI 优先）
- 人类索引：首页与导航/（MOC，人类优先）

### 决策 3：ACE 三 agent 制约
- Generator 生成 → Reflector 批判 → Curator 决策
- 错误知识不进 wiki

### 决策 4：加法策略
- 保留现有中文字段体系（标题/layer/type/触发词/风险等级）
- 追加 confidence + sources 字段
