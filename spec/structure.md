---
标题: FlowWiki 目录结构（本知识库）
layer: 10-元文档
type: spec
触发词: ["结构", "目录", "structure"]
适用场景: 理解本库目录组织方式
风险等级: 🟡
version: 1.0
status: 现行
tags: [10-元文档, 🟡常规, spec, 现行]
confidence: high
sources: []
---

# FlowWiki 目录结构 — 执法督察评查知识库

```
执法督察评查知识库/
│
├── CLAUDE.md              L6 Claude Code 入口
├── AGENTS.md              L6 通用 Agent 入口
├── CODEX.md               L6 Codex 入口
├── SCHEMA.md              L1 知识库宪法（维护约定）
├── TESTING.md             验收说明书
├── index.md               机器索引
├── log.md                 操作时间轴
│
├── raw/                   L1 源真层（只读）
│   ├── laws/              法律原文（8单行法+法典+条例）
│   ├── regulations/       规章办法原文
│   ├── standards/         评查细则原文
│   └── articles/          其他源真
│
├── wiki/                  L1 编译知识层（AI维护）
│   ├── concepts/          概念知识
│   ├── playbooks/         操作手册 + 每日更新
│   ├── comparisons/       对比分析
│   ├── criteria/          判据体系
│   ├── entities/          实体定义
│   └── meta/              元文档
│
├── 首页与导航/          L1 人类入口
│   ├── 首页与导航.md        MOC 总索引
│   ├── 评查场景Hub.md        评查入口
│   └── 督察场景Hub.md        督察入口
│
├── .memory/               L4 记忆层
│   ├── zettelkasten/       A-MEM 卡片
│   ├── episodic/           跨会话记录
│   ├── conflict/           矛盾追踪
│   ├── ace/                反思循环记录
│   ├── gaps/               知识缺口
│   └── ops/                操作日志（JSONL）
│
├── .agents/skills/        L5 Skill（通用 Agent 格式）
│   ├── ingest/             入仓操作
│   ├── query/              查询操作
│   ├── lint/               体检操作
│   ├── research/           研究操作
│   └── enforcement-review/ 行业专属（8个）
│
├── .claude/skills/        L5 Skill（Claude Code 格式）
│   └── （同上 12 个 SKILL.md）
│
├── spec/                  L3 全局设计
│   ├── design.md           架构设计
│   ├── requirements.md     需求规约
│   ├── structure.md        目录结构
│   └── tasks.md            里程碑
│
├── openspec/              L3 变更治理
│   ├── changes/            活跃变更
│   └── archive/            归档变更
│
├── 提示词库/            Prompt 管理
│   ├── 01_生成类.md
│   ├── 02_校对类.md
│   ├── 03_问句类.md
│   └── 04_拆解类.md
│
├── .scripts/               工具脚本（7个）
├── .templates/             模板（6个）
└── 工具资源/                遗留工具索引
```
