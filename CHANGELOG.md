# 更新日志

FlowWiki 的所有重要变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

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
