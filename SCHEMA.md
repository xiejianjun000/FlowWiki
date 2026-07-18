---
标题: 执法督察评查知识库 · FlowWiki Schema
layer: 10-元文档
type: schema
触发词: ["schema", "维护约定", "怎么改库", "入库规范", "ingest流程", "flowwiki"]
适用场景: LLM 每次 Ingest/Query/Lint 前读取本文件，作为统一维护纪律
关联法条: []
调用skill: [eco-review-kb]
风险等级: 🟡
version: 2.0
status: 现行
ingested: 2026-07-18T00:00:00+08:00
updated: 2026-07-18
tags: [10-元文档, schema, 现行, flowwiki]
confidence: high
sources: []
---

# FlowWiki SCHEMA — 知识库宪法

> 本库基于 FlowWiki 方法论（7 层架构），本文件为 LLM 维护公约。

## 1. 七层架构

| 层 | 名称 | 本库对应 | 说明 |
|----|------|---------|------|
| L1 | 知识编译层 | raw/ + wiki/ + 首页/ | 人类放 raw、AI 编 wiki、人类用入口 |
| L2 | 检索增强层 | config.toml | BM25→nano-graphrag→LightRAG 自适应 |
| L3 | Spec-Driven 层 | spec/ + openspec/ | 全局设计 + 变更治理 |
| L4 | Agent 记忆层 | .memory/ (ace/gaps/zettelkasten) | ACE 反思 + A-MEM 卡片 + 缺口学习 |
| L5 | Skill 化层 | .agents/skills/enforcement-review/ | 7 个执法评查专属 Skill |
| L6 | 多 Agent 层 | CLAUDE.md / AGENTS.md / CODEX.md / WORKBUDDY.md | 4 家 agent 共享同一套知识库 |
| L7 | 场景层 | 首页/03_实战场景/ | 评查/督察/法条 3 大场景入口 |

## 2. L5 Skills（执法督察评查专属）

### 行业入口 Skill
- **enforcement-review-kb** → `.agents/skills/enforcement-review/SKILL.md`

### 6 个子 Skill
| Skill | 文件 | 用途 |
|-------|------|------|
| legality-review | legality-review/SKILL.md | 合法性审查 |
| evidence-verification | evidence-verification/SKILL.md | 证据链核验 |
| discretion-matching | discretion-matching/SKILL.md | 裁量权匹配 |
| permit-compliance | permit-compliance/SKILL.md | 排污许可检查 |
| onsite-checklist | onsite-checklist/SKILL.md | 现场核查清单 |
| code-transition | code-transition/SKILL.md | 法典衔接判断 |

## 3. 提示词（Prompts）

位置: `提示词库/task/enforcement-review/`

| Prompt | 触发场景 |
|--------|---------|
| 案卷评查.md | 用户提交案卷或询问评查结果 |
| 现场核查.md | 用户需要现场核查指导 |
| 法典衔接.md | 用户询问新旧法衔接 |

## 4. CIC 工作流

- **Collect（收集）**：人类拖资料到 `/raw/` → 自动打 `ingested` 时间戳
- **Compile（编译）**：运行 `python .scripts/bootstrap.py --slug enforcement-review`
- **Compound（复利）**：ACE 反思 + gap 学习 → 知识持续增长

## 5. 三验标准

| 验证 | 方法 | 达标线 |
|------|------|--------|
| 一验 lint | frontmatter + 断链 | 0 缺 / 0 断 |
| 二验 graph | 孤立 + 密度 | 0 孤立 / 密度 ≥ 2.0 |
| 三验 hermes | LLM 评审 | pass / 评分 ≥ 7.0 |

## 6. 入库双标准（raw→wiki 编译必须遵守）

1. **格式标准** → `wiki/meta/入库文档格式标准.md`
   - 网页残留清洗（导航/版权/跳转提示）
   - 表格还原为 markdown 表格
   - 标题层级规范化（正文从 ## 起）
   - Generator 阶段执行
2. **质量标准** → `wiki/meta/入库质量标准.md`
   - 5 维度评分卡（信息密度/结构/溯源/独特性/可操作）
   - Curator 按分决策：≥9 优质入库、6-8 合格、3-5 待核、<3 退回

## 7. 实时数据来源

宪法不写死数字。以下命令产出即当前真实状态：

```bash
# 篇数统计
find raw -name '*.md' | wc -l    # raw/ 源真层
find wiki -name '*.md' | wc -l   # wiki/ 编译层

# 图谱质量
python3 .scripts/graph.py --format stats

# 全身体检
python3 .scripts/lint.py
```

## 8. 操作纪律

1. raw/ 只读，AI 绝不修改原始内容
2. wiki/ 写入必须经过 ACE 反思循环
3. 所有知识必须可追溯到 raw/ 原始证据
4. 每次操作自动记录到 .memory/ops/YYYY-MM-DD.jsonl
5. 前端改动后必须运行 bootstrap.py 重新入库
