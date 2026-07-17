# Standard Match Skill — 标准匹配

## 功能

根据企业所属行业、产品类型和生产工艺，匹配适用的排放标准和环境质量标准。

## 输入

```json
{
  "enterprise_info": {
    "industry": "行业类型",
    "product": "产品类型",
    "process": "生产工艺",
    "pollutants": ["主要污染物"],
    "location": "所在区域",
    "scale": "生产规模"
  }
}
```

## 输出

```json
{
  "status": "success",
  "matched_standards": [
    {
      "standard_id": "标准编号",
      "standard_name": "标准名称",
      "match_type": "强制性|推荐性",
      "applicable_pollutants": ["适用污染物"],
      "limits": [
        {
          "pollutant": "污染物",
          "limit": "限值",
          "unit": "单位",
          "condition": "适用条件"
        }
      ],
      "match_reason": "匹配理由"
    }
  ],
  "unmatched_pollutants": ["未找到适用标准的污染物"],
  "summary": "标准匹配结论"
}
```

## 匹配规则

1. **行业优先**：先查行业排放标准，再查综合排放标准
2. **地域优先**：地方标准优先于国家标准
3. **时段优先**：按标准适用时段匹配
4. **工艺匹配**：不同工艺适用不同标准限值
5. **规模匹配**：不同规模企业适用不同标准

## 标准层级

1. 地方排放标准（优先）
2. 行业排放标准
3. 综合排放标准
4. 质量标准（参考）

## 约束

- 引用标准编号、名称和具体条款
- 标准间冲突时按"严格优先"原则
- 标注标准适用时段和条件
- 未匹配的污染物需明确提示
