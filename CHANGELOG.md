# 更新日志

FlowWiki 的所有重要变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [0.4.0] - 2026-07-20

### 新增
- **执法督察评查知识库全栈升级** — 155 篇专业文档的 enforcement-review 参考实现完全落地，含 109 节点 479 边关系图谱、6 页 00_首页/运营看板、7 行业适配器数据同步
- **ACE 原文指针铁律** — `ace_review.py` v3.0 强制指针+按需展开替代全文入库，raw/ 保持只读不可篡改
- **4 项方法论迭代** — status 字段修复、strict 强制执行模式、引用追踪链、知识缺口自动检测
- **Lint 增强 4 项检查** — 新增 index 自动同步、frontmatter 完整性、wikilink 有效性、命名规范检查
- **raw 入仓时间戳** — 每次文件采集自动记录入仓时间，每日采集记录自动生成
- **Playbook 模板增强** — coverage 报告新增类型建议，场景模板更完善
- **行业路由完整性** — 7 行业适配器路由覆盖验证，限值表标准化

### 修复
- 修复入仓时间戳插入逻辑，消除重复 `updated` 字段
- 刷新 00_首页/6 页 enforcement-review 运营数据（109 节点 479 边）

### 变更
- **仓库治理** — 从仓库彻底移除知识库内容文件，`.gitignore` 添加路径防护规则，确保方法论项目与用户知识库严格分离
- 参考实现数据同步到 `raw/enforcement-review/` 路径

### 数据
- 执法督察评查知识库：155 篇文档 / 109 节点 / 479 边 / 85%+ 可路由率
- 测试覆盖：13 脚本全绿 / 5 知识库全通过 / CI lint 零告警

## [0.3.0] - 2026-07-20

### P0 新增（竞品研究驱动 · 1-2天迭代）
- **全局 Skill 部署** — `.skills/wiki-query/SKILL.md` + `.skills/wiki-update/SKILL.md` + `_scripts/setup.sh`，一键安装到 8 个 Agent 路径（Claude Code/Gemini CLI/Codex/Hermes/OpenClaw/Copilot CLI/Kiro/OpenCode），知识可跨项目流动
- **`_raw/` 快速暂存** — `_scripts/ingest_pipeline.py --quick`，TRIAGE 级浅层过滤，支持 stdin/--file/--text 三种输入，content-hash 去重幂等
- **GEMINI.md + HERMES.md** — 新增 Gemini CLI 和 Hermes 核验 Agent 引导文件，Agent 兼容性 4→8

### P1 新增（伴侣式记忆驱动 · 3-5天迭代）
- **记忆衰减机制** — `_scripts/decay.py`，生命力公式（recency + frequency + utility + gravity - wear_penalty），引力保护底线条目免衰减，低价值条目压缩为摘要，归档为终态不删除
- **少数派分支** — ACE v3.0 新增 `.memory/minority/` 矛盾缓存机制，V4（单源矛盾→Buffer）→ V5（多源多周期≥3→Compensate），矛盾不静默抹平
- **冲突路由矩阵** — SCHEMA §10 新增 7 种冲突类型的明确路由规则（Mirror/Compensate/Buffer/AUDIT override/External correction），附缓冲压力管道图
- **git-snapshot 防御性写入** — ACE v3.0 写入前自动 git stash，异常时 git stash pop 回滚（参考 Ar9av v2026.07.6）

### 变更
- SCHEMA.md 版本 2.1→2.2：新增 §10 冲突路由矩阵、L6 Agent 数量 4→8
- AGENTS.md 触发词更新：新增 gemini/hermes/opencode/aider/droid
- `_scripts/ace_review.py` v2.0→v3.0：新增 minority branch + git-snapshot + dedup bug 修复

### 参考
- 竞品深度研究：Ar9av/obsidian-wiki (2,928 Stars) + 伴侣式记忆论文 (Miteski 2026)
- 完整研究：`junge-hermes/监控日报/竞品深度研究-Ar9av与伴侣式记忆-2026-07-20.md`

---

## [0.2.0] - 2026-07-18

### 新增
- **MCP Server** — `_scripts/mcp_server.py`，暴露 5 个工具（query/read/lint/research/index），支持 stdio/SSE 双传输
- **Docker 部署** — `Dockerfile`（多阶段构建）、`docker-compose.yml`（flowwiki + mcp-server 双服务）、`.dockerignore`
- **MCP 集成文档** — `docs/mcp-integration.md`，含 Claude Code/Codex/Cursor 接入指南
- **`.mcp.json`** — 项目级 MCP 配置，Claude Code 打开项目自动加载
- **`requirements.txt`** — 锁定 PyYAML + MCP SDK 依赖

### 变更
- **README** — 新增 2026 Q3 竞品全景对比表（nashsu/SamurAIGPT/atomicstrata/agentmemory/mem0）
- **README** — 新增 Docker 部署和 MCP Server 接入说明
- **README** — Tech Stack 表更新为含 Docker + MCP
- **GitHub Topics** — 添加 14 个标签（llm-wiki, knowledge-base, agent-memory 等）提升可发现性

---

## [0.1.0] - 2026-07-17

### 新增

#### 七层架构（首个完整实现）

- **L1 知识编译层** — 双索引架构，`raw/`（只读源文件）→ `wiki/`（AI 编译）→ `00_首页/`（6 板块人类入口）
- **L2 检索增强层** — 自适应三级检索：≤100 页 BM25+CJK 分词 → 100-500 页 nano-graphrag → 500+ 页 LightRAG
- **L3 Spec-Driven 层** — OpenSpec 集成，`spec/` 全局设计 + `openspec/changes/` 单任务变更追溯
- **L4 Agent 记忆层** — A-MEM Zettelkasten 卡片（跨会话记忆）+ ACE 反思循环（Generator→Reflector→Curator 三 agent 防幻觉）
- **L5 Skill 化层** — 任务→知识→Skill 三元组，高频任务自动抽象为 O(1) 调用
- **L6 多 Agent 层** — 五家 agent 兼容：CLAUDE.md / AGENTS.md / CODEX.md / WORKBUDDY.md 四引导文件
- **L7 场景层** — 行业场景可插拔，通用骨架 + `industry.yaml` 业务变量分离

#### 业务场景（7 个）

- 根因分析（root-cause）— 建立一企一档和长期溯源知识库
- 合规审查（compliance-review）— 对已知源做多维合规审查
- 证照管理（license-management）— 证照全生命周期追踪
- 企业合规（enterprise-compliance）— 企业资质与环境义务合规
- 审计现场（audit-onsite）— 审计现场即时问答与证据检索
- 案例分析（case-review）— 典型案件结构化分析与经验库建设
- 审计准备（audit-prep）— 审计前的清单/模板/时间线生成

#### Skill 系统（27 个）

- 4 核心操作 skill：`ingest` / `query` / `lint` / `research`
- 23 行业场景 skill：覆盖 7 大业务场景的专用 skill
- **双部署**：`.agents/skills/` 和 `.claude/skills/` 同步维护，五家 agent 通用

#### ACE 反思循环

- Generator → Reflector → Curator 三 agent 逐级制约
- ingest 时拦截错误知识，防止幻觉永久化
- 矛盾显式标注，旧说法被推翻时不静默覆盖
- `conflict/` 目录记录和跟踪知识冲突

#### A-MEM 卡片记忆系统

- Zettelkasten 卡片格式，跨会话可读
- `episodic/` 情景记忆记录每次操作上下文
- `.memory/` 持久化存储，零数据库依赖

#### 测试体系

- 114 个端到端测试覆盖核心场景
- `_scripts/test-e2e.sh` 一键运行

#### CI/CD

- GitHub Actions CI 自动运行测试
- 幂等性检查
- Frontmatter 格式验证
- 文件结构完整性检查

#### 检索系统

- BM25 基础检索 + CJK 中文分词支持
- nano-graphrag 轻量图谱检索（100-500 页规模）
- LightRAG 完整图谱增强（500+ 页规模）
- 按知识库规模自动切换检索策略

---

[0.1.0]: https://github.com/xiejianjun000/FlowWiki/releases/tag/v0.1.0
