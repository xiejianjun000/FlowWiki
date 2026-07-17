# Procedure Review Skill — 程序审查

## 功能

审查行政执法程序是否合法合规。

## 输入

```json
{
  "case_content": "案卷内容",
  "procedure_type": "立案|调查|处罚|执行"
}
```

## 输出

```json
{
  "status": "合规|不合规|需补充",
  "issues": [
    {
      "step": "程序步骤",
      "requirement": "法定要求",
      "actual": "实际情况",
      "gap": "差距"
    }
  ]
}
```

## 约束

- 引用具体法律条款
- 区分强制性程序和内部规范
- 给出明确的补正建议