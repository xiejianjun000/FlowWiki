# FlowWiki 竞品分析报告
## GitHub 类似项目全面调研

> 生成时间：2026-07-17  
> 覆盖项目数：35+  
> 数据来源：GitHub Search API + Web Search

---

## 目录

1. [LLM Wiki / 知识编译类](#1-llm-wiki--知识编译类)
2. [Obsidian + AI Agent 类](#2-obsidian--ai-agent-类)
3. [Spec-Driven Development 类](#3-spec-driven-development-类)
4. [GraphRAG / 知识图谱类](#4-graphrag--知识图谱类)
5. [DeepWiki / 代码转文档类](#5-deepwiki--代码转文档类)
6. [Agent 记忆系统类](#6-agent-记忆系统类)
7. [Agent 技能 / 知识库基础设施类](#7-agent-技能--知识库基础设施类)
8. [Meta / 参考指南类](#8-meta--参考指南类)

---

## 1. LLM Wiki / 知识编译类

这是与 FlowWiki 最直接相关的类别，均基于 Karpathy LLM Wiki 模式。

### 1.1 nashsu/llm_wiki
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/nashsu/llm_wiki |
| **Stars** | 14,773 |
| **Forks** | 1,760 |
| **Open Issues** | 205 |
| **语言** | TypeScript |
| **License** | NOASSERTION |
| **创建时间** | 2026-04-08 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | 跨平台桌面应用，将文档自动转为结构化、互联的知识库 |

**核心特性：**
- 两步 Chain-of-Thought 摄入（先分析后生成 wiki 页面）
- 多模态图像摄入（PDF 内嵌图片提取 + 视觉 LLM 生成描述）
- 多格式文档解析（PDF/Office/EPUB/MOBI/图片/媒体/网页）
- 4 信号知识图谱（直接链接 + 源重叠 + Adamic-Adar + 类型亲和）
- Louvain 社区发现自动聚类
- 向量语义搜索（LanceDB，支持任何 OpenAI 兼容端点）
- 持久化摄入队列（串行处理 + 崩溃恢复 + 取消/重试）
- Deep Research（Tavily/SerpApi/SearXNG 多查询网络搜索）
- Rust 后端聊天 Agent（工具调用 + wiki/source/graph/web 检索）
- Agent Skills 支持（扫描本地 SKILL.md，按需加载）
- 内置 MCP Server + 本地 HTTP API（127.0.0.1:19828）
- Chrome 网页剪藏器一键采集
- 三层架构：Raw Sources (不可变) → Wiki (LLM 生成) → Schema (规则配置)
- 场景模板：Research/Reading/Personal Growth/Business/General

**技术栈：** TypeScript + Rust + LanceDB  
**测试方法：** 未在 README 中明确提及测试策略  
**部署方式：** 跨平台桌面应用（Tauri 架构）

---

### 1.2 SamurAIGPT/llm-wiki-agent
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/SamurAIGPT/llm-wiki-agent |
| **Stars** | 3,219 |
| **Forks** | 371 |
| **Open Issues** | 2 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2023-04-21 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | 自构建自维护的个人知识库，支持 Claude Code/Codex/OpenCode/Gemini CLI |

**核心特性：**
- 无需 API Key（利用已有 agent 订阅）
- 三层结构：raw/ (只读源) + wiki/ (AI 维护) + graph/ (知识图谱可视化)
- 自动创建实体页（人物/公司/项目）和概念页（框架/方法）
- 摄入时矛盾检测
- living overview.md 随每次摄入更新
- vis.js 交互式知识图谱（社区检测聚类）
- Lint 报告（孤立页/断链/缺失实体页/数据空白）
- 支持 Markdown/PDF/DOCX/PPTX/XLSX/HTML/TXT/CSV/JSON 等格式
- markitdown 自动转换非 Markdown 文件
- slash commands: /wiki-ingest, /wiki-query, /wiki-lint, /wiki-graph

**技术栈：** Python + markitdown + vis.js  
**测试方法：** 未明确提及  
**部署方式：** Agent skill 模式（git clone + 打开 agent），无需 Python 环境

---

### 1.3 inkeep/open-knowledge
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/inkeep/open-knowledge |
| **Stars** | 2,962 |
| **Forks** | 186 |
| **Open Issues** | 18 |
| **语言** | TypeScript |
| **License** | GPL-3.0 |
| **创建时间** | 2026-06-03 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | AI 原生 Markdown IDE 和 LLM Wiki |

**核心特性：**
- AI 原生 Markdown 编辑器（IDE 级编辑体验）
- LLM Wiki 模式（Karpathy 风格）
- Agent Skills 兼容
- 第二大脑 / 知识管理
- 由 Inkeep（AI 文档搜索公司）维护

**技术栈：** TypeScript  
**测试方法：** 未明确提及  
**部署方式：** 桌面应用 / IDE

---

### 1.4 Ar9av/obsidian-wiki
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/Ar9av/obsidian-wiki |
| **Stars** | 2,893 |
| **Forks** | 291 |
| **Open Issues** | 8 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2026-04-06 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | AI agent 构建和维护 Obsidian 数字大脑的框架 |

**核心特性：**
- 基于 Karpathy LLM Wiki 模式
- Agent Skills 架构
- Obsidian 知识库自动构建和维护
- 数字大脑概念

**技术栈：** Python  
**测试方法：** 未明确提及  
**部署方式：** Agent skill 模式

---

### 1.5 sdyckjq-lab/llm-wiki-skill
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/sdyckjq-lab/llm-wiki-skill |
| **Stars** | 2,177 |
| **Forks** | 265 |
| **Open Issues** | 34 |
| **语言** | TypeScript |
| **License** | N/A |
| **创建时间** | 2026-04-05 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | 基于 Karpathy llm-wiki 方法论的个人知识库构建 Skill，支持多平台 |

**核心特性：**
- 多平台支持
- TypeScript 实现

---

### 1.6 atomicstrata/llm-wiki-compiler
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/atomicstrata/llm-wiki-compiler |
| **Stars** | 1,779 |
| **Forks** | 168 |
| **Open Issues** | 6 |
| **语言** | TypeScript |
| **License** | MIT |
| **创建时间** | 2026-04-05 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | 知识编译器：原始源入，互联 wiki 出 |

**核心特性（高度对标 FlowWiki）：**
- 两阶段 LLM 管线：先提取概念，后生成类型化页面（concept/entity/comparison/overview）
- **可配置生命周期配置文件（CLP）**：`.llmwiki/profile.json` 声明实体 schema、类型化关系、生命周期状态机
- 安装式域模板（autosci 研究模板 / newsroom 编辑模板）
- 运行时信任门（关系/证据/工件/人工门由写入路径强制执行）
- 引用可追溯输出（段落和声明引用源文件和行范围）
- 混合检索（语义分块搜索 + BM25 重排 + wikilink 图扩展）
- 本地查看器（只读浏览器 UI）
- 评审策略（按置信度/矛盾/schema/来源规则触发）
- 新鲜度修复（检测陈旧/孤立页面并修复）
- **评估工具**（llmwiki eval：健康评分、每页健康分布、引用覆盖/精度、语料统计、回归差异）
- **MCP Server**（llmwiki serve 暴露摄入/编译/查询/lint/读取/状态/eval/context-pack）
- SDK（createWiki({ root }) 从 TypeScript 驱动）
- Open Knowledge Format (OKF) 交换
- 多种导出格式（JSON/JSON-LD/GraphML/Marp/llms.txt）
- Provider 可移植（Anthropic/OpenAI/Ollama/Copilot/本地）
- 签名模板分发（Ed25519 签名 + 密钥轮换 + 包撤销）

**技术栈：** TypeScript + CI (GitHub Actions)  
**测试方法：** CI pipeline + llmwiki eval 评估框架  
**部署方式：** npm 全局安装 (`npm install -g llm-wiki-compiler`) + MCP Server + CLI + SDK

---

### 1.7 skyllwt/AutoSci
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/skyllwt/AutoSci |
| **Stars** | 1,546 |
| **Forks** | 205 |
| **Open Issues** | 3 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2026-04-09 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | Karpathy LLM-Wiki 愿景的完整实现 — wiki 中心的全生命周期 AI 研究平台 |

**核心特性（高度对标 FlowWiki）：**
- **记忆中心架构**：SciMem · SciFlow · SciDAG · SciEvolve
- 全生命周期覆盖：读取/思考/实验/写作/演化
- **多 agent 平台支持**：Claude Code (main 分支) + Codex (autosci-codex 分支) + OpenCode (autosci-opencode 分支)
- 双语 skill 源（i18n/<lang>/skills 为唯一真相源，自动生成各平台 skills）
- 实验流程：/ideate → /exp-design → /exp-run → /exp-status → /exp-eval
- 先导实验：/exp-pilot-run + /exp-pilot-eval
- 5 条结构化生成路径（A-E）
- Review LLM MCP 集成
- 每日 arXiv 推荐自动化
- 已发表 arXiv 论文（2605.31468）

**技术栈：** Python + Claude Code + MCP  
**测试方法：** 未明确提及测试框架  
**部署方式：** git clone + ./setup.sh + 打开对应 agent

---

### 1.8 Astro-Han/karpathy-llm-wiki
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/Astro-Han/karpathy-llm-wiki |
| **Stars** | 1,534 |
| **Forks** | 178 |
| **Open Issues** | 3 |
| **语言** | Markdown (无主语言) |
| **License** | MIT |
| **创建时间** | 2026-04-05 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | Agent Skills 兼容的 LLM wiki，支持 Claude Code/Cursor/Codex |

**核心特性：**
- Agent Skills 兼容（Claude Code / Cursor / Codex）
- Karpathy 风格知识库从原始源构建
- 引用追踪
- Lint 功能

**技术栈：** 纯 Markdown skill 定义  
**部署方式：** Agent skill 模式

---

### 1.9 lucasastorian/llmwiki
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/lucasastorian/llmwiki |
| **Stars** | 1,378 |
| **Forks** | 211 |
| **Open Issues** | 19 |
| **语言** | Python |
| **License** | Apache-2.0 |
| **创建时间** | 2026-04-04 |
| **最后更新** | 2026-07-17 |
| **描述** | Karpathy LLM Wiki 的开源实现，通过 MCP 连接 Claude |

**核心特性：**
- 上传文档 → 连接 Claude 账户（MCP）→ AI 写 wiki
- Supabase 后端
- MCP Server 架构

**技术栈：** Python + Supabase + MCP  
**部署方式：** Web 应用 + MCP

---

### 1.10 axoviq-ai/synthadoc
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/axoviq-ai/synthadoc |
| **Stars** | 613 |
| **Forks** | 54 |
| **Open Issues** | 2 |
| **语言** | Python |
| **License** | AGPL-3.0 |
| **创建时间** | 2026-04-11 |
| **最后更新** | 2026-07-16 |
| **描述** | 开源 LLM 知识编译引擎，将原始文档转为结构化本地 wiki |

**核心特性（高度对标 FlowWiki）：**
- **摄入时编译**（非查询时合成）
- 矛盾检测：摄入时冲突检测，页面标记 `status: contradicted`
- **对抗性审查**：并发第二 LLM 过审，标记过度自信声明
- 声明级溯源：`^[file:L-L]` 引用每个声明
- 5 状态生命周期机：draft → active → contradicted / stale → archived
- [[wikilinks]] 自动构建 + D3 力导向图 + Louvain 聚类
- 孤立页检测 + 断链修复
- 3 层缓存（embedding/LLM/provider prompt）
- 3 层懒加载技能/插件系统
- Obsidian 插件
- **Hook 系统**（CI/CD 集成）
- OpenTelemetry 可观测性
- 成本门控（per-job token+cost 日志 + 软警告/硬门限）
- 多 Provider（Gemini Flash 免费 / Ollama 本地 / Claude Code CLI）
- OKF v0.1 兼容

**技术栈：** Python 3.11+ + CI (GitHub Actions) + Coverage badge  
**测试方法：** CI + Coverage 跟踪  
**部署方式：** CLI + Obsidian 插件 + Web UI + MCP + REST API

---

### 1.11 lewislulu/llm-wiki-skill
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/lewislulu/llm-wiki-skill |
| **Stars** | 626 |
| **Forks** | 104 |
| **Open Issues** | 3 |
| **语言** | TypeScript |
| **License** | N/A |
| **创建时间** | 2026-04-05 |
| **最后更新** | 2026-07-14 |
| **描述** | Karpathy 风格 LLM 知识库 Agent Skill for OpenClaw/Codex |

---

### 1.12 jordan-gibbs/hyperresearch
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/jordan-gibbs/hyperresearch |
| **Stars** | 495 |
| **Forks** | 47 |
| **Open Issues** | 11 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2026-04-09 |
| **最后更新** | 2026-07-15 |
| **描述** | Agent 驱动的研究知识库，Agent 收集/搜索/合成网络研究为持久可搜索 wiki |

**核心特性（高度对标 FlowWiki 多 agent 模式）：**
- **16 步研究管线**（tier 自适应）
- **多 agent 编排**：13 种专门 agent（fetcher/source-analyst/loci-analyst/depth-investigator/corpus-critic/draft-orchestrator/synthesizer/dialectic-critic 等）
- 对抗性审计（4 个并行 critic）
- **补丁而非重生成**（patcher/polish-auditor 工具锁定为 [Read, Edit]）
- 持久化可搜索 vault（SQLite 索引 + Markdown 真相）
- 来源溯源面包屑
- 认证爬取（LinkedIn/Twitter/付费墙）
- 学术 API 优先（Semantic Scholar/arXiv/OpenAlex/PubMed）
- DeepResearch-Bench RACE 排行榜领先

**技术栈：** Python + SQLite + crawl4ai + PyPI  
**测试方法：** 内部基准测试（DeepResearch-Bench）  
**部署方式：** `pip install hyperresearch && hyperresearch install` + Claude Code skill

---

### 1.13 crabin/llm-wiki
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/crabin/llm-wiki |
| **Stars** | 7 |
| **Forks** | 3 |
| **Open Issues** | 0 |
| **语言** | Markdown |
| **License** | N/A |
| **创建时间** | 2026-04-06 |
| **最后更新** | 2026-06-14 |
| **描述** | 基于 Karpathy 的个人知识库模板，支持网络查证/健康检查/操作日志 |

**核心特性：**
- raw/ 只读层 → wiki/ AI 维护层
- [[双向链接]] 
- agent-browser 网络检索增强
- concepts/ 概念沉淀
- index.md 全库导航 + log.md 操作历史
- **跨 agent 兼容**：AGENTS.md + .agents/skills/（Codex）+ CLAUDE.md + .claude/skills/（Claude Code）
- 三语支持（中文/英文/日文）

---

## 2. Obsidian + AI Agent 类

### 2.1 AgriciDaniel/claude-obsidian
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/AgriciDaniel/claude-obsidian |
| **Stars** | 9,513 |
| **Forks** | 1,106 |
| **Open Issues** | 102 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2026-04-07 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | Obsidian + Claude Code 自组织 AI 第二大脑 |

**核心特性（高度对标 FlowWiki）：**
- **15 个 Claude Code skills**
- 多 agent 支持
- 多写入安全（per-file advisory locks, v1.7+）
- **方法论模式**：LYT / PARA / Zettelkasten / Generic（v1.8+，first-class）
- 10 原则思考框架（v1.9）
- 混合检索（上下文前缀 + BM25 + cosine rerank）
- Hot cache 会话间持久化
- 8 类 lint（孤立页/断链/空白/陈旧声明等）
- 3 轮自主网络研究 + 空白填补
- 视觉画布（claude-canvas）
- Compound Vault 基础（v1.7 重构）
- DragonScale Memory 扩展（log folds / 确定性页面地址 / 语义平铺 lint）
- 基于 Karpathy LLM Wiki 模式

**技术栈：** Python + CI (GitHub Actions)  
**测试方法：** CI test workflow  
**部署方式：** Claude Code plugin (`claude plugin install`) / git clone + Obsidian vault

---

### 2.2 RAIT-09/obsidian-agent-client
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/RAIT-09/obsidian-agent-client |
| **Stars** | 2,284 |
| **Forks** | 204 |
| **Open Issues** | 53 |
| **语言** | TypeScript |
| **License** | Apache-2.0 |
| **创建时间** | 2025-09-18 |
| **最后更新** | 2026-07-17 |
| **描述** | 通过 Agent Client Protocol (ACP) 将 AI agent 引入 Obsidian |

**核心特性：**
- Agent Client Protocol (ACP) 实现
- 支持 Claude Code / Codex / Gemini CLI / OpenCode
- Obsidian 插件

**技术栈：** TypeScript  
**部署方式：** Obsidian 插件

---

### 2.3 AdamTylerLynch/obsidian-agent-memory-skills
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/AdamTylerLynch/obsidian-agent-memory-skills |
| **Stars** | 42 |
| **Forks** | 5 |
| **Open Issues** | 0 |
| **语言** | Shell |
| **License** | MIT |
| **创建时间** | 2026-02-15 |
| **最后更新** | 2026-07-17 |
| **描述** | 通过 Obsidian 知识库给 agent 持久化记忆 |

**核心特性：**
- 会话开始时自动定位（读取 vault 状态）
- 通过图遍历导航项目架构
- 将发现写回 vault

---

## 3. Spec-Driven Development 类

### 3.1 github/spec-kit
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/github/spec-kit |
| **Stars** | 121,893 |
| **Forks** | 10,855 |
| **Open Issues** | 331 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2025-08-21 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | 帮助你开始 Spec-Driven Development 的工具包 |

**核心特性：**
- GitHub 官方出品
- 四阶段门控流程：Specify → Plan → Tasks → Implement
- 规格即通用语言（spec 是主要制品，代码是其表达）
- 可执行规格（足够精确以生成可工作系统）
- 持续精化（AI 分析模糊性/矛盾/空白）
- 研究驱动上下文
- 双向反馈（生产现实反馈规格演化）
- 探索性分支（从同一规格生成多种实现）
- Specify CLI (`uvx --from git+https://github.com/github/spec-kit.git specify init`)
- 跨 agent 支持（GitHub Copilot / Claude Code / Gemini CLI / Cursor 等）
- slash commands: /specify, /plan, /tasks

**技术栈：** Python (CLI) + 跨 agent 模板  
**部署方式：** uvx 全局 CLI 安装

---

### 3.2 Fission-AI/OpenSpec
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/Fission-AI/OpenSpec |
| **Stars** | 61,305 |
| **Forks** | 4,249 |
| **Open Issues** | 476 |
| **语言** | TypeScript |
| **License** | MIT |
| **创建时间** | 2025-08-05 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | AI 编码助手的 Spec-Driven Development 框架 |

**核心特性（高度对标 FlowWiki spec 层）：**
- 无需 API Key / 无需 MCP
- **新工作流**：/opsx:explore → /opsx:propose → /opsx:apply → /opsx:archive
- 制品引导工作流（proposal.md / specs/ / design.md / tasks.md）
- **Stores（beta）**：跨仓库规划，独立 repo 存储 spec
- 跨仓库功能（一次变更跨多个 repo）
- 共享需求（平台团队拥有 spec，产品团队只读引用）
- 先规划后编码
- 支持 25+ 工具
- npm 全局安装
- OpenSpec Dashboard

**技术栈：** TypeScript + Node.js 20+ + CI (GitHub Actions)  
**测试方法：** CI + E2E 测试（cross-platform CI matrix, vitest）  
**部署方式：** `npm install -g @fission-ai/openspec` + `openspec init`

---

## 4. GraphRAG / 知识图谱类

### 4.1 HKUDS/LightRAG
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/HKUDS/LightRAG |
| **Stars** | 37,757 |
| **Forks** | 5,314 |
| **Open Issues** | 221 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2024-10-02 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | [EMNLP2025] "LightRAG: Simple and Fast Retrieval-Augmented Generation" |

**核心特性：**
- EMNLP 2025 论文
- 简单快速的 GraphRAG 实现
- 知识图谱增强检索
- 大语言模型 + 图结构

**技术栈：** Python  
**部署方式：** pip install + Python API

---

### 4.2 xerrors/Yuxi
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/xerrors/Yuxi |
| **Stars** | 6,145 |
| **Forks** | 900 |
| **Open Issues** | 80 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2024-07-05 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | 结合知识库/知识图谱管理的多租户 Agent Harness 平台 |

**核心特性：**
- LightRAG 知识库 + 知识图谱集成
- **多租户 Agent Harness 平台**
- LangChain + Vue + FastAPI
- DeepAgents 支持
- MinerU PDF 处理
- Neo4j 图数据库
- MCP 支持

**技术栈：** Python (FastAPI) + Vue + Neo4j + LangChain + Docker  
**部署方式：** Docker

---

### 4.3 gusye1234/nano-graphrag
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/gusye1234/nano-graphrag |
| **Stars** | 3,934 |
| **Forks** | 420 |
| **Open Issues** | 84 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2024-07-25 |
| **最后更新** | 2026-07-17 |
| **描述** | 简单易改的 GraphRAG 实现 |

**核心特性：**
- 极简 GraphRAG 实现，适合学习和二次开发
- FlowWiki 检索层（L2）直接引用的项目之一

**技术栈：** Python  
**部署方式：** pip install

---

### 4.4 robert-mcdermott/ai-knowledge-graph
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/robert-mcdermott/ai-knowledge-graph |
| **Stars** | 2,545 |
| **Forks** | 354 |
| **Open Issues** | 13 |
| **语言** | Python |
| **License** | Apache-2.0 |
| **创建时间** | 2025-03-23 |
| **最后更新** | 2026-07-16 |
| **描述** | AI 驱动的知识图谱生成器 |

**技术栈：** Python + NetworkX + PyVis  
**部署方式：** Python 脚本

---

### 4.5 1517005260/graph-rag-agent
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/1517005260/graph-rag-agent |
| **Stars** | 2,275 |
| **Forks** | 319 |
| **Open Issues** | 36 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2025-02-12 |
| **最后更新** | 2026-07-17 |
| **描述** | 融合 GraphRAG/LightRAG/Neo4j 知识图谱 + DeepSearch 推理 + GraphRAG 评估框架 |

**核心特性：**
- GraphRAG + LightRAG + Neo4j 三合一
- DeepSearch 私域 RAG 推理
- 自制 GraphRAG 评估框架
- Think-on-Graph 思考链

---

### 4.6 raphaelmansuy/edgequake
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/raphaelmansuy/edgequake |
| **Stars** | 2,041 |
| **Forks** | 235 |
| **Open Issues** | 21 |
| **语言** | Rust |
| **License** | Apache-2.0 |
| **创建时间** | 2025-12-21 |
| **最后更新** | 2026-07-17 |
| **描述** | LightRag 启发的高性能 GraphRAG (Rust 实现) |

**技术栈：** Rust  
**部署方式：** Rust 二进制

---

## 5. DeepWiki / 代码转文档类

### 5.1 AsyncFuncAI/deepwiki-open
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/AsyncFuncAI/deepwiki-open |
| **Stars** | 17,344 |
| **Forks** | 1,943 |
| **Open Issues** | 264 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2025-04-30 |
| **最后更新** | 2026-07-17 (今天) |
| **描述** | 开源 DeepWiki：GitHub/Gitlab/Bitbucket 仓库的 AI Wiki 生成器 |

**核心特性：**
- 支持 GitHub/Gitlab/Bitbucket 仓库
- 多 LLM 支持（OpenAI/OpenRouter/Ollama/Grok CLI/Gemini/Codex）
- 自托管
- 开源版 DeepWiki

**技术栈：** Python  
**部署方式：** Docker / 自托管

---

### 5.2 AIDotNet/OpenDeepWiki
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/AIDotNet/OpenDeepWiki |
| **Stars** | 3,423 |
| **Forks** | 433 |
| **Open Issues** | 25 |
| **语言** | C# |
| **License** | MIT |
| **创建时间** | 2025-04-27 |
| **最后更新** | 2026-07-17 |
| **描述** | DeepWiki 开源版，知识管理和协作平台 |

**技术栈：** C# + TypeScript  
**部署方式：** .NET 应用

---

### 5.3 sopaco/deepwiki-rs
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/sopaco/deepwiki-rs |
| **Stars** | 1,361 |
| **Forks** | 153 |
| **Open Issues** | 5 |
| **语言** | Rust |
| **License** | MIT |
| **创建时间** | 2025-09-05 |
| **最后更新** | 2026-07-16 |
| **描述** | 将代码转为清晰文档，为人类团队和智能 agent 生成技术文档和 AI-ready 上下文 |

**技术栈：** Rust  
**部署方式：** Rust 二进制

---

### 5.4 regenrek/deepwiki-mcp
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/regenrek/deepwiki-mcp |
| **Stars** | 1,375 |
| **Forks** | 80 |
| **Open Issues** | 9 |
| **语言** | TypeScript |
| **License** | MIT |
| **创建时间** | 2025-04-28 |
| **最后更新** | 2026-07-17 |
| **描述** | MCP server 用于获取 deepwiki.com 知识 |

---

### 5.5 aibox22/readmeX
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/aibox22/readmeX |
| **Stars** | 413 |
| **Forks** | 26 |
| **Open Issues** | 10 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2025-07-02 |
| **最后更新** | 2026-07-09 |
| **描述** | AI 驱动的 README 和交互式 Wiki 生成工具，面向中文的开源 DeepWiki |

---

## 6. Agent 记忆系统类

### 6.1 glommer/memelord
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/glommer/memelord |
| **Stars** | 191 |
| **Forks** | 22 |
| **Open Issues** | 5 |
| **语言** | TypeScript |
| **License** | MIT |
| **创建时间** | 2026-02-17 |
| **最后更新** | 2026-07-17 |
| **描述** | 进程内 agentic 记忆系统 |

---

### 6.2 avibebuilder/claude-prime
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/avibebuilder/claude-prime |
| **Stars** | 108 |
| **Forks** | 17 |
| **Open Issues** | 0 |
| **语言** | Python |
| **License** | MIT |
| **创建时间** | 2026-03-03 |
| **最后更新** | 2026-07-16 |
| **描述** | 一键配置 Claude Code 的 Skills/hooks/agents/memory systems |

**核心特性：**
- 一键安装 Claude Code 全套配置
- Skills + hooks + agents + memory systems

---

### 6.3 emson/elfmem
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/emson/elfmem |
| **Stars** | 56 |
| **Forks** | - |
| **Open Issues** | - |
| **语言** | - |
| **License** | - |
| **创建时间** | - |
| **最后更新** | 2026-07-16 |
| **描述** | 自我改进的 agent 记忆系统 |

---

## 7. Agent 技能 / 知识库基础设施类

### 7.1 shuyu-labs/AntSK
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/shuyu-labs/AntSK |
| **Stars** | 1,324 |
| **Forks** | 213 |
| **Open Issues** | 0 |
| **语言** | C# (CSS 标记) |
| **License** | NOASSERTION |
| **创建时间** | 2024-02-01 |
| **最后更新** | 2026-07-16 |
| **描述** | .NET 9 + AntBlazor + Semantic Kernel + Kernel Memory 的 AI 知识库/agent |

**核心特性：**
- 支持本地离线 AI 大模型
- 无需互联网连接
- Aspire 监控

**技术栈：** .NET 9 + AntBlazor + Semantic Kernel + Kernel Memory + Aspire  
**部署方式：** .NET 应用 / 离线部署

---

### 7.2 vercel-labs/knowledge-agent-template
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/vercel-labs/knowledge-agent-template |
| **Stars** | 944 |
| **Forks** | 126 |
| **Open Issues** | 3 |
| **语言** | TypeScript |
| **License** | MIT |
| **创建时间** | 2026-01-20 |
| **最后更新** | 2026-07-16 |
| **描述** | 开源文件系统和知识库 agent 模板 |

**核心特性：**
- Vercel Labs 出品
- 文件系统 + 知识库 agent 模板
- AI agent 与知识库保持同步

**技术栈：** TypeScript + Nuxt + Vue + Sandbox  
**部署方式：** Nuxt 应用

---

### 7.3 mcglothi/ai-knowledge-base
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/mcglothi/ai-knowledge-base |
| **Stars** | 3 |
| **Forks** | 0 |
| **Open Issues** | 1 |
| **语言** | Python |
| **License** | N/A |
| **创建时间** | 2026-02-24 |
| **最后更新** | 2026-07-08 |
| **描述** | 给 AI agent 持久化记忆 — 跨 Claude Code/Gemini CLI/ChatGPT/Cursor 共享的结构化 Markdown 知识库 |

**核心特性（概念对标 FlowWiki）：**
- 跨 agent 共享记忆层
- 本地优先 + Git 备份
- 可检查、可 diff、可同步
- "remember that..." 自然语言记忆捕获
- "Let's wrap up" 会话结束 closeout
- 跨 agent 笔记传递（"send Claude a note..."）
- 过时检测
- Python TUI 安装器（支持 Windows/WSL）

---

## 8. Meta / 参考指南类

### 8.1 kennethlaw325/awesome-llm-knowledge-systems
| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/kennethlaw325/awesome-llm-knowledge-systems |
| **Stars** | 87 |
| **Forks** | 0 |
| **Open Issues** | 2 |
| **语言** | HTML |
| **License** | MIT |
| **创建时间** | 2026-04-06 |
| **最后更新** | 2026-07-15 |
| **描述** | 2026 LLM 知识工程统一指南：连接 RAG/Context Engineering/Harness Engineering/Skill Systems/Agent Memory/MCP/Progressive Disclosure |

**核心特性：**
- 13 章完整体系
- 三代演进：Prompt Eng → Context Eng → Harness Eng → Loop Eng
- 跨章节连接 RAG/知识图谱/长上下文/MCP/skill 路由/记忆系统/渐进式披露
- 中国 AI 生态专章
- 本地模型专章
- 案例研究
- 时间线追踪
- 多语言翻译（英/繁中/简中/日/韩/西）

---

## 总结对比矩阵

| 项目 | Stars | LLM Wiki | Spec-Driven | Agent Memory | Skill System | Multi-Agent | RAG/GraphRAG | 可插拔架构 |
|------|-------|----------|-------------|-------------|-------------|-------------|-------------|-----------|
| **FlowWiki** (自身) | - | ✅ 双索引 | ✅ OpenSpec | ✅ A-MEM+ACE | ✅ 双部署 | ✅ 5家 | ✅ 自适应 | ✅ L7场景 |
| nashsu/llm_wiki | 14.8K | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ 向量 | ✅ 模板 |
| AgriciDaniel/claude-obsidian | 9.5K | ✅ | ❌ | ✅ Hot Cache | ✅ 15 skills | ✅ | ✅ 混合 | ✅ 方法论 |
| SamurAIGPT/llm-wiki-agent | 3.2K | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| inkeep/open-knowledge | 3.0K | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Ar9av/obsidian-wiki | 2.9K | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| sdyckjq-lab/llm-wiki-skill | 2.2K | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| atomicstrata/llm-wiki-compiler | 1.8K | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ 混合 | ✅ CLP |
| skyllwt/AutoSci | 1.5K | ✅ | ❌ | ✅ SciMem | ✅ | ✅ 3平台 | ❌ | ✅ 模板 |
| Astro-Han/karpathy-llm-wiki | 1.5K | ✅ | ❌ | ❌ | ✅ | ✅ 3平台 | ❌ | ❌ |
| lucasastorian/llmwiki | 1.4K | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| axoviq-ai/synthadoc | 0.6K | ✅ | ❌ | ✅ 5状态 | ✅ 3层 | ✅ | ✅ 混合 | ✅ 领域 |
| lewislulu/llm-wiki-skill | 0.6K | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| jordan-gibbs/hyperresearch | 0.5K | ✅ | ❌ | ✅ Vault | ✅ | ✅ 13 agent | ❌ | ❌ |
| github/spec-kit | 121.9K | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Fission-AI/OpenSpec | 61.3K | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ Stores |
| HKUDS/LightRAG | 37.8K | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| AsyncFuncAI/deepwiki-open | 17.3K | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| xerrors/Yuxi | 6.1K | ❌ | ❌ | ❌ | ❌ | ✅ 多租户 | ✅ | ❌ |
| gusye1234/nano-graphrag | 3.9K | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| robert-mcdermott/ai-knowledge-graph | 2.5K | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| 1517005260/graph-rag-agent | 2.3K | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| raphaelmansuy/edgequake | 2.0K | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| RAIT-09/obsidian-agent-client | 2.3K | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| glommer/memelord | 0.2K | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| avibebuilder/claude-prime | 0.1K | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| shuyu-labs/AntSK | 1.3K | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ RAG | ❌ |
| vercel-labs/knowledge-agent-template | 0.9K | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## FlowWiki 独特价值定位

基于以上 35+ 项目的全面调研，FlowWiki 的独特性在于它是**唯一同时整合以下 7 个维度的项目**：

1. **LLM Wiki 双索引** — 机器走 `wiki/index.md`，人类走 `00_首页/` 6 板块 MOC（TRAE Work UX）
2. **Spec-Driven** — 直接集成 OpenSpec 变更管理（spec/ + openspec/changes/）
3. **Agent 记忆** — A-MEM Zettelkasten 卡片 + ACE 反思循环（Generator→Reflector→Curator 三 agent 制约）
4. **Skill 双部署** — `.agents/` + `.claude/` 双 bootstrap，5 家 agent 通吃
5. **多 agent 接手** — CLAUDE.md + AGENTS.md 双入口
6. **自适应检索** — BM25+CJK → nano-graphrag → LightRAG 三级弹窗
7. **L7 场景可插拔** — 通用骨架 L1-L6 + 场景作为变量（生态环境/SaaS 行业/任意领域）

没有任何单一竞品同时覆盖这 7 个维度。最接近的是：
- **atomicstrata/llm-wiki-compiler**（CLP 可插拔 + 混合检索 + MCP + eval，但无 spec-driven/memory/multi-agent）
- **AgriciDaniel/claude-obsidian**（方法论模式 + 混合检索 + hot cache + 15 skills，但无 spec-driven/自适应RAG）
- **skyllwt/AutoSci**（记忆中心 + 多平台 + 实验 skill，但无 spec-driven/双索引/可插拔场景）
- **axoviq-ai/synthadoc**（5 状态生命周期 + 对抗性审查 + hook 系统 + 成本门控，但无 spec-driven/skill 双部署）

