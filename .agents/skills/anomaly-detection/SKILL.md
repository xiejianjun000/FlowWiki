# Anomaly Detection Skill

> 异常检测 — 从数据中识别偏离正常模式的异常值

## 功能

根据输入数据和基线模型，检测异常值或异常行为，输出异常列表和可能原因。

## 输入

```json
{
  "data": "数据描述或数据文件路径",
  "baseline": "正常基线（可选）",
  "threshold": "异常阈值（可选，默认自动）"
}
```

## 输出

```json
{
  "anomalies": [
    {
      "timestamp": "异常时间",
      "metric": "异常指标",
      "value": "异常值",
      "expected": "预期值",
      "severity": "high|medium|low"
    }
  ],
  "summary": "异常概况",
  "possible_causes": ["可能原因列表"]
}
```

## 约束

- 需要足够的基线数据（至少 7 天）
- 注意季节性因素对基线的影响
- 异常不等于错误，需人工确认
