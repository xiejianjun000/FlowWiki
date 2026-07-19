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

## 检查项（含宪法强制项）

### 宪法强制检查（SCHEMA §1.3 / §4.2）

- **原文指针段**：每个 wiki/ 页面必须含 `## 原文指针` 段
- **指针完整性**：段内必须含 `全文路径` 和 `引用规则` 字段
- **指针有效性**：`全文路径` 指向的 raw/ 文件必须真实存在（非悬空）
- **零全文搬运**：wiki/ 主体不得出现 ≥3 次"第X章"模式（视为全文搬运）

### 常规检查

- 悬空链：`[[xxx]]` 无对应文件
- 孤儿页：无人引用的 wiki 页面
- frontmatter 缺失或字段不完整（type/title/confidence/sources/status）
- confidence=low 但未标"待核"
- 矛盾未解决（`.memory/conflict/` 中状态≠"已解决"）
- 旧说法被推翻但 wiki 未更新

## 约束

- 定期自动运行
- 发现宪法强制项违规，severity 强制标 high
- 支持修复建议自动执行（除指针段缺失需人工裁决外）