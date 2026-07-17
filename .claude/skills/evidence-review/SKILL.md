# Evidence Review Skill — 证据审核

## 功能

审核执法案卷中的证据链完整性和合法性。

## 输入

```json
{
  "evidence_list": ["证据1", "证据2"],
  "case_type": "行政处罚|行政强制",
  "procedure_stage": "立案|调查|处罚|执行"
}
```

## 输出

```json
{
  "status": "完整|不完整|需补充",
  "issues": [
    {
      "evidence": "证据名称",
      "problem": "问题描述",
      "requirement": "法定要求"
    }
  ],
  "suggestions": ["建议1", "建议2"]
}
```

## 约束

- 引用具体法律条款
- 区分证据能力和证明力
- 给出补证建议