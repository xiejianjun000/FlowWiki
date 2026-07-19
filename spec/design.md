---
标题: FlowWiki 架构设计（知识库级别）
layer: 10-元文档
type: spec
触发词: ["架构", "设计", "flowwiki", "7层"]
适用场景: 理解本库的架构设计与关键决策
风险等级: 🟡
version: 1.1
status: 现行
tags: [10-元文档, 🟡常规, spec, 现行]
confidence: high
sources: []
---

# FlowWiki 架构设计 — 执法督察评查知识库

> 基于 FlowWiki 7 层架构。关联文档：requirements.md / structure.md / tasks.md / SCHEMA.md

## 7 层总览

```
L7 场景层      执法督察评查（enforcement-review）
L6 多Agent层   CLAUDE.md / AGENTS.md / CODEX.md
L5 Skill化层   .agents/skills/ + .claude/skills/（4操作+8行业+1全文加载）
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

### 决策 5：原文指针铁律（v1.1 新增）

**问题**：raw/ 已存原文，wiki/ 若再搬一份会双写、检索降效、违反分层架构。

**方案**：每个 wiki/ 页面强制含 `## 原文指针` 段，给出 raw/ 全文路径 + 逐字引用规则；wiki/ 主体只存摘要 + 判断要点。需要逐字引用时通过 `/fulltext` skill 按需 read raw/。

**ACE 三阶段分工**：
- **Generator**：产出摘要 + 判断要点 + 原文指针段（raw 路径 + 引用规则 + 加载方式）
- **Reflector**：三必查（矛盾/幻觉/过时）+ **指针段完整性检查**（路径是否指向真实 raw/ 文件、是否缺失字段）
- **Curator**：决策——指针缺失或路径悬空 → **直接退回 Generator**，不得入 wiki/；无 issue + 指针齐全 → 接受入 wiki/

**循环终止**：Reflector 不再 raise issue，或达到 3 轮上限。

**矛盾追踪**：`.memory/conflict/<topic>.md`，需 confidence=high + 新 source 权威才能自动覆盖。

**成本控制**：低频任务可关闭 Reflector；3 轮上限防止成本失控。

**落地实现**：
- `_scripts/ingest_pipeline.py::run_ace_review()` 7 项强制检查（frontmatter/摘要段/原文指针段/全文路径/引用规则/路径有效性/全文搬运启发式）
- 缺任一项返回 `needs_revision`，Curator 据此退回 Generator
- `_templates/wiki_page.md.j2` 模板已内置 `## 摘要` + `## 原文指针` 双段结构
- `.agents/skills/fulltext/` + `.claude/skills/fulltext/` 双格式部署 skill：按需加载 raw/ 全文

### 决策 6：为什么 wiki/ 不存全文而用指针

**问题**：用户场景中 AI 需要频繁引用法条原文，把全文塞进 wiki/ 看似方便，但有 4 个代价：
1. **冗余双写**：raw/ 已有原文，wiki/ 再存一份，更新时两边都要改
2. **检索降效**：112 篇法条全文合计几十万字，全塞 wiki/ 会让 LLM 查询时爆 context
3. **违反分层**：wiki/ 是"编译后的结构化知识"，原文搬运违背"编译"定位
4. **维护成本**：raw/ 改了 wiki/ 全文也要同步改，否则数据不一致

**方案**：wiki/ 主体保留精炼版，但每页强制嵌入 raw/ 全文路径指针 + '需逐字引用时调用 /fulltext skill'。ACE 检查指针是否齐全。优点：保留分层、无双写、AI 需要时一键 read raw/。

**对比**：
| 方案 | 优点 | 缺点 |
|------|------|------|
| 强制全文入库 | 引用方便 | 双写、爆 context、违反分层 |
| **指针+按需展开** ✓ | 保留分层、无双写、按需加载 | 需要额外 fulltext skill |
| 混合模式 | 渐进迁移 | 两套规则并行，复杂度高 |

本库采用方案 2：指针+按需展开。

## 风险与权衡

| 风险 | 缓解 |
|------|------|
| ACE 三 agent 成本高 | 设 3 轮上限 + 低频任务可关 Reflector |
| 双索引维护成本 | LLM 自动同步，人类仅策展 |
| 指针悬空 | lint 强制检查路径有效性，发现悬空自动标记 high severity |
| 全文搬运误判 | 启发式检查（≥3 次"第X章"），允许人工裁决 |
| A-MEM 卡片膨胀 | 30 天后 AI 自动蒸馏到 wiki/meta/，旧卡片归档 |
