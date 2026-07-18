# monitoring/ — 运维监控

## 自动化调度

三套自动化由 WorkBuddy Automations 引擎驱动，每天/每周自动执行。

数据输出到 `~/.workbuddy/monitoring/flowwiki/`（不在项目仓库内）。

## 监控指标

| 指标 | 来源 | 频率 |
|------|------|------|
| Stars / Forks / Watchers | GitHub Repo API | 每日 |
| Traffic Views / Unique Visitors | GitHub Traffic API | 每日 |
| Traffic Clones / Unique Cloners | GitHub Traffic API | 每日 |
| Open Issues / PRs | GitHub Issues API | 每日 |
| Referrers (流量来源) | GitHub Traffic API | 每周 |
| Popular Content (热门路径) | GitHub Traffic API | 每周 |

## 手动操作

```bash
# 一键拉取今日数据
cd /Users/mac/Desktop/FlowWiki
gh api repos/xiejianjun000/FlowWiki --jq '{
  stars: .stargazers_count,
  forks: .forks_count,
  issues: .open_issues_count,
  watchers: .subscribers_count
}'

# 查看流量趋势
gh api repos/xiejianjun000/FlowWiki/traffic/views --jq '.views[]'

# 查看 clone 数据
gh api repos/xiejianjun000/FlowWiki/traffic/clones --jq '.clones[]'
```

## 报告存档

- `reports/` 目录预留，实际数据存在 `~/.workbuddy/monitoring/flowwiki/`
- 格式：`daily-YYYY-MM-DD.md` / `weekly-YYYY-Www.md`
