# Hermes AI 框架与 FlowWiki 集成提案

## 1. 背景

用户愿景：开发 AI 应用时，只开发前端 UI，以 Hermes 为 AI 框架基座，把 FlowWiki 放到该基座下，通过了解用户所属行业后，Hermes 自动按照 FlowWiki 创建完善知识库，实现"越用越懂"。

现有四个知识库（大气溯源、执法督察评查、环评排污许可、企业合规AI管家）各自独立，缺乏统一骨架，无法快速复制到新行业。

## 2. 核心问题

四个知识库共同缺失的「骨」：
- L3 spec/openspec（SpecCoding 变更治理）
- L4 Agent 记忆（A-MEM 卡片 + ACE 反思循环）
- 70_Prompt库（统一 Prompt 管理）
- L2 检索配置（统一检索引擎配置）
- L5 Skill 化（通用 4 操作）
- L6 多 agent（双 bootstrap）

## 3. 解决方案

**骨肉分离原则**：
- 骨架（L2-L6 + _scripts/_templates/SCHEMA）— 所有行业完全相同，零修改
- 肉（L1 raw/wiki/00_首页/.memory + L7 场景）— 每个行业不同内容

**行业适配器**：`industry.yaml` 作为连接骨架与肉的桥梁

## 4. 架构决策

| 决策 | 方案 |
|------|------|
| D1：FlowWiki 部署位置 | 单一大仓库 + 命名空间隔离（/flowwiki/tenant-{id}/） |
| D2：冷启动包粒度 | 44 套（与 Hermes 行业路由对齐） |
| D3："越用越懂"体验 | 显式告知 + 隐式提升（首页增长看板 + 回答质量提升） |
| D4：FlowWiki spec | 增加自动化引擎章节（spec/hermes-integration.md） |

## 5. 部署模式

「4+1」模式：
- 4 个现有行业库：大气溯源、执法督察评查、环评排污许可、企业合规AI管家
- 1 个通用骨架：所有行业共用一份 FlowWiki 标准版

## 6. 冷启动流程

用户 → 行业识别 → industry.yaml 生成 → 骨架拷贝 → raw/ 资料入仓 → ingest 编译 → wiki/ 生成 → .memory/ 记忆卡片 → L7 场景页 → 就绪

## 7. 推进策略

- 选环评库做试点改造（差距最小，只缺 5/11）
- 验证 industry.yaml 机制
- 推广到其他 3 个库
- 新行业自动冷启动

## 8. 交付物

- proposal.md（本文件）
- design.md（详细设计）
- specs/industry-adapter.yaml（行业适配器规范）
- plan.md（执行计划）
- spec/hermes-integration.md（全局 spec 章节）