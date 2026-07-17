# ACE 反思记录库

## 概述

ACE (Agent Critique Evaluate) 反思循环是 FlowWiki 防止"AI 幻觉永久化"的核心机制。每次 ingest 时，Generator → Reflector → Curator 三 agent 依次运行，审查结果记录在此目录。

## 目录结构

```
.memory/ace/
├── <YYYYMMDD>-<hash>.md    # 每次反思循环一个文件
└── README.md                # 本文件
```

## 反思记录格式

```markdown
# ACE 反思记录

- **时间**: YYYY-MM-DD HH:MM:SS
- **Raw 文件**: raw/path/to/file.md
- **Wiki 目标**: wiki/concepts/topic.md

## Generator 输出

<AI 生成的摘要内容>

## Reflector 审查

- 矛盾检查: <通过/发现矛盾>
- 幻觉检查: <通过/发现幻觉>
- 过时检查: <通过/发现过时>
- 审查意见: <具体问题>

## Curator 决策

- 决策: <入 wiki / 标待核 / 触发矛盾追踪>
- 理由: <决策理由>
```

## 生命周期

1. **生成**：ingest_pipeline.py 触发 ace_review.py，每次生成一条记录
2. **留存**：记录保留用于审计和回溯
3. **归档**：超过 30 天的记录可归档或清理（不影响 wiki 已入库内容）

## 查询

- 所有反思记录：`ls .memory/ace/*.md`
- 按日期：`ls .memory/ace/20260717-*.md`
- 查找矛盾：`grep -r "触发矛盾" .memory/ace/`
