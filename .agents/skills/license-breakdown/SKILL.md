# License Breakdown Skill

> 许可证拆解 — 分析许可证的许可事项、条件和要求

## 功能

拆解许可证文件，分析许可事项、限制条件、有效期限等关键信息。

## 输入

```json
{
  "file_path": "许可证文件路径",
  "analysis_type": "全部|许可事项|限制条件|有效期|合规"
}
```

## 输出

```json
{
  "license_info": {
    "holder": "持证主体",
    "type": "许可类型",
    "validity": "有效期",
    "conditions": ["许可条件列表"],
    "restrictions": ["限制条件列表"]
  },
  "compliance_notes": ["合规注意事项"]
}
```

## 约束

- 需要许可证原件或扫描件
- 注意许可证的版本和变更记录
- 引用相关法规条款
