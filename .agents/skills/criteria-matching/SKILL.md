# Criteria Matching Skill

> 判据匹配 — 将数据与判据体系进行匹配

## 功能

将输入数据与判据库进行自动匹配，识别满足的判据和异常特征。

## 输入

```json
{
  "data": "待匹配数据",
  "data_type": "数据类型标识",
  "criteria_set": "判据集名称（可选）"
}
```

## 输出

```json
{
  "matched": [
    {"criterion": "判据名称", "value": "数据值", "result": "通过|不通过"}
  ],
  "unmatched": ["未找到适用判据的数据项"],
  "summary": "匹配概况"
}
```

## 约束

- 判据库需要持续维护
- 新数据类型需先注册判据
- 匹配结果需人工复核
