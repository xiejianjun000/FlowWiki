# ops/ — FlowWiki 项目运维与发布操作台

> 所有运维监控、内容发布、社区互动的操作入口。自动化调度在 WorkBuddy Automations 中管理，本目录是配置备份和手动操作手册。

## 目录导航

| 目录 | 职责 | 关键文件 |
|------|------|---------|
| `monitoring/` | 项目数据监控与报告 | 每日 stats / 周报配置 |
| `publishing/` | 内容发布全流程 | 文章稿件 / 配图素材 / 回复模板 / 发布脚本 |
| `automation/` | 自动化备份 | automations.json 快照 |

## 自动化任务对照

| 自动化名称 | 频率 | 在 WorkBuddy 中管理 |
|-----------|------|-------------------|
| FlowWiki 每日数据监控 | 每天 9:00 | automation-1784287880606 |
| FlowWiki Issue/PR 巡检与回复 | 工作日 9:00 + 17:00 | automation-1784287892702 |
| FlowWiki 每周增长周报 | 每周一 9:00 | automation-1784287902610 |

## 快速操作

```bash
# 手动拉取仓库数据
gh api repos/xiejianjun000/FlowWiki --jq '{stars: .stargazers_count, forks: .forks_count}'

# 查看所有 open issues
gh issue list -R xiejianjun000/FlowWiki --state open

# 发布一篇新文章
# 1. 在 publishing/articles/ 下创建文章包
# 2. 用 publishing/scripts/publish.md 中的指令发布
```
