---
name: 法条查询与适用
trigger: 查询法条或适用法律
skill: eco-review-kb
---
# 法条查询与适用 Prompt

## 触发条件
查询法条或适用法律

## 工作流
1. 检索 wiki/enforcement-review/ 相关知识
2. 对照 raw/enforcement-review/ 原始证据
3. ACE 反思验证
4. 输出结构化回答

## 依赖
- Skill: eco-review-kb
- 知识库: wiki/enforcement-review/ + raw/enforcement-review/
