# FlowWiki

> AI 与人类协同复利的知识库方法论
>
> 版本：v0.7（M0-M6 已完成，M7 白皮书发布中，2026-07-17）

[![CI](https://github.com/xiejianjun000/FlowWiki/actions/workflows/ci.yml/badge.svg)](https://github.com/xiejianjun000/FlowWiki/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 一句话定义

**FlowWiki = Karpathy LLM Wiki × TRAE Work × ACE 反思循环 × A-MEM 卡片记忆 × SpecCoding 七阶段**

它让 AI 编译知识像复利一样积累，让人类像走工作流一样使用，让多 agent 像接力一样接手。

---

## 为什么需要 FlowWiki

### 现有方法的痛点

| 方法论 | 优点 | 致命短板 |
|--------|------|---------|
| **Karpathy LLM Wiki** | raw→wiki→schema 三层 + 4 操作，AI 自动编译复利 | 无记忆层 / 无人类 UX / 无变更管理 / 超 500 页爆 context |
| **TRAE Work** | 6 板块 + 7 场景，人类工作流闭环 | 知识不复利 / AI 无法接手 / 维护成本高 |
| **传统 RAG** | 任何规模可查询 | 每次重算 / 不积累 / 矛盾静默覆盖 |
| **现有 LLM Wiki 实现** | 单平台可用 | 绑死 Claude Code / 业务领域硬编码 / 工程化弱 |

### FlowWiki 的解法

| 痛点 | FlowWiki 解法 |
|------|--------------|
| AI 永久化幻觉 | **ACE 反思循环**：Generator→Reflector→Curator 三 agent 制约 |
| 跨会话记忆丢失 | **A-MEM 卡片**：每个 raw 生成 Zettelkasten 卡片，跨会话可读 |
| 人类入口缺失 | **双索引**：机器走 `wiki/index.md`，人类走 `00_首页/` 6 板块 MOC |
| 知识不复利 | **任务→知识→Skill 三元组**：高频任务自动抽象为 O(1) 调用的 skill |
| 变更不可追溯 | **SpecCoding 七阶段**：每个变更走 openspec/changes/ |
| 规模超 200 页爆 context | **双索引 + 自适应检索**：BM25→nano-graphrag→LightRAG |
| 单平台绑定 | **CLAUDE.md + AGENTS.md 双 bootstrap**：5 家 agent 通吃 |
| 业务领域硬编码 | **L7 场景外壳可插拔**：通用骨架 L1-L6 + 场景作为变量 |

---

## 6 层架构

```
┌──────────────────────────────────────────────────────────────┐
│ L7 场景层（业务外壳，可插拔）                                    │
│   生态环境 7 场景 / SaaS 行业 7 场景 / 任意领域场景               │
├──────────────────────────────────────────────────────────────┤
│ L6 多 agent 接手层                                              │
│   CLAUDE.md (Claude Code) + AGENTS.md (Codex/Amp/Gemini/WorkBuddy) │
├──────────────────────────────────────────────────────────────┤
│ L5 Skill 化层                                                   │
│   4 操作 skill (ingest/query/lint/research) + 高频任务自动抽象    │
├──────────────────────────────────────────────────────────────┤
│ L4 Agent 记忆层 ★ FlowWiki 独有                                  │
│   A-MEM 卡片（Zettelkasten）+ ACE 反思循环（三 agent 制约）        │
├──────────────────────────────────────────────────────────────┤
│ L3 Spec-Driven 层                                                │
│   spec/ 全局设计 + openspec/changes/<name>/ 单任务变更             │
├──────────────────────────────────────────────────────────────┤
│ L2 检索增强层（自适应插件）                                        │
│   ≤100 页 BM25+CJK → 100-500 nano-graphrag → 500+ LightRAG       │
├──────────────────────────────────────────────────────────────┤
│ L1 知识编译层（双索引，核心骨架）                                   │
│   raw/ (只读) + wiki/ (AI 编译) + 00_首页/ (TRAE 6 板块人类 UX)    │
└──────────────────────────────────────────────────────────────┘
```

详细设计见 [spec/design.md](./spec/design.md)。

---

## 三大创新招牌

### 创新 A：任务→知识→Skill 三元组

```
任务层（openspec/changes/） → 知识层（wiki/） → Skill 层（.claude/skills/）
       ↑                                                │
       └────────── O(1) 调用 ──────────────────────────┘
```

- Karpathy 只有 raw→wiki 两层（O(n) 查询）
- TRAE 只有任务→流程（不复利）
- FlowWiki 引入第三层 Skill，让"复利"从知识扩展到能力，下次同类任务 O(1) 调用

### 创新 B：ACE 反思循环嵌入 ingest

```
┌──────────────┐
│  Generator   │ ← 根据 raw 生成摘要
└──────┬───────┘
       ▼
┌──────────────┐
│  Reflector   │ ← 批判：找矛盾/幻觉/过时
└──────┬───────┘
       ▼
┌──────────────┐
│   Curator    │ ← 决策：入 wiki / 标"待核" / 触发 conflict/
└──────────────┘
```

- Karpathy 的 lint 只扫结构不扫内容
- FlowWiki 在 ingest 时三 agent 制约，错误知识不进 wiki

### 创新 C：双索引（机器 + 人类）

| 索引 | 受众 | 形态 |
|------|------|------|
| `wiki/index.md` | AI agent | 紧凑扁平（1000 页只占 50KB） |
| `00_首页/` 6 板块 | 人类 | TRAE 风格 MOC + Dataview 看板 |

- 两者内容可重复但呈现不同
- 机器走 index，人类走 6 板块，互不干扰
- 解决 Karpathy "500 页爆 context" 痛点

---

## 快速开始（M1 完成后可用）

```bash
# 1. 克隆脚手架
git clone https://github.com/<your-name>/flowwiki-template.git my-wiki
cd my-wiki

# 2. 选择 agent bootstrap
# Claude Code 用 CLAUDE.md，其他用 AGENTS.md

# 3. 投入第一篇 raw
mkdir -raw/articles
cp ~/some-article.md raw/articles/

# 4. 触发 ingest skill（在 Claude Code / Codex / WorkBuddy 中）
> 请按 ingest skill 把 raw/articles/some-article.md 入库
```

详细使用见 `docs/getting-started.md`（M7 阶段补全）。

---

## 核心操作

FlowWiki 继承 Karpathy 的 4 操作，并在每个操作中嵌入创新：

| 操作 | Karpathy 原教 | FlowWiki 增强 |
|------|--------------|--------------|
| **ingest** | 单 agent 生成摘要 | ★ ACE 三 agent 反思循环 + A-MEM 卡片生成 |
| **query** | 读 index + 加载相关页 | ★ 答案回存 episodic + 检查是否值得抽象 skill |
| **lint** | 扫结构（悬空/孤儿/缺口） | ★ 加扫矛盾未解决 + confidence 不匹配 |
| **research** | （Karpathy 未定义） | ★ 跨页综合研究 + 自动生成 comparison 页 |

每个操作有对应的 `.claude/skills/<op>/SKILL.md` 和 `.agents/skills/<op>/SKILL.md`，5 家 agent 都能直接调用。

### Skill vs Prompt：什么时候用哪个

| 用 Skill | 用 Prompt |
|----------|----------|
| 高频操作（≥3 次同类任务） | 一次性或低频（≤2 次） |
| 多步骤工作流（如 ingest 7 步） | 单步骤操作或风格切换 |
| 跨场景通用（如 lint 体检） | 场景专属引导（如"用执法者视角回答"） |
| 有明确输入输出契约 | 探索性实验（还没形成标准流程） |
| 长期维护、版本管理 | 用完即弃，不持久化 |

**升级路径**：Prompt（探索期）→ 高频使用 ≥3 次 + 流程可标准化 → **升级为 Skill**（O(1) 调用）

详细规则见 [spec/design.md § L5 设计决策](./spec/design.md#l5-设计决策skill-vs-prompt-边界规则)。

---

## 与现有方法论的对比

| 维度 | Karpathy LLM Wiki | TRAE Work | 传统 RAG | **FlowWiki** |
|------|------------------|-----------|---------|------------|
| 知识复利 | ✅ | ❌ | ❌ | ✅ |
| 人类 UX | ❌ | ✅ | ❌ | ✅ 双索引 |
| AI 接手友好 | 🟡 仅 Claude | ❌ | ❌ | ✅ 5 家 agent |
| 防幻觉 | ❌ lint 只扫结构 | N/A | ❌ | ✅ ACE 三 agent |
| 跨会话记忆 | ❌ | ❌ | 🟡（向量库） | ✅ A-MEM 卡片 |
| 变更追溯 | ❌ | ❌ | ❌ | ✅ SpecCoding |
| 业务可插拔 | ❌ | ❌ | ❌ | ✅ L7 场景外壳 |
| 规模上限 | 200 页 | 无限（但人工） | 万页 | 自适应 |

---

## 里程碑路线图

| 里程碑 | 名称 | 状态 |
|--------|------|------|
| M0 | 全局 spec 设计 | ✅ 已完成 |
| M1 | 骨架脚手架 | ✅ 已完成 |
| M2 | 4 操作 skill 实现 | ✅ 已完成 |
| M3 | ACE 反思循环 + A-MEM ★ | ✅ 已完成 |
| M4 | 双索引同步 | ✅ 已完成 |
| M5 | L7 场景参考实现 | ✅ 已完成 |
| M6 | 多 agent 兼容矩阵 | ✅ 已完成 |
| M7 | 方法论白皮书发布 | ✅ 已完成 |

详细任务见 [spec/tasks.md](./spec/tasks.md)。

---

## 设计哲学

### 1. 物理分离原则（继承 Karpathy）

思考、规格、执行在物理上分开。raw 只读 / wiki AI 写 / spec 人写。三者不交叉。

### 2. 极简优先

默认零依赖：纯 Markdown + frontmatter + git。L2 检索、L4 记忆都不强制引入数据库。

### 3. 双侧友好

AI 走 index.md，人类走 6 板块。两者并行不冲突。

### 4. 工作流闭环（继承 TRAE）

每个任务都走"接任务 → spec → 执行 → archive → 复利"五步，不留孤立操作。

### 5. 防止幻觉永久化（FlowWiki 原创）

ACE 三 agent 制约 + 矛盾显式标注 + 旧说法被推翻时不静默覆盖。

### 6. 复利飞轮

raw → wiki → skill → 自动调用 → 新任务 → 新 raw → wiki 增厚 → skill 增多 → ...

---

## 适用场景

### 适合 FlowWiki 的场景

- 个人/团队知识库（100-10000 页规模）
- AI agent 长期维护的专业领域知识库
- 需要多 agent 接手的协作型知识库
- 业务领域可插拔的多场景知识库

### 不适合 FlowWiki 的场景

- 单次查询的临时知识需求（用 RAG 即可）
- 必须用云服务的多租户 SaaS（FlowWiki 是本地优先）
- 必须图形界面（FlowWiki 依赖 Obsidian 等第三方可视化）
- 万页以上且需秒级查询（用专业向量数据库）

---

## 参考与致谢

FlowWiki 站在以下巨人的肩膀上：

| 来源 | 贡献 |
|------|------|
| [Karpathy LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | 三层架构 + 4 操作原教 |
| [TRAE Work 官方知识库](https://mp.weixin.qq.com/s/Fu-nLAF_iIhOy77anlqcJQ) | 6 板块 + 7 场景人类 UX |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | Spec-Driven 变更管理 |
| [SuperSpec / Superpowers](https://github.com/obra/superpowers) | 6 阶段执行节奏 |
| [A-MEM 论文（NeurIPS 2025）](https://github.com/agentros/A-MEM) | Zettelkasten 卡片记忆 |
| [ACE 论文（LangChain）](https://github.com/langchain-ai/ace) | Generator→Reflector→Curator 三 agent |
| [llm-wiki-agent (SamurAIGPT)](https://github.com/SamurAIGPT/llm-wiki-agent) | 5 平台 agent 兼容矩阵 |
| [llm-wiki CLI](https://github.com/krakiun/llmwiki) | BM25+CJK 检索 + Rust 扩展方案 |
| [nano-graphrag](https://github.com/gusye1234/nano-graphrag) | 轻量图谱检索 |
| [LightRAG](https://github.com/HKUDS/LightRAG) | 实体抽取 + 图谱增强 |
| [SpecCoding 模板](https://github.com/beautifulSoup/speccoding-template) | 七阶段工作流 |
| [claude-obsidian](https://github.com/karpathy/claude-obsidian) | `/wiki /save` 命令交互 |

---

## License

MIT（M1 阶段补全）

---

## 状态

✅ **当前阶段**：M0-M7 全部完成

📋 **已完成内容**：
- M0: 全局 spec 设计（含 Hermes 集成方案）
- M1: 骨架脚手架（SCHEMA.md/CLAUDE.md/AGENTS.md/config.toml）
- M2: 4 操作 skill 实现（ingest/query/lint/research）
- M3: ACE 反思循环 + A-MEM（ace_review.py + .memory/）
- M4: 双索引同步（sync_dual_index.py）
- M5: L7 场景参考实现（4 行业 × 2-4 场景）
- M6: 多 agent 兼容矩阵（CLAUDE.md/AGENTS.md/CODEX.md/WORKBUDDY.md）
- M7: 方法论白皮书发布（README.md + docs/）

📋 **试点验证**：环评与排污许可知识库（37 raw 文件 → ingest 成功）

📋 **文件统计**：FlowWiki 标准版 73 个文件，环评库试点 94 个文件

详见 [spec/tasks.md](./spec/tasks.md)。
