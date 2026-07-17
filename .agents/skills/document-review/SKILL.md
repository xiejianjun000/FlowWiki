# Document Review Skill

> 文档审查 — 审查文件是否符合法律法规和技术标准

## 功能

对上传的文件进行合规性审查，检查是否符合相关法规和标准要求。

## 输入

```json
{
  "file_path": "文件路径",
  "file_type": "文件类型",
  "review_criteria": ["审查标准列表"]
}
```

## 输出

```json
{
  "compliance_status": "合规|不合规|部分合规",
  "issues": [
    {"item": "问题项", "severity": "high|medium|low", "reference": "法规/标准依据"}
  ],
  "suggestions": ["改进建议"]
}
```

## 约束

- 审查标准需与文件类型匹配
- 重点关注法律强制性条款
- 输出需引用具体条款
