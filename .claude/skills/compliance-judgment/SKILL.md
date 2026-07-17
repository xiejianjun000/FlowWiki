# Compliance Judgment Skill — 合规判定

## 功能

根据监测数据和排放标准，判定企业排放是否达标，输出合规判定结果。

## 输入

```json
{
  "enterprise_id": "企业编号",
  "monitoring_data": {
    "pollutant": "污染物名称",
    "concentration": "浓度值",
    "unit": "单位",
    "monitoring_type": "在线|手工|委托",
    "time": "监测时间"
  },
  "applicable_standard": "适用标准"
}
```

## 输出

```json
{
  "status": "达标|超标|临界",
  "judgment": {
    "pollutant": "污染物",
    "actual_value": "实际值",
    "limit_value": "限值",
    "exceed_ratio": "超标倍数",
    "standard_reference": "标准引用"
  },
  "legal_consequence": "法律后果说明",
  "summary": "判定结论"
}
```

## 判定规则

1. 对比监测值与排放标准限值
2. 考虑监测类型（在线/手工/委托）的法律效力
3. 判断是否超过许可排放量
4. 评估超标程度（轻微/一般/严重）

## 约束

- 引用具体标准条款和限值
- 区分浓度达标和总量达标
- 超标判定必须附法律后果说明
