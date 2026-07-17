# wiki/ AI 编译知识层

## 概述

本目录存放 AI 编译的结构化知识，由 ingest pipeline 自动生成。

## 目录结构

```
wiki/
├── index.md          # 总索引
├── concepts/         # 核心概念
├── playbooks/        # 操作手册
├── comparisons/      # 对比分析
├── entities/         # 实体定义
├── sources/          # 源解析
├── synthesis/        # 综合研判
└── README.md         # 本文件
```

## 页面规范

1. 所有内容必须能追溯到 raw/ 原始证据
2. 使用 Markdown 格式
3. 遵循 wiki/ 页面模板
4. 禁止无证据的 AI 编造内容

## 页面模板

```markdown
# 页面标题

## 概述

## 核心内容

## 相关资料

## 关联知识

## 原始证据
```

## 更新机制

- 自动更新：ingest pipeline 编译时自动更新
- 手动更新：通过 openspec 变更流程
- ACE 审查：所有更新必须经过 ACE 反思循环

## 质量要求

- 准确性：内容必须准确无误
- 完整性：覆盖所有相关知识点
- 时效性：及时更新最新知识
- 可追溯：所有内容有证据来源