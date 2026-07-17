# Source Fingerprint Skill — 源类指纹识别

## 功能

通过化学组分特征识别污染排放源类型。

## 输入

```json
{
  "chemical_composition": "化学组分数据",
  "ratios": {"PM2.5/PM10": 0.5, "NO2/SO2": 2.0},
  "location": "监测站点"
}
```

## 输出

```json
{
  "status": "success",
  "sources": [
    {
      "type": "源类型",
      "confidence": 0.9,
      "features": ["特征1", "特征2"]
    }
  ],
  "match_criteria": ["匹配的判据"]
}
```

## 约束

- 引用具体判据来源
- 给出指纹识别置信度
- 区分确定性结论和推测性结论