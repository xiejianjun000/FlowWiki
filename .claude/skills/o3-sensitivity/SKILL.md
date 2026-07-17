# O3 Sensitivity Skill — O3敏感性诊断

## 功能

诊断O3污染的生成机制和前体物敏感性。

## 输入

```json
{
  "data": {
    "NO2": "浓度",
    "VOCs": "浓度",
    "temperature": "温度",
    "radiation": "辐射"
  },
  "method": "EKMA|FNR|观测比值"
}
```

## 输出

```json
{
  "status": "success",
  "sensitivity": "VOCs敏感|NOx敏感|协同控制",
  "mechanism": "生成机制分析",
  "recommendations": ["建议1", "建议2"]
}
```

## 约束

- 引用具体诊断方法
- 给出敏感性判定依据
- 区分短期和长期控制策略