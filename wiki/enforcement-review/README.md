# wiki/ 页面规范

> 基于 FlowWiki 官方 wiki/ 规范，适配企业环保合规知识库。

## 目录结构

```
wiki/
├── index.md              # 机器索引（AI 优先，紧凑链接列表）
├── log.md                # 操作时间轴（追加式，只增不改）
├── README.md             # 本文件 — 页面规范说明
├── sources/              # 法律渊源（AI 编译自 raw/，只读归档）
│   ├── laws/             # 法律
│   ├── regulations/      # 行政法规
│   ├── departmental_rules/ # 部门规章
│   ├── judicial/         # 司法解释
│   └── local_rules/      # 地方性法规
├── criteria/             # 排放标准判据（AI 编译自 raw/standards/）
├── concepts/             # 核心概念知识（AI 编译自 raw/concepts/）
├── cases/                # 典型案例（AI 编译自 raw/cases/）
└── playbooks/            # 操作手册 / Skill / Prompt（AI 编译自 raw/skills/ + raw/prompts/）
```

## Frontmatter 规范

每个 wiki 页面（除 index.md / log.md / README.md 外）必须包含 8 字段 frontmatter：

```yaml
---
title: "页面标题"
category: source | concept | criterion | case | playbook
subcategory: law | regulation | standard | system | indicator | procedure | skill | prompt
status: reviewed | draft | deprecated
confidence: 0.0 ~ 1.0
source: "raw/相对路径"
generated: YYYY-MM-DD
tags: [tag1, tag2, ...]
---
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| title | 是 | 页面标题 |
| category | 是 | 顶层分类 |
| subcategory | 是 | 二级分类 |
| status | 是 | reviewed=已审 / draft=草稿 / deprecated=已废弃 |
| confidence | 是 | 知识置信度 0-1 |
| source | 是 | 对应 raw/ 源文件路径 |
| generated | 是 | 生成日期 |
| tags | 是 | 标签数组 |

## 写作规范

1. **正文层级**：正文从 `##` 开始，`#` 保留给页面标题（frontmatter title）
2. **链接格式**：使用相对路径 Markdown 链接 `[文本](路径.md)`
3. **不使用** wikilink `` 语法（本库使用标准 Markdown）
4. **来源引用**：每条关键结论必须标注法律条文出处
5. **AI 维护**：wiki/ 目录由 AI Agent 维护，人类不直接编辑

## 与 raw/ 的关系

- raw/ = 源真层（只读，人类/爬虫写入）
- wiki/ = 编译知识层（AI 编译生成，人类可阅读）
- 编译方向：raw/ → wiki/（单向，不可逆）