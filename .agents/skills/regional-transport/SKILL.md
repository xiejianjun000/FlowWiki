# Regional Transport Skill — 区域传输分析

## 功能

分析大气污染物的区域传输路径和贡献率。

## 输入

```json
{
  "pollutant": "PM2.5|O3|NO2|SO2",
  "station_data": "监测数据",
  "meteorology": "气象数据",
  "time_range": "时间范围"
}
```

## 输出

```json
{
  "status": "success",
  "transport_paths": [
    {
      "direction": "传输方向",
      "distance": "传输距离",
      "contribution": "贡献率"
    }
  ],
  "local_vs_regional": "本地 vs 区域贡献",
  "recommendations": ["建议1", "建议2"]
}
```

## 约束

- 引用气象数据和监测数据
- 区分本地排放和区域传输
- 给出传输路径可视化建议