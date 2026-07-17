# 03_实战场景

## 概述

FlowWiki 的实战场景入口，将通用骨架与行业肉结合。每个场景对应一个 `storage/` 行业适配器（industry.yaml），驱动 Skill 调度、判据匹配和知识编译。

## 场景列表

| 场景 | Slug | 行业适配器 | Skills 数 | 说明 |
|------|------|-----------|----------|------|
| 大气溯源 | atmospheric-tracing | `storage/atmospheric-tracing/industry.yaml` | 5 | 污染源追踪与贡献率解析 |
| 执法办案 | law-enforcement-review | `storage/law-enforcement-review/industry.yaml` | 6 | 行政处罚案件全流程审查 |
| 排污许可 | eia-permit | `storage/eia-permit/industry.yaml` | 6 | 许可证核发与变更合规审查 |
| 企业合规 | enterprise-compliance | `storage/enterprise-compliance/industry.yaml` | 6 | 企业环保合规自查与整改 |
| 督察现场 | inspection-onsite | `storage/inspection-onsite/industry.yaml` | 6 | 现场督察取证与问题判定 |
| 案卷评查 | case-review | `storage/case-review/industry.yaml` | 7 | 案卷质量评查与问题汇总 |
| 迎检准备 | inspection-prep | `storage/inspection-prep/industry.yaml` | 7 | 迎检材料准备与模拟演练 |

## 使用方式

1. **进入场景**：点击上方场景名，查看该场景的详细说明
2. **加载适配器**：系统自动读取对应 `industry.yaml`，激活场景专属 Skill
3. **执行任务**：通过 Skill 调度完成具体工作（如判据匹配、合规审查）
4. **知识沉淀**：任务结果经 ACE 反思循环后写入 wiki/ 和 .memory/

## 导航

- [知识图谱](../01_知识图谱/README.md) — 概念与实体
- [判据体系](../02_判据体系/README.md) — 判据应用基础
- [进化学习](../04_进化学习/README.md) — 场景迭代记录
- [采集记录](../05_采集记录/README.md) — 原始资料来源
