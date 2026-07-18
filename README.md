# FlowWiki

> Knowledge compounds like code. FlowWiki is the compiler.

[![CI](https://github.com/xiejianjun000/FlowWiki/actions/workflows/ci.yml/badge.svg)](https://github.com/xiejianjun000/FlowWiki/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Specs](https://img.shields.io/badge/Specs-7%E9%98%B6%E6%AE%B5-blue)](./spec/)
[![Agents](https://img.shields.io/badge/Agents-5%E5%AE%B6%E5%85%BC%E5%AE%B9-green)](./CLAUDE.md)
[![Scenes](https://img.shields.io/badge/Scenes-L7%E5%8F%AF%E6%8F%92%E6%8B%94-orange)](./storage/)

---

## Contents

- [Karpathy 的愿景](#karpathy-的愿景)
- [原始愿景的 6 个缺口](#原始愿景的-6-个缺口)
- [FlowWiki 的 6 个增强](#flowwiki-的-6-个增强)
- [架构总览](#架构总览)
- [三大创新招牌](#三大创新招牌)
- [快速开始](#快速开始)
- [核心操作](#核心操作)
- [Skill vs Prompt 决策指南](#skill-vs-prompt-决策指南)
- [与具体项目对比](#与具体项目对比)
- [Tech Stack](#tech-stack)
- [设计哲学](#设计哲学)
- [适用场景](#适用场景)
- [里程碑路线图](#里程碑路线图)
- [FAQ](#faq)
- [参考与致谢](#参考与致谢)
- [License](#license)

---

## Karpathy 的愿景

2025 年，Andrej Karpathy 提出了一个简洁而强大的类比：

> **Obsidian 是 IDE，LLM 是程序员，Wiki 是代码库。**

传统 RAG 是解释器——每次查询都重新推导。LLM Wiki 是编译器——知识只编译一次，保持最新，查询时直接读取。好的查询结果归档回 Wiki，探索本身也复利积累。

三层架构：`raw/`（不可变源文件）→ `wiki/`（LLM 编译维护）→ `schema/`（协同演进配置）。

四个操作：`ingest` → `query` → `lint` → `research`。

这个概念启发了整个社区——GitHub 上已涌现 30+ 个 LLM Wiki 项目，累计 30,000+ Stars。

**但原始愿景有缺口。**

---

## 原始愿景的 6 个缺口

| # | 缺口 | 症状 | 后果 |
|---|------|------|------|
| 1 | **无防幻觉机制** | AI 生成的摘要可能包含事实错误 | 错误知识永久化，越积越深 |
| 2 | **无跨会话记忆** | 每次 ingest 独立执行，不记得上次做了什么 | 重复劳动，无法累积上下文 |
| 3 | **无人类入口** | wiki/ 是扁平文件列表，人类找不到东西 | 技术好但不好用 |
| 4 | **知识不复利到能力** | 高频任务每次都从零开始 | 效率不随知识增长而提升 |
| 5 | **变更不可追溯** | 改了什么、为什么改，无记录 | 知识库变成黑箱 |
| 6 | **单平台绑定** | 绑死 Claude Code 或单一 agent | 换工具就丢知识库 |

---

## FlowWiki 的 6 个增强

| 缺口 | FlowWiki 解法 | 层级 |
|------|--------------|------|
| 无防幻觉 | **ACE 反思循环** — Generator→Reflector→Curator 三 agent 制约，错误知识不进 wiki | L4 |
| 无跨会话记忆 | **A-MEM 卡片** — 每个 raw 生成 Zettelkasten 卡片，跨会话可读 | L4 |
| 无人类入口 | **双索引** — 机器走 `wiki/index.md`，人类走 `00_首页/` 6 板块 MOC | L1 |
| 知识不复利 | **任务→知识→Skill 三元组** — 高频任务自动抽象为 O(1) 调用的 skill | L5 |
| 变更不可追溯 | **SpecCoding 七阶段** — 每个变更走 `openspec/changes/` | L3 |
| 单平台绑定 | **多 agent bootstrap** — CLAUDE.md + AGENTS.md + CODEX.md + WORKBUDDY.md | L6 |

---

## 架构总览

```
┌──────────────────────────────────────────────────────────────┐
│ L7 场景层（业务外壳，可插拔）                                    │
│   通用 7 场景（根因分析/合规审查/证照管理/...）/ 任意领域场景      │
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

## 测试用知识库

仓库预置 **enforcement-review（执法督察评查）** 作为测试知识库：

```bash
# 一键引导（入仓 → 设计 → 入库 → 三验 → 自修复）
python _scripts/bootstrap.py --source raw/enforcement-review --slug enforcement-review --skip-to 2

# 验收
python _scripts/hermes_review.py --industry enforcement-review
python _scripts/graph.py --format stats --industry enforcement-review
```

| 指标 | 值 |
|------|-----|
| raw/ | 155 篇原始资料 |
| wiki/ | 98 节点知识图 |
| Hermes | 8-9 / 10 pass |
| 三验 | lint 0 + graph 0 孤立 + hermes pass |

详见 [TESTING.md](./TESTING.md)

---

## 快速开始

### Option 1：从模板克隆（推荐）

```bash
git clone https://github.com/xiejianjun000/FlowWiki.git my-wiki
cd my-wiki

# 自动检测区域 + 生成本地化目录（中文/英文）
bash _scripts/setup.sh

# 选择你的 agent bootstrap
# Claude Code → 读 CLAUDE.md
# Codex / Gemini / WorkBuddy → 读 AGENTS.md

# 投入第一篇 raw
mkdir -p raw/articles
cp ~/some-article.md raw/articles/

# 在 agent 中触发 ingest
> 请按 ingest skill 把 raw/articles/some-article.md 入库
```

> 💡 **区域自适应**：`setup.sh` 会自动检测你的 IP 归属地。国内用户看到中文目录（`原始资料/` `知识库/` `首页/`），海外用户保持英文目录。AI Agent 始终走英文路径，互不干扰。

### Option 2：添加到现有 Obsidian Vault

```bash
# 把 FlowWiki 骨架文件复制到你的 vault 根目录
cp -r raw/ wiki/ 00_首页/ config.toml SCHEMA.md your-vault/

# 把 CLAUDE.md / AGENTS.md 放到 vault 根目录
# Obsidian 会自动识别 00_首页/ 为 MOC 入口
```

### Option 3：从零搭建

参考 [SCHEMA.md](./SCHEMA.md) 手动创建目录结构，或使用 `_scripts/` 下的脚本初始化。

### Option 4：Docker 一键部署

```bash
git clone https://github.com/xiejianjun000/FlowWiki.git my-wiki
cd my-wiki

# 构建并启动
docker compose up -d

# 接入 MCP（让 AI Agent 直接调用 FlowWiki）
# 参考 docs/mcp-integration.md
```

### Option 5：MCP Server 接入

```bash
pip install -r requirements.txt
python _scripts/mcp_server.py
```
然后在你的 AI Agent 的 MCP 配置中添加 FlowWiki server，详见 [docs/mcp-integration.md](./docs/mcp-integration.md)。

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

---

## Skill vs Prompt 决策指南

| 用 Skill | 用 Prompt |
|----------|----------|
| 高频操作（≥3 次同类任务） | 一次性或低频（≤2 次） |
| 多步骤工作流（如 ingest 7 步） | 单步骤操作或风格切换 |
| 跨场景通用（如 lint 体检） | 场景专属引导（如"用执法者视角回答"） |
| 有明确输入输出契约 | 探索性实验（还没形成标准流程） |
| 长期维护、版本管理 | 用完即弃，不持久化 |

**升级路径**：Prompt（探索期）→ 高频使用 ≥3 次 + 流程可标准化 → **升级为 Skill**（O(1) 调用）

---

## 与具体项目对比

### 方法论维度对比

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

### 与 GitHub 同类项目对比

| 能力 | FlowWiki | llm-wiki-agent | claude-obsidian | llm-wiki-compiler | synthadoc |
|------|:-:|:-:|:-:|:-:|:-:|
| 防幻觉机制 | ACE 三 agent | 矛盾标记 | 无 | 无 | Pre-LLM 净化 |
| 跨会话记忆 | A-MEM 卡片 | 无 | Hot Cache | 无 | 无 |
| 多 agent 兼容 | 5 家 agent | 3 家 | 仅 Claude | 仅 Claude | 3 家 |
| 人类 UX | 双索引 6 板块 | 无 | Obsidian 原生 | 桌面 GUI | Web UI |
| 业务可插拔 | L7 场景外壳 | 无 | 无 | 无 | 无 |
| 变更追溯 | SpecCoding | 无 | 无 | 无 | 无 |
| 知识复利到能力 | 任务→知识→Skill | 无 | 无 | 无 | 无 |
| 自适应检索 | BM25→graphrag→LightRAG | 无 | 混合检索 | BM25 | 知识图谱 |
| 矛盾追踪 | conflict/ 目录 | 标记不追踪 | 无 | 无 | 无 |

> **FlowWiki 是唯一同时覆盖以上 9 个维度的项目。**

### 2026 Q3 竞品全景（截至 2026-07-18）

| 项目 | Stars | 定位 | 核心亮点 | FlowWiki 对比 |
|------|-------|------|----------|-------------|
| **nashsu/llm_wiki** | 14.8K | 桌面 GUI 应用 | Tauri+React GUI，Louvain 图谱聚类，Chrome 剪藏，MCP | FlowWiki 无 GUI 但方法论更深 |
| **SamurAIGPT/llm-wiki-agent** | 3.2K | 多 Agent Skill 包 | Agent-agnostic，Git 版本控制，知识图谱可视化 | FlowWiki 的 ACE 是其没有的防幻觉层 |
| **Ar9av/obsidian-wiki** | 2.9K | 完整框架 | 13 skill 文件，Delta tracking，图片编译，多 AI 兼容 | FlowWiki 有 ACE+A-MEM，但缺少技能数量 |
| **atomicstrata/llm-wiki-compiler** | 1.8K | npm 知识编译器 | OKF 格式，eval harness，MCP Server，review policy | 最接近 FlowWiki 品质控制理念的竞品 |
| **lucasastorian/llmwiki** | 1.4K | Web 托管 | llmwiki.app 在线服务，Chrome 扩展，自动维护 | FlowWiki 本地优先，数据主权更好 |
| **agentmemory** | 22K | Agent 持久记忆 | MCP 集中式记忆，BM25+向量+图谱三流检索，自动遗忘 | FlowWiki 的 A-MEM 卡片更轻量，零依赖 |
| **mem0** | 22K | 通用记忆层 | 生产级 SDK/API，LongMemEval=94.8，托管服务 | FlowWiki 面向方法论用户，mem0 面向开发者 |

**FlowWiki 的差异化定位**：最严格的知识质量保证 + 能力复利飞轮。
- 桌面应用选 nashsu，Web 托管选 lucasastorian，工程化编译选 atomicstrata
- **要对知识质量有洁癖 → FlowWiki（ACE 三 agent 制约 + SpecCoding 追溯）**

---

## Tech Stack

| 层 | 技术 | 说明 |
|----|------|------|
| 知识格式 | Markdown + YAML frontmatter | 人类可读、Obsidian 兼容 |
| 检索 L2 | BM25 + CJK 分词 → nano-graphrag → LightRAG | 自适应三档，按规模自动切换 |
| 记忆 L4 | A-MEM Zettelkasten 卡片 | 跨会话持久化，零数据库依赖 |
| 防幻觉 L4 | ACE Generator→Reflector→Curator | 三 agent 制约，ingest 时拦截错误 |
| 变更管理 L3 | OpenSpec + SpecCoding 七阶段 | 可追溯，每个变更有提案/执行/归档 |
| Agent 兼容 L6 | CLAUDE.md + AGENTS.md + CODEX.md + WORKBUDDY.md | 5 家 agent 通吃 |
| Skill 分发 L5 | .agents/skills/ + .claude/skills/ 双部署 | 同一 skill 两套格式 |
| 可视化 | Obsidian Graph View + Dataview | 零额外依赖 |
| 部署 | Docker + docker compose | 一键启动 |
| MCP 接口 | `_scripts/mcp_server.py` | 5 工具暴露给 AI Agent |
| 依赖 | PyYAML + MCP SDK | 极简优先 |

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

```
raw → wiki → skill → 自动调用 → 新任务 → 新 raw → wiki 增厚 → skill 增多 → ...
```

---

## 适用场景

### 适合 FlowWiki

- 个人/团队知识库（100-10000 页规模）
- AI agent 长期维护的专业领域知识库
- 需要多 agent 接手的协作型知识库
- 业务领域可插拔的多场景知识库

### 不适合 FlowWiki

- 单次查询的临时知识需求（用 RAG 即可）
- 必须用云服务的多租户 SaaS（FlowWiki 是本地优先）
- 必须图形界面（FlowWiki 依赖 Obsidian 等第三方可视化）
- 万页以上且需秒级查询（用专业向量数据库）

---

## 里程碑路线图

| 里程碑 | 名称 | 状态 |
|--------|------|------|
| M0 | 全局 spec 设计 | ✅ |
| M1 | 骨架脚手架 | ✅ |
| M2 | 4 操作 skill 实现 | ✅ |
| M3 | ACE 反思循环 + A-MEM | ✅ |
| M4 | 双索引同步 | ✅ |
| M5 | L7 场景参考实现 | ✅ |
| M6 | 多 agent 兼容矩阵 | ✅ |
| M7 | 方法论白皮书发布 | ✅ |

详细任务见 [spec/tasks.md](./spec/tasks.md)。

---

## FAQ

### FlowWiki 和 Karpathy 的 LLM Wiki 有什么区别？

Karpathy 提出了 raw→wiki→schema 三层架构和 4 操作的核心理念。FlowWiki 在此基础上新增了 6 个增强：ACE 防幻觉循环、A-MEM 跨会话记忆、双索引人类 UX、任务→知识→Skill 复利、SpecCoding 变更追溯、多 agent 兼容。简单说，Karpathy 是编译器，FlowWiki 是带类型检查、缓存和插件的编译器。

### FlowWiki 和传统 RAG 有什么区别？

RAG 是解释器——每次查询都重新推导，结果不持久化。FlowWiki 是编译器——知识只编译一次并保持最新，查询时直接读取编译产物。更关键的是，FlowWiki 的探索结果会归档回 wiki，让探索本身也复利积累。传统 RAG 没有防幻觉机制，FlowWiki 有 ACE 三 agent 制约。

### FlowWiki 适合什么规模的知识库？

100-10000 页是最佳区间。100 页以下用纯 Obsidian 即可，不需要 FlowWiki 的 L2 自适应检索。10000 页以上且需秒级查询，建议用专业向量数据库。FlowWiki 的 BM25→nano-graphrag→LightRAG 三档自适应正好覆盖中间地带。

### FlowWiki 需要向量数据库吗？

不需要。FlowWiki 默认零数据库依赖，100 页以下用 BM25+CJK 分词就够了。超过 100 页可以按需启用 nano-graphrag（轻量图谱检索），超过 500 页可以启用 LightRAG。全部是纯 Python + 文件系统，不引入任何外部服务。

### FlowWiki 支持哪些 AI agent？

5 家：Claude Code（读 CLAUDE.md）、Codex（读 AGENTS.md）、Gemini CLI（读 AGENTS.md）、Amp（读 AGENTS.md）、WorkBuddy（读 WORKBUDDY.md）。所有 agent 共享同一套 skill（.agents/skills/ 和 .claude/skills/ 双部署），换 agent 不丢知识库。

### FlowWiki 是 Obsidian 插件吗？

不是。FlowWiki 是一套方法论 + 目录规范 + 脚本工具，输出的是标准 Markdown 文件。你可以用 Obsidian 打开（推荐，因为有 Graph View 和 Dataview），也可以用 VS Code、Typora 或任何 Markdown 编辑器打开。

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

[MIT](./LICENSE)
