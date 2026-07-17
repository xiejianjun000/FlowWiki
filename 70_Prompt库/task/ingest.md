---
name: "Ingest Task Prompt"
version: "1.0"
tags: ["task", "ingest"]
---

# Ingest Task Prompt

## 任务

将原始资料入仓到 raw/，并触发编译到 wiki/。

## 输入

- 原始资料内容
- 资料类型（法律/标准/报告/数据）
- 元数据（标题/来源/日期）

## 步骤

1. 验证资料完整性
2. 写入 raw/ 目录
3. 更新 raw/README.md 索引
4. 触发 ingest pipeline
5. 等待编译完成

## 输出

- raw/ 新文件路径
- 生成的 wiki 页面列表
- 编译状态