---
name: 案卷评查任务
trigger: 收到案卷评查任务
skill: eco-review-kb
---
# 案卷评查任务 Prompt

## 触发条件
收到案卷评查任务

## 工作流
1. 检索 wiki/enforcement-review/ 相关知识
2. 对照 raw/enforcement-review/ 原始证据
3. ACE 反思验证
4. 输出结构化回答

## 依赖
- Skill: eco-review-kb
- 知识库: wiki/enforcement-review/ + raw/enforcement-review/
