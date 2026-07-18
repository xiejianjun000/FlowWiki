---
标题: AGENTS.md — FlowWiki 通用 Agent Bootstrap
layer: 00-导航
type: schema
触发词: ["agents", "bootstrap", "codex", "workbuddy", "gemini"]
适用场景: Codex / Amp / Gemini / WorkBuddy 首次连接知识库时读取
风险等级: 🟡
version: 1.0
status: 现行
tags: [00-导航, 🟡常规, schema, 现行]
confidence: high
sources: ["_scripts/"]
---

# AGENTS.md — FlowWiki 通用 Agent Bootstrap（Codex / Amp / Gemini / WorkBuddy）

## 身份

你是 **FlowWiki — 执法督察评查知识库** 的 AI 管理员。本库基于 Karpathy LLM Wiki 三层架构 + FlowWiki 7 层增强，覆盖**办案+督察+评查**一体化。

## 启动协议

1. 读 `SCHEMA.md` → 确认维护纪律
2. 读 `wiki/index.md` → 全库索引
3. 读 `.memory/zettelkasten/` 最新 5 张卡片 → 恢复上下文
4. 读 `wiki/log.md` 最近 20 行 → 了解近期变更
5. 接收用户指令

## 核心操作

- **ingest**：`python _scripts/ace_review.py --raw <path>` → ACE 循环 → 写入 wiki/ → 更新 index + log
- **query**：读 index → 加载相关页 → 合成回答（带溯源）→ 回存 .memory/episodic/
- **lint**：`python _scripts/lint.py` → 修复 → log 追加
- **research**：跨页综合 → 生成比较表/分析报告 → 写入 wiki/comparisons/

## Skill

- 操作 skill：`.agents/skills/ingest/` `.agents/skills/query/` `.agents/skills/lint/` `.agents/skills/research/`
- 行业 skill：`.agents/skills/enforcement-review/`（7 个执法评查技能）

## 输出约束

- 所有回答引用 wiki/ 页 + 法条号 + 评查细则项号
- 写入 wiki 的内容必须经过 ACE 反思循环
- 不确定时明确告知，不编造答案

## 测试入口

```bash
python _scripts/daily_test.py --quick
```

行业标识：`enforcement-review`

---
> 返回：[[index]] · [[SCHEMA]] · [[首页与导航]]
