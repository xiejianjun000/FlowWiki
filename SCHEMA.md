---
标题: 执法督察评查知识库 · FlowWiki Schema
layer: 10-元文档
type: schema
触发词: ["schema", "维护约定", "怎么改库", "入库规范", "ingest流程", "flowwiki"]
适用场景: LLM 每次 Ingest/Query/Lint 前读取本文件，作为统一维护纪律
关联法条: []
调用skill: [eco-review-kb]
风险等级: 🟡
version: 2.3
status: 现行
ingested: 2026-07-18T00:00:00+08:00
updated: 2026-07-21
tags: [10-元文档, schema, 现行, flowwiki]
confidence: high
sources: []
---

# FlowWiki SCHEMA — 知识库宪法

> 本库基于 FlowWiki 方法论（7 层架构），本文件为 LLM 维护公约。

## 1. 七层架构

| 层 | 名称 | 本库对应 | 说明 |
|----|------|---------|------|
| L1 | 知识编译层 | raw/ + wiki/ + 首页/ | 人类放 raw（自动打时间戳）、AI 编 wiki、人类用入口 |
| L2 | 检索增强层 | config.toml | BM25→nano-graphrag→LightRAG 自适应 |
| L3 | Spec-Driven 层 | spec/ + openspec/ | 全局设计 + 变更治理 |
| L4 | Agent 记忆层 | .memory/ (ace/gaps/zettelkasten/episodic/conflict/minority/ops) | ACE 反思 + A-MEM 卡片 + 缺口学习 + 少数派分支 |
| L5 | Skill 化层 | .agents/skills/enforcement-review/ | 7 个执法评查专属 Skill + 5 个通用操作 Skill |
| L6 | 多 Agent 层 | CLAUDE.md / AGENTS.md / CODEX.md / WORKBUDDY.md / GEMINI.md / HERMES.md | 8 家 agent 共享同一套知识库 |
| L7 | 场景层 | 首页/03_实战场景/ | 7 行业适配器可插拔，评查/督察/法条 3 大场景入口 |

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

### 通用 Skill（FlowWiki 方法论自带）
| Skill | 文件 | 用途 |
|-------|------|------|
| ingest | `.agents/skills/ingest/SKILL.md` | 入仓 ACE 反思循环 |
| query | `.agents/skills/query/SKILL.md` | 双索引查询 |
| lint | `.agents/skills/lint/SKILL.md` | 知识体检（含原文指针检查） |
| research | `.agents/skills/research/SKILL.md` | 跨页研究 |
| **fulltext** | `.agents/skills/fulltext/SKILL.md` | **按需加载 raw/ 全文（指针铁律配套）** |

## 3. 提示词（Prompts）

位置: `提示词库/task/enforcement-review/`

| Prompt | 触发场景 |
|--------|---------|
| 案卷评查.md | 用户提交案卷或询问评查结果 |
| 现场核查.md | 用户需要现场核查指导 |
| 法典衔接.md | 用户询问新旧法衔接 |

## 4. CIC 工作流

- **Collect（收集）**：人类拖资料到 `/raw/` → 自动打 `ingested` 时间戳 + 每日采集记录
- **Compile（编译）**：运行 `python .scripts/bootstrap.py --slug enforcement-review --strict`
- **Compound（复利）**：ACE 反思 + gap 学习 → 知识持续增长

## 5. 三验标准

| 验证 | 方法 | 达标线 |
|------|------|--------|
| 一验 lint | frontmatter + 断链 + **原文指针** | 0 缺 / 0 断 / **指针齐全** |
| 二验 graph | 孤立 + 密度 | 0 孤立 / 密度 ≥ 2.0 |
| 三验 hermes | LLM 评审 | pass / 评分 ≥ 7.0 |

## 6. 入库三标准（raw→wiki 编译必须遵守）

1. **格式标准** → `wiki/meta/入库文档格式标准.md`
   - 网页残留清洗（导航/版权/跳转提示）
   - 表格还原为 markdown 表格
   - 标题层级规范化（正文从 ## 起）
   - Generator 阶段执行

2. **质量标准** → `wiki/meta/入库质量标准.md`
   - 5 维度评分卡（信息密度/结构/溯源/独特性/可操作）
   - Curator 按分决策：≥9 优质入库、6-8 合格、3-5 待核、<3 退回

3. **原文指针铁律**（v2.1 新增，SCHEMA §1.3 升级条款）
   - 每个 wiki/ 页面**必须**包含 `## 原文指针` 段
   - 段内必须给出三字段：
     ```
     ## 原文指针
     - 全文路径：`../raw/<subdir>/<file>.md`
     - 引用规则：逐字引用到条/款/项，引用后回链本页
     - 加载方式：通过 `/fulltext` skill 按需 read
     ```
   - wiki/ 主体**只存摘要 + 判断要点**，禁止搬运全文（raw/ 已存原文，双写违反分层）
   - 指针有效性：路径必须指向真实存在的 raw/ 文件，lint 必须检查悬空指针
   - 全文搬运启发式检查：单页出现 ≥3 次"第X章"模式视为全文搬运，Curator 退回 Generator

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

## 8. Lint 增强（v2.3 · 4 项新增检查）

继承 Karpathy 原版结构扫描，FlowWiki v2.3 新增以下 4 项 lint 检查：

| # | 检查项 | 说明 | 严重级别 |
|---|--------|------|---------|
| 1 | **index 自动同步** | lint 运行后自动对比 wiki/ 文件列表与 wiki/index.md，缺失条目自动补全 | medium |
| 2 | **frontmatter 完整性** | 强制检查三空字段（触发词/适用场景/关联法条），空字段统计为可路由率扣分 | high |
| 3 | **wikilink 有效性** | 扫描所有 `[[xxx]]` 双链，目标不存在则标记为断链，区分文件缺失 vs Obsidian 路径差异 | high |
| 4 | **命名规范** | 检查文件名是否符合小写+连字符规范，中文文件名给出警告 | medium |

运行方式：
```bash
python _scripts/lint.py          # 全量检查（含 4 项新检查）
python _scripts/lint.py --quick  # 仅结构检查
python _scripts/lint.py --strict # 强制模式，任一 high 检查不通过返回非零退出码
```

## 9. Strict 强制执行模式（v2.3）

ACE 循环新增 `--strict` 标志，启用后 Curator 对以下条件零容忍：

| 条件 | strict 行为 | 默认行为 |
|------|------------|---------|
| 原文指针缺失 | 直接退回，不计数回退轮次 | 警告，允许 ≤3 轮修复 |
| 三空字段 | 禁止写入 wiki/，阻止 ingest 完成 | 记录 warning，允许后续修复 |
| frontmatter 格式错误 | 终止 ingest，要求人工干预 | 标记 confidence=low |
| 全文搬运检测触发（≥3 次"第X章"） | 直接拒收 | 退回 Generator 重写 |

启用方式：
```bash
python _scripts/ace_review.py --strict       # 单次强制
python _scripts/ingest_pipeline.py --strict  # 管线强制
```

## 10. 引用追踪链（v2.3）

每个 wiki/ 页面需维护从 wiki → raw → source 的完整引用链：

```
wiki/page.md
  └── ## 原文指针 → raw/file.md
        └── frontmatter.sources → [原始URL/法规号/文件路径]
```

Lint 检查项：
1. wiki/ → raw/ 指针路径有效
2. raw/ → sources 字段非空（入仓文件必须有来源记录）
3. 断链在任一环节均触发 `high severity` 告警

## 11. 知识缺口自动检测（v2.3）

ACE Curator 在 ingest 时自动检测知识缺口：

| 缺口类型 | 检测方法 | 响应 |
|---------|---------|------|
| **术语缺口** | 新页面提到术语但 wiki/ 中无对应解释页 | 生成 `.memory/gaps/term-*.md`，链接到待补充清单 |
| **法条缺口** | 引用法条号但 raw/ 中无对应法条全文 | 标记 `status: needs_raw`，阻止后续操作 |
| **场景缺口** | 新知识属于某场景但该场景尚无 playbook | 生成场景脚手架建议，写入 `.memory/gaps/scene-*.md` |
| **覆盖缺口** | 行业适配器中某子领域页面数为零 | 生成行业覆盖报告，写入 `ops/monitoring/coverage-*.md` |

缺口文件格式：`.memory/gaps/<type>-YYYYMMDD-NNN.md`，包含缺口描述、影响评估、优先级（P0/P1/P2）。

## 12. raw/ 入仓时间戳（v2.3）

每次将文件放入 raw/ 时，自动记录入仓元数据：

```yaml
# frontmatter 自动追加（ace_review.py v3.0）
ingested: 2026-07-21T13:30:00+08:00  # 入仓时间（ISO 8601）
updated: 2026-07-21T13:30:00+08:00   # 最后更新时间
```

```bash
# 每日采集记录自动生成
python _scripts/ingest_pipeline.py --log-daily  # 生成 raw/.log/YYYY-MM-DD.md
```

约束：
- `ingested` 字段由脚本自动设置，不可手动修改
- `updated` 仅在文件内容变化时更新（非重复更新）
- 每日采集记录自动追加到 `raw/.log/`，记录文件数、字节数、hash

## 13. 行业路由完整性（v2.3）

7 个行业适配器的路由覆盖验证：

| 适配器 | 覆盖子领域 | 限值表 | 状态 |
|--------|-----------|--------|------|
| enforcement-review | 办案/督察/评查 | 生态环境标准限值表 | ✅ |
| enterprise-compliance | 排污许可/环境义务 | 排放标准分级表 | ✅ |
| permit-management | 许可证全生命周期 | 许可类型×有效期矩阵 | ✅ |
| compliance-review | 合规检查清单 | 法规条款索引 | ✅ |
| audit-onsite | 审计现场问答 | 检查清单模板 | ✅ |
| case-review | 典型案例分析 | 案例要素模板 | ✅ |
| audit-prep | 审计准备工作 | 时间线+清单模板 | ✅ |

路由规则：行业适配器通过 `industry.yaml` 声明其 raw/ + wiki/ 路径前缀、专属 Skill 列表、限值表路径。bootstrap.py 启动时验证所有适配器路由可达。

## 14. 操作纪律

1. raw/ 只读，AI 绝不修改原始内容
2. wiki/ 写入必须经过 ACE 反思循环
3. 所有知识必须可追溯到 raw/ 原始证据
4. **每个 wiki/ 页面必须含 `## 原文指针` 段（v2.1 铁律）**
5. **禁止把 raw/ 全文搬运到 wiki/ 主体，需要逐字引用时调用 `/fulltext` skill**
6. **引用追踪链完整**：wiki/ → raw/ → sources 三环节不可断（v2.3）
7. **知识缺口自动检测**：ingest 时 ACE Curator 自动检测术语/法条/场景/覆盖四类缺口（v2.3）
8. 每次操作自动记录到 .memory/ops/YYYY-MM-DD.jsonl
9. 前端改动后必须运行 bootstrap.py 重新入库
10. **strict 模式**：生产环境 ingest 必须启用 `--strict` 标志（v2.3）

## 15. 验收红线

- 文件结构符合 7 层架构
- 命名规范统一（小写+连字符）
- frontmatter 完整（type/title/confidence/sources/status）
- **原文指针齐全**：每个 wiki/ 页面均含 `## 原文指针` 段，路径有效、引用规则明确
- **零全文搬运**：wiki/ 主体无大段法条/标准原文（raw/ 已存原文，禁止双写）
- ACE 三阶段全部通过（Generator→Reflector→Curator）
- 错误内容必须回退到上一版本，人类可否决 AI 输出

## 16. 冲突路由矩阵（伴侣式记忆 §6 · v2.2 新增）

### 核心原则

FlowWiki 的 ACE 循环在处理"新证据 vs 已有知识"的冲突时，遵循"映射与补偿"双职责原则：

| 职责 | 说明 |
|------|------|
| **Mirror（映射）** | 反映用户的工作词汇、认知结构和上下文连续性 |
| **Compensate（补偿）** | 抵抗知识钙化、压制矛盾证据、库恩式范式僵化 |

只 Mirror → 强化盲点，变成回音壁。只 Compensate → 感觉敌对。两者兼备 → 真正的伴侣式记忆。

### 七种冲突类型与路由规则

| # | 冲突类型 | 领域 | 路由 | 理由 | ACE 对应 |
|---|---------|------|------|------|---------|
| **V1** | 用户词汇偏离 wiki 本体，无效用退化 | 操作性 | **Mirror** | 操作连续性优先，保留分歧标记供后续审查 | Reflector 记录 warning，Curator 决策不降级 |
| **V2** | 用户词汇偏离 + 查询效用跨周期退化 | 操作性→认识论 | **Compensate** | 效用退化触发重分类，CONSOLIDATE 以更高摩擦评分 | Curator 提高合并阈值至 0.7 |
| **V3** | 用户反复强化有害内容（安全风险） | 安全 | **Compensate**（无视效用） | 谄媚失败模式，效用信号在此不可靠 | Curator 强制 `reject`，不论评分 |
| **V4** | 新证据与高引力条目矛盾，单源、单周期 | 认识论 | **Buffer**（少数派分支） | 单源矛盾是候选信号，不是确认信号 | phase_minority_check → write_minority_branch |
| **V5** | 新证据与高引力条目矛盾，多源、多周期 | 认识论 | **Compensate**（整合候选） | 积累的缓冲压力超过在位者有效引力时整合 | check_minority_accumulation ≥ 3 → label_pending 覆盖 |
| **V6** | 高引力条目导致重复坏结果 | 认识论+安全 | **AUDIT override** | 连续性不能无限期保护产生坏结果的条目 | decay.py 归档 + AUDIT 暂停测试（待实现） |
| **V7** | 基础模型更新引入矛盾事实先验 | 认识论 | **External correction** | wiki 标记为下个 Curator 周期重审（依赖可分离架构） | 手动标记 `status: disputed` + 追加 log |

### V4→V5 缓冲压力管道（核心创新）

```
单源矛盾 (V4)          多源矛盾 (V5)          整合 (V5 Compensate)
    │                      │                       │
    ▼                      ▼                       ▼
Buffer 到             检查 .memory/minority/    Curator label_pending
.minority/minority-*.md  →  积累 ≥3 条独立证据 →  覆盖原 reject 决策
    │                      │                       │
    └──────────────────────┴───────────────────────┘
           每个 cycle 递增 1，最多保留 5 个 cycle
```
"""

### 少数派分支约束

- 分支文件存储在 `.memory/minority/minority-YYYYMMDD-NNN.md`
- 仅通过两个显式路径关闭：
  1. **Promotion**（晋升）：当积累 ≥3 条独立证据时，Curator 触发 `label_pending`
  2. **AUDIT 归档**：当在位条目保持负荷承载且分支在 ≥5 个 cycle 后无增长时
- **分支永不静默关闭** — 两个条件都必须被显式评估
- 衰减扫描（decay.py）跳过少数派分支中的条目

### 冲突路由不解决的问题

路由矩阵明确不处理以下情况：
- 校准参数（cycle 数、来源多样性阈值）— 留给实现和实证验证
- 结构性残差（基础模型中的全新坏信念）— 矩阵不捕获，需外部纠正

### 参考

- Miteski, S. (2026). *Memory as Metabolism: A Design for Companion Knowledge Systems*. arXiv:2604.12034
- panmcai/karpathy-wiki: `references/governance.md`（伴侣式记忆代谢模型）
- 实现脚本：`_scripts/ace_review.py` v3.0（minority branch）| `_scripts/decay.py`（DECAY + AUDIT）
