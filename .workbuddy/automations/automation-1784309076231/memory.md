# Automation Memory - FlowWiki 掘金每日文章撰写

## 执行历史

### 2026-07-19 (第1次执行)
- 撰写 article-02：ACE 反思循环防幻觉机制深度拆解
- 约 3000+ 字，覆盖：痛点引入（RAG 幻觉率数据）、ACE 四 Agent 原理、FlowWiki 代码实现（5 维度质量评分、原文指针铁律、内容去重引擎）、实战演示、竞品对比
- 草稿保存到 ops/publishing/series/drafts/article-02.md
- article-plan.yaml 中 article-02 状态从 draft → ready_for_review，新增 draft_date 和 draft_file 字段
- Git log 今日变更 6 commits：ACE 原文指针铁律、lint 增强、strict 模式、行业路由完整性等
- 下一篇待写：article-03（A-MEM 卡片记忆系统）

### 2026-07-19 第2次执行（22:00 定时）
- 发现 article-02 draft 文件不存在，article-plan.yaml 仍显示 draft（疑似第1次执行未持久化）
- 重新撰写 article-02：约 3000+ 字，结合今日 ACE 原文指针铁律 commit (23a2678) 深化实现细节
- 核心增量：质量评分 5 维度体系细节、原文指针铁律的 7 项强制检查、Jaccard 去重阈值设计
- 草稿重新保存，yaml 更新为 ready_for_review
- 下一篇：article-03（A-MEM Zettelkasten 卡片记忆系统）

### 2026-07-21（第3次执行）
- 撰写 article-03：A-MEM 卡片记忆系统，约 3200 字
- 核心内容：无状态 LLM 的失忆问题 → Zettelkasten 方法原理 → 164 行 Python 零数据库实现 → 跨会话/跨 Agent 记忆恢复流程 → 与 agentmemory/mem0/MemGPT 对比
- 深度结合项目实际：ZKCardGenerator 源码分析、卡片 6 段式结构、_find_related_cards 自动关联、decay.py 衰减管理、conflict/minority 冲突路由矩阵
- 承接 article-02 结尾预告，与第一篇三大创新框架呼应
- 草稿保存到 ops/publishing/series/drafts/article-03.md
- yaml 更新 article-03: draft → ready_for_review，补充 draft_date 和 draft_file
- 下一篇待写：article-04（Skill 化层──任务→知识→Skill 三元组）

### 2026-07-21（第4次执行，22:00）
- 撰写 article-04：Skill 化层──任务→知识→Skill 三元组，约 3200 字
- 核心内容：Karpathy raw→wiki 两层模型的瓶颈（知识只能查不能动）→ 探索→标准化→O(1)三级升级路径 → criteria-matching 真实案例（20min→5s）→ 双部署机制（.agents/skills/ + .claude/skills/ 同步）→ 完整复利飞轮（ACE+A-MEM+Skill 三角关系）
- 三大创新系列完结：article-02 (ACE) + article-03 (A-MEM) + article-04 (Skill)
- 草稿保存到 ops/publishing/series/drafts/article-04.md
- yaml 更新 article-04: draft → ready_for_review
- 下一篇待写：article-05（双索引人机协作架构）

### 2026-07-22（第5次执行）
- 撰写 article-05：双索引人机协作架构，约 3000 字
- 核心内容：AI 与人类信息消费方式差异 → sync_dual_index.py 同一份源数据两套视图 → 机器索引 index.md vs 人类 6 板块 MOC + 看板.html → 幂等同步机制 → v0.4.1 VERIFY-BEFORE-WRITE 作为双索引质量守门人 → 竞品对比（llm-wiki-agent / Obsidian MOC / atomicstrata）
- Git log 今日变更：1 commit（v0.4.1 VERIFY-BEFORE-WRITE + 引用验证 + 隔离区机制），与双索引质量保障自然适配
- 6 缺口进度：已填 4/6（ACE 防幻觉 + A-MEM 记忆 + Skill 复利 + 双索引 UX）
- 草稿保存到 ops/publishing/series/drafts/article-05.md
- yaml 更新 article-05: draft → ready_for_review
- 下一篇待写：article-06（SpecCoding 变更管理体系——知识库的 CI/CD）

### 2026-07-23（第6次执行）
- 撰写 article-06：知识库也需要 CI/CD──FlowWiki 的 SpecCoding 变更管理体系，约 3000 字
- 核心内容：知识库变更的四个死穴（无提案/无设计/无审查/无归档）→ SpecCoding 七阶段详解（分支→目录→提案→计划→执行→归档→合并）→ 三层硬核防护（ACE 五 Agent + VERIFY-BEFORE-WRITE 六级验证 + git-stash 防御性快照）→ v0.5.0 OKF 兼容层作为真实案例全生命周期演示 → 与 llm-wiki-agent/claude-obsidian/atomicstrata 竞品变更管理对比
- 结合今日 git log：v0.5.0 OKF 兼容层 + VERIFY-BEFORE-WRITE 独立工具 commit，将其作为 SpecCoding 变更的完整案例融入文章
- 6 缺口进度：已填 5/6（ACE + A-MEM + Skill + 双索引 + SpecCoding），剩 gap #6 多 Agent 兼容下一篇完成
- 草稿保存到 ops/publishing/series/drafts/article-06.md
- yaml 更新 article-06: draft → ready_for_review，补充 draft_date 和 draft_file
- 下一篇待写：article-07（多 Agent 兼容架构──换 AI 助手不换知识库）

### 2026-07-24（第7次执行）
- 撰写 article-07：多 Agent 兼容架构──换 AI 助手不换知识库，约 3000 字
- 核心内容：供应商锁定风险分析 → 六个 Bootstrap 文件详解（CLAUDE.md/AGENTS.md/CODEX.md/WORKBUDDY.md/GEMINI.md/HERMES.md 各自定位差异）→ Skill 双部署机制（.agents/skills/ + .claude/skills/ 30 对同步）→ 三 Agent 交叉实测（Claude Code / Codex / WorkBuddy 同任务对比）→ 竞品对比（llm-wiki-agent/claude-obsidian/atomicstrata/Mem0 多 Agent 能力）
- 6 缺口全部填完：ACE（article-02）+ A-MEM（article-03）+ Skill（article-04）+ 双索引（article-05）+ SpecCoding（article-06）+ 多 Agent（article-07）
- Git log 今日无变更，按计划顺序撰写
- 草稿保存到 ops/publishing/series/drafts/article-07.md
- yaml 更新 article-07: draft → ready_for_review，补充 draft_date 和 draft_file
- 下一篇待写：article-08（L7 场景可插拔设计──同一个架构，不同的行业）

### 2026-07-26（第8次执行）
- 撰写 article-08：同一个架构，不同的行业──FlowWiki 的 L7 场景可插拔设计，约 3000 字
- 核心内容：多业务线维护困境（三仓库 vs 一仓库 vs 分支策略都不可行）→ 骨肉分离设计（L2-L6 骨架/L1+L7 肉）→ industry.yaml 驱动机制（根因分析 vs 审计准备横向对比）→ 7 场景对比表（perspective/scenarios/skills差异）→ 3 步新增场景实战（写 YAML + bootstrap.py + e2e_test.py）→ 竞品对比（llm-wiki-agent/claude-obsidian/atomicstrata 复用率差异）→ 复用本质思考（复用的是质量保障机制而非代码）
- 深度结合项目实际：引用 lint.py check_routing() 路由验证源码、e2e_test.py 7 场景验证逻辑、bootstrap.py 8 步流水线、storage/ 下 industry.yaml 双例对比、spec/hermes-integration.md 骨肉分离架构
- Git log 今日无变更，按计划顺序撰写
- 从 article-07（多 Agent 兼容）结尾自然过渡到"换 Agent 解决了，但场景切换怎么办"
- 草稿保存到 ops/publishing/series/drafts/article-08.md
- yaml 更新 article-08: draft → ready_for_review，补充 draft_date 和 draft_file
- 下一篇待写：article-09（自适应检索策略──100页BM25、500页GraphRAG、2000页LightRAG）

### 2026-07-27（第9次执行）
- 撰写 article-09：100 页用 BM25、500 页上 GraphRAG──FlowWiki 的自适应检索策略，约 3000 字
- 核心内容：知识库规模增长导致搜索质量下降的痛点 → BM25/CJK分词/GraphRAG/LightRAG 三重进化原理 → config.toml 显式切换+fallback链路设计 → mcp_server.py search_wiki() BM25 真实代码分析 → 未来三引擎路由伪代码 → 竞品检索策略对比 → 诚实说明当前仅完整实现BM25，nano-graphrag/LightRAG为设计规范阶段 → 检索是整个信任链条的起点
- 从 article-08 结尾自然过渡到"场景建好了，规模上来后检索怎么办"
- Git log 今日无变更，按计划顺序撰写
- 坦诚说明当前检索实现状态（BM25 working，graphrag/lightrag 为设计规范），避免过度承诺
- 草稿保存到 ops/publishing/series/drafts/article-09.md
- yaml 更新 article-09: draft → ready_for_review，补充 draft_date 和 draft_file
- 下一篇待写：article-10（从 v0.1.0 到 v0.2.0──MCP Server + Docker 实战）
