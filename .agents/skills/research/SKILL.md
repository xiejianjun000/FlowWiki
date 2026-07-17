# Research Skill — 研究操作

## 功能

深度研究任务，跨知识库检索，生成研究报告。

## 输入

```json
{
  "question": "研究问题",
  "scope": "当前行业|跨行业",
  "depth": "shallow|medium|deep",
  "sources": ["raw", "wiki", "web"]
}
```

## 输出

```json
{
  "status": "success",
  "report": {
    "title": "研究报告标题",
    "summary": "摘要",
    "findings": ["发现1", "发现2"],
    "sources": ["来源1", "来源2"],
    "recommendations": ["建议1", "建议2"]
  }
}
```

## 执行流程

1. 解析研究问题
2. 根据 scope 确定检索范围
3. 多来源检索
4. 综合分析
5. 生成报告

## 约束

- 多来源验证
- 引用权威资料
- 支持跨行业检索