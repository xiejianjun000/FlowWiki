# 贡献指南

感谢你对 FlowWiki 的关注！FlowWiki 是一个融合了 Karpathy LLM Wiki、ACE 反思循环、A-MEM 卡片记忆和 SpecCoding 七阶段开发的知识管理方法论。

## 项目简介

FlowWiki 采用 **7 层架构**：

| 层级 | 名称 | 说明 |
|------|------|------|
| L1 | 知识编译层 | `raw/`（只读源文件）→ `wiki/`（AI 编译）→ `00_首页/`（人类入口） |
| L2 | 检索增强层 | BM25 → nano-graphrag → LightRAG 自适应三档检索 |
| L3 | Spec-Driven 层 | OpenSpec 变更治理，每个变更有提案/执行/归档 |
| L4 | Agent 记忆层 | A-MEM Zettelkasten 卡片 + ACE 反思循环（Generator→Reflector→Curator） |
| L5 | Skill 化层 | 高频任务自动抽象为 O(1) 调用的 skill |
| L6 | 多 Agent 层 | CLAUDE.md + AGENTS.md + CODEX.md + WORKBUDDY.md 五家 agent 兼容 |
| L7 | 场景层 | 行业场景可插拔，通用骨架 + 业务变量分离 |

## 贡献流程

### 1. 准备工作

```bash
# Fork 本仓库
# Clone 你的 fork
git clone https://github.com/<your-username>/FlowWiki.git
cd FlowWiki

# 添加上游仓库
git remote add upstream https://github.com/xiejianjun000/FlowWiki.git
```

### 2. 创建功能分支

```bash
# 从 main 分支创建功能分支
git checkout -b feature/your-feature-name
# 或修复分支
git checkout -b fix/your-fix-name
```

分支命名建议：
- `feature/xxx` — 新功能
- `fix/xxx` — Bug 修复
- `docs/xxx` — 文档更新
- `skill/xxx` — Skill 相关变更

### 3. 进行修改

根据修改类型参考对应规范：

- **wiki/ 目录变更** → 必须通过 ACE 反思循环审查（见下文）
- **Skill 变更** → 必须同步更新 `.agents/skills/` 和 `.claude/skills/` 两处
- **raw/ 目录** → 只读，仅可新增，不可修改已有文件
- **spec/ 变更** → 必须走 SpecCoding 七阶段流程

### 4. 提交 PR

```bash
git add .
git commit -m "feat: 简短描述你的变更"
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request，请使用 PR 模板填写完整信息。

## ACE 审查要求

**所有涉及 `wiki/` 目录的变更，必须通过 ACE 反思循环审查。**

ACE 是 FlowWiki 的核心防幻觉机制，由三个 Agent 逐级制约：

1. **Generator** — 根据 raw 源文件生成 wiki 摘要
2. **Reflector** — 批判性审查，查找矛盾/幻觉/过时信息
3. **Curator** — 最终决策：入 wiki / 标"待核" / 触发 `conflict/` 目录

提交 PR 时，请在 PR 描述中附上 ACE 审查结果摘要，包括：
- Generator 生成的内容摘要
- Reflector 发现的问题（如有）
- Curator 的最终处理决策

未通过 ACE 审查的 wiki 变更将不被合并。

## 编码规范

### 幂等性要求

所有 `_scripts/` 下的脚本必须是**幂等的**——多次执行结果相同，不会产生副作用或累积错误。编写新脚本时，请确保：

- 支持 `--dry-run` 预览模式
- 检查已有状态再执行操作
- 使用确定性输出（相同输入 → 相同输出）

### Frontmatter 要求

所有 `wiki/` 目录下的 Markdown 文件必须包含完整 YAML frontmatter：

```yaml
---
title: 页面标题
category: 分类
status: draft | reviewed | approved
confidence: 0.0-1.0
source: raw/xxx.md
generated: 2026-01-01T00:00:00Z
ace_review:
  generator: 通过
  reflector: 无问题
  curator: 已入库
---
```

### raw/ 目录规则

- `raw/` 目录下的文件为**只读源文件**
- 仅可新增，不可修改或删除已有文件
- 如需更正源内容，请在 `wiki/` 中标注矛盾，而非直接修改 `raw/`

## Skill 贡献

FlowWiki 的 skill 采用**双部署**机制，确保五家 agent 都能调用：

| Agent | Skill 路径 | 引导文件 |
|-------|-----------|---------|
| Claude Code | `.claude/skills/<skill>/SKILL.md` | `CLAUDE.md` |
| Codex / Amp / Gemini CLI | `.agents/skills/<skill>/SKILL.md` | `AGENTS.md` |
| WorkBuddy | `.agents/skills/<skill>/SKILL.md` | `WORKBUDDY.md` |

**新增或修改 skill 时，必须同时更新两个目录下的同名文件。**

Skill 升级路径：
1. 新任务先用 Prompt 探索（≤2 次使用）
2. 使用 ≥3 次且流程标准化后 → 升级为 Skill（O(1) 调用）
3. 在 `.claude/skills/` 和 `.agents/skills/` 下创建 `SKILL.md`
4. 确保两份 `SKILL.md` 内容一致

## PR 模板

提交 PR 时请使用 `.github/PULL_REQUEST_TEMPLATE.md` 中的模板，包含：
- 变更类型
- 变更说明
- ACE 审查结果（如涉及 wiki/）
- 测试验证
- 关联 Issue

## 行为准则

- 尊重所有贡献者，保持专业友好的交流氛围
- 建设性地提出反馈，聚焦问题而非人身
- 帮助新手理解项目架构和贡献流程

感谢你的贡献！
