# Query Skill — 查询操作

## 功能

查询 wiki/ 内容，支持全文搜索和结构化查询。

## 输入

```json
{
  "query": "查询关键词",
  "mode": "fulltext|structured",
  "filters": {
    "industry": "行业 slug",
    "type": "concept|playbook|comparison",
    "tags": ["标签1", "标签2"]
  }
}
```

## 输出

```json
{
  "status": "success",
  "results": [
    {
      "title": "页面标题",
      "path": "wiki/路径",
      "score": 0.9,
      "summary": "摘要"
    }
  ]
}
```

## 执行流程

1. 解析查询参数
2. 根据 mode 选择检索引擎
3. 执行检索
4. 返回结果

## 约束

- 检索范围限定在当前行业
- 结果必须引用 raw/ 原始证据
- 支持 BM25、nano-graphrag、LightRAG 自适应