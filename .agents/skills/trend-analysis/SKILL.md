# Trend Analysis Skill

> 趋势分析 — 识别数据变化的方向和模式

## 功能

对时间序列数据进行趋势分析，输出变化方向、速率和周期性模式。

## 输入

```json
{
  "data": "时间序列数据",
  "period": "分析周期",
  "method": "移动平均|线性回归|季节性分解"
}
```

## 输出

```json
{
  "trend": "上升|下降|平稳",
  "rate": "变化速率",
  "cycles": ["周期性模式列表"],
  "confidence": "high|medium|low"
}
```

## 约束

- 数据量不足时降低 confidence
- 注意异常值对趋势的影响
- 多维度数据需分别分析
