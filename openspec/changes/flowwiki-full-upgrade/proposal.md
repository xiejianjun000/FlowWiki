---
标题: FlowWiki 全栈升级 — 变更提案
layer: 10-元文档
type: spec
date: 2026-07-18
status: archived
tags: [10-元文档, spec, 现行]
---

# 变更提案：FlowWiki 全栈升级

## 背景
执法督察评查知识库原基于 Karpathy LLM Wiki 三层架构，未落地 FlowWiki 的 6 项增强。

## 变更范围
| 层 | 动作 | 文件数 |
|----|------|--------|
| L6 | 创建 CLAUDE.md / AGENTS.md / CODEX.md | 3 |
| L4 | 创建 .memory/ 六子目录 + ACE 脚本 + 10 ZK 卡片 | 17 |
| L1 | 迁移 22 篇源真到 raw/, 112 篇到 wiki/ | 134 |
| L1 | 追加 confidence + sources 到全部 170 页 | 170 |
| L5 | 创建 4 操作 skill + 8 行业 skill | 24 |
| L3 | 创建 spec/ + openspec/ + 提示词库/ | 12 |

## 验收标准
- [x] lint 0 断链
- [x] 图谱 1 分量 100% 可达
- [x] frontmatter 100% 完整
- [x] confidence/sources 全覆盖
- [x] ACE 脚本可运行
- [x] 10 张 ZK 种子卡片就位
