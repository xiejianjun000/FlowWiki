# Permit Analysis Skill — 许可证拆解

## 功能

拆解排污许可证，分析许可事项、排放限值、监测要求等。

## 输入

```json
{
  "permit_content": "许可证内容",
  "analysis_type": "全部|排放口|污染物|监测|合规"
}
```

## 输出

```json
{
  "status": "success",
  "emission_outlets": [
    {
      "id": "排放口编号",
      "location": "位置",
      "pollutants": ["污染物列表"],
      "limits": {"COD": "500mg/L"}
    }
  ],
  "monitoring_requirements": [
    {
      "pollutant": "污染物",
      "frequency": "监测频次",
      "method": "监测方法"
    }
  ],
  "compliance_status": "达标|不达标|需关注"
}
```

## 分析维度

1. 排放口信息
2. 污染物种类和限值
3. 监测要求
4. 合规判定
5. 变更评估

## 约束

- 严格依据许可证原文
- 引用相关排放标准
- 给出合规判定依据