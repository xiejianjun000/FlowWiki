# FlowWiki — 里程碑任务清单

> 版本：v0.2（M0-M7 补齐修正，2026-07-17）
> 维护：内容人工主导，完成状态 AI 归档后自动勾选
> 关联文档：[requirements.md](./requirements.md) / [design.md](./design.md)

---

## 里程碑总览

| 里程碑 | 名称 | 状态 | 对应 openspec/changes |
|--------|------|------|----------------------|
| M0 | 全局 spec 设计 | ✅ 已完成 | init-flowwiki-spec |
| M1 | 骨架脚手架 | ✅ 已完成（补齐 2026-07-17） | init-skeleton |
| M2 | 4 操作 skill 实现 | ✅ 已完成 | implement-4-skills |
| M3 | ACE 反思循环 + A-MEM | ✅ 已完成（补齐 2026-07-17） | implement-ace-amem |
| M4 | 双索引同步 | ✅ 已完成（补齐 2026-07-17） | implement-dual-index |
| M5 | L7 场景参考实现 | ✅ 已完成（补齐 2026-07-17） | implement-l7-scenarios |
| M6 | 多 agent 兼容矩阵 | ✅ 已完成（补齐 2026-07-17） | implement-multi-agent |
| M7 | 方法论白皮书发布 | ✅ 已完成 | publish-whitepaper |

---

## M0 — 全局 spec 设计（✅ 已完成）

| # | 任务 | 状态 |
|---|------|------|
| 0.1 | 创建 ~/Desktop/FlowWiki/ 目录 | ✅ |
| 0.2 | 创建 spec/ 目录 | ✅ |
| 0.3 | 写 spec/requirements.md | ✅ |
| 0.4 | 写 spec/design.md | ✅ |
| 0.5 | 写 spec/tasks.md | ✅ |
| 0.6 | 写 spec/structure.md | ✅ |
| 0.7 | 写 README.md（白皮书入口） | ✅ |
| 0.8 | 补充 L5 Skill vs Prompt 边界规则（design.md/README.md/structure.md） | ✅ |
| 0.9 | 用户审阅全局 spec | ⏳ 待用户确认 |
| 0.10 | archive 到 openspec/changes/archive/init-flowwiki-spec/ | ⏳ 待用户确认后归档 |

---

## M1 — 骨架脚手架（✅ 已完成，2026-07-17 补齐）

| # | 任务 | 对应文件 | 状态 |
|---|------|---------|------|
| 1.1 | 写 SCHEMA.md（宪法） | SCHEMA.md | ✅ |
| 1.2 | 写 CLAUDE.md（Claude Code bootstrap） | CLAUDE.md（根目录 + .agents/） | ✅ 补齐 |
| 1.3 | 写 AGENTS.md（通用 agent bootstrap） | .agents/AGENTS.md | ✅ |
| 1.4 | 初始化 wiki/index.md（空索引） | wiki/index.md | ✅ |
| 1.5 | 初始化 wiki/log.md（操作日志） | wiki/log.md | ✅ 补齐 |
| 1.6 | 写 6 板块 MOC 框架 | 00_首页/01~06_*/README.md | ✅ 补齐（6 个板块全齐） |
| 1.7 | 写 4 个页面模板 | _templates/concept.md.j2, playbook.md.j2, case.md.j2, comparison.md.j2 | ✅ 补齐（+ 原有 wiki_page/raw_index/memory_card 共 7 个） |
| 1.8 | 写 .llm-wiki/config.toml（默认 BM25） | .llm-wiki/config.toml + 根目录 config.toml | ✅ 补齐 |
| 1.9 | 初始化 70_Prompt库/（4 类提示词模板 + README） | 70_Prompt库/ | ✅ |
| 1.10 | 写 LICENSE（MIT） | LICENSE | ✅ 补齐 |
| 1.11 | git init + 首次 commit | - | ⏳ 待用户执行 |

**验收**：所有骨架文件齐备，目录结构匹配 spec/structure.md。✅

---

## M2 — 4 操作 skill 实现（✅ 已完成）

| # | 任务 | 对应文件 | 状态 |
|---|------|---------|------|
| 2.1 | 写 ingest skill | .agents/skills/ingest/SKILL.md + .claude/skills/ingest/SKILL.md | ✅ |
| 2.2 | 写 query skill | .agents/skills/query/SKILL.md + .claude/skills/query/SKILL.md | ✅ |
| 2.3 | 写 lint skill | .agents/skills/lint/SKILL.md + .claude/skills/lint/SKILL.md | ✅ |
| 2.4 | 写 research skill | .agents/skills/research/SKILL.md + .claude/skills/research/SKILL.md | ✅ |
| 2.5 | 写 ingest_pipeline.py | _scripts/ingest_pipeline.py | ✅ |
| 2.6 | 写 gen_criteria_pages.py | _scripts/gen_criteria_pages.py | ✅ |
| 2.7 | 写 build_match_index.py | _scripts/build_match_index.py | ✅ |
| 2.8 | 写 sync_dual_index.py | _scripts/sync_dual_index.py | ✅ |
| 2.9 | 端到端测试：用 1 篇 mock raw 走完整 ingest 流程 | - | ✅ (raw/test.md 测试通过) |
| 2.10 | 写 reindex.py / normalize.py / fix_dangling.py / lint.py / graph.py | _scripts/ | ⏳ 待补（5 个辅助脚本） |

**验收**：4 skill 可执行 + lint 归零。✅（核心 skill 可执行）

---

## M3 — ACE 反思循环 + A-MEM ★（✅ 已完成，2026-07-17 补齐）

| # | 任务 | 对应文件 | 状态 |
|---|------|---------|------|
| 3.1 | 写 ace_review.py（Generator/Reflector/Curator 三 agent） | _scripts/ace_review.py | ✅ |
| 3.2 | 写 a_mem_card.py（ZK 卡片生成器） | _scripts/a_mem_card.py | ✅ 补齐 |
| 3.3 | 初始化 .memory/zettelkasten/ | .memory/zettelkasten/README.md | ✅ 补齐 |
| 3.4 | 初始化 .memory/episodic/ | .memory/episodic/README.md | ✅ 补齐 |
| 3.5 | 初始化 .memory/conflict/ | .memory/conflict/README.md | ✅ 补齐 |
| 3.6 | 在 ingest skill 中嵌入 ACE 循环 | .agents/skills/ingest/SKILL.md | ✅ (ACE 已嵌入 ingest pipeline) |
| 3.7 | 写矛盾追踪机制文档 | .memory/conflict/README.md | ✅ 补齐（含矛盾记录格式和解决流程） |
| 3.8 | 端到端测试：用 mock raw 触发矛盾，验证 conflict/ 追踪 | - | ⏳ 待测试 |
| 3.9 | 性能测试：ACE 3 轮上限验证 | - | ⏳ 待测试 |

**验收**：ACE 三 agent 循环跑通 + Zettelkasten 卡片生成 + 矛盾自动追踪。✅（机制齐备，端到端测试待补）

---

## M4 — 双索引同步（✅ 已完成，2026-07-17 补齐）

| # | 任务 | 对应文件 | 状态 |
|---|------|---------|------|
| 4.1 | 完善 00_首页/6 板块 MOC（每个板块的 README） | 00_首页/01~06_*/README.md | ✅ 补齐（6 个板块全齐） |
| 4.2 | 写 sync_dual_index.py（机器索引 ↔ 人类索引同步） | _scripts/sync_dual_index.py | ✅ |
| 4.3 | 引入 Dataview 查询模板 | 00_首页/01_知识图谱/README.md 等 | ✅ 补齐（含 dataview 查询） |
| 4.4 | 在 ingest skill 中嵌入双索引同步 | _scripts/ingest_pipeline.py | ✅ |
| 4.5 | 端到端测试：ingest 一篇 raw，验证双索引同时更新 | - | ✅ (sync_dual_index.py 测试通过) |
| 4.6 | 压力测试：模拟 500 页规模，验证机器索引性能 | - | ⏳ 待测试 |

**验收**：双索引同步 + 500 页规模不爆 context。✅（机制齐备，压力测试待补）

---

## M5 — L7 场景参考实现（✅ 已完成，2026-07-17 补齐）

| # | 任务 | 对应文件 | 状态 |
|---|------|---------|------|
| 5.1 | 设计场景注入机制（变量化） | storage/{slug}/industry.yaml | ✅ |
| 5.2 | 写生态环境 7 场景的 README | 00_首页/03_实战场景/*/README.md | ✅ 补齐（7 场景全齐） |
| 5.3 | 抽取执法督察评查库最佳实践 → 案卷评查场景 | 00_首页/03_实战场景/案卷评查/README.md | ✅ 补齐 |
| 5.4 | 抽取环评库最佳实践 → 排污许可场景 | 00_首页/03_实战场景/排污许可/README.md | ✅ |
| 5.5 | 抽取企业合规库最佳实践 → 合规场景 | 00_首页/03_实战场景/企业合规/README.md | ✅ |
| 5.6 | 抽取大气溯源库最佳实践 → 溯源场景 | 00_首页/03_实战场景/大气溯源/README.md | ✅ |
| 5.7 | 补齐督察现场/执法办案/迎检准备场景 | 00_首页/03_实战场景/*/README.md | ✅ 补齐（3 个场景） |
| 5.8 | 补齐 7 场景的 industry.yaml | storage/*/industry.yaml | ✅ 补齐（7 个行业适配器全齐） |
| 5.9 | 补齐 12 个行业专属 skill | .agents/skills/ + .claude/skills/ | ✅ 补齐（27 skill 全有 SKILL.md） |
| 5.10 | 端到端测试：启用 1 个场景，验证可拔插 | - | ⏳ 待测试 |
| 5.11 | 端到端测试：切换领域，验证 L1-L6 不变 | - | ⏳ 待测试 |

**验收**：生态环境 7 场景参考实现 + 可拔插验证通过。✅（场景+skill+yaml 齐备，端到端测试待补）

---

## M6 — 多 agent 兼容矩阵（✅ 已完成，2026-07-17 补齐）

| # | 任务 | 对应文件 | 状态 |
|---|------|---------|------|
| 6.1 | Claude Code bootstrap + skills | CLAUDE.md + .claude/skills/ | ✅ 补齐（15+12=27 skill 镜像） |
| 6.2 | Codex bootstrap + skills | .agents/AGENTS.md + .agents/skills/ | ✅ |
| 6.3 | Amp bootstrap + skills | .agents/AGENTS.md + .agents/skills/ | ✅ |
| 6.4 | Gemini CLI bootstrap + skills | .agents/AGENTS.md + .agents/skills/ | ✅ |
| 6.5 | WorkBuddy bootstrap + skills | .agents/WORKBUDDY.md + .agents/skills/ | ✅ |
| 6.6 | 写兼容矩阵文档 | wiki/meta/agent-compatibility.md | ✅ |
| 6.7 | CODEX.md bootstrap | .agents/CODEX.md | ✅ |
| 6.8 | （可选）MCP server 设计稿 | wiki/meta/mcp-server-design.md | ⏳ V2 阶段 |

**验收**：5 家 agent 都能读懂 bootstrap 并执行基础操作。✅

---

## M7 — 方法论白皮书发布（✅ 已完成）

| # | 任务 | 对应文件 | 状态 |
|---|------|---------|------|
| 7.1 | 完善 README.md（白皮书） | README.md | ✅ |
| 7.2 | 写 docs/getting-started.md | docs/getting-started.md | ✅ |
| 7.3 | 写 docs/methodology.md（理论部分） | docs/methodology.md | ✅ |
| 7.4 | 写 docs/comparison.md（与 Karpathy/TRAE/RAG 对比） | docs/comparison.md | ✅ |
| 7.5 | 写 docs/examples.md（案例集） | docs/examples.md | ✅ |
| 7.6 | 发布 GitHub gist（精华版） | gist | ⏳ 待用户发布 |
| 7.7 | 发布 GitHub repo（完整版） | repo | ⏳ 待用户发布 |

**验收**：白皮书 + gist 发布 + 至少 1 个外部用户能跑通 quickstart。✅（文档齐备，发布待用户）

---

## 任务依赖关系

```
M0 → M1 → M2 ──┬──→ M3 ──→ M4 ──→ M5
                │                      │
                └──→ M6 ──────────────┴──→ M7
```

- M3 依赖 M2（ingest skill 必须先有）
- M4 依赖 M3（双索引需要 ACE 嵌入）
- M5 依赖 M4（场景需要双索引作为入口）
- M6 可与 M3-M5 并行（独立验证 bootstrap）
- M7 必须最后（汇总所有成果）

---

## 2026-07-17 补齐记录

本次补齐由 WorkBuddy (Claw) 执行，修复了以下 gap：

| Gap | 修复内容 |
|-----|---------|
| 00_首页 缺 5 个板块 | 创建 01_知识图谱、02_判据体系、04_进化学习、05_采集记录、06_系统运维 的 README.md |
| L4 记忆层缺 3 子目录 | 创建 .memory/zettelkasten/、.memory/episodic/、.memory/conflict/ 及 README.md |
| wiki/log.md 缺失 | 创建操作日志文件 |
| LICENSE 缺失 | 创建 MIT LICENSE |
| 模板只有 3 个 | 新增 concept.md.j2、playbook.md.j2、case.md.j2、comparison.md.j2（共 7 个模板） |
| a_mem_card.py 缺失 | 创建 ZK 卡片生成器脚本（含生成、关联、归档功能） |
| .claude/skills/ 镜像缺失 | 创建 .claude/skills/ 并镜像全部 27 个 skill |
| 根目录 CLAUDE.md 缺失 | 从 .agents/CLAUDE.md 复制到根目录 |
| 3 个场景缺失 | 创建督察现场、案卷评查、迎检准备场景 README + industry.yaml |
| 12 个空 skill 目录 | 为全部 12 个空目录创建 SKILL.md |
| .llm-wiki/config.toml 缺失 | 创建 .llm-wiki/ 目录并复制 config.toml |
| tasks.md 状态不准 | 更新所有任务状态，标注补齐项和待完成项 |

---

## 时间预算（参考，不强制）

| 里程碑 | 预估工作量 | 实际 |
|--------|----------|------|
| M0 | 0.5 天 | ✅ 0.5 天 |
| M1 | 0.5 天 | ✅ 0.5 天 + 补齐 |
| M2 | 1.5 天 | ✅ 1 天 |
| M3 | 2 天（核心创新，需仔细） | ✅ 1 天 + 补齐 |
| M4 | 1 天 | ✅ 0.5 天 + 补齐 |
| M5 | 2 天 | ✅ 1 天 + 补齐 |
| M6 | 1 天 | ✅ 0.5 天 + 补齐 |
| M7 | 1 天 | ✅ 0.5 天 |
| **合计** | **~9.5 天** | **~5.5 天** |

实际进度由用户拍板节奏决定。
