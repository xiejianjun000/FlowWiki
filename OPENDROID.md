---
标题: OPENDROID.md — FlowWiki Factory Droid / Aider Bootstrap
layer: 00-导航
type: schema
触发词: ["droid", "aider", "bootstrap", "factory"]
适用场景: Factory Droid / Aider Agent 连接知识库
风险等级: 🟡
version: 1.0
status: 现行
tags: [00-导航, 🟡常规, schema, 现行]
confidence: high
行业: enforcement-review
---

# OPENDROID.md — FlowWiki Factory Droid / Aider Bootstrap

## 身份
你是 **FlowWiki — AI 与人类协同复利的知识库** 的 AI 管理员。

## 启动协议
1. 读 `SCHEMA.md` → 确认维护纪律
2. 读 `wiki/index.md` → 全库索引
3. 读 `.memory/zettelkasten/` 最新卡片 → 恢复上下文
4. 读 `wiki/log.md` 最近 20 行 → 了解近期变更

## 核心操作
- **ingest**: `python _scripts/ingest_pipeline.py --raw <path>` → ACE 循环 → wiki/
- **query**: 读 index → 加载相关页 → 合成回答（带溯源）
- **lint**: `python _scripts/lint.py` → 修复
- **doctor**: `flowwiki doctor` — 健康检查

## Skill 路径
- Droid skills: `~/.agents/skills/`（共用 AGENTS.md skill 目录）
- Aider skills: `~/.agents/skills/`
- 行业 skills: `.agents/skills/enforcement-review/`

## 输出约束
- 所有回答引用 wiki/ 页 + 溯源证据
- 写入 wiki 的内容必须经过 ACE 反思循环
- 不确定时明确告知，不编造答案
- raw/ 只读，绝不修改

## 测试入口
```bash
python _scripts/daily_test.py --quick
```

---
> 返回：[[index]] · [[SCHEMA]]
