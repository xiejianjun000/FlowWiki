# FlowWiki README 竞品对比分析报告

> 基于 6 个 GitHub 顶级 LLM Wiki 项目 + Karpathy 原始概念 + 2 个方法论搜索的完整分析
> 生成日期：2026-07-17

---

## 一、执行摘要

本报告分析了 6 个 GitHub 上最热门的 LLM Wiki 项目（总计 31.4K+ Stars）的 README 文档策略，并结合 Karpathy 原始 LLM Wiki 概念描述和方法论文献，为 FlowWiki 的 README 改进提供具体建议。

### 核心发现

1. **所有成功项目都锚定 Karpathy 原始概念**——6 个项目中有 5 个明确引用并致谢 Karpathy
2. **"编译 vs 检索"是所有项目的共同叙事锚点**——这是区分 LLM Wiki 和 RAG 的核心叙事
3. **竞品对比表是标配**——6 个项目中 4 个有明确的对比表
4. **无一个项目同时做到：竞品表 + 截图/GIF + Badge + 独立文档站**——这是整个品类的共同短板
5. **FlowWiki 当前的 README 在方法论融合深度上是品类最深的**，但在视觉呈现、用户引导和情感钩子上存在明显短板

---

## 二、逐项目深度分析

### 项目 1：nashsu/llm_wiki（14.8K Stars）

| 维度 | 详情 |
|------|------|
| **定位声明** | "A personal knowledge base that builds itself." |
| **语气** | 专业产品文档（自信但不夸张） |
| **README 行数** | ~800-900 行 |
| **独立文档站** | 无 |
| **Badge** | 无 |
| **截图/GIF** | 无 |
| **竞品对比表** | 有（4-Signal Relevance Model 表 + Tech Stack 表） |
| **Star History** | 有 |

**结构特点：**
- 以 "What We Kept" vs "What We Changed & Added" 为主线
- 19 个 H3 子节逐一展开功能点
- 伪代码 + 信号权重表 + 检索管线流程

**关键差异化卖点（按强调顺序）：**
1. 增量持久化 Wiki vs 传统 RAG
2. 两阶段 Chain-of-Thought Ingest
3. 知识图谱 + Louvain 社区发现
4. 桌面应用 vs CLI/Web
5. 完整的 Agent + MCP 生态
6. 异步 Review 系统

**启示：** 该项目的 "保留 vs 新增" 结构非常适合 Fork 自 Karpathy 概念的项目。19 个功能点逐一展开虽然长，但给技术用户提供了完整的决策依据。

---

### 项目 2：SamurAIGPT/llm-wiki-agent（3.2K Stars）

| 维度 | 详情 |
|------|------|
| **定位声明** | "A coding agent skill. Drop source documents into raw/ and tell the agent to ingest them." |
| **语气** | 休闲-专业混合（口语化但技术精确） |
| **README 行数** | ~180-220 行 |
| **独立文档站** | 无 |
| **Badge** | 无 |
| **截图/GIF** | 无 |
| **竞品对比表** | 有（RAG vs LLM Wiki Agent，5行2列） |
| **Star History** | 有 |

**结构特点：**
- 极简结构：Related Projects → Install → Usage → What You Get → Use Cases → Graph → CLAUDE.md → What Makes This Different from RAG → Obsidian Integration → Multi-Format Ingest → Tips → Tech Stack
- 大量代码块作为示例，而非长段文字
- 目录树可视化（ASCII）展示 wiki/ 和 graph/ 结构

**关键差异化卖点：**
1. 自维护（Self-maintaining）
2. 无需 API Key（直接在 Claude Code/Codex/Gemini CLI 中运行）
3. 持久性 + 累积性
4. 摄入时标记矛盾（Ingest-time contradiction flagging）
5. 多格式自动转换（21 种文件格式）
6. 完全本地运行

**启示：** 这个项目展示了"极简 README"的力量——~200 行，代码示例驱动，口语化但精确。"You never write it" 这类直接陈述句比长篇论述更有冲击力。

---

### 项目 3：atomicstrata/llm-wiki-compiler（1.8K Stars）

| 维度 | 详情 |
|------|------|
| **定位声明** | "The knowledge compiler. Raw sources in, interlinked wiki out." |
| **语气** | 专业工程文档 + 轻度幽默 |
| **README 行数** | ~450-550 行 |
| **独立文档站** | **有**（Mint 框架，docs/ 目录，`npx mint dev`） |
| **Badge** | 无 |
| **截图/GIF** | 无 |
| **竞品对比表** | 有（Agent 决策表 + 核心命令表 + Provider 配置表） |
| **Star History** | 未提及 |

**结构特点：**
- 24 个章节（21 H2 + 2 H3 + 1 H1）
- 独有章节："Agent decision guide"（面向 AI agent 读者）
- 独有章节："Quality and safety model"、"Scale and what works"
- 独有章节："Companion: Atomic Memory"
- 底部 Disclaimer 轻幽默：*"No LLMs were harmed in the making of this repo."*

**关键差异化卖点：**
1. 编译 vs 检索（compile time vs query time 范式转移）
2. 引用可追溯（段落级引用源文件及行范围）
3. 可配置生命周期配置（CLP）—— `.llmwiki/profile.json` 单一契约
4. Fail-closed 安全模型
5. 模板分发生态（Ed25519 签名）
6. Open Knowledge Format (OKF) 可移植知识交换
7. 多 Provider 可移植

**启示：** 这是唯一有独立文档站的项目，也是工程化最完整的。它的 "Agent decision guide" 章节是一个创新——将 AI agent 作为 README 的预期读者。FlowWiki 可以借鉴这个思路。

---

### 项目 4：skyllwt/AutoSci（1.5K Stars）

| 维度 | 详情 |
|------|------|
| **定位声明** | "Karpathy's LLM-Wiki vision, fully realized — wiki-centric full-lifecycle AI research platform powered by Claude Code" |
| **语气** | 专业工程文档 + 轻微愿景营销 |
| **README 行数** | ~150-300 行（详细文档分散在 docs/ 和各技能的 SKILL.md） |
| **独立文档站** | 无（仓库内嵌 docs/ + 技能内联文档） |
| **Badge** | 无 |
| **截图/GIF** | 有（poster_demo.png + wechat_group_4.png） |
| **竞品对比表** | 无 |

**结构特点：**
- "What's New" 时间线
- Demo 截图区（附带虚构内容免责声明）
- Architecture 说明（wiki2dag.py 桥接隐喻）
- CHANGELOG 引用
- i18n 双语支持（EN/ZH）

**关键差异化卖点：**
1. 全生命周期覆盖（论文发现→海报生成）
2. Wiki-centric 架构
3. "fully realized"——暗示比其他项目更完整
4. 技能体系（/init、/discover、/ingest、/ideate、/survey、/poster、/daily-arxiv）
5. i18n 双语支持
6. 自动化工作流（daily-arxiv GitHub Actions）

**启示：** "fully realized" 这个定位策略很巧妙——借 Karpathy 名人效应 + 声称完整实现，暗示竞品不完整。Demo 截图附虚构内容免责声明的做法值得注意。

---

### 项目 5：axoviq-ai/synthadoc（613 Stars）

| 维度 | 详情 |
|------|------|
| **定位声明** | "An open-source LLM knowledge compilation engine that turns raw documents into structured, local-first wikis." |
| **语气** | 专业技术型，面向开发者 |
| **README 行数** | ~300-500 行 |
| **独立文档站** | 有（docs/ 目录，含 design.md、quick-start guide、demo guide） |
| **Badge** | **有**（Skills count、CLI Commands、Obsidian Commands、Version） |
| **截图/GIF** | 未确认 |
| **竞品对比表** | **有且最完善**（6 个子类别：Knowledge Quality、Knowledge Structure、Search & Query、Interfaces & Integration、Content Sources、Operations & Trust） |

**结构特点：**
- "Why Synthadoc?" 章节链接到所有能力点
- 竞品对比表从 35 行扁平表重构为 6 个子类别表
- 多平台 Agent 技能文件（CLAUDE.md、GEMINI.md、AGENTS.md）
- Provider 支持表
- 备份与恢复文档
- 贡献指南（CONTRIBUTING.md）

**关键差异化卖点：**
1. 本地优先（Local-First）
2. 人类可读输出
3. 传统 RAG 透明替代方案
4. AI 会话历史摄取（独特功能）
5. 知识图谱（Louvain 聚类 + D3 可视化）
6. Pre-LLM 源净化器（安全特性）
7. 比例上下文预算

**启示：** 这是唯一系统使用 Badge 的项目，也是竞品对比表做得最细的（6 个子类别）。Badge 虽然是小事，但能给项目"活跃维护"的信号。35 行扁平表 → 6 子表的演进说明读者需要分类对比而非一坨大表。

---

### 项目 6：AgriciDaniel/claude-obsidian（9.5K Stars）

| 维度 | 详情 |
|------|------|
| **定位声明** | "Self-Organizing AI Second Brain for Obsidian + Claude Code" |
| **开场金句** | "Knowledge compounds like interest." |
| **语气** | 专业营销型（Professional-Marketing） |
| **README 行数** | ~650-750 行（含空行可能 800-900 行） |
| **独立文档站** | 无（仓库内 docs/ 目录） |
| **Badge** | 无 |
| **截图/GIF** | 有 YouTube Demo 链接，无内嵌截图/GIF |
| **竞品对比表** | **有且最强**（14 个能力维度 vs Smart Connections 和 Copilot） |
| **Star History** | 有 |

**结构特点：**
- 30+ 主章节 + 多个子节
- 完整目录（Contents）——唯一有目录的项目
- 三种安装方式（Clone as vault / Install as plugin / Add to existing vault）
- 方法论模式（LYT / PARA / Zettelkasten）——原生支持一线 PKM 方法论
- FAQ 部分——明显经过 SEO 优化
- 版本号标注（v1.7+、v1.8+、v1.9+）传达产品迭代活跃信号
- 架构部分含量化指标（+32pp top-1 准确率，-41% 错误率）

**关键差异化卖点：**
1. 自主组织（Self-organizing）
2. 数据主权（Plain Markdown you own）
3. 知识复利（Compounding knowledge）
4. Hot Cache 会话记忆
5. 多写者安全（v1.7+ 逐文件锁）
6. 方法论模式（LYT / PARA / Zettelkasten）
7. 自主研究循环（3 轮 web 研究 + gap-filling）
8. 混合检索（基于 Anthropic 研究，+32pp 准确率）
9. 10 原则思考框架
10. 开源 MIT vs Copilot freemium

**启示：** "Knowledge compounds like interest" 是所有项目中最有传播力的金句。14 行竞品对比表是最强的差异化论证工具。FAQ 的 SEO 优化是获取自然搜索流量的关键。版本号标注传达"活跃维护"信号。

---

### 项目 7：Karpathy 原始概念（GitHub Gist，5000+ Stars）

| 维度 | 详情 |
|------|------|
| **定位声明** | "Obsidian 是 IDE，LLM 是程序员，Wiki 是代码库。" |
| **核心类比** | RAG 是解释器（interpreter），LLM Wiki 是编译器（compiler） |
| **形态** | Idea File（抽象设计模式文档，非产品/非代码） |
| **语气** | 思想领袖 + 极简实用主义 |

**三层架构：**
1. Raw Sources（不可变）→ 2. Wiki（LLM 生成维护）→ 3. Schema（协同演进配置）

**四个操作阶段：**
1. Ingest（摄入）→ 2. Compile（编译）→ 3. Query & Enhance（查询与增强）→ 4. Lint & Maintain（校验与维护）

**核心洞察：**
- "知识只编译一次并保持最新，而非每次查询重新推导"
- 好的查询结果归档回 Wiki → "探索本身也复利积累"
- 个人规模（~100 篇文章）不需要向量数据库
- 与 Vannevar Bush 1945 年 Memex 概念遥相呼应

**启示：** Karpathy 的原始概念是所有项目的叙事锚点。FlowWiki 应该明确致谢 Karpathy 并清晰定位"我们在原始概念上做了什么增强"。

---

## 三、横向对比矩阵

### 3.1 README 元素对比

| 维度 | nashsu/llm_wiki | SamurAIGPT/llm-wiki-agent | atomicstrata/llm-wiki-compiler | skyllwt/AutoSci | axoviq-ai/synthadoc | AgriciDaniel/claude-obsidian | **FlowWiki（当前）** |
|------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **Stars** | 14.8K | 3.2K | 1.8K | 1.5K | 613 | 9.5K | - |
| **README 行数** | ~850 | ~200 | ~500 | ~225 | ~400 | ~700 | **297** |
| **定位声明** | "builds itself" | "coding agent skill" | "knowledge compiler" | "fully realized" | "local-first wikis" | "second brain" | "AI与人类协同复利" |
| **Badge** | 无 | 无 | 无 | 无 | 有(4枚) | 无 | 有(2枚) |
| **竞品对比表** | 有(功能级) | 有(RAG对比) | 有(命令级) | 无 | 有(6子类) | 有(14维度) | **有(8维度)** |
| **截图/GIF** | 无 | 无 | 无 | 有 | 未确认 | YouTube链接 | 无 |
| **Star History** | 有 | 有 | 未提及 | 未提及 | 未提及 | 有 | 无 |
| **独立文档站** | 无 | 无 | 有(Mint) | 无 | 有(docs/) | 无 | 无(docs/目录) |
| **完整目录** | 无 | 无 | 无 | 无 | 无 | **有** | 无 |
| **Quick Start** | 有(9步) | 有 | 有 | 有 | 有 | 有(3选项) | 有(4步) |
| **Tech Stack 表** | 有 | 有 | 有 | 隐含 | 有 | 有 | 无 |
| **Agent 决策指南** | 无 | 无 | **有** | 无 | 无 | 无 | 无 |
| **FAQ/SEO** | 无 | 无 | 无 | 无 | 无 | **有** | 无 |
| **多语言 README** | 有(中/日/韩) | 无 | 无 | 有(EN/ZH) | 无 | 无 | 无 |
| **致谢 Karpathy** | 有 | 隐含 | 有 | 有 | 有 | 有 | **有** |

### 3.2 语气对比

| 项目 | 语气类型 | 典型表达 |
|------|---------|---------|
| nashsu/llm_wiki | 专业产品文档 | "Knowledge is compiled once and kept current" |
| SamurAIGPT/llm-wiki-agent | 休闲-专业混合 | "You never write it"、"no one wants to do" |
| atomicstrata/llm-wiki-compiler | 专业工程+轻幽默 | "Compiled wiki, not chunks." / "No LLMs were harmed" |
| skyllwt/AutoSci | 专业+愿景营销 | "fully realized" |
| axoviq-ai/synthadoc | 专业技术型 | Conventional Commits 格式 |
| AgriciDaniel/claude-obsidian | **专业营销型** | "Knowledge compounds like interest" |
| **FlowWiki** | **方法论白皮书型** | "Karpathy LLM Wiki × TRAE Work × ACE × A-MEM × SpecCoding" |

### 3.3 架构说明方式对比

| 项目 | 架构说明方式 | 有无架构图 |
|------|------------|-----------|
| nashsu/llm_wiki | 伪代码 + 信号权重表 + 检索管线 + 目录树 | 无图（纯文字/表格） |
| SamurAIGPT/llm-wiki-agent | ASCII 目录树 + 工作流代码块 + 两阶段说明 | 无图 |
| atomicstrata/llm-wiki-compiler | 概念层 + 模式对比 + 目录结构 + 配置契约 + Agent 决策表 | 无图 |
| skyllwt/AutoSci | 组件枚举 + 流程式 + 桥接隐喻 | 无图（有 poster demo） |
| axoviq-ai/synthadoc | 链接到 design.md + README 摘要 | 无图 |
| AgriciDaniel/claude-obsidian | Vault Flow 文字描述 + 量化指标 + 版本号 | 无图（有 YouTube） |
| **FlowWiki** | **ASCII 架构图（7层）+ 创新招牌图** | **有（ASCII 图）** |

---

## 四、关键模式识别

### 模式 1：所有成功项目都锚定 Karpathy

6 个项目中有 5 个明确引用 Karpathy。成功的叙事结构是：
> "Karpathy 提出了 X → 原始概念有 Y 局限 → 我们在 Z 维度增强"

**FlowWiki 当前状态：** 已致谢 Karpathy，但叙事结构是 "5 个方法论相乘" 而非 "Karpathy + 我们的增强"。建议调整叙事顺序。

### 模式 2：竞品对比表是标配

4/6 项目有竞品对比表。最佳实践：
- **claude-obsidian** 的 14 维度表（vs 具体竞品 Smart Connections/Copilot）最有效
- **synthadoc** 的 6 子类别表（分类对比而非一坨大表）最可读
- **FlowWiki** 的 8 维度表已到位，但缺少与具体竞品（而非抽象方法论）的对比

### 模式 3：视觉呈现是全品类短板

6 个项目中：
- 0 个有内嵌截图/GIF（仅 AutoSci 有 poster demo，claude-obsidian 有 YouTube 链接）
- 5 个无 Badge
- 0 个有真正的架构图（只有 ASCII 图/目录树）

**这意味着**：任何在这一维度做到位的项目都将获得显著差异化优势。

### 模式 4：独立文档站是少数派

仅 2/6 项目有独立文档站（atomicstrata 用 Mint，synthadoc 用 docs/ 目录）。多数项目选择"README 即完整文档"策略。

### 模式 5：情感钩子差异巨大

- **最强金句**：claude-obsidian 的 "Knowledge compounds like interest."
- **最直接陈述**：llm-wiki-agent 的 "You never write it."
- **最精准类比**：Karpathy 的 "Obsidian 是 IDE，LLM 是程序员，Wiki 是代码库。"
- **FlowWiki 当前**："AI 与人类协同复利的知识库方法论"——偏学术，缺少情感冲击力

### 模式 6：版本号标注传达活跃信号

claude-obsidian 在每个功能描述后标注版本号（v1.7+、v1.8+），这是一种隐性的"产品在活跃迭代"信号。FlowWiki 的里程碑表（M0-M7）已有类似效果，但功能点未标注。

---

## 五、FlowWiki 当前 README 评估

### 5.1 优势（品类领先）

| 维度 | FlowWiki 表现 | 品类对比 |
|------|-------------|---------|
| **方法论融合深度** | 5 个方法论相乘（Karpathy × TRAE × ACE × A-MEM × SpecCoding） | 品类最深，无竞品达到此深度 |
| **架构图** | ASCII 7 层架构图 | 品类唯一有完整分层架构图的项目 |
| **竞品对比维度** | 8 维度对比（含 Karpathy/TRAE/RAG/现有实现） | 维度最全之一 |
| **设计哲学** | 6 条设计哲学明确阐述 | 品类中最系统化的设计哲学 |
| **创新招牌** | 3 大创新招牌（三元组/ACE/双索引）各有独立说明 | 品类中最清晰创新定位 |
| **致谢体系** | 12 个参考来源表格化 | 品类中最完整的致谢体系 |
| **适用/不适用场景** | 明确列出 4 适合 + 4 不适合 | 品类中罕见诚实标注不适用场景 |

### 5.2 短板（需改进）

| 维度 | 当前状态 | 品类最佳实践 | 改进优先级 |
|------|---------|------------|-----------|
| **情感钩子** | "AI与人类协同复利的知识库方法论" | "Knowledge compounds like interest." | **P0** |
| **一句话定义** | 5 个方法论缩写相乘，非技术读者难理解 | "Drop in sources — the agent builds and maintains a persistent interlinked wiki. You never write it." | **P0** |
| **截图/Demo** | 无 | claude-obsidian 有 YouTube，AutoSci 有 poster demo | **P1** |
| **Badge** | 有 2 枚（CI + License） | synthadoc 有 4 枚（+ Skills/CLI/Obsidian/Version） | **P2** |
| **完整目录** | 无 | claude-obsidian 有 Contents 目录 | **P2** |
| **FAQ/SEO** | 无 | claude-obsidian 有 SEO 优化的 FAQ | **P1** |
| **Tech Stack 表** | 无 | 5/6 项目有 | **P2** |
| **Star History** | 无 | 3/6 项目有 | **P3** |
| **多语言 README** | 无 | nashsu 有中/日/韩，AutoSci 有 EN/ZH | **P3** |
| **与具体竞品对比** | 仅对比抽象方法论 | claude-obsidian 对比 Smart Connections/Copilot | **P1** |
| **Quick Start 完整度** | 4 步，但引用未完成的 docs | claude-obsidian 有 3 种安装选项 | **P1** |

---

## 六、FlowWiki README 改进建议（按优先级）

### P0：立即改进

#### 建议 1：重写开场钩子和一句话定义

**当前：**
```
> AI 与人类协同复利的知识库方法论

**FlowWiki = Karpathy LLM Wiki × TRAE Work × ACE 反思循环 × A-MEM 卡片记忆 × SpecCoding 七阶段**
```

**建议改为：**
```
# FlowWiki

> Knowledge compounds like code. FlowWiki is the compiler.

**让 AI 编译知识像复利一样积累，让人类像走工作流一样使用，让多 agent 像接力一样接手。**

FlowWiki 基于 Karpathy 的 LLM Wiki 方法论，在原始 raw→wiki→schema 三层架构之上，
新增了 ACE 防幻觉层、A-MEM 记忆层、双索引人类 UX 层和 Skill 复利层——
让知识库不仅能自编译，更能防幻觉、可接手、可复利。
```

**理由：** 5 个方法论缩写相乘对外部读者太重。先讲"是什么、解决什么问题"，再讲"怎么做到的"。参考 claude-obsidian 的金句策略。

#### 建议 2：调整叙事顺序为"Karpathy → 痛点 → 增强"

**当前结构：** 一句话定义 → 为什么需要 → 6 层架构 → 三大创新 → 快速开始

**建议结构：**
1. 情感钩子 + 一句话定义
2. **Karpathy 的愿景**（1 段话引用原始概念 + 链接到 Gist）
3. **但原始愿景有 6 个缺口**（直接引出痛点表）
4. **FlowWiki 的 6 个增强**（痛点→解法一一对应）
5. 6 层架构图
6. 三大创新招牌
7. 快速开始
8. ...其余内容

**理由：** 所有成功项目都以 "Karpathy 提出了 X → 原始概念有 Y 局限 → 我们在 Z 维度增强" 为叙事主线。FlowWiki 当前的 "5 个方法论相乘" 叙事缺少这个锚点。

### P1：短期改进（1-2 周）

#### 建议 3：增加与具体竞品的对比表

**当前：** 仅对比 Karpathy/TRAE/RAG/现有实现（抽象方法论）

**建议增加：** 与 3-5 个具体项目对比

```markdown
| 能力 | FlowWiki | nashsu/llm_wiki | llm-wiki-agent | claude-obsidian | synthadoc |
|------|:-:|:-:|:-:|:-:|:-:|
| 防幻觉机制 | ACE 三 agent | 无 | 矛盾标记 | 无 | Pre-LLM 净化 |
| 跨会话记忆 | A-MEM 卡片 | 无 | 无 | Hot Cache | 无 |
| 多 agent 兼容 | 5 家 agent | 仅 Claude | 3 家 | 仅 Claude | 3 家 |
| 人类 UX | 双索引 6 板块 | 桌面 GUI | 无 | Obsidian 原生 | Web UI |
| 业务可插拔 | L7 场景外壳 | 无 | 无 | 无 | 无 |
| 变更追溯 | SpecCoding 七阶段 | 无 | 无 | 无 | 无 |
| 知识复利到能力 | 任务→知识→Skill | 无 | 无 | 无 | 无 |
```

**理由：** claude-obsidian 的 14 维度竞品表是最强差异化工具。抽象方法论对比不够直观，用户想看"FlowWiki vs 具体项目"。

#### 建议 4：增加 FAQ 部分（SEO 优化）

参考 claude-obsidian 的 FAQ 策略，增加搜索意图导向的 FAQ：

```markdown
## FAQ

### FlowWiki 和 Karpathy 的 LLM Wiki 有什么区别？
（回答中自然嵌入 "LLM Wiki"、"Karpathy"、"知识编译" 等搜索关键词）

### FlowWiki 和传统 RAG 有什么区别？
（回答中嵌入 "RAG"、"知识库"、"检索增强生成" 等关键词）

### FlowWiki 适合什么规模的知识库？
（回答中嵌入 "个人知识库"、"团队知识库" 等关键词）

### FlowWiki 需要向量数据库吗？
（回答中嵌入 "向量数据库"、"BM25"、"Obsidian" 等关键词）

### FlowWiki 支持哪些 AI agent？
（回答中嵌入 "Claude Code"、"Codex"、"Gemini" 等关键词）
```

**理由：** claude-obsidian 的 FAQ 明显经过 SEO 优化，是获取自然搜索流量的关键。FlowWiki 作为方法论项目，FAQ 更重要。

#### 建议 5：增加 Demo 截图或 GIF

**建议：** 在 "快速开始" 之前增加一个 Demo 部分：
- Obsidian 图谱视图截图（展示知识复利效果）
- ingest 流程截图（展示 ACE 三 agent 工作）
- 双索引对比截图（机器 index.md vs 人类 6 板块）

**理由：** 全品类 0 个项目有内嵌截图。这是最大的视觉差异化机会。

#### 建议 6：完善 Quick Start

**当前：** 4 步，但引用未完成的 `docs/getting-started.md`

**建议：**
- 参考 claude-obsidian 的 3 种安装方式策略
- 增加 "Option 1: 从模板克隆（2 分钟）" 和 "Option 2: 添加到现有 Obsidian Vault"
- 确保每一步都有预期输出示例

### P2：中期改进（2-4 周）

#### 建议 7：增加 Tech Stack 表

```markdown
## Tech Stack

| 层 | 技术 | 说明 |
|----|------|------|
| 知识格式 | Markdown + YAML frontmatter | 人类可读、Obsidian 兼容 |
| 检索 L2 | BM25 + CJK 分词 → nano-graphrag → LightRAG | 自适应三档 |
| 记忆 L4 | A-MEM Zettelkasten 卡片 | 跨会话持久化 |
| 防幻觉 L4 | ACE Generator→Reflector→Curator | 三 agent 制约 |
| 变更管理 L3 | OpenSpec + SpecCoding 七阶段 | 可追溯 |
| Agent 兼容 L6 | CLAUDE.md + AGENTS.md | 5 家 agent 通吃 |
| 可视化 | Obsidian Graph View + Dataview | 零额外依赖 |
```

#### 建议 8：增加 Badge

```
[![CI](...)] - 已有
[![License: MIT](...)] - 已有
新增：
[![Stars](https://img.shields.io/github/stars/xiejianjun000/FlowWiki)]
[![Specs](https://img.shields.io/badge/Specs-7阶段-blue)]
[![Agents](https://img.shields.io/badge/Agents-5家兼容-green)]
[![Scenes](https://img.shields.io/badge/Scenes-L7可插拔-orange)]
```

#### 建议 9：增加完整目录（Contents）

参考 claude-obsidian，在 README 顶部增加目录，方便 297 行的长 README 导航。

#### 建议 10：增加 Star History

在 README 底部增加 Star History 图表，传达社区活跃度信号。

### P3：长期改进

#### 建议 11：多语言 README

参考 nashsu/llm_wiki 的中/日/韩策略，至少增加英文版 README。

#### 建议 12：独立文档站

参考 atomicstrata 的 Mint 策略或 synthadoc 的 docs/ 策略，将详细文档从 README 分离。

---

## 七、FlowWiki README 改进版建议结构

基于以上分析，建议 FlowWiki README 的章节顺序调整为：

```
1. # FlowWiki（标题 + 情感钩子 + 一句话定义）
2. Badge 行
3. --- 目录（Contents）---
4. ## Karpathy 的愿景（1 段引用 + Gist 链接）
5. ## 但原始愿景有 6 个缺口（痛点表）
6. ## FlowWiki 的 6 个增强（痛点→解法对应表）
7. ## 6 层架构（ASCII 架构图）
8. ## 三大创新招牌（三元组 / ACE / 双索引）
9. ## Demo（截图/GIF）
10. ## 快速开始（3 种安装方式）
11. ## 核心操作（4 操作增强表）
12. ## Skill vs Prompt 决策指南
13. ## 与现有方案对比（方法论对比 + 具体项目对比两张表）
14. ## Tech Stack
15. ## 设计哲学（6 条）
16. ## 适用场景（适合 + 不适合）
17. ## 里程碑路线图
18. ## FAQ（SEO 优化）
19. ## 参考与致谢
20. ## Star History
21. ## License
```

---

## 八、总结

FlowWiki 的 README 在**方法论深度、架构完整性和创新定位**上已是品类最强。但在以下三个维度有显著提升空间：

1. **情感传播力**——需要一句像 "Knowledge compounds like interest" 那样可传播的金句
2. **视觉呈现**——全品类的共同短板，谁先做好谁就获得差异化优势
3. **用户引导**——从"方法论白皮书"转向"产品文档"，降低首次使用门槛

**核心策略建议：** 将叙事从"5 个方法论相乘的方法论白皮书"调整为"Karpathy 愿景的最完整工程实现"，用"Karpathy 提出了 X → 原始概念有 Y 缺口 → FlowWiki 用 Z 填补"的主线重新组织 README。

