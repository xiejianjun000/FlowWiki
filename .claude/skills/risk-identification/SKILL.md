# Risk Identification Skill — 风险识别

## 功能

识别企业合规风险点和潜在法律风险。

## 输入

```json
{
  "enterprise_info": "企业信息",
  "industry": "行业类型",
  "scope": "环保|安全|劳动|税务"
}
```

## 输出

```json
{
  "status": "success",
  "risks": [
    {
      "type": "风险类型",
      "level": "高|中|低",
      "description": "风险描述",
      "law": "相关法律",
      "suggestion": "防范建议"
    }
  ]
}
```

## 约束

- 引用具体法律法规
- 区分法律风险和管理风险
- 给出可操作的防范建议