# FlowWiki 项目记忆

## 项目概述
FlowWiki 是一个 AI 与人类协同复利的知识库方法论，融合 Karpathy LLM Wiki、TRAE Work、ACE 反思循环、A-MEM 卡片记忆和 SpecCoding 七阶段。

## 7 层架构
- L1 知识编译层：raw/ + wiki/ + 00_首页/
- L2 检索增强层：config.toml（BM25 → nano-graphrag → LightRAG 自适应）
- L3 Spec-Driven 层：spec/ + openspec/
- L4 Agent 记忆层：.memory/（zettelkasten + episodic + conflict + ace）
- L5 Skill 化层：.agents/skills/ + .claude/skills/（双格式部署）
- L6 多 agent 接手层：CLAUDE.md + AGENTS.md + CODEX.md + WORKBUDDY.md
- L7 场景层：00_首页/03_实战场景/（7 场景可插拔）

## 关键约定
- raw/ 只读，AI 绝不修改
- wiki/ 写入必须经过 ACE 反思循环
- 所有知识必须可追溯到 raw/ 原始证据
- .agents/skills/ 和 .claude/skills/ 必须保持同步
- config.toml 同时存在于根目录和 .llm-wiki/

## 里程碑状态（2026-07-17 补齐后）
- M0-M7 全部标记完成
- 待完成：git init、端到端测试、GitHub 发布
- 文件统计：27 skill（双部署）、7 场景、7 行业适配器、7 模板、6 脚本

## 开发时间线
- 2026-07-17 上午：M0-M7 骨架搭建（约 10:00-10:53）
- 2026-07-17 下午：gap 补齐（16:26-16:40，由 WorkBuddy/Claw 执行）
