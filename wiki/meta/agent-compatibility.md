---
type: concept
title: Agent 兼容矩阵
created: '2026-07-17'
updated: '2026-07-17'
confidence: medium
sources: []
tags: [flow-wiki]
status: draft
---
# Agent 兼容矩阵

## 概述

FlowWiki 设计为多 Agent 兼容，支持以下 Agent 平台：

| Agent | 状态 | 测试日期 | 备注 |
|-------|------|---------|------|
| Claude Code | ✅ 已验证 | 2026-07-17 | CLAUDE.md bootstrap |
| Codex | ⏳ 待测试 | - | AGENTS.md bootstrap |
| Amp | ⏳ 待测试 | - | AGENTS.md bootstrap |
| Gemini CLI | ⏳ 待测试 | - | AGENTS.md bootstrap |
| WorkBuddy | ⏳ 待测试 | - | AGENTS.md bootstrap |

## Bootstrap 机制

### CLAUDE.md（Claude Code 专用）

- **位置**：`.agents/CLAUDE.md`
- **内容**：Claude Code 专用 bootstrap，包含：
  - 身份定义
  - 核心职责
  - 工作流程
  - 可用 Skill
  - 输出格式
  - 约束条件

### AGENTS.md（通用 Agent）

- **位置**：`.agents/AGENTS.md`
- **内容**：通用 Agent bootstrap，包含：
  - Agent 列表（Generator/Reflector/Curator/Ingestor/Researcher/Linter/MemoryManager/SkillManager）
  - Agent 协作流程
  - 通信协议
  - 扩展机制

## 兼容性设计

### 1. 文件路径兼容

所有 Agent 使用相同的文件路径约定：
- `raw/` — 只读证据层
- `wiki/` — AI 编译知识层
- `.agents/skills/` — Skill 登记册
- `.memory/` — Agent 记忆层

### 2. 通信协议兼容

```json
{
  "agent": "{agent_name}",
  "action": "{action}",
  "payload": {...},
  "timestamp": "{ISO 8601}",
  "trace_id": "{UUID}"
}
```

### 3. Skill 调用兼容

所有 Agent 使用统一的 Skill 调用格式：
```json
{
  "skill": "{skill_name}",
  "input": {...},
  "context": {...}
}
```

## 测试清单

### Claude Code 测试

- [ ] 读取 CLAUDE.md 并理解角色
- [ ] 执行 ingest skill
- [ ] 执行 query skill
- [ ] 执行 lint skill
- [ ] 执行 research skill
- [ ] 运行 ACE 反思循环
- [ ] 生成 A-MEM 卡片

### Codex 测试

- [ ] 读取 AGENTS.md 并理解角色
- [ ] 执行基础操作
- [ ] 理解 Agent 协作流程

### Amp 测试

- [ ] 读取 AGENTS.md 并理解角色
- [ ] 执行基础操作
- [ ] 理解 Agent 协作流程

### Gemini CLI 测试

- [ ] 读取 AGENTS.md 并理解角色
- [ ] 执行基础操作
- [ ] 理解 Agent 协作流程

### WorkBuddy 测试

- [ ] 读取 AGENTS.md 并理解角色
- [ ] 执行基础操作
- [ ] 理解 Agent 协作流程

## 已知限制

1. **Claude Code**：需要 CLAUDE.md 专用 bootstrap
2. **Codex**：可能需要额外的上下文提示
3. **Amp**：可能需要调整通信协议
4. **Gemini CLI**：可能需要适配文件路径约定
5. **WorkBuddy**：可能需要适配 Skill 调用格式

## 扩展计划

- 支持更多 Agent 平台（如 AutoGPT、BabyAGI 等）
- 设计 MCP server 接口
- 实现 Agent 间自动切换