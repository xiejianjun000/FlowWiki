# Public Participation Skill — 公众参与核查

## 功能

审查建设项目环评中公众参与程序的合规性，包括参与方式、公示要求、意见反馈处理。

## 输入

```json
{
  "project_info": {
    "project_name": "项目名称",
    "project_type": "项目类型",
    "eia_type": "报告书|报告表",
    "location": "建设地点"
  },
  "participation_records": {
    "methods": ["参与方式"],
    "publicity_periods": ["公示时间"],
    "feedback_received": 0,
    "feedback_handling": "意见处理情况"
  }
}
```

## 输出

```json
{
  "status": "合规|需补充|不合规",
  "checklist": [
    {
      "item": "核查项",
      "requirement": "规范要求",
      "actual": "实际情况",
      "result": "通过|不通过|不适用",
      "evidence": "证据材料"
    }
  ],
  "issues": [
    {
      "type": "程序|内容|时限",
      "severity": "高|中|低",
      "description": "问题描述",
      "correction": "整改建议"
    }
  ],
  "summary": "核查结论"
}
```

## 核查要点

1. **参与方式**：是否采用法定参与方式（问卷调查、座谈会、听证会等）
2. **公示要求**：首次公示、第二次公示时间是否合规
3. **公示期限**：公示期是否满足法定最短期限
4. **公示渠道**：是否在规定媒体和场所公示
5. **意见处理**：公众意见是否收集、归纳、回应
6. **信息保密**：商业秘密和个人隐私是否得到保护
7. **材料归档**：公众参与材料是否完整归档

## 约束

- 审查依据《环境影响评价公众参与办法》
- 区分报告书和报告表的不同要求
- 公示期限计算精确到日
