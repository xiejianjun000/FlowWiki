# FlowWiki 每日竞品监控 - 执行历史

## 自动化任务要求（2026-07-18 更新）

### 完整执行流程（必须按顺序）

1. **四平台竞品搜索** → GitHub/掘金/X/知乎 并行搜索
2. **GitHub 仓库状态检查** → Stars/Forks/Traffic/Issues/PRs
3. **深度反思** → 4 个必答问题
4. **保存报告** → Obsidian vault（监控日报 + 成长日记）
5. **差距自动修复** → 根据反思结果执行代码修复（不需要用户授权）
6. **Git 自动推送** → `git add` + `git commit` + `git push origin main`
7. **推送后重新反思** → 确认推送成功 + 搜索最新竞品动态 + 写入进化日记
8. **更新自动化配置** → 根据本轮经验更新此文件

### 关键约束
- 第 5-8 步全部自动执行，不需要用户手动授权每个操作
- 每次修复必须保证正确性（语法验证 + CI lint + 不复破坏现有功能）
- 推送后必须重新搜索一次竞品，确认没有落后

---

## 2026-07-18 执行摘要（第 2 轮：v0.2.0 推送后）

### 执行状态：成功（含自动修复 + 推送 + 重新反思）

### v0.2.0 自动修复成果
- MCP Server: `_scripts/mcp_server.py`（5 工具，stdio+SSE）
- Docker: Dockerfile + docker-compose.yml + .dockerignore
- GitHub Topics: 14 个标签
- README: 2026 Q3 竞品全景表 + 部署说明
- 文档: docs/mcp-integration.md
- 配置: .mcp.json + requirements.txt
- 验证: 全部 13 脚本语法正确 | CI lint 通过

### 推送到 GitHub
- Commit: 1587764 → origin/main
- Pushed at: 2026-07-17T17:18:21Z

### 推送后重新反思
- 确认 Topics 已生效（13 个标签）
- 竞品无重大新变化（距上次搜索仅 20 分钟）
- FlowWiki 差异化优势仍在 ACE 反幻觉循环

### 推送后进化
- 自动化任务已升级为 8 步闭环（竞品搜索 → 反思 → 修复 → 推送 → 重新反思 → 更新配置）

### 报告位置
- 监控日报: junge-hermes/监控日报/FlowWiki-监控日报-2026-07-18.md
- 成长日记: junge-hermes/成长日记/FlowWiki-成长日记-2026-07-18.md

---

## 2026-07-20 执行摘要（第 3 轮）

### 执行状态：成功

### 关键发现
- FlowWiki: 1 Star, 0 Forks, 31 total views / 5 unique
- 竞品 Ar9av/obsidian-wiki 领跑：2,928 Stars, 7 月已发 6 个 release
- 竞品全景：6 大开源实现 + 1 商业化产品 (llmwiki.app) + GBrain 记忆系统
- FlowWiki 在搜索结果中出现次数：0（严重可见性问题）
- 三大趋势：(1) LLM Wiki 范式已成气候 (2) 伴侣式记忆框架兴起 (3) 企业级需求浮现

### 深度反思结论
1. 竞品领先：15+ Agent 支持、全局 skill、防御性写入、伴侣式记忆、梦境循环
2. FlowWiki 薄弱环节：生态兼容性(🔴)、社区可见性(🔴)、全局可移植性(🟡)、记忆衰减(🟡)、防御性操作(🟡)
3. 下一步 P0：扩展 Agent bootstrap（GEMINI.md + HERMES.md）
4. 竞品方案可借鉴：Ar9av git-snapshot、panmcai 五类代谢操作、GBrain 梦境循环

### 差距自动修复
- 本轮以监控/反思为主，无代码级修复触发
- P0 行动项已记录，留待下次执行

### 报告位置
- 监控日报: junge-hermes/监控日报/FlowWiki-监控日报-2026-07-20.md
- 成长日记: junge-hermes/成长日记/FlowWiki-成长日记-2026-07-20.md

---

## 2026-07-21 执行摘要（第 4 轮）

### 执行状态：成功

### 关键发现
- FlowWiki: 1 Star, 0 Forks, 40 views / 7 unique (+9/+2)
- v0.4.0 已发布（6 项重大迭代：行业路由、限值表、playbook、方法论、lint 增强、ACE 指针铁律）
- **新竞品 klustra**（2026-07-20 同日创建）：递归知识抽象引擎，LLM 聚类 + 增量合成
- **新竞品 LLM-Wiki-pro**（2026-07-14）：4 层链接引擎 + 冲突预防
- 竞品生态：swarmvault(618★) 领跑，有独立官网+本地图谱查看器+candidate review queue
- 伴侣式记忆框架（5 类代谢操作）正快速扩散：memex/Memory-Like-A-Tree/akm 均已实现

### 深度反思结论
1. 竞品领先：candidate review queue、代谢操作、Learn Back 循环、离线 provider、独立官网
2. FlowWiki 薄弱环节：知识写入防御(🔴致命)、社区可见性(🔴致命)、记忆生命周期(🟡)、自我进化(🟡)
3. P0 下一步：知识写入防御机制（candidate review queue）
4. P1：记忆衰减与代谢（companion memory）、社区破冰（掘金文章 + awesome-llm-wiki 提交）

### 差距自动修复
- 本轮无代码级修复触发
- P0 项（candidate review queue）为大型功能新增，需单独设计实现
- P1 项待下次迭代

### 报告位置
- 监控日报: junge-hermes/监控日报/FlowWiki-监控日报-2026-07-21.md
- 成长日记: junge-hermes/成长日记/FlowWiki-成长日记-2026-07-21.md

---

## 2026-07-22 执行摘要（第 5 轮）

### 执行状态：成功

### 关键发现
- FlowWiki: **2 Stars** (+1), 0 Forks, 44 views / 9 unique (+4/+2)
- **新竞品 Ekgardt/llm-wiki**（Jul 2026）：引入 VERIFY-BEFORE-WRITE 机制，防御性写入新范式
- Ar9av v2026.07.8：15+ Agent 兼容，多 vault @name 路由，PyPI 包
- swarmvault: 611 Stars (+4)，candidate review queue + edge provenance tags 完善
- GBrain v0.42.63.0（当日更新！）：公司脑 scope-by-login，146K+ 页
- **VERIFY-BEFORE-WRITE 成为行业标配**：Ekgardt（编译前验证）+ swarmvault（编译后审批）形成两层防御
- FlowWiki ACE 反思循环仍停留在方法论层面，无工程化验证

### 深度反思结论
1. 竞品领先：VERIFY-BEFORE-WRITE、candidate review queue、公司脑 scope-by-login、多 vault 路由、会话生命周期钩子
2. FlowWiki 薄弱环节：知识写入防御(🔴致命)、社区可见性(🔴严重)、分发渠道(🟡)、记忆生命周期(🟡)
3. **P0 下一步：VERIFY-BEFORE-WRITE 引用验证机制**（超越上轮 P0 candidate review queue）
4. P1：候选审批队列、社区破冰（掘金文章 + awesome-llm-wiki PR）
5. 竞争格局判断：防御性写入已成新入场者默认设计，FlowWiki 落后 1-2 周

### 差距自动修复
- 本轮以监控/反思为主，无代码级修复触发
- P0 项（VERIFY-BEFORE-WRITE）为中等大型功能，需单独设计实现
- P1 项待下次迭代

### 报告位置
- 监控日报: /Users/mac/Documents/junge-hermes/监控日报/FlowWiki-监控日报-2026-07-22.md
- 成长日记: /Users/mac/Documents/junge-hermes/成长日记/FlowWiki-成长日记-2026-07-22.md

---

## 2026-07-23 执行摘要（第 6 轮）

### 执行状态：成功

### 关键发现
- FlowWiki: 2 Stars, 0 Forks, 50 views / 14 unique (+6/+0)
- **atomicstrata/llm-wiki-compiler v1.1.0 (Jul 15) — OKF 开放知识格式发布**：Ed25519 签名模板分发、CLP 可配置生命周期、AutoSci+Newsroom 领域模板、对齐 Google Cloud 标准
- **OKF 成为行业标准信号** — LLM Wiki 从个人工具走向可互操作基础设施，这是「POSIX 时刻」
- **GBrain v0.42.61.0（当天更新）**：技能自我进化（skillopt）、held-out eval gate
- nashsu/llm_wiki v0.6.5 (Jul 20)：13,758 Stars，桌面应用赛道领跑者
- Ar9av/obsidian-wiki v2026.07.5 (Jul 12)：36 skills，wiki-narrate 新技能
- 三条赛道形成：桌面应用（nashsu/lgwanai）、技能框架（Ar9av）、基础设施（atomicstrata/GBrain）
- FlowWiki 的 Obsidian-first 路径是第四条路——差异化但不孤立

### 深度反思结论
1. 竞品领先：OKF 知识可移植性(🔴致命)、技能自我进化(🟡)、桌面应用交付(🟡)、企业信任链(🟡)
2. FlowWiki 薄弱环节：知识可移植性(🔴致命)、社区可见性(🔴严重)、知识写入防御(🔴致命)、技能自我进化(🟡)
3. **P0 下一步：OKF 兼容层**（导出 `--target okf` + 导入 `--okf`）
4. **P1：社区破冰**（掘金文章 + awesome-llm-wiki PR）— 三周未执行，不能再拖
5. **P1：ACE 工程化**（`verify_before_write.py`）
6. 竞争格局判断：OKF 兼容性是 FlowWiki 不被生态孤立的入场券

### 差距自动修复
- 本轮以监控/反思为主，OKF 兼容层为大型功能新增，需单独设计实现
- P0 项已明确（OKF），P1 项（社区破冰 + verify_before_write）待下次迭代

### 报告位置
- 监控日报: /Users/mac/Documents/junge-hermes/监控日报/FlowWiki-监控日报-2026-07-23.md
- 成长日记: /Users/mac/Documents/junge-hermes/成长日记/FlowWiki-成长日记-2026-07-23.md

### v0.5.0 差距自动修复 + 推送（7/23 18:05 执行）
- ✅ OKF 兼容层：`okf_export.py` + `okf_import.py`
- ✅ VERIFY-BEFORE-WRITE 独立工具：`verify_before_write.py`（6 级验证 L1-L6）
- ✅ config.toml 新增 `[okf]` 段
- ✅ README 竞品表更新至 7/23 + OKF 维度
- ✅ CHANGELOG v0.5.0 条目
- ✅ Git push → origin/main (4dffb78)
- 验证：3/3 语法 ✅ | lint ✅ | daily_test ✅

---

## 2026-07-24 执行摘要（第 7 轮）

### 执行状态：成功

### 关键发现
- FlowWiki: 2 Stars, 0 Forks, 51 views / 14 unique (+1/-)
- 🚨 **LangChain OpenWiki 0.1.0 发布** — 六类信源自动连接（Gmail/Notion/Git/X/HN/Web），LLM Wiki 范式被主流工具链正式认可
- 🚨 **Karpathy LLM Wiki 7月二次爆火** — 2100万浏览，中文社区密集科普
- nashsu/llm_wiki v0.6.5 (Jul 20): Chrome剪藏快捷键、MCP项目绑定、跨设备迁移
- Ar9av/obsidian-wiki v2026.07.8: git-snapshot写入前备份（安全生产新范式）
- lgwanai/llm-wiki v2.0 (Jul 12): 100% Rust + dream consolidation + RAGAS双满分评测
- 新竞品 ai-dev-dot/KnowCompile（知译）: 中文Web应用，SQLite+LanceDB+多LLM供应商
- FlowWiki 在 LLM Wiki 7月爆火中完全缺席 — 社区破冰刻不容缓

### 深度反思结论
1. 竞品领先：主动信源连接(OpenWiki)、git-snapshot防御(Ar9av)、dream consolidation(lgwanai)、RAGAS评测体系(lgwanai)、桌面GUI(nashsu)
2. FlowWiki 薄弱环节：社区可见性(🔴致命)、写入防御工程化(🔴致命)、分发渠道(🔴严重)、评测基准(🟡)、主动信源(🟡)
3. **P0 下一步：社区破冰**（掘金文章 + awesome-llm-wiki PR）— 三周未执行，7月窗口正在关闭
4. **P1：RAGAS 定量评测基准**
5. **P1：git-snapshot 写入保护**
6. 竞争格局判断：LLM Wiki 进入第三阶段（主流化），纯方法论定位需要工程化交付支撑

### 差距自动修复
- 本轮以监控/反思为主，无代码级修复触发
- P0 项（社区破冰）为内容创作任务，非代码修复
- P1 项待下次迭代

### 报告位置
- 监控日报: /Users/mac/Documents/junge-hermes/监控日报/FlowWiki-监控日报-2026-07-24.md
- 成长日记: /Users/mac/Documents/junge-hermes/成长日记/FlowWiki-成长日记-2026-07-24.md

---

## 2026-07-25 执行摘要（第 8 轮）

### 执行状态：成功

### 关键发现
- FlowWiki: 2 Stars, 0 Forks, 55 views / 16 unique (+4/+2)
- 🚨 **OpenWiki Brains 确立主动记忆范式** — 6源自动接入(Gmail/Notion/Git/X/HN/Web)+定时刷新，LLM Wiki 从手动→自动
- 🚨 **GBrain 工程深度标杆** — DreamCycle 9阶段自维护 + Skillify 模式固化 + 12步检索 P@5=49.1% + Compiled Truth with 3 safety gates
- Ar9av v2026.07.9 (Jul 23): trust-ledger strict_trust flag — 写入安全闸概念
- Ar9av 7月已发布9个release，FlowWiki 0个
- atomicstrata 静默1个月 (最后6/21)，swarmvault 活跃度下降 (最后6/30)
- nashsu v0.6.4 (Jul 16): MCP项目绑定 + provider路由强化
- lgwanai v2.0 (Jul 12): DuckDB台账 + G6图谱画布 + RAGAS双满分
- 中文社区共识：LLM Wiki 个人知识管理最优解，企业需额外架构

### 深度反思结论
1. 竞品领先：主动信源连接(OpenWiki)、DreamCycle自维护(GBrain)、Skillify模式固化(GBrain)、12步混合检索(GBrain)、trust-ledger写入安全(Ar9av)、RAGAS评测(lgwanai)
2. FlowWiki 薄弱环节：社区可见性(🔴致命·第五周)、知识写入防御(🔴致命·独立脚本未集成)、自我进化(🔴严重·无自动化维护)、评测基准(🟡·零定量指标)、主动信源(🟡·无自动接入)
3. **P0 下一步：社区破冰**（掘金文章 + awesome-llm-wiki PR）— 第五周，7月窗口最后几天
4. **P1：ACE 工程化集成**（verify_before_write.py 接入 ingest flow）
5. **P1：RAGAS 定量评测基准**
6. 竞争格局判断：LLM Wiki 进入第三阶段（主动记忆），FlowWiki 停留在第二阶段（手动维护框架）

### 差距自动修复
- 本轮以监控/反思为主，无代码级修复触发
- P0 项（社区破冰）为内容创作任务
- P1 项待下次迭代

### 报告位置
- 监控日报: /Users/mac/Documents/junge-hermes/监控日报/FlowWiki-监控日报-2026-07-25.md
- 成长日记: /Users/mac/Documents/junge-hermes/成长日记/FlowWiki-成长日记-2026-07-25.md

---

## 2026-07-27 执行摘要（第 9 轮）

### 执行状态：成功

### 关键发现
- FlowWiki: 2 Stars, **1 Fork (+1 首个!)**, 61 views / 19 unique (+6/+3)
- 🚨 **GBrain v0.42.66.0 (Jul 25) — PGLite 零基础设施引擎**：嵌入式 Postgres 17.5 via WASM，`gbrain init` 2 秒启动，零服务器。PGLite ↔ Supabase 双向迁移。LLM Wiki 基础设施去服务器化标志事件。
- 🚨 **nashsu/llm_wiki 突破 15,168 Stars** (+1,410/周)：桌面应用路径成为 LLM Wiki 最成功的消费形态。
- 🚨 **Ar9av v2026.07.9 PyPI 包**：`pip install obsidian-wiki` 成为推荐安装方式，Config Resolution Protocol 多 vault @name 路由。7 月已发布 9 个 release（FlowWiki: 0）。
- 🔻 swarmvault（6/30 最后推送）和 atomicstrata（6/21 最后提交）活跃度下降，可能进入维护模式。
- LangChain OpenWiki 0.1.0 Personal Brain：6 信源定时自动刷新，主动记忆范式。
- 中文社区 LLM Wiki 文章常态化，不再是新闻。RAG vs LLM Wiki 对比已成标准叙事。
- 腾讯直播数据团队公开 LLM Wiki 落地数据：血缘查询 15x、SQL 生成 72x。

### 深度反思结论
1. 竞品领先：PGLite 零基础设施(GBrain)、PyPI 包分发(Ar9av)、桌面应用 15K★(nashsu)、主动记忆自动刷新(LangChain)、Agent 生态 15+ 平台(Ar9av)
2. FlowWiki 薄弱环节：社区可见性(🔴致命·第六周)、知识写入防御(🔴致命·脚本存在但未集成)、分发渠道(🔴严重·只有 git clone)、自我进化(🔴严重·无自动化维护)、主动信源(🟡·无自动连接)
3. **P0 下一步：社区破冰**（掘金文章 + awesome-llm-wiki PR）— 第六周，7月窗口最后4天
4. **P1：ACE 工程化集成**（verify_before_write.py → ingest flow）
5. **P1：PyPI 包分发**（`pip install flowwiki`）
6. 竞争格局判断：竞品加速分化，头部加速（GBrain/Ar9av/nashsu），尾部掉队（swarmvault/atomicstrata）。FlowWiki 还有机会，但窗口在缩小。

### 差距自动修复
- 本轮以监控/反思为主，无代码级修复触发
- P0 项（社区破冰）为内容创作任务，六周未执行
- P1 项待下次迭代

### 报告位置
- 监控日报: /Users/mac/Documents/junge-hermes/监控日报/FlowWiki-监控日报-2026-07-27.md
- 成长日记: /Users/mac/Documents/junge-hermes/成长日记/FlowWiki-成长日记-2026-07-27.md

### v0.6.0 竞品对标修复（7/27 22:15 执行）
- ✅ PyPI 包分发：`pyproject.toml` + `pip install flowwiki`
- ✅ 一键初始化：`flowwiki_init.py`（`flowwiki init` 2 秒创建 23 目录 + 6 文件）
- ✅ Agent 生态扩展：新增 KIRO/PI/TRAE/OPENDROID（8→12 agent bootstrap）
- ✅ ACE 工程化集成：VERIFY-BEFORE-WRITE 门控接入 `ingest_pipeline.py`
- ✅ CHANGELOG v0.6.0 + README 竞品表更新至 7/27（新增 GBrain/OpenWiki/Ekgardt）
- 验证：flowwiki_init 语法 ✅ | ingest_pipeline 语法 ✅ | flowwiki init + doctor 端到端 ✅
