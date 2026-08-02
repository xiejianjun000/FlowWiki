# FlowWiki 每日全量测试报告 — 2026-07-30

**执行时间**: 2026-07-30T02:01:50.819017 | **耗时**: 382.5s

## 总体结果

| 阶段 | 状态 | 详情 |
|------|------|------|
| Phase 1: 脚本编译 | ✅ | 13/13 通过 |
| Phase 2: CI Lint | ⚠️ | 30693 页 wiki |
| Phase 3: 4 知识库 | ✅ | 5/5 行业通过 |
| Phase 4: Hermes 验证 | ⚠️ | llm |
| Phase 5: Docker | ⚠️ | fail |
| Phase 6: 关系图质量 | ⚠️ | 30696 节点 / 27083 边 / 78.4% 孤立 |

---

## Phase 1: 脚本编译检查

- ✅ ingest_pipeline
- ✅ ace_review
- ✅ a_mem_card
- ✅ lint
- ✅ graph
- ✅ sync_dual_index
- ✅ reindex
- ✅ normalize
- ✅ build_match_index
- ✅ gen_criteria_pages
- ✅ fix_dangling
- ✅ e2e_test
- ✅ mcp_server

## Phase 2: CI Lint 检查

- 状态: warning
- wiki 页数: 30693
- frontmatter 完整: 30462
### 发现问题
- No frontmatter: wiki/enforcement-review/concepts/民航行业温室气体排放核算方法与报告指南.md
- No frontmatter: wiki/enforcement-review/concepts/水污染事件现场断控处置checklist.md
- No frontmatter: wiki/enforcement-review/concepts/2026-07-05-环境应急每日学习.md
- No frontmatter: wiki/enforcement-review/concepts/娄政发2025-2号-娄底市突发环境事件应急预案-全文与要点.md
- No frontmatter: wiki/enforcement-review/concepts/微塑料污染防治政策汇编.md
- No frontmatter: wiki/enforcement-review/concepts/温室气体排放核查机构要求.md
- No frontmatter: wiki/enforcement-review/concepts/辐射应急防护三原则.md
- No frontmatter: wiki/enforcement-review/concepts/2026-07-19-环境应急每日学习.md
- No frontmatter: wiki/enforcement-review/concepts/检验检测机构监督管理办法_2025修订版.md
- No frontmatter: wiki/enforcement-review/concepts/Phase1_深度学习笔记_20260624.md
- No frontmatter: wiki/enforcement-review/concepts/企业事业单位突发环境事件应急预案备案管理办法.md
- No frontmatter: wiki/enforcement-review/concepts/2026-06-27-环境应急每日学习.md
- No frontmatter: wiki/enforcement-review/concepts/应急演练评估标准.md
- No frontmatter: wiki/enforcement-review/concepts/化工行业温室气体排放核算方法与报告指南.md
- No frontmatter: wiki/enforcement-review/concepts/2026-07-10-环境应急每日学习.md
- No frontmatter: wiki/enforcement-review/concepts/娄底市重点河流一河一策一图编制模板与空间清单.md
- No frontmatter: wiki/enforcement-review/concepts/环境监测数据弄虚作假判定及处理办法.md
- No frontmatter: wiki/enforcement-review/concepts/2026-07-09-环境应急每日学习.md
- No frontmatter: wiki/enforcement-review/concepts/Phase5A_高德地图应急应用_20260624.md
- No frontmatter: wiki/enforcement-review/concepts/Phase4A_环境化学与毒理学_20260624.md

## Phase 3: 4 知识库顺序跑

### ✅ 根因分析 (root-cause)
- 页面数: 30707
- lint: error
- ingest: fail
### ✅ 合规审查 (compliance-review)
- 页面数: 30707
- lint: error
- ingest: fail
### ✅ 证照管理 (license-management)
- 页面数: 30707
- lint: error
- ingest: fail
### ✅ 企业合规AI管家 (enterprise-compliance)
- 页面数: 30707
- lint: error
- ingest: fail
### ✅ 执法督察评查（测试用） (enforcement-review)
- 页面数: 30707
- lint: error
- ingest: fail

## Phase 4: Hermes 验证

- 模式: llm
- 状态: ?

## Phase 5: Docker 构建

- 状态: fail

## Phase 6: 关系图质量检测

- 状态: needs_attention
- 总节点: 30696 | 总边: 27083
- 图密度: 0.88 | 孤立节点: 24054 (78.4%) | 断链: 27027

### 质量指标

| 指标 | 值 | 阈值 | 通过 |
|------|-----|------|------|
| 图密度 | 0.88 | 0.3 | ✅ |
| 孤立率 | 78.4 | 40.0 | ❌ |
| 断链数 | 27027 | 3 | ❌ |

### 4 知识库覆盖度

| 知识库 | 期望概念 | 已覆盖 | 覆盖率 | 互联密度 | 状态 |
|--------|----------|--------|--------|----------|------|
| 根因分析 | 9 | 7 | 77.8% | 0.0 | ⚠️ |
| ↳ 缺失: 自上而下 vs 自下而上, 定量分析 vs 定性分析 | | | | | |
| 合规审查 | 8 | 0 | 0.0% | 0 | ⚠️ |
| ↳ 缺失: 案卷评查标准, 程序合法性, 证据链完整性, 案卷评查操作流程, 程序审查五步法 | | | | | |
| 证照管理 | 9 | 0 | 0.0% | 0 | ⚠️ |
| ↳ 缺失: 行政许可, 资质证书, 合规边界, 审批条件, 证照审批工作流 | | | | | |
| 企业合规AI管家 | 9 | 0 | 0.0% | 0 | ⚠️ |
| ↳ 缺失: 合规管理体系, 风险评估, 合规审计, 合规培训, 合规清单生成流程 | | | | | |
| 执法督察评查（测试用） | 0 | 0 | 0% | N/A | ⚠️ |

### 发现的问题
- ❌ 孤立节点过多: 78.4%（阈值 ≤ 40.0%），24054 个节点无任何连接
- ❌ 断链: 27027 个（阈值 ≤ 3）: enforcement-review/SCHEMA → '[[../SCHEMA.md]]'; comparisons/定量分析-vs-定性分析 → '[[自上而下-vs-自下而上]]'; comparisons/定量分析-vs-定性分析 → '[[异常检测方法]]'; comparisons/自上而下-vs-自下而上 → '[[定量分析-vs-定性分析]]'; meta/lint-report → '[[数据溯源链路]]'

### 孤立节点（20）
- `enforcement-review/tools/14大类违法取证要点卡`
- `enforcement-review/comparisons/08_湖南省裁量权基准（2021版）`
- `enforcement-review/comparisons/生态环境法典_案卷评查新标准_20260815起施行`
- `enforcement-review/comparisons/07_评查细则全文（2024年版）`
- `enforcement-review/comparisons/生态环境法典_案卷评查快速查阅手册_20260815起施行`
- `enforcement-review/comparisons/生态环境法典核心解读_执法评查视角`
- `enforcement-review/comparisons/01_评查标准体系`
- `enforcement-review/comparisons/05_评查实务要点`
- `enforcement-review/articles/102_生态环境执法要有力度更要守住法治底线`
- `enforcement-review/articles/《生态环境法典》九大“检察条款”全梳理`

---
*自动生成于 2026-07-30T02:01:50.819205*