---
name: enforcement-review-kb
version: "1.0"
industry: enforcement-review
tags: [skill, enforcement-review, 执法督察评查]
---

# 执法督察评查 — 行业 Skill

## 触发条件

用户提出的问题涉及：
- 生态环境执法案卷评查
- 行政处罚合法性/规范性审查
- 排污许可合规检查
- 自动监测异常判定
- 裁量权基准适用
- 法典衔接与新旧法对比

## 工作流

1. **query** → 检索 `wiki/enforcement-review/concepts/` 和 `wiki/enforcement-review/playbooks/`
2. **verify** → 对照 `raw/enforcement-review/` 原始证据
3. **ace** → ACE 反思循环验证
4. **output** → 生成结构化回答（违法认定 + 证据链 + 处罚建议）

## 子 Skill

| Skill | 路径 |
|-------|------|
| 合法性审查 | legality-review/SKILL.md |
| 证据链核验 | evidence-verification/SKILL.md |
| 裁量权匹配 | discretion-matching/SKILL.md |
| 排污许可检查 | permit-compliance/SKILL.md |
| 现场核查清单 | onsite-checklist/SKILL.md |
| 法典衔接判断 | code-transition/SKILL.md |
