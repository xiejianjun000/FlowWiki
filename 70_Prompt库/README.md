---
标题: 70_Prompt库 · 索引与升级规则
layer: 05-工具资源
type: index
触发词: ["prompt", "提示词", "skill升级"]
适用场景: 管理提示词库，触发 skill 升级检查
风险等级: 🟡
version: 1.0
status: 现行
tags: [05-工具资源, 🟡常规, index, 现行]
confidence: high
sources: []
---

# 70_Prompt库 — 索引 & 升级规则

## 分类

| 文件 | 内容 | 升级候选 |
|------|------|---------|
| 01_生成类.md | 生成审计清单、分析方案、评查报告 | 🟡 有机会 → skill |
| 02_校对类.md | 校对案卷程序、数据一致性、证据链 | 🟡 有机会 → skill |
| 03_问句类.md | 执法者视角、企业视角、条文解释 | 🔵 风格调参，不升级 |
| 04_拆解类.md | 拆解法规、许可证、案卷要素 | 🟡 有机会 → skill |

## 升级规则

同类 prompt 使用 ≥3 次 + 流程可标准化 → **升级为 L5 skill**

```text
1. 该 prompt 使用次数 ≥3？
   → 否：保持不动
   → 是：进入第 2 步
2. 流程可标准化？（有明确输入/输出/步骤）
   → 否：保持 prompt
   → 是：生成 .agents/skills/<name>/SKILL.md + .claude/skills/<name>/SKILL.md
3. 标记原 prompt 为 "⚠️ 已升级为 skill，请使用 /<name>"
```
