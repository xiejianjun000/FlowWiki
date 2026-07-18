---
标题: FlowWiki 需求规约
layer: 10-元文档
type: spec
触发词: ["需求", "规约", "requirement"]
适用场景: 明确本知识库的需求与目标
风险等级: 🟡
version: 1.0
status: 现行
tags: [10-元文档, 🟡常规, spec, 现行]
confidence: high
sources: []
---

# FlowWiki 需求规约 — 执法督察评查知识库

## 功能性需求

| ID | 需求 | 优先级 | 状态 |
|----|------|--------|------|
| F1 | 法律原文只读归档（raw/） | P0 | ✅ |
| F2 | AI 编译知识层（wiki/） | P0 | ✅ |
| F3 | LLM 索引 index.md | P0 | ✅ |
| F4 | 操作日志 log.md | P0 | ✅ |
| F5 | 维护契约 SCHEMA.md | P0 | ✅ |
| F6 | Agent bootstrap（CLAUDE/AGENTS/CODEX） | P0 | ✅ |
| F7 | 跨会话记忆（.memory/） | P1 | ✅ |
| F8 | ACE 反思循环 | P1 | ✅ |
| F9 | Skill 能力复利 | P1 | ✅ |
| F10 | 变更追溯（spec/openspec） | P2 | ✅ |
| F11 | 70_Prompt库 → Skill 升级链 | P2 | ✅ |

## 非功能性需求

| ID | 需求 | 指标 | 状态 |
|----|------|------|------|
| N1 | 零断链 | lint 通过 | ✅ |
| N2 | 单连通图 | 1 分量 | ✅ |
| N3 | 100% 可达 | 入口 BFS 覆盖 | ✅ |
| N4 | 8/8 frontmatter | 全部页面 | ✅ |
| N5 | 全库 git 版本管理 | git log | ✅ |
