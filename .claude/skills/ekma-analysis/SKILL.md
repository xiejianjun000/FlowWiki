# EKMA Analysis Skill — EKMA曲线分析

## 功能

绘制和分析 EKMA 曲线，诊断 O3 污染的前体物敏感性。

## 输入

```json
{
  "NOx_data": "NOx浓度数据",
  "VOCs_data": "VOCs浓度数据",
  "O3_data": "O3浓度数据",
  "plot_type": "EKMA|FNR|观测比值"
}
```

## 输出

```json
{
  "status": "success",
  "sensitivity": "VOCs敏感|NOx敏感|协同控制",
  "plot_data": "绘图数据",
  "control_strategy": "控制策略建议"
}
```

## 约束

- 引用具体诊断方法
- 给出敏感性判定依据
- 区分短期和长期控制策略