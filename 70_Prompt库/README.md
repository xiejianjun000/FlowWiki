# Prompt 库

## 概述

统一管理 FlowWiki 所有 Prompt，支持版本控制和复用。

## 目录结构

```
70_Prompt库/
├── system/          # 系统级 Prompt
│   ├── generator.md
│   ├── reflector.md
│   └── curator.md
├── task/            # 任务级 Prompt
│   ├── ingest.md
│   ├── query.md
│   ├── lint.md
│   └── research.md
├── retrieval/       # 检索级 Prompt
│   ├── bm25.md
│   ├── graphrag.md
│   └── lightrag.md
└── output/          # 输出级 Prompt
    ├── report.md
    ├── card.md
    └── summary.md
```

## Prompt 规范

### 格式

```markdown
---
name: "Prompt 名称"
version: "1.0"
tags: ["标签1", "标签2"]
---

# Prompt 内容

{Prompt 正文}
```

### 变量

使用 `{{ variable }}` 格式定义变量：
- `{{ context }}`：上下文
- `{{ query }}`：查询词
- `{{ industry }}`：行业
- `{{ max_tokens }}`：最大 token 数

## 管理策略

- 统一版本控制
- 定期审查更新
- 支持 A/B 测试
- 性能监控