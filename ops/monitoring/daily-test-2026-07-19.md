# FlowWiki 每日全量测试报告 — 2026-07-19

**执行时间**: 2026-07-19T06:42:58.708775 | **耗时**: 4.4s

## 总体结果

| 阶段 | 状态 | 详情 |
|------|------|------|
| Phase 1: 脚本编译 | ✅ | 13/13 通过 |
| Phase 2: CI Lint | ✅ | 132 页 wiki |
| Phase 3: 4 知识库 | ✅ | 5/5 行业通过 |
| Phase 4: Hermes 验证 | ⚠️ | llm |
| Phase 5: Docker | ⚠️ | fail |
| Phase 6: 关系图质量 | ✅ | 137 节点 / 441 边 / 8.8% 孤立 |

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

- 状态: pass
- wiki 页数: 132
- frontmatter 完整: 132

## Phase 3: 4 知识库顺序跑

### ✅ 根因分析 (root-cause)
- 页面数: 141
- lint: pass
- ingest: pass
### ✅ 合规审查 (compliance-review)
- 页面数: 141
- lint: pass
- ingest: pass
### ✅ 证照管理 (license-management)
- 页面数: 141
- lint: pass
- ingest: pass
### ✅ 企业合规AI管家 (enterprise-compliance)
- 页面数: 141
- lint: pass
- ingest: pass
### ✅ 执法督察评查（测试用） (enforcement-review)
- 页面数: 141
- lint: pass
- ingest: pass

## Phase 4: Hermes 验证

- 模式: llm
- 状态: api_error
- root-cause: ok (4 concepts)
- compliance-review: needs_attention (0 concepts)
- license-management: needs_attention (0 concepts)
- enterprise-compliance: needs_attention (0 concepts)
- enforcement-review: needs_attention (0 concepts)

## Phase 5: Docker 构建

- 状态: fail

## Phase 6: 关系图质量检测

- 状态: pass
- 总节点: 137 | 总边: 441
- 图密度: 3.22 | 孤立节点: 12 (8.8%) | 断链: 0

### 质量指标

| 指标 | 值 | 阈值 | 通过 |
|------|-----|------|------|
| 图密度 | 3.22 | 0.3 | ✅ |
| 孤立率 | 8.8 | 40.0 | ✅ |
| 断链数 | 0 | 3 | ✅ |

### 4 知识库覆盖度

| 知识库 | 期望概念 | 已覆盖 | 覆盖率 | 互联密度 | 状态 |
|--------|----------|--------|--------|----------|------|
| 根因分析 | 9 | 7 | 77.8% | 0.0 | ⚠️ |
| ↳ 缺失: 自上而下 vs 自下而上, 定量分析 vs 定性分析 | | | | | |
| 合规审查 | 8 | 1 | 12.5% | 0.0 | ⚠️ |
| ↳ 缺失: 案卷评查标准, 证据链完整性, 案卷评查操作流程, 程序审查五步法, 证据链审核指南 | | | | | |
| 证照管理 | 9 | 0 | 0.0% | 0 | ⚠️ |
| ↳ 缺失: 行政许可, 资质证书, 合规边界, 审批条件, 证照审批工作流 | | | | | |
| 企业合规AI管家 | 9 | 0 | 0.0% | 0 | ⚠️ |
| ↳ 缺失: 合规管理体系, 风险评估, 合规审计, 合规培训, 合规清单生成流程 | | | | | |
| 执法督察评查（测试用） | 0 | 0 | 0% | 0 | ⚠️ |

### 孤立节点（12）
- `comparisons/定量分析-vs-定性分析`
- `comparisons/自上而下-vs-自下而上`
- `meta/lint-report`
- `meta/agent-compatibility`
- `meta/e2e-test-report`
- `playbooks/局部分析工作流`
- `playbooks/跨域分析工作流`
- `playbooks/根因分析五步法`
- `criteria/环境条件`
- `criteria/数据质量`

---
*自动生成于 2026-07-19T06:42:58.708890*