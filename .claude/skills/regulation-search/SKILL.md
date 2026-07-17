# Regulation Search Skill — 法规检索

## 功能

检索与企业合规相关的法律法规和标准。

## 输入

```json
{
  "query": "检索关键词",
  "scope": "法律|行政法规|部门规章|标准",
  "industry": "行业类型"
}
```

## 输出

```json
{
  "status": "success",
  "results": [
    {
      "name": "法规名称",
      "level": "法律效力层级",
      "effective_date": "生效日期",
      "relevance": "相关度"
    }
  ]
}
```

## 约束

- 确保法规时效性
- 区分现行有效和已废止
- 给出适用性分析