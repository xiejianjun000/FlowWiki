# 01_知识图谱

## 概述

行业知识结构可视化入口，展示概念关联、实体关系和知识全貌。

## 内容

### 核心概念

AI 编译的知识概念页，每个概念可追溯到 raw/ 原始证据。

- 来源：`wiki/concepts/`
- 更新机制：ingest 时自动生成

### 概念关联图谱

概念之间的依赖、对比、演化关系。

```dataview
TABLE type, confidence, updated
FROM "wiki/concepts"
WHERE status = "reviewed"
SORT updated DESC
```

### 实体关系图

行业关键实体（法规、标准、机构、污染物等）及其关系。

- 来源：`wiki/entities/`（按需创建）
- 关联：判据体系中的判据条目

## 导航

- [机器索引](../wiki/index.md) — AI 使用的紧凑索引
- [判据体系](../02_判据体系/README.md) — 判据集与匹配引擎
- [实战场景](../03_实战场景/README.md) — 场景化知识应用
