# Step Verification Skill — 步骤验证

## 功能

验证行政执法程序的每个步骤是否合法合规，确保程序链条完整无缺。

## 输入

```json
{
  "case_type": "行政处罚|行政强制|行政许可",
  "steps": [
    {
      "step_name": "步骤名称",
      "step_order": 1,
      "executed": true,
      "execution_time": "执行时间",
      "executor": "执行人",
      "documents": ["相关文书"]
    }
  ],
  "case_context": "案件背景"
}
```

## 输出

```json
{
  "status": "合规|程序瑕疵|程序违法",
  "verification_results": [
    {
      "step": "步骤名称",
      "required": true,
      "executed": true,
      "order_correct": true,
      "timing_compliant": true,
      "document_complete": true,
      "issues": ["问题列表"],
      "severity": "高|中|低"
    }
  ],
  "missing_steps": ["缺失步骤"],
  "order_issues": ["顺序问题"],
  "timing_issues": ["时限问题"],
  "summary": "验证结论"
}
```

## 行政处罚标准步骤

1. **立案**：立案审批表 → 审批
2. **调查取证**：现场检查 → 询问 → 证据收集
3. **审查**：案件审查 → 法制审核
4. **告知**：处罚前告知 → 听取陈述申辩
5. **决定**：处罚决定审批 → 制作决定书
6. **送达**：依法送达处罚决定书
7. **执行**：督促执行 → 强制执行（如需）
8. **结案**：结案审批 → 归档

## 约束

- 每个步骤检查"是否执行、顺序是否正确、时限是否合规、文书是否完整"
- 程序违法可能导致处罚决定被撤销，需高严重度标注
- 区分"程序瑕疵"（可补正）和"程序违法"（不可逆）
