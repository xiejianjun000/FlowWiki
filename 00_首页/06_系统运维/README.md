# 06_系统运维

## 概述

知识库健康度监控、检索配置和备份恢复。

## 内容

### 知识库健康度

通过 `lint` skill 定期体检：

- **悬空链**：`[[xxx]]` 无对应文件
- **孤儿页**：无人引用的页面
- **frontmatter 缺失**：必填字段未填
- **confidence 不匹配**：low 但未标"待核"
- **矛盾未解决**：`.memory/conflict/` 中未关闭的矛盾

体检报告输出到 `wiki/meta/lint-report.md`

### 检索配置

```toml
# config.toml
[retrieval]
engine = "bm25"           # 当前引擎
fallback_engines = ["nano-graphrag", "lightrag"]
```

自适应切换规则：
- ≤100 页：BM25 + CJK 分词（零依赖）
- 100-500 页：nano-graphrag 轻量图谱
- 500+ 页：LightRAG 实体抽取 + 图谱增强

### 备份恢复

- **自动备份**：`config.toml` 中 `backup_interval = "24h"`
- **备份位置**：`storage/` 目录
- **恢复方式**：从 `storage/` 恢复 raw/ + wiki/

### 多 Agent 兼容矩阵

| Agent | bootstrap | skills 目录 | 状态 |
|-------|-----------|------------|------|
| Claude Code | CLAUDE.md | .claude/skills/ | ✅ |
| Codex | AGENTS.md | .agents/skills/ | ✅ |
| Amp | AGENTS.md | .agents/skills/ | ✅ |
| Gemini CLI | AGENTS.md | .agents/skills/ | ✅ |
| WorkBuddy | WORKBUDDY.md | .agents/skills/ | ✅ |

详见 `wiki/meta/agent-compatibility.md`

## 导航

- [检索配置](../../config.toml) — 引擎参数
- [Agent 兼容矩阵](../../wiki/meta/agent-compatibility.md) — 多 agent 详情
- [进化学习](../04_进化学习/README.md) — ACE 与记忆
