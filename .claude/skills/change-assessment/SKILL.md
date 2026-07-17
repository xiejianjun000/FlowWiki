# Change Assessment Skill

> 变更评估 — 评估变更事项的合规性和影响范围

## 功能

评估企业变更事项的合规性和影响范围，判断是否需要重新申请、变更或备案。

## 输入

```json
{
  "entity": "企业名称",
  "change_type": "变更类型",
  "change_details": "变更详情",
  "current_license": "当前许可证信息"
}
```

## 输出

```json
{
  "assessment": "需重新申请|需变更|需备案|无需操作",
  "impact_areas": ["受影响的合规领域"],
  "required_actions": ["需要执行的操作"],
  "deadline": "操作期限"
}
```

## 约束

- 变更评估需对照许可证条件
- 重大变更需法律顾问确认
- 评估结果需记录归档
