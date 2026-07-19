---
type: ops
title: "AI 自检自愈运维手册"
created: 2026-07-19
updated: 2026-07-19
tags: ["flow-wiki", "ops", "self-healing", "ci-cd"]
status: active
---

# AI 自检自愈运维手册

## 概述

FlowWiki AI 自检自愈流水线定时扫描知识库健康度，自动修复可修复的问题，并通过 Pull Request 方式提交给人类审核。

**修复从不直接合入主分支**，所有变更都走 PR，人工审核后再合并。

---

## 流水线组成

| 组件 | 文件 | 职责 |
|------|------|------|
| 自检引擎 | `_scripts/self_check.py` | 5 维度扫描（含竞品对标），输出结构化自检报告 |
| 自愈引擎 | `_scripts/self_heal.py` | 读取报告，自动修复可修复问题 |
| 竞品对标引擎 | `_scripts/benchmark_competitors.py` | 扫描 GitHub 同类项目，生成 9 维度对比分析 |
| CI 流水线 | `.github/workflows/ai-self-healing.yml` | 定时触发 + 自动开 PR |

---

## 检查维度（自检）

| # | 维度 | 检查项 | 严重程度 |
|---|------|--------|---------|
| 1 | **结构完整性** | 必备目录/文件是否存在 | high/critical |
| 2 | **Lint 合规性** | frontmatter / 断链 / 命名 / 标签 | high/medium/low |
| 3 | **内容质量** | 低置信度占比 / 矛盾信号 / 孤立页面 | high/medium/low |
| 4 | **双索引同步** | 机器索引 ↔ 人类索引覆盖率 | high/medium |
| 5 | **外部竞品对标** | 9 维度横向对比 + 差距分析 + 改进建议 | medium/low/info |

健康评分 = 100 - Σ(问题 × 严重度权重)

- 90+ = excellent
- 70-89 = good
- 50-69 = fair
- <50 = poor

---

## 可自动修复 vs 需人工

### ✅ 可自动修复（Self-Healing）

| 问题类型 | 修复策略 |
|---------|---------|
| frontmatter 缺失 | 自动补全默认 frontmatter |
| 字段缺失（type/title/created 等） | 按类型推断填充默认值 |
| confidence 无效值 | 修正为 `medium` |
| status 无效值 | 修正为 `draft` |
| tags 缺少 flow-wiki | 添加 `flow-wiki` 标签 |
| 缺少必备目录 | 自动创建目录 |
| 首页板块缺失 | 创建 MOC 模板 |
| 双索引不同步 | 调用 `sync_dual_index.py` |
| 文件名不规范 | 替换非法字符后重命名 |

### ❌ 需人工审核

| 问题类型 | 原因 |
|---------|------|
| 悬空链接 | 不确定正确目标，需人工判断 |
| sources 为空 | 证据链需要人工补充原始资料 |
| 内容矛盾 / 疑似幻觉 | 语义级判断，AI 可能误判 |
| 低置信度过高 | 需要补充高质量原始资料 |
| 孤立页面 | 相关链接需要人工选择 |

---

## 定时调度

### Cron 时间表

GitHub Actions 使用 **UTC 时间**，北京时间 = UTC + 8。

| 北京时间 | UTC 时间 | Cron 表达式 |
|---------|---------|------------|
| 09:00 | 01:00 | `0 1 * * *` |
| 12:00 | 04:00 | `0 4 * * *` |
| 15:00 | 07:00 | `0 7 * * *` |
| 18:00 | 10:00 | `0 10 * * *` |
| 21:00 | 13:00 | `0 13 * * *` |
| 00:00 | 16:00 | `0 16 * * *` |
| 03:00 | 19:00 | `0 19 * * *` |
| 06:00 | 22:00 | `0 22 * * *` |

当前配置：**每 3 小时一次**（北京时间 9/12/15/18/21/0/3/6 点）

```yaml
cron: '0 1,4,7,10,13,16,19,22 * * *'
```

### 手动触发

也可以在 GitHub Actions 页面手动触发 `workflow_dispatch`，填写触发原因。

---

## 分支策略

### 修复分支命名

```
refactor/ai-self-healing-YYYYMMDD-HHMMSS
```

每次运行创建独立分支，避免覆盖。

### PR 流程

```
main → 自检 → 自愈 → refactor/ai-self-healing-xxx → 开 PR → 人工审核 → 合并
         ↑                                          ↓
         └──── 无变更则不开 PR，直接结束 ────────────┘
```

**关键原则**：AI 修复从不直接合 main，必须人工审核。

---

## 上下文控制（大项目优化）

当知识库超过 50 万 token 时，需要控制扫描范围，避免上下文溢出。

### 配置方式

在 `_scripts/self_check.py` 顶部调整：

```python
SCAN_PRIORITY = [
    "wiki/concepts",    # 优先扫描核心概念
    "wiki/playbooks",   # 操作手册
    "wiki/criteria",    # 判据体系
    "raw/laws",         # 法律原文
]

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    ".obsidian",
    "__pycache__",
}
```

### 建议

- 100 页以内：全量扫描，无压力
- 100-500 页：设置 SCAN_PRIORITY，优先核心目录
- 500 页以上：分批次扫描，每次只扫一个分类目录

---

## 外部竞品对标（强制要求）

### 为什么必须对标

FlowWiki 不是闭门造车。每次自检必须同步扫描 GitHub 同类项目，做**横向 + 纵向对比**，保持对生态的敏感度。

- **横向对比**：同维度能力矩阵对比，识别哪些是标配、哪些是差异化优势
- **纵向对比**：跟踪头部竞品的演进速度，判断自己是在拉开差距还是被追赶

### 九维度对标矩阵

| 维度 | FlowWiki 水平 | 权重 |
|------|--------------|------|
| 防幻觉机制 | ACE Generator→Reflector→Curator 三 agent 制约 | ⭐⭐⭐ |
| 跨会话记忆 | A-MEM Zettelkasten 卡片，零数据库依赖 | ⭐⭐⭐ |
| 多 agent 兼容 | Claude Code / Codex / Gemini / Amp / WorkBuddy 五家 | ⭐⭐ |
| 人类 UX | 双索引（机器 index + 人类 6 板块 MOC） | ⭐⭐ |
| 业务可插拔 | L7 场景层外壳，industry.yaml 适配器 | ⭐⭐⭐ |
| 变更追溯 | SpecCoding 七阶段 + openspec/changes/ | ⭐⭐ |
| 知识复利到能力 | 任务→知识→Skill 三元组，O(1) 调用 | ⭐⭐⭐ |
| 自适应检索 | BM25 → nano-graphrag → LightRAG 三档 | ⭐⭐ |
| 矛盾追踪 | conflict/ 目录显式记录，不静默覆盖 | ⭐⭐ |

### 对标输出

每次对标自动生成：

1. **竞品总览表**：Star / Fork / 创建时间 / 语言 / 9 维度能力标记
2. **九维度对比矩阵**：每个维度下各竞品的能力等级和信号强度
3. **差距分析**：按"紧迫度"排序的改进建议
   - 🔴 高紧迫：≥80% 竞品已具备，属基础标配
   - 🟡 中紧迫：过半竞品具备，需持续领先
   - 🟢 低紧迫：少数竞品有，是差异化护城河
4. **反思与行动**：保持优势 / 持续加固 / 必须警惕 三栏

### 对标白名单

默认对标 12 个精选竞品（`COMPETITOR_WHITELIST`），涵盖：
- LLM Wiki 类
- Obsidian + AI 类
- 知识复利 / Skill 类
- GraphRAG 类

可在 `_scripts/benchmark_competitors.py` 中增减。

### 跳过对标

调试时可临时跳过：

```bash
FLOW_WIKI_SKIP_BENCHMARK=1 python _scripts/self_check.py report.json
```

---

## 本地手动运行

```bash
cd /path/to/flowwiki

# 1. 自检（输出 JSON 报告）
python _scripts/self_check.py self-check-report.json

# 2. 自愈（读取报告，执行修复）
python _scripts/self_heal.py self-check-report.json heal-report.json

# 3. 查看修复结果
cat heal-report.json
```

---

## 常见问题

### Q: AI 修复把内容改错了怎么办？

A: 所有修复都走 PR，不直接合 main。审核时发现问题可以直接在 PR 里修改或关闭 PR。

### Q: 为什么有些问题不自动修复？

A: 涉及语义判断的（如断链目标、内容矛盾、证据链补充）AI 没有足够上下文做正确判断，强制修复可能引入错误。

### Q: 可以修改修复频率吗？

A: 修改 `.github/workflows/ai-self-healing.yml` 中的 cron 表达式即可。注意是 UTC 时间。

### Q: 自愈后健康评分还是低怎么办？

A: 说明存在大量需人工修复的问题（如 sources 为空、内容矛盾）。查看自检报告中的 `fixable=false` 项，逐一人工处理。

### Q: 竞品对标分析的准确性如何？

A: 对标基于 README 和项目描述的关键词信号分析，只能做**粗粒度**的能力判断，不能替代人工调研。主要价值是：
- 快速发现生态新趋势
- 识别"大家都做了我们还没做"的基础项
- 记录我们的差异化优势是否仍然成立

高紧迫项建议人工核实后再决策。

### Q: 可以增减对标竞品吗？

A: 可以，编辑 `_scripts/benchmark_competitors.py` 顶部的 `COMPETITOR_WHITELIST` 列表即可。

---

## 相关文件

- 自检引擎: [self_check.py](file:///Users/mac/Desktop/FlowWiki/_scripts/self_check.py)
- 自愈引擎: [self_heal.py](file:///Users/mac/Desktop/FlowWiki/_scripts/self_heal.py)
- 竞品对标引擎: [benchmark_competitors.py](file:///Users/mac/Desktop/FlowWiki/_scripts/benchmark_competitors.py)
- CI 配置: [ai-self-healing.yml](file:///Users/mac/Desktop/FlowWiki/.github/workflows/ai-self-healing.yml)
- Lint 工具: [lint.py](file:///Users/mac/Desktop/FlowWiki/_scripts/lint.py)
- ACE 反思: [ace_review.py](file:///Users/mac/Desktop/FlowWiki/_scripts/ace_review.py)
