# Cross Domain Tracing Skill

> 跨域追踪 — 跨系统/数据域的因果链路追踪

## 功能

分析问题在多个系统或数据域之间的传播路径和影响范围。

## 输入

```json
{
  "issue": "问题描述",
  "domains": ["涉及的数据域"],
  "timeline": "事件时间线"
}
```

## 输出

```json
{
  "trace_path": [
    {"domain": "数据域", "event": "事件", "timestamp": "时间"}
  ],
  "root_cause_domain": "根因所在域",
  "impact_domains": ["受影响的域"],
  "contribution": {"domain": "贡献率"}
}
```

## 约束

- 需要跨域数据访问权限
- 不同域的时间精度可能不一致
- 跨域因果推断需要领域专家确认
