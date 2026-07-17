# FlowWiki 竞品对比分析报告

> 生成时间：2026-07-17
> 调研范围：GitHub 35+ 同类项目，覆盖 8 个类别
> 数据来源：GitHub Search API + GitHub REST API + README 内容分析

---

## 一、FlowWiki 自身画像

| 指标 | 数值 |
|------|------|
| 仓库 | xiejianjun000/FlowWiki |
| Stars | 0（新建项目，尚未推广） |
| Forks | 0 |
| Commits | 8 |
| 总文件 | 160 |
| 代码行数 | 10,847 |
| Markdown 文件 | 128 |
| Python 脚本 | 7（1,140 行） |
| SKILL.md | 54（27 unique × 2 双部署） |
| YAML 配置 | 10 |
| Jinja2 模板 | 7 |
| E2E 测试 | 114 项（100% 通过） |
| CI/CD | GitHub Actions（双 job 全绿） |
| License | MIT |
| 依赖 | 仅 PyYAML |

---

## 二、35+ 竞品全景

### 按类别分布

| 类别 | 项目数 | 最高 Stars | 代表项目 |
|------|--------|-----------|---------|
| LLM Wiki / 知识编译 | 13 | 14.8K | nashsu/llm_wiki |
| Obsidian + AI Agent | 3 | 9.5K | AgriciDaniel/claude-obsidian |
| Spec-Driven Development | 2 | 121.9K | github/spec-kit |
| GraphRAG / 知识图谱 | 6 | 37.8K | HKUDS/LightRAG |
| DeepWiki / 代码转文档 | 5 | 17.3K | AsyncFuncAI/deepwiki-open |
| Agent 记忆系统 | 3 | 191 | glommer/memelord |
| 知识库基础设施 | 3 | 1.3K | shuyu-labs/AntSK |
| Meta / 参考指南 | 1 | 87 | kennethlaw325/awesome-llm-knowledge-systems |

### 7 维度覆盖矩阵

| 项目 | Stars | LLM Wiki | Spec-Driven | Agent Memory | Skill 系统 | 多 Agent | 自适应检索 | 场景可插拔 |
|------|-------|----------|-------------|-------------|-----------|---------|-----------|-----------|
| **FlowWiki** | 0 | ✅ 双索引 | ✅ OpenSpec | ✅ A-MEM+ACE | ✅ 双部署 | ✅ 5家 | ✅ 三级 | ✅ L7场景 |
| nashsu/llm_wiki | 14.8K | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ 向量 | ✅ 模板 |
| claude-obsidian | 9.5K | ✅ | ❌ | ✅ Hot Cache | ✅ 15 skills | ✅ | ✅ 混合 | ✅ 方法论 |
| llm-wiki-agent | 3.2K | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| open-knowledge | 3.0K | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| obsidian-wiki | 2.9K | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| llm-wiki-skill | 2.2K | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| llm-wiki-compiler | 1.8K | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ 混合 | ✅ CLP |
| AutoSci | 1.5K | ✅ | ❌ | ✅ SciMem | ✅ | ✅ 3平台 | ❌ | ✅ 模板 |
| karpathy-llm-wiki | 1.5K | ✅ | ❌ | ❌ | ✅ | ✅ 3平台 | ❌ | ❌ |
| llmwiki | 1.4K | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| synthadoc | 0.6K | ✅ | ❌ | ✅ 5状态 | ✅ 3层 | ✅ | ✅ 混合 | ✅ 领域 |
| llm-wiki-skill (lew) | 0.6K | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| hyperresearch | 0.5K | ✅ | ❌ | ✅ Vault | ✅ | ✅ 13 agent | ❌ | ❌ |
| spec-kit | 121.9K | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| OpenSpec | 61.3K | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ Stores |
| LightRAG | 37.8K | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| deepwiki-open | 17.3K | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Yuxi | 6.1K | ❌ | ❌ | ❌ | ❌ | ✅ 多租户 | ✅ | ❌ |
| nano-graphrag | 3.9K | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |

---

## 三、最接近的 4 个竞品逐项对比

### 3.1 atomicstrata/llm-wiki-compiler (1,779 stars)

| 维度 | llm-wiki-compiler | FlowWiki | 谁赢 |
|------|-------------------|----------|------|
| LLM Wiki | ✅ 两阶段管线+类型化页面 | ✅ 双索引(raw→wiki→00_首页) | FlowWiki（双索引更完整） |
| 可配置模板 | ✅ CLP 生命周期配置文件 | ✅ industry.yaml 行业适配器 | 平手（不同抽象层） |
| 检索 | ✅ 语义分块+BM25重排+wikilink扩展 | ✅ BM25→nano-graphrag→LightRAG 三级 | FlowWiki（三级降级更弹） |
| Spec-Driven | ❌ | ✅ OpenSpec 集成 | **FlowWiki 独有** |
| Agent 记忆 | ❌ | ✅ A-MEM+ACE 四层 | **FlowWiki 独有** |
| 多 Agent 接手 | ❌ | ✅ 5 家 bootstrap | **FlowWiki 独有** |
| MCP Server | ✅ 完整 MCP(摄入/编译/查询/lint/eval) | ❌ | **llm-wiki-compiler 独有** |
| 评估工具 | ✅ eval 框架(健康评分/引用覆盖/回归) | ✅ 114 项 E2E | 平手（不同方向） |
| 签名模板 | ✅ Ed25519 签名+密钥轮换 | ❌ | **llm-wiki-compiler 独有** |
| 导出格式 | ✅ JSON/JSON-LD/GraphML/Marp/llms.txt | ❌ | **llm-wiki-compiler 独有** |
| Stars | 1,779 | 0 | llm-wiki-compiler |

**结论**：llm-wiki-compiler 在工程工具链（MCP/eval/签名/导出）上更成熟，FlowWiki 在方法论完整性（Spec+Memory+Multi-Agent）上更全面。两者互补。

### 3.2 AgriciDaniel/claude-obsidian (9,513 stars)

| 维度 | claude-obsidian | FlowWiki | 谁赢 |
|------|----------------|----------|------|
| LLM Wiki | ✅ Karpathy 模式 | ✅ 双索引 | FlowWiki（双索引） |
| Skill 数量 | ✅ 15 个 Claude skills | ✅ 27 个(4通用+23行业) | FlowWiki（更多） |
| 方法论模式 | ✅ LYT/PARA/Zettelkasten | ✅ A-MEM Zettelkasten | 平手 |
| 检索 | ✅ 上下文前缀+BM25+cosine | ✅ BM25→nano-graphrag→LightRAG | FlowWiki（三级降级） |
| 会话记忆 | ✅ Hot cache 持久化 | ✅ episodic 记忆 | 平手 |
| Lint | ✅ 8 类 | ✅ 6 项 | claude-obsidian（更细） |
| Spec-Driven | ❌ | ✅ OpenSpec | **FlowWiki 独有** |
| 自适应检索 | ❌（单一混合） | ✅ 三级降级 | **FlowWiki 独有** |
| ACE 反思循环 | ❌ | ✅ Generator→Reflector→Curator | **FlowWiki 独有** |
| 矛盾追踪 | ❌ | ✅ conflict/ 目录 | **FlowWiki 独有** |
| 场景可插拔 | ✅ 方法论模式 | ✅ L7 场景+industry.yaml | FlowWiki（更深） |
| Stars | 9,513 | 0 | claude-obsidian |

**结论**：claude-obsidian 在 Obsidian 生态集成和 lint 粒度上更强，FlowWiki 在防幻觉机制（ACE）、矛盾追踪和自适应检索上更深入。

### 3.3 skyllwt/AutoSci (1,546 stars)

| 维度 | AutoSci | FlowWiki | 谁赢 |
|------|---------|----------|------|
| 记忆中心架构 | ✅ SciMem/SciFlow/SciDAG/SciEvolve | ✅ A-MEM(zk/episodic/conflict/ace) | 平手（不同范式） |
| 多 Agent | ✅ Claude Code/Codex/OpenCode | ✅ Claude/Codex/Amp/Gemini/WorkBuddy | FlowWiki（更多） |
| 双语 skill | ✅ i18n 自动生成 | ❌ | **AutoSci 独有** |
| 实验流程 | ✅ /ideate→/exp-design→/exp-run | ✅ 7 场景 + 23 行业 skill | 不同领域 |
| Spec-Driven | ❌ | ✅ OpenSpec | **FlowWiki 独有** |
| 双索引 | ❌ | ✅ 机器+人类 | **FlowWiki 独有** |
| 自适应检索 | ❌ | ✅ 三级 | **FlowWiki 独有** |
| ACE 反思 | ❌ | ✅ 三 agent 制约 | **FlowWiki 独有** |
| arXiv 论文 | ✅ 已发表 | ❌ | **AutoSci 独有** |
| Stars | 1,546 | 0 | AutoSci |

**结论**：AutoSci 在学术影响力（arXiv论文+实验流程）和 i18n 上更强，FlowWiki 在工程方法论（Spec+双索引+ACE+自适应检索）上更完整。

### 3.4 axoviq-ai/synthadoc (613 stars)

| 维度 | synthadoc | FlowWiki | 谁赢 |
|------|-----------|----------|------|
| 矛盾检测 | ✅ 摄入时冲突检测+标记 | ✅ conflict/ 目录+ACE Reflector | FlowWiki（更有结构） |
| 对抗性审查 | ✅ 并发第二 LLM 过审 | ✅ ACE Reflector 独立 agent | 平手（不同实现） |
| 生命周期 | ✅ 5 状态机(draft→active→contradicted→stale→archived) | ✅ status 字段(draft→reviewed→approved) | synthadoc（更细粒度） |
| Hook 系统 | ✅ CI/CD 集成 | ✅ GitHub Actions CI | 平手 |
| 可观测性 | ✅ OpenTelemetry | ❌ | **synthadoc 独有** |
| 成本门控 | ✅ token+cost 日志+软/硬门限 | ❌ | **synthadoc 独有** |
| Skill 系统 | ✅ 3 层懒加载 | ✅ 双部署 27 个 | FlowWiki（双部署更通用） |
| Spec-Driven | ❌ | ✅ OpenSpec | **FlowWiki 独有** |
| 双索引 | ❌ | ✅ 机器+人类 | **FlowWiki 独有** |
| 场景可插拔 | ✅ 领域模板 | ✅ L7 场景+industry.yaml | FlowWiki（更深） |
| Stars | 613 | 0 | synthadoc |

**结论**：synthadoc 在企业级特性（OpenTelemetry/成本门控/5状态机）上更成熟，FlowWiki 在方法论广度（Spec+双索引+多Agent接手）上更全面。

---

## 四、FlowWiki 的独特价值

### 4.1 唯一性分析

在 35+ 个调研项目中，**没有任何单一竞品同时覆盖以下 7 个维度**：

| 维度 | FlowWiki 实现 | 最接近的竞品 | 差距 |
|------|-------------|-------------|------|
| LLM Wiki 双索引 | wiki/index.md(机器) + 00_首页/(人类6板块) | nashsu/llm_wiki(三层架构) | 无双索引 |
| Spec-Driven | spec/ + openspec/changes/ 完整变更治理 | github/spec-kit(仅spec) | 无 wiki+memory |
| Agent 记忆 | A-MEM ZK卡片 + ACE 三agent反思循环 | AutoSci(SciMem) / synthadoc(5状态) | 无ACE反思 |
| Skill 双部署 | .agents/ + .claude/ 双 bootstrap, 5家agent | claude-obsidian(15 skills) | 无双部署 |
| 多 Agent 接手 | CLAUDE/AGENTS/CODEX/WORKBUDDY 四文件 | AutoSci(3平台) / hyperresearch(13 agent) | 少1-2家 |
| 自适应检索 | BM25→nano-graphrag→LightRAG 三级降级 | llm-wiki-compiler(混合) / synthadoc(混合) | 无三级降级 |
| L7 场景可插拔 | 通用L1-L6骨架 + industry.yaml场景变量 | nashsu(模板) / claude-obsidian(方法论) | 无骨架+变量分离 |

### 4.2 FlowWiki 独有特性清单

以下特性在所有 35+ 竞品中**仅 FlowWiki 拥有**：

1. **ACE 反思循环** — Generator→Reflector→Curator 三 agent 制约，防幻觉
2. **Spec-Driven + LLM Wiki 融合** — OpenSpec 变更治理嵌入知识编译流程
3. **双索引架构** — 机器紧凑索引 + 人类 6 板块 MOC，同源双出口
4. **矛盾追踪目录** — `.memory/conflict/` 专门记录和解决知识矛盾
5. **三级检索降级** — BM25(轻量) → nano-graphrag(图谱) → LightRAG(全量) 自适应

---

## 五、FlowWiki 的短板

### 5.1 社区影响力

| 指标 | FlowWiki | 中位竞品 | 头部竞品 |
|------|----------|---------|---------|
| Stars | 0 | ~1,500 | 14,800 |
| Forks | 0 | ~200 | 1,760 |
| Commits | 8 | ~50+ | ~200+ |
| 贡献者 | 1 | ~3-5 | ~10+ |
| 创建天数 | 1 天 | ~100 天 | ~100 天 |

**差距**：FlowWiki 刚创建 1 天，零社区曝光。竞品平均运营 3-4 个月，已积累显著 stars/forks。

### 5.2 工程工具链

| 缺失能力 | 竞品拥有者 | 影响 |
|---------|-----------|------|
| MCP Server | llm-wiki-compiler, llmwiki | 无法通过 MCP 协议被其他工具调用 |
| 导出格式 | llm-wiki-compiler(JSON/GraphML/Marp) | 仅 Markdown，无法导出其他格式 |
| 签名模板 | llm-wiki-compiler(Ed25519) | 无法验证 skill 来源可信度 |
| OpenTelemetry | synthadoc | 无运行时可观测性 |
| 成本门控 | synthadoc | 无 token/cost 预算控制 |
| Obsidian 插件 | synthadoc, claude-obsidian | 无法直接在 Obsidian 中使用 |
| Web UI | nashsu/llm_wiki, deepwiki-open | 无在线浏览界面 |
| arXiv 论文 | AutoSci | 无学术背书 |
| i18n 国际化 | AutoSci(双语 skill 源) | 仅中文，无多语言 |
| PyPI/npm 分发 | hyperresearch, spec-kit | 无包管理器安装 |

### 5.3 代码成熟度

| 指标 | FlowWiki | 成熟竞品 |
|------|----------|---------|
| 单元测试 | 0（仅集成测试） | pytest 单元+集成 |
| 类型检查 | 无 mypy | 部分有 mypy |
| pre-commit hooks | 无 | 部分有 |
| 覆盖率报告 | 无 | synthadoc 有 coverage badge |
| 文档站 | 无 README 内嵌 | 部分有 MkDocs/GitHub Pages |
| 变更日志 | spec/tasks.md | 部分有 CHANGELOG.md |

---

## 六、FlowWiki 当前水平定位

### 6.1 综合评分

| 评估维度 | 满分 | FlowWiki | 说明 |
|---------|------|---------|------|
| 方法论完整性 | 30 | **28** | 7/7 维度全覆盖，唯一性高 |
| 工程实现 | 25 | **18** | 114 测试+CI 但缺 MCP/UI/导出 |
| 社区影响力 | 20 | **2** | 0 stars，1 天项目 |
| 文档质量 | 15 | **12** | README 完整，缺在线文档站 |
| 可扩展性 | 10 | **9** | industry.yaml 可插拔设计优秀 |
| **总分** | **100** | **69** | |

### 6.2 水平定位

```
┌─────────────────────────────────────────────────────────┐
│  FlowWiki 当前水平：方法论领先，工程初成，社区零起步       │
│                                                         │
│  方法论深度:  ████████████████████░░░░  90%  (行业领先)  │
│  工程成熟度:  ██████████████░░░░░░░░░░  65%  (中等)      │
│  社区影响力:  █░░░░░░░░░░░░░░░░░░░░░░░  5%   (零起步)    │
│  可扩展性:   █████████████████████░░░  90%  (优秀)      │
│                                                         │
│  综合定位: 方法论创新型项目（Pre-alpha → Alpha 过渡期）    │
└─────────────────────────────────────────────────────────┘
```

### 6.3 竞争象限定位

```
                    社区影响力高
                        ↑
                        │
    nashsu/llm_wiki ●   │   ● spec-kit (121K)
    claude-obsidian ●   │   ● OpenSpec (61K)
                        │
    ────────────────────┼──────────────────── 工程成熟度高 →
                        │
                        │   ● llm-wiki-compiler
                        │   ● synthadoc
                        │   ● AutoSci
                        │
         FlowWiki ●     │
                        │
                    社区影响力低
```

**FlowWiki 位于「方法论领先但社区影响力低」象限** — 与 crabin/llm-wiki（7 stars）和 mcglothi/ai-knowledge-base（3 stars）处于类似的早期阶段，但方法论深度远超两者。

### 6.4 总结判断

| 判断项 | 结论 |
|--------|------|
| **方法论创新性** | 行业领先 — 7 维度唯一全覆盖 |
| **工程完成度** | 中等偏上 — 114 测试 + CI + 幂等脚本 |
| **社区成熟度** | 零起步 — 0 stars / 0 forks / 1 天 |
| **生产可用性** | 概念验证阶段 — 可用于个人知识管理，未达到团队生产级 |
| **竞争力** | 潜力高 — 独特性强，但需要社区验证和工程补齐 |
| **建议阶段** | Pre-alpha → Alpha 过渡 — 需补齐 MCP/UI/文档站后进入 Alpha |

---

## 七、提升路径建议

### 7.1 短期（1-2 周）— 补齐工程短板

| 优先级 | 任务 | 预期效果 |
|--------|------|---------|
| P0 | Quartz v4 静态站点 | wiki 可在线浏览 |
| P0 | 补齐 5 个辅助脚本 | reindex/normalize/fix_dangling/lint/graph |
| P1 | MCP Server 封装 | 可被其他工具调用 |
| P1 | 单元测试补充 | 覆盖率 > 60% |
| P2 | PyPI 打包 | `pip install flowwiki` |

### 7.2 中期（1-2 月）— 社区冷启动

| 优先级 | 任务 | 预期效果 |
|--------|------|---------|
| P0 | 写技术博客/教程 | 搜索引擎收录 |
| P0 | 提交到 awesome-llm-knowledge-systems | 获得初始曝光 |
| P1 | 录制 5 分钟演示视频 | 直观展示价值 |
| P1 | 跨平台测试（Codex/Gemini CLI） | 验证多 Agent 声明 |
| P2 | 英文 README | 国际化覆盖 |

### 7.3 长期（3-6 月）— 生态建设

| 优先级 | 任务 | 预期效果 |
|--------|------|---------|
| P0 | 第二个行业场景（非生态环保） | 验证可插拔声明 |
| P1 | arXiv 论文 | 学术背书 |
| P1 | 贡献者指南 + Issue 模板 | 社区参与入口 |
| P2 | Docker 镜像 | 一键部署 |
| P2 | Obsidian 插件 | Obsidian 生态接入 |
