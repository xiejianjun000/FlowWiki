# 实战场景

> L7 场景层 — 可插拔的业务外壳。每个场景独立启用/禁用。

## 7 大场景

| 场景 | slug | 配置 | Skill 数 | 说明 |
|------|------|------|---------|------|
| 根因分析 | root-cause | `storage/root-cause/industry.yaml` | 5 | 数据溯源与根因定位 |
| 合规审查 | compliance-review | `storage/compliance-review/industry.yaml` | 7 | 案卷合规审查 |
| 证照管理 | license-management | `storage/license-management/industry.yaml` | 6 | 证照审查与合规判定 |
| 企业合规 | enterprise-compliance | `storage/enterprise-compliance/industry.yaml` | 6 | 企业合规管理 |
| 现场核查 | audit-onsite | `storage/audit-onsite/industry.yaml` | 6 | 现场审计与取证 |
| 案卷评查 | case-review | `storage/case-review/industry.yaml` | 7 | 案卷质量评查 |
| 审计准备 | audit-prep | `storage/audit-prep/industry.yaml` | 7 | 审计前准备 |

## 使用方式

1. 在 `storage/<scene-slug>/industry.yaml` 中配置场景参数
2. 在 `00_首页/03_实战场景/<场景名>/` 中编写场景文档
3. 在 `.agents/skills/` 和 `.claude/skills/` 中部署场景专属 skill
4. 切换场景：修改 `config.toml` 中 `[industry].default`

## 可插拔验证

每个场景可独立启用/禁用，不影响 L1-L6 通用骨架。
