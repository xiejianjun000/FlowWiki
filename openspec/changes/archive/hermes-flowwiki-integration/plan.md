# Hermes + FlowWiki 集成执行计划

## 1. 计划概述

本计划按 SpecCoding 七阶段执行，将 Hermes AI 框架与 FlowWiki 的集成方案落地到代码和文档中。

## 2. 阶段一：Git Branch

- 创建独立分支：`hermes-flowwiki-integration`
- 目标：隔离变更，便于代码审查和回滚

## 3. 阶段二：Openspec Scaffold

- 已完成：创建 `openspec/changes/hermes-flowwiki-integration/` 目录
- 已完成：创建 `.openspec.yaml` 元数据文件

## 4. 阶段三：Brainstorming

- 已完成：`proposal.md` — 集成提案
- 已完成：`design.md` — 详细设计文档
- 已完成：`specs/industry-adapter.yaml` — 行业适配器规范

## 5. 阶段四：Writing Plans

- 本文件：`plan.md` — 执行计划

## 6. 阶段五：Executing Plans

### 6.1 任务清单

| 序号 | 任务 | 负责人 | 预计时间 | 依赖 |
|------|------|--------|---------|------|
| 1 | 编写 `spec/hermes-integration.md` | flowwiki-team | 2h | design.md |
| 2 | 创建 `storage/` 目录结构 | flowwiki-team | 1h | - |
| 3 | 为 4 个现有库创建 industry.yaml | flowwiki-team | 4h | industry-adapter.yaml |
| 4 | 创建 `.agents/CLAUDE.md` | flowwiki-team | 1h | - |
| 5 | 创建 `.agents/AGENTS.md` | flowwiki-team | 1h | - |
| 6 | 创建 `SCHEMA.md` | flowwiki-team | 2h | - |
| 7 | 创建 `config.toml` | flowwiki-team | 1h | - |
| 8 | 创建 `70_Prompt库/` 目录结构 | flowwiki-team | 1h | - |
| 9 | 创建 `.memory/` 目录结构 | flowwiki-team | 0.5h | - |
| 10 | 创建 `_scripts/` 目录和脚本骨架 | flowwiki-team | 2h | - |
| 11 | 创建 `_templates/` 目录和模板 | flowwiki-team | 2h | - |
| 12 | 创建 `.agents/skills/` 目录结构 | flowwiki-team | 1h | - |

### 6.2 执行顺序

```
Step 1: spec/hermes-integration.md
  ↓
Step 2: storage/ 目录 + 4 个 industry.yaml
  ↓
Step 3: SCHEMA.md + config.toml
  ↓
Step 4: 70_Prompt库/ + .memory/
  ↓
Step 5: .agents/CLAUDE.md + AGENTS.md
  ↓
Step 6: .agents/skills/ 目录结构
  ↓
Step 7: _scripts/ + _templates/
```

## 7. 阶段六：Archive

- 将 `openspec/changes/hermes-flowwiki-integration/` 移入 `openspec/changes/archive/`
- 更新 `.openspec.yaml` status 为 "completed"

## 8. 阶段七：Git Merge

- 将分支 `hermes-flowwiki-integration` 合回主分支
- 更新 CHANGELOG.md

## 9. 里程碑

| 里程碑 | 目标 | 完成条件 |
|--------|------|---------|
| M0.9 | 用户审阅全局 spec | spec/hermes-integration.md 写入完成 |
| M0.10 | Archive 变更 | 移入 openspec/changes/archive/ |
| M1.1 | 骨架脚手架启动 | CLAUDE.md + AGENTS.md + SCHEMA.md 创建完成 |
| M1.2 | 检索配置就绪 | config.toml 创建完成 |
| M1.3 | 行业适配器就绪 | storage/ + 4 个 industry.yaml 创建完成 |
| M1.4 | Skill 化层就绪 | .agents/skills/ 目录结构创建完成 |

## 10. 风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| industry.yaml schema 不完整 | 中 | 中 | 先做最小可用版本，后续迭代完善 |
| 4 个现有库数据迁移复杂 | 高 | 高 | 选环评库做试点，验证后推广 |
| Hermes API 接口变化 | 低 | 中 | 接口设计留有余量，支持版本兼容 |
| 跨行业切换性能问题 | 中 | 中 | 预加载常用行业数据，缓存机制 |

## 11. 验证标准

- spec/hermes-integration.md 写入 FlowWiki 全局 spec
- 4 个行业的 industry.yaml 符合规范
- 骨架文件创建完成：CLAUDE.md、AGENTS.md、SCHEMA.md、config.toml
- 目录结构完整：storage/、70_Prompt库/、.memory/、.agents/skills/、_scripts/、_templates/