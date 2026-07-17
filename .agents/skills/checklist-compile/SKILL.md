# Checklist Compile Skill — 清单编制

## 功能

根据行业类型、法规要求和检查标准，自动生成合规自查清单或迎检清单。

## 输入

```json
{
  "checklist_type": "迎检|自查|日常|专项",
  "industry": "行业类型",
  "enterprise_info": {
    "name": "企业名称",
    "scale": "规模",
    "pollutants": ["主要污染物"]
  },
  "inspection_type": "中央督察|省级督察|日常执法|专项检查"
}
```

## 输出

```json
{
  "status": "success",
  "checklist": [
    {
      "category": "检查项分类",
      "items": [
        {
          "name": "检查项名称",
          "legal_basis": "法律依据",
          "self_check_method": "自查方法",
          "common_issues": ["常见问题"],
          "priority": "高|中|低"
        }
      ]
    }
  ],
  "total_items": 0,
  "summary": "清单说明"
}
```

## 清单分类

1. 环评与排污许可（批复文件、许可证、备案）
2. 污染防治设施（运行台账、维护记录）
3. 在线监控（安装、联网、运行）
4. 排放达标（监测报告、达标证明）
5. 环境管理（台账、报告、公开）
6. 应急管理（预案、演练、物资）

## 约束

- 每个检查项必须有法律依据
- 区分强制性要求和推荐性要求
- 优先级标注帮助企业聚焦关键问题
