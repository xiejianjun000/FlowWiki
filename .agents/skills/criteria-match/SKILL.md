# Criteria Match Skill — 判据匹配

## 功能

将监测数据与判据体系进行匹配，自动识别污染特征和来源。

## 输入

```json
{
  "data_type": "PM2.5|O3|NO2|SO2|CO|PM10|VOCs",
  "values": {"key": "value"},
  "location": "监测站点",
  "time_range": "时间范围"
}
```

## 输出

```json
{
  "status": "success",
  "matches": [
    {
      "criteria": "判据名称",
      "threshold": "阈值",
      "actual_value": "实际值",
      "match_result": "匹配|不匹配|边缘",
      "confidence": 0.9
    }
  ],
  "conclusion": "综合结论",
  "suggestions": ["建议1", "建议2"]
}
```

## 判据类别

1. 化学组分判据
2. 气象条件判据
3. O3敏感性判据
4. 区域传输判据
5. 源类特征指纹判据

## 约束

- 引用具体判据来源
- 给出匹配置信度
- 区分确定性结论和推测性结论