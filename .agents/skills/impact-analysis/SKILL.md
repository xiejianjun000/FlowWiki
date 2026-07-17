# Impact Analysis Skill — 影响分析

## 功能

分析法规政策变更、企业变更或环境事件对合规状态的影响范围和程度。

## 输入

```json
{
  "analysis_type": "法规变更|企业变更|环境事件|政策调整",
  "trigger": "触发事件描述",
  "scope": {
    "enterprises": ["受影响企业"],
    "region": "影响区域",
    "timeframe": "时间范围"
  },
  "current_status": "当前合规状态"
}
```

## 输出

```json
{
  "status": "success",
  "impact_assessment": {
    "direct_impacts": [
      {
        "area": "影响领域",
        "severity": "高|中|低",
        "description": "影响描述",
        "affected_count": 0
      }
    ],
    "indirect_impacts": [
      {
        "area": "间接影响领域",
        "description": "影响描述"
      }
    ]
  },
  "risk_level": "高风险|中风险|低风险",
  "action_required": ["需要采取的行动"],
  "summary": "影响分析结论"
}
```

## 分析维度

1. **合规影响**：是否导致不合规、需变更许可证
2. **经济影响**：整改成本、罚款风险、停产风险
3. **环境影响**：排放变化、环境质量影响
4. **管理影响**：管理流程调整、人员培训需求
5. **时效影响**：整改时限、过渡期安排

## 约束

- 区分直接影响和间接影响
- 影响程度分级必须附依据
- 给出明确的风险等级和行动建议
