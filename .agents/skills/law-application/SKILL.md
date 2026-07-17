# Law Application Skill — 法律适用

## 功能

审查行政处罚案件中法律适用的准确性，包括法规选择、条款引用、自由裁量权行使。

## 输入

```json
{
  "violation_facts": "违法事实描述",
  "current_application": {
    "law": "适用法律",
    "article": "适用条款",
    "penalty_type": "处罚种类",
    "penalty_amount": "处罚幅度"
  },
  "case_context": {
    "enterprise_type": "企业类型",
    "violation_severity": "违法情节",
    "history": "历史违法记录"
  }
}
```

## 输出

```json
{
  "status": "正确|需修正|错误",
  "analysis": {
    "law_correctness": "法律选择是否正确",
    "article_correctness": "条款引用是否准确",
    "penalty_appropriateness": "处罚幅度是否适当",
    "discretion_reasonableness": "自由裁量是否合理"
  },
  "issues": [
    {
      "type": "法律错误|条款错误|幅度不当|裁量不当",
      "description": "问题描述",
      "correction": "修正建议",
      "legal_basis": "正确依据"
    }
  ],
  "correct_application": "正确的法律适用建议",
  "summary": "审查结论"
}
```

## 审查要点

1. **法律选择**：是否选择正确的法律（环保法 vs 专项法 vs 行政法）
2. **条款引用**：是否引用正确条款，是否漏引或多引
3. **处罚种类**：处罚种类是否与违法行为匹配
4. **处罚幅度**：是否在法定幅度内，是否与违法情节相当
5. **自由裁量**：从轻/从重/减轻处罚是否有事实依据
6. **竞合处理**：法条竞合时是否按正确规则适用

## 约束

- 引用具体法律条文和款项目
- 自由裁量审查依据裁量基准
- 区分"适用错误"和"适用不当"
