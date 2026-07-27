---
type: research_paper
domain: ai-governance
title: AI Agent 记忆系统设计原则
date: 2026-07-15
author: A-MEM Research Group
confidence: high
tags: [ai, agent, memory, design-principles]
---

# AI Agent 记忆系统设计原则

## 摘要

AI Agent 的记忆系统需要解决四个核心问题：持久化、可追溯、衰减管理、跨会话连续性。本文提出 A-MEM（Agent Memory）框架的四层架构。

## 四层架构

### L1 瞬时记忆层
- 范围：单次对话上下文
- 容量：取决于模型上下文窗口
- 衰减：会话结束即清除

### L2 工作记忆层
- 范围：当前任务相关
- 容量：10-20 个信息单元
- 衰减：任务完成后 1 小时

### L3 长期记忆层
- 范围：持久化知识
- 容量：10000+ 卡片
- 衰减：按 access_frequency × recency × importance 三维衰减

### L4 元记忆层
- 范围：对记忆本身的记忆
- 容量：500 个索引条目
- 衰减：按匹配率动态调整

## 关键指标

| 维度 | 目标值 | 测量方法 |
|------|--------|---------|
| 召回率 (Recall@10) | ≥ 85% | A-MEM benchmark |
| 幻觉率 | ≤ 5% | Source verification |
| 新鲜度 | 24h 自动更新 | Staleness check |
| 冲突解决 | 自动标记 | Contradiction detection |

## 参考实现

- Karpathy LLM Wiki: raw/ → wiki/ 编译模式
- GBrain: DreamCycle 9 阶段自维护
- A-MEM: Zettelkasten 卡片 + 三维衰减

## 开放问题

1. 记忆衰减的权重如何自适应？
2. 冲突记忆如何自动解决？
3. 跨 Agent 记忆共享的协议标准？
