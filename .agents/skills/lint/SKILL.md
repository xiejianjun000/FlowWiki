# Lint Skill — 检查操作

## 功能

检查知识库健康度，发现问题并提供修复建议。

## 输入

```json
{
  "check_type": "all|dangling|consistency|quality",
  "target": "raw|wiki|memory"
}
```

## 输出

```json
{
  "status": "success",
  "issues": [
    {
      "type": "dangling_link|inconsistency|low_quality",
      "severity": "high|medium|low",
      "location": "文件路径",
      "description": "问题描述",
      "suggestion": "修复建议"
    }
  ],
  "summary": {
    "total_issues": 0,
    "high_severity": 0,
    "medium_severity": 0,
    "low_severity": 0
  }
}
```

## 执行流程

1. 解析检查类型和目标
2. 执行检查
3. 生成问题报告
4. 提供修复建议

## 约束

- 定期自动运行
- 发现问题及时通知
- 支持修复建议自动执行