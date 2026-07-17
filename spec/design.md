# FlowWiki — 架构设计

> 版本：v0.1（M0 全局设计阶段）
> 关联文档：[requirements.md](./requirements.md) / [tasks.md](./tasks.md) / [structure.md](./structure.md)

---

## 1. 6 层 + L7 场景总览

```
┌─────────────────────────────────────────────────────────────────┐
│ L7 场景层（业务外壳，可插拔）                                       │
│   通用 7 场景（根因分析/合规审查/证照管理/企业合规/现场核查/案卷评查/审计准备）                  │
├─────────────────────────────────────────────────────────────────┤
│ L6 多 agent 接手层                                                 │
│   CLAUDE.md (Claude Code) + AGENTS.md (Codex/Amp/Gemini/WorkBuddy) │
├─────────────────────────────────────────────────────────────────┤
│ L5 Skill 化层                                                     │
│   4 操作 skill (ingest/query/lint/research) + 高频任务自动抽象 skill │
├─────────────────────────────────────────────────────────────────┤
│ L4 Agent 记忆层 ★ FlowWiki 独有创新                                 │
│   A-MEM 卡片（Zettelkasten）+ ACE 反思循环（Generator→Reflector→Curator）│
├─────────────────────────────────────────────────────────────────┤
│ L3 Spec-Driven 层                                                  │
│   spec/ 全局设计 + openspec/changes/<name>/ 单任务变更               │
├─────────────────────────────────────────────────────────────────┤
│ L2 检索增强层（自适应插件）                                          │
│   ≤100 页 BM25+CJK → 100-500 nano-graphrag → 500+ LightRAG         │
├─────────────────────────────────────────────────────────────────┤
│ L1 知识编译层（双索引，核心骨架）                                     │
│   raw/ (只读) + wiki/ (AI 编译) + 00_首页/ (TRAE 6 板块人类 UX)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 各层详细设计

### L1 知识编译层（双索引核心）

**物理分离原则**（继承 Karpathy）：
- `raw/` 只读归档，AI **绝不**修改原始资料
- `wiki/` AI 编译层，LLM 撰写，人几乎不直接编辑
- `00_首页/` 人类 UX 入口，TRAE 6 板块

**双索引机制**（FlowWiki 创新招牌 C）：

| 索引 | 受众 | 形态 | 更新机制 |
|------|------|------|---------|
| 机器索引 `wiki/index.md` | AI agent | 紧凑扁平列表（标题 + 一句话 + 链接） | LLM ingest 时自动追加 |
| 人类索引 `00_首页/00_首页.md` | 人类 | TRAE 6 板块 MOC（带 Dataview 看板） | LLM 编译 + 人类策展 |

**两者关系**：互不干扰。AI 走 index.md（紧凑，避免爆 context），人类走 6 板块（认知友好，分步引导）。两者内容**可重复但呈现不同**。

**wiki/ 子目录**：
```
wiki/
├── index.md          ← 机器索引（紧凑）
├── log.md            ← 操作日志（追加式）
├── concepts/         ← 概念页（是什么）
├── playbooks/        ← 操作手册（怎么做）
├── cases/            ← 案例页（实例）
├── comparisons/      ← 对比页（A vs B）
└── meta/             ← 元文档（设计原则、命名规范）
```

**页面类型**（通用类型 + 扩展）：
- concept / playbook / case / comparison / source-summary / workflow / prompt / tool

**frontmatter 强制规范**：
```yaml
---
type: concept | playbook | case | comparison | source-summary | workflow | prompt | tool
title: <页面标题>
created: 2026-07-17
updated: 2026-07-17
confidence: high | medium | low   # low 必须标"待核"
sources: ["[[raw/xxx]]"]           # 必须溯源到 raw
tags: [flow-wiki, <layer>, <topic>]
status: draft | reviewed | archived
---
```

### L2 检索增强层（自适应插件）

**配置文件**：`.llm-wiki/config.toml`

```toml
[retrieval]
mode = "bm25"           # bm25 | nano-graphrag | lightrag
cjk_tokenizer = "jieba" # 中文分词
auto_switch_threshold = 100  # 自动切换 nano-graphrag 阈值
auto_switch_threshold_2 = 500 # 自动切换 lightrag 阈值

[index]
index_file = "wiki/index.md"
log_file = "wiki/log.md"

[lint]
check_dangling = true
check_orphan = true
check_frontmatter = true
check_confidence = true
```

**铁律**：默认 `mode = "bm25"`，零向量库依赖。规模超过阈值时 AI 提示用户切换。

### L3 Spec-Driven 层（变更治理）

**两级 Spec 体系**（继承 SpecCoding）：

| 层级 | 位置 | 用途 |
|------|------|------|
| 项目级 | `spec/` | 全局设计（requirements/design/tasks/structure/devlog） |
| 需求级 | `openspec/changes/<name>/` | 单任务变更（proposal/design/specs/tasks/plan） |

**七阶段工作流**：
1. git branch → 独立 feature 分支
2. openspec scaffold → 空变更目录
3. brainstorming → proposal.md + design.md
4. writing-plans → plan.md
5. executing-plans → 严格按 plan.md 执行
6. archive → 移入 openspec/changes/archive/
7. git merge → 合回主分支

**「谁写谁改」原则**：
- `spec/requirements.md` / `spec/design.md` — 人工主导，AI 仅在明确指示下修改
- `spec/tasks.md` 状态 — AI 归档后自动勾选
- `spec/devlog.md` — 每次 PR 合并后 AI 追加
- `spec/structure.md` — 顶层目录变动时 AI 更新

### L4 Agent 记忆层 ★（FlowWiki 创新招牌 A + B）

**A-MEM 卡片记忆**（来源：NeurIPS 2025 A-MEM 论文，与 Zettelkasten 理念契合）

每个 raw 文件入库时，AI 生成一张 Zettelkasten 卡片：

```markdown
# ZK-2026-07-17-001

> 一句话主旨

## 关键论点
- ...

## 关联卡片
- [[ZK-2026-07-17-002]]
- [[ZK-2026-07-15-005]]

## 溯源
- raw 来源：[[raw/xxx]]
- 入库时间：2026-07-17
- confidence: high
```

存放位置：`.memory/zettelkasten/YYYY-MM-DD-NNN.md`

**ACE 反思循环**（来源：LangChain ACE 论文）：

ingest 时三 agent 循环：

```
┌─────────────────────────────────────┐
│  Generator（生成器）                  │
│  根据 raw 生成摘要 + ZK 卡片           │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Reflector（反思器）                  │
│  批判 Generator 输出：                │
│  - 找矛盾（与现有 wiki 冲突？）        │
│  - 找幻觉（无 raw 支撑的论断？）       │
│  - 找过时（旧说法被推翻？）            │
│  输出 issues 列表                    │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Curator（策展者）                    │
│  根据 issues 决定：                   │
│  - 接受入 wiki（无 issue）            │
│  - 标"待核"（confidence=low）         │
│  - 触发 conflict/ 追踪（有矛盾）      │
│  - 退回 Generator（重大 issue）        │
└─────────────────────────────────────┘
```

**循环终止条件**：Reflector 不再 raise issue，或达到 3 轮上限。

**矛盾追踪**：

`.memory/conflict/<topic>.md` 文件结构：
```markdown
# 矛盾：<topic>

## 旧说法
- [[wiki/concepts/old-view]]
- 溯源：[[raw/old-source]]

## 新说法
- [[wiki/concepts/new-view]]
- 溯源：[[raw/new-source]]

## 状态
- 已解决 / 待人工裁决 / 自动覆盖（需 confidence=high + 新 source 权威）

## 决议时间
2026-07-17
```

**episodic 跨会话记忆**：

每次 query 答案回存：`.memory/episodic/YYYY-MM-DD-NNN.md`

```markdown
# Episodic-2026-07-17-001

## 问题
<用户原始问题>

## 答案
<AI 整合答案>

## 引用
- [[wiki/concepts/xxx]]
- [[wiki/playbooks/yyy]]

## 复利价值
- 是否值得提取为 playbook？是 / 否
- 是否值得抽象为 skill？是 / 否
```

### L5 Skill 化层（FlowWiki 创新招牌 A：三元组）

**4 个核心 skill**：

| Skill | 用途 |
|-------|------|
| `ingest` | 执行 ACE 反思循环入库流程 |
| `query` | 执行双索引查询 + 答案回存 |
| `lint` | 扫矛盾/孤立/缺口/悬空链 |
| `research` | 跨页研究 + 综合报告生成 |

**双格式部署**：
- `.agents/skills/<name>/SKILL.md` — Codex/Amp 格式
- `.claude/skills/<name>/SKILL.md` — Claude Code 格式（内容相同）

**高频任务自动抽象**：

每个 openspec/changes/<name>/ 完成后，AI 自动判断：
- 该任务是否高频（同类问题出现 ≥3 次）？
- 是否值得抽象为 skill？

若是，自动在 `.agents/skills/<name>/` + `.claude/skills/<name>/` 生成 skill 文件，记录：
- 触发条件
- 输入/输出契约
- 引用的 wiki 页
- 执行步骤

**Skill 复利**：调用 skill 是 O(1) 而非 O(n) 重新推理。

#### L5 设计决策：Skill vs Prompt 边界规则

**核心原则**：Skill 是"可复用的能力"，Prompt 是"一次性的指令"。

| 维度 | Skill | Prompt（提示词） |
|------|-------|-----------------|
| **频率** | 高频（≥3 次同类任务） | 低频（≤2 次或一次性） |
| **生命周期** | 长期维护，版本管理 | 用完即弃，不持久化 |
| **触发方式** | AI 自动识别场景后调用 | 用户显式输入 |
| **复杂度** | 多步骤工作流（带分支） | 单步骤操作或风格微调 |
| **复用范围** | 跨场景通用（FlowWiki 级别） | 场景专属或单任务专属 |
| **沉淀价值** | 值得长期维护（有 wiki 页引用） | 不值得抽象（无引用） |
| **存储位置** | `.claude/skills/<name>/SKILL.md` | `70_Prompt库/` 或直接在对话里 |

**判断流程**（AI 在每次任务完成后自动执行）：

```
任务完成
  ↓
同类问题出现过吗？（查 .memory/episodic/）
  ├─ 否 → 不升级，保持 prompt
  └─ 是，≥3 次？
      ├─ 否 → 记录到 episodic，不升级
      └─ 是 →
          ├─ 任务流程可标准化？（有明确输入/输出/步骤）
          │   ├─ 是 → ★ 升级为 skill
          │   └─ 否 → 保持 prompt
          └─ 任务依赖特定场景上下文？
              ├─ 是 → 升级为 L7 场景 skill
              └─ 否 → 升级为 L5 通用 skill
```

**5 类典型 prompt（不应升级为 skill）**：
1. **风格切换 prompt**：如"用正式公文语气回复"（只是调参数，无执行流程）
2. **一次性探索 prompt**：如"试试用 B 方法再分析一遍"（实验性质）
3. **用户偏好约束**：如"回答控制在 100 字内"（系统级指令，非任务）
4. **场景专属引导**：如"从执法者视角回答"（调视角，非操作）
5. **输出格式 prompt**：如"用表格输出"（调格式，非操作）

**4 类典型 skill（必须从 prompt 升级）**：
1. **重复性操作**：如"每次上传新稿都走 ACE 反思循环"（ingest skill）
2. **多步骤工作流**：如"知识体检 5 步（悬空→孤儿→frontmatter→矛盾→置信度）"（lint skill）
3. **跨场景通用**：如"任何问题先读 index.md 再加载 5-10 页"（query skill）
4. **有输入输出契约**：如"输入 raw 路径 + 场景标识 → 输出 wiki 页面 + ZK 卡片 + 索引更新"（ingest skill）

**升级为 skill 后的收益**：
- 调用从"AI 重新理解上下文并推理"（O(n)）降为"AI 加载预编译步骤并执行"（O(1)）
- 执行一致性提升（不会再因为不同会话中 AI 理解偏差导致输出不稳定）
- 可被多 agent 复用（skill 文件是 agent-agnostic 的 Markdown）

**Prompt 库存放与索引**：

```
FlowWiki/
├── 70_Prompt库/          ← 场景&功能提示词存档
│   ├── 01_生成类.md      ← "生成审计清单"/"生成分析方案"
│   ├── 02_校对类.md      ← "校对案卷程序合法性"/"校对数据一致性"
│   ├── 03_问句类.md      ← "从执法者视角回答"/"用企业视角解释"
│   ├── 04_拆解类.md      ← "拆解许可证为 N 项检查要点"
│   └── README.md         ← Prompt 索引（AI 和人都可读）
└── .claude/skills/       ← 已升级为 skill 的高频 prompt
    └── <name>/SKILL.md
```

**关键规则**：`70_Prompt库/` 里的 prompt 如果同一类的使用次数 ≥3，AI 自动触发升级检查——生成 `.claude/skills/<name>/SKILL.md`，并把原 prompt 标记为 `⚠️ 已升级为 skill，请用 /<skill-name>`。

### L6 多 agent 接手层

**双 bootstrap**：

`CLAUDE.md` 内容结构（Claude Code 入口）：
```markdown
# FlowWiki Bootstrap (Claude Code)

## 角色
你是 FlowWiki 知识库的 AI 管理员。

## 边界
- 不修改 raw/ 任何文件
- 不绕过 ACE 反思循环直接写 wiki/
- 不静默覆盖已有页面（必须走 conflict/）

## 启动协议
1. 先读 spec/SCHEMA.md
2. 读 wiki/index.md 了解全貌
3. 读 .memory/zettelkasten/ 最新 10 张卡片
4. 接收用户指令

## 4 操作 skill
- ingest: .claude/skills/ingest/SKILL.md
- query: .claude/skills/query/SKILL.md
- lint: .claude/skills/lint/SKILL.md
- research: .claude/skills/research/SKILL.md
```

`AGENTS.md` 内容结构（Codex/Amp/Gemini/WorkBuddy 等价入口）：
```markdown
# FlowWiki Bootstrap (Generic Agent)

（与 CLAUDE.md 内容相同，但路径指向 .agents/skills/）
```

**兼容矩阵**（参考 llm-wiki-agent）：

| Agent | bootstrap 文件 | skills 目录 |
|-------|---------------|------------|
| Claude Code | CLAUDE.md | .claude/skills/ |
| Codex | AGENTS.md | .agents/skills/ |
| Amp | AGENTS.md | .agents/skills/ |
| Gemini CLI | AGENTS.md | .agents/skills/ |
| WorkBuddy | AGENTS.md | .agents/skills/ |

**V2 阶段**：MCP server，让任意 MCP 客户端可用（在 M6 后再考虑）。

### L7 场景层（业务外壳，可插拔）

**通用骨架**：FlowWiki 不绑定任何业务领域。

**场景作为变量**：用户在使用 FlowWiki 时，按以下方式注入场景：

```
00_首页/03_实战场景/<场景名>/
├── README.md       ← 场景说明
├── playbooks.md    ← 该场景的标准操作手册
├── cases.md        ← 该场景的案例索引
└── skills.md       ← 该场景专属 skill 索引
```

**参考实现**（M5 阶段）：通用 7 场景
1. 合规审查
2. 现场核查
3. 案卷评查
4. 证照管理
5. 企业合规
6. 审计准备
7. 根因分析

每个场景作为 L7 子模块，可独立启用/禁用。

#### L7 场景下 Skill 与 Prompt 的调用时机

当用户进入一个 L7 场景后，AI 按以下规则判断调用 skill 还是 prompt：

```
用户指令进入 L7 场景
  ↓
第一步：指令匹配 L5 通用 skill？
  ├─ "把这篇文章入库" → ingest skill（L5 通用）
  ├─ "查一下 X 的知识" → query skill（L5 通用）
  ├─ "跑一次知识体检" → lint skill（L5 通用）
  └─ "对比 A 和 B" → research skill（L5 通用）
  ↓ 不匹配
第二步：指令匹配 L7 场景 skill？
  ├─ "生成审计清单" → 场景 skill（00_首页/03_实战场景/审计准备/skills.md）
  ├─ "拆解许可证" → 场景 skill（00_首页/03_实战场景/证照管理/skills.md）
  ├─ "评审案卷" → 场景 skill（00_首页/03_实战场景/案卷评查/skills.md）
  └─ "根因分析" → 场景 skill（00_首页/03_实战场景/根因分析/skills.md）
  ↓ 不匹配
第三步：指令匹配 70_Prompt库/ 中的 prompt？
  ├─ 匹配到 → 加载对应 prompt 执行
  └─ 未匹配 → 新建 prompt 执行，完成后判断是否高频
  ↓
第四步：高频升级检查
  ├─ 同类 prompt 使用 ≥3 次 + 流程可标准化？
  │   └─ 是 → ★ 升级为场景 skill，更新场景 skills.md
  └─ 同类 prompt 跨 ≥2 场景出现？
      └─ 是 → ★ 升级为 L5 通用 skill
```

**L7 场景 skill 与 L5 通用 skill 的区别**：

| 维度 | L5 通用 skill | L7 场景 skill |
|------|-------------|--------------|
| 作用域 | 所有场景可用 | 仅当前场景可用 |
| 示例 | ingest/query/lint/research | 审计清单生成/许可证拆解/案卷评审 |
| 存位置 | `.claude/skills/<name>/` | `00_首页/03_实战场景/<场景>/skills.md` |
| 输入依赖 | 只依赖 raw + wiki（无场景上下文） | 依赖场景上下文（行业/法规/角色） |
| 升级路径 | prompt 跨 ≥2 场景出现 → L5 | prompt 仅在 1 个场景 ≥3 次 → L7 |

**Prompt 的场景归属**：

`70_Prompt库/` 中的 prompt 按 Tag 标注场景归属：

```markdown
## 生成审计清单

> 场景：[[03_实战场景/审计准备]]
> 类型：生成类
> 频率：使用 2 次 → 再 1 次触发升级检查
> 升级候选：是（流程可标准化：选择企业行业→匹配法规条款→生成检查项清单）

请根据目标企业的行业类型和许可证内容，生成一份审计准备清单...
```

**关键规则**：`70_Prompt库/` 中的 prompt 必须标注 `频率` 和 `升级候选` 字段——让 AI 和人类都能一眼判断该 prompt 是否该升级为 skill。

---

## 3. 三大数据流

### 3.1 ingest 流（新资料入库）

```
用户丢入 raw/<category>/
    ↓
[ACE Generator] 生成摘要 + ZK 卡片
    ↓
[ACE Reflector] 扫矛盾/幻觉/过时
    ↓ (有 issue 则退回 Generator)
[ACE Curator] 决策
    ├─ 接受入 wiki/concepts/ 或 wiki/playbooks/
    ├─ 标"待核"（confidence=low）
    └─ 触发 .memory/conflict/<topic>.md
    ↓
[更新] wiki/index.md + wiki/log.md + .memory/zettelkasten/
    ↓
[L2 检索] 增量更新索引
    ↓
[Lint] 检查悬空链/孤儿页
    ↓
[Skill 检查] 该任务是否高频？抽象为 skill？
```

### 3.2 query 流（用户查询）

```
用户提问
    ↓
[AI 先读] wiki/index.md + SCHEMA.md
    ↓
[加载] 相关 5-10 个 wiki 页 + ZK 卡片
    ↓
[整合] 答案 + 引用 + confidence
    ↓
[回存] .memory/episodic/ + wiki/playbooks/（若优质）
    ↓
[Skill 检查] 该问题是否高频？抽象为 skill？
    ↓
返回用户
```

### 3.3 lint 流（持续集成）

```
定时（或手动）触发
    ↓
[检查]
├─ 悬空链：[[xxx]] 无对应文件
├─ 孤儿页：无人引用的页面
├─ frontmatter 缺失
├─ confidence=low 但未标"待核"
├─ 矛盾未解决
└─ 旧说法被推翻但未更新
    ↓
[输出] _lint-report.md
    ↓
[fix_dangling.py] 自动修复简单悬空链
    ↓
[人工裁决] 复杂矛盾 → .memory/conflict/
    ↓
[更新] wiki/log.md
```

---

## 4. 关键设计决策

### 决策 1：为什么 ACE 三 agent 而不是单 agent？

**问题**：单 agent ingest 时，自己生成的内容自己审核，幻觉无法发现。

**方案**：Generator / Reflector / Curator 角色分离，互相制约。
- Generator 不知道会被批判，尽量产出
- Reflector 不创作，只挑刺
- Curator 不创作不挑刺，只决策入不入

**代价**：ingest 成本 3 倍。但若不这样做，错误知识永久化，后期清理成本 N 倍。

### 决策 2：为什么 A-MEM 卡片用 Markdown 而不是 sqlite？

**问题**：sqlite 需要部署、跨平台兼容性差、git diff 不可读。

**方案**：Markdown 文件 + frontmatter。
- 优点：git diff 可读、零依赖、跨 agent 兼容（任何 agent 都能读 md）
- 缺点：检索速度慢（但 ≤10000 张卡片够用）
- 风险缓解：超 10000 张时，引入 ripgrep + fzf 加速

### 决策 3：为什么双索引而不是统一 index？

**问题**：Karpathy 单一 index.md 超 500 页爆 context。

**方案**：机器走 wiki/index.md（紧凑扁平），人类走 00_首页/6 板块 MOC（认知友好）。
- 机器索引：每页一行，"标题 - 一句话 - 链接"，1000 页也只占 50KB
- 人类索引：分板块、带看板、有 Dataview 动态聚合
- 两者内容可重复但呈现不同

### 决策 4：为什么 Skill 化是 L5 而不是 L1？

**问题**：Skill 是任务沉淀，与知识沉淀不同维度。

**方案**：Skill 在 L5，是"知识复利"的二次升级——
- L1 知识复利：wiki 越来越厚（O(n) 查询）
- L5 能力复利：skill 越来越多（O(1) 调用）
- 顺序：raw → wiki（L1）→ 高频任务识别 → skill 抽象（L5）

### 决策 5：为什么场景是 L7 而不是 L1？

**问题**：场景绑死业务领域会失去通用性。

**方案**：场景作为 L7 业务外壳，可插拔。
- 通用骨架 L1-L6 适用于任何领域
- 场景作为 L7 子模块，独立启用/禁用
- 切换领域时，只换 L7，不动 L1-L6

---

## 5. 风险与权衡

| 风险 | 缓解 |
|------|------|
| ACE 三 agent 成本高 | 设 3 轮上限 + 低频任务可关 Reflector |
| 双索引维护成本 | LLM 自动同步，人类仅策展 |
| L7 场景过载 | 默认不启用，按需加载 |
| 多 agent 兼容性测试成本 | V1 只保证 Claude Code + WorkBuddy 两家，V2 扩展 |
| A-MEM 卡片膨胀 | 30 天后 AI 自动蒸馏到 wiki/meta/，旧卡片归档 |

---

## 6. 与现有 4 个库的关系

FlowWiki 是抽象方法论，**不是替代**现有库：

| 库 | 在 FlowWiki 中的角色 |
|----|------------------|
| 合规审查 | 工程化工具链（_scripts/）+ 持续运营看板的参考来源 |
| 证照管理 | Agent bootstrap（CLAUDE.md/AGENTS.md）+ 4 skill 的参考来源 |
| 企业合规AI管家 | L7 场景层 + 行业路由的参考来源 |
| 根因分析 | 判据体系作为 L7 根因分析场景的素材 |

M5 阶段以通用场景填充 FlowWiki 的 L7 参考实现。
