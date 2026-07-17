# Compliance Suggestion Skill — 合规建议

## 功能

基于合规审查结果或风险识别结果，生成具体的合规整改建议和改进方案。

## 输入

```json
{
  "review_result": {
    "issues": [
      {
        "type": "法律|标准|程序|管理",
        "severity": "高|中|低",
        "description": "问题描述"
      }
    ]
  },
  "enterprise_context": {
    "industry": "行业",
    "scale": "规模",
    "current_status": "当前合规状态"
  }
}
```

## 输出

```json
{
  "status": "success",
  "suggestions": [
    {
      "issue": "对应问题",
      "priority": "紧急|高|中|低",
      "action": "整改措施",
      "legal_basis": "法律依据",
      "timeline": "建议时限",
      "expected_outcome": "预期效果"
    }
  ],
  "overall_plan": "整体整改方案",
  "summary": "建议汇总"
}
```

## 建议分类

1. **紧急整改**：立即停止违法行为，消除环境风险
2. **限期整改**：在规定期限内完成整改
3. **优化建议**：提升合规水平，降低风险
4. **长效机制**：建立常态化管理机制

## 约束

- 建议必须可执行，不可泛泛而谈
- 每条建议标注优先级和建议时限
- 引用具体法律条款作为依据
