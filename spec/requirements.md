# FlowWiki — 全局需求规格

> 版本：v0.1（M0 全局设计阶段）
> 维护：人工主导，AI 仅在明确指示下修改
> 关联文档：[design.md](./design.md) / [tasks.md](./tasks.md) / [structure.md](./structure.md)

---

## 1. 项目定位

**FlowWiki** 是一个让 AI 与人类协同复利的知识库方法论。

它融合三套现有方法论的优势，并补齐各自短板：

| 来源 | 借鉴的"骨" | FlowWiki 补齐的短板 |
|------|-----------|------------------|
| Karpathy LLM Wiki（2026.04，5K+ star） | raw/wiki/schema 三层架构 + 4 操作（ingest/query/lint/index+log） | 无记忆层、无人类 UX、无变更管理、规模超 500 页爆 context |
| TRAE Work（字节跳动官方知识库） | 6 板块（导航/新手/功能/实战/工具/活动）+ 7 场景驱动 | 知识不复利、AI 无法接手、维护成本高 |
| OpenSpec + SuperSpec | Spec-Driven 七阶段 + spec delta 变更追踪 | 无 agent bootstrap、无业务场景外壳 |

**一句话定位**：用 Karpathy 的「AI 编译复利」做底座，用 TRAE Work 的「工作流闭环」做人类入口，用 ACE 反思循环 + A-MEM 卡片记忆做"防幻觉 + 跨会话"，用 SpecCoding 七阶段做变更治理——四位一体。

---

## 2. 核心痛点（必须解决）

| ID | 痛点 | 来源 |
|----|------|------|
| P1 | AI 编译的知识会永久化幻觉（lint 只扫结构不扫内容） | Karpathy LLM Wiki |
| P2 | 跨会话记忆丢失，AI 每次重新读 wiki | Karpathy LLM Wiki |
| P3 | 人类入口缺失，非 AI 用户无法使用知识库 | Karpathy LLM Wiki |
| P4 | 知识不复利，每次任务从零开始推理 | TRAE Work |
| P5 | 变更不可追溯，新旧知识冲突静默覆盖 | 二者共有 |
| P6 | 规模超 200 页 index.md 爆 context | Karpathy 原文 |
| P7 | 单平台绑定（只支持 Claude Code） | 现有所有实现 |
| P8 | 业务领域硬编码，无法跨领域复用 | 现有所有实现 |

---

## 3. 功能需求

### R1 — 6 层架构 + L7 场景外壳（必选）

```
L1 知识编译层    ← Karpathy raw/wiki + TRAE 6 板块人类 UX（双索引）
L2 检索增强层    ← 自适应：BM25+CJK（默认）→ nano-graphrag → LightRAG
L3 Spec-Driven 层 ← OpenSpec 全局 spec + openspec/changes/ 单任务变更
L4 Agent 记忆层   ← A-MEM 卡片 + ACE 反思循环（FlowWiki 独有）
L5 Skill 化层     ← 4 操作 skill + 高频任务自动抽象为 skill
L6 多 agent 接手层 ← CLAUDE.md + AGENTS.md 双 bootstrap
L7 场景层（业务外壳，可插拔） ← 通用骨架 + 领域场景作为变量
```

### R2 — 三大创新招牌（必选）

| 创新点 | 解决痛点 | 与现有方法论区别 |
|--------|---------|----------------|
| **A. 任务→知识→Skill 三元组** | P4 知识不复利 | Karpathy 只有 raw→wiki 两层；TRAE 只有任务→流程；引入第三层 Skill 让"复利"从知识扩展到能力，调用 O(1) 而非 O(n) |
| **B. ACE 反思循环嵌入 ingest** | P1 永久化幻觉 | Generator→Reflector→Curator 三 agent 循环，错误知识不进 wiki；Karpathy 的 lint 只扫结构 |
| **C. 双索引（机器+人类）** | P3 人类入口缺失 + P6 爆 context | 机器走 wiki/index.md（紧凑），人类走 00_首页/6 板块 MOC；两套入口互不干扰 |

### R3 — 检索自适应（必选）

| 规模 | 检索策略 | 启用方式 |
|------|---------|---------|
| ≤100 页 | 纯 BM25 + CJK 分词 | 默认 |
| 100-500 页 | nano-graphrag 图谱检索 | config.toml 切换 |
| 500+ 页 | LightRAG 实体抽取 | config.toml 切换 |
| 10000+ 页 | Rust+MCP（krakiun 方案） | V2 阶段引入 |

**铁律**：默认零向量库依赖，符合 Karpathy 极简精神。

### R4 — 记忆层纯 Markdown（必选）

- 记忆载体：`.memory/` 目录，全部 Markdown + frontmatter
- 子目录：
  - `zettelkasten/` — A-MEM 卡片（每个 raw 入库时生成）
  - `episodic/` — 跨会话记忆（每次 query 答案回存）
  - `conflict/` — 矛盾追踪（新旧知识冲突）
- **零数据库依赖**：不引入 sqlite / LanceDB / Mem0 server
- **回滚机制**：通过 git，不用 DB 回滚

### R5 — 多 agent bootstrap 兼容（必选）

- `CLAUDE.md` — Claude Code 专属入口
- `AGENTS.md` — Codex / Amp / Gemini / WorkBuddy 等价入口
- 兼容矩阵参考 `llm-wiki-agent`（5 平台 CLI，无需 API key）
- V2 阶段引入 MCP server，让任意 MCP 客户端可用

### R6 — 强制 SpecCoding 七阶段工作流（必选）

每个变更必须走：

| # | 阶段 | 产出 |
|---|------|------|
| 1 | git branch | 独立 feature 分支 |
| 2 | openspec scaffold | 空变更目录 + .openspec.yaml |
| 3 | brainstorming | proposal.md + design.md + specs/ |
| 4 | writing-plans | plan.md（落在 openspec/changes/<name>/ 内） |
| 5 | executing-plans | 严格按 plan.md 执行代码变更 |
| 6 | archive | 变更移入 openspec/changes/archive/ |
| 7 | git merge | 合回主分支 |

### R7 — 落地形态（必选）

**方法论白皮书 + 脚手架模板**，分两份交付物：

| 交付物 | 形态 | 受众 |
|--------|------|------|
| 方法论白皮书 | README.md + spec/ 全套 | 想理解原理的人 |
| 脚手架模板 | 空目录 + 模板 + 脚本 | 想直接用的人 |

V2 阶段补充：通用领域参考实现（7 场景可插拔架构）。

---

## 4. 角色边界（红线）

FlowWiki **不做** 以下事情：

| 红线 | 理由 |
|------|------|
| 不做向量库默认依赖 | 违反 Karpathy 极简；规模 ≤200 页纯 BM25 已够 |
| 不做单平台绑定 | 必须支持 Claude Code/Codex/Amp/Gemini/WorkBuddy 五家 |
| 不做业务领域硬编码 | 场景作为 L7 业务外壳，可插拔 |
| 不做"零人工审核全自动 ingest" | ACE Curator 必须有人类 review 机制（可配置自动 vs 半自动） |
| 不做 OS 级运行时（Letta/MemGPT） | 违背极简原则 |
| 不做角色化 agent（BMAD PM/架构/Dev） | 与 taiji-design 团队 SOP 重叠 |
| 不引入 sqlite/pg（Nocturne 模式） | git 已足够回滚 |

---

## 5. 验收标准

| 验收点 | 标准 |
|--------|------|
| M0 全局 spec 完成 | 4 个 spec 文件齐备 + 用户审阅通过 |
| M1 骨架脚手架 | CLAUDE.md/AGENTS.md/SCHEMA.md/wiki/index.md/wiki/log.md/_templates/ 齐备 |
| M2 4 操作 skill | ingest/query/lint/research 都可执行 + lint 归零 |
| M3 ACE + A-MEM | ACE 三 agent 循环跑通 + Zettelkasten 卡片生成 |
| M4 双索引 | 6 板块 MOC + index.md 自动同步 |
| M5 L7 场景 | 通用 7 场景参考实现 + 可拔插验证 |
| M6 多 agent | Claude Code/Codex/Amp 三家都能接手维护 |
| M7 白皮书 | README.md + gist 发布 |

---

## 6. 非目标（明确排除）

- 不重写 Karpathy LLM Wiki 原教旨
- 不替代 SpecCoding（FlowWiki 是 SpecCoding 的脚手架产物，不是替代）
- 不做云服务（FlowWiki 是本地优先的 Markdown 仓库）
- 不做图形界面（依赖 Obsidian 等第三方可视化）
- 不绑定具体业务领域（7 场景仅为参考实现）
