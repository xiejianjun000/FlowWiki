# automation/ — 自动化配置备份

## 当前运行中的自动化

### 1. FlowWiki 每日数据监控
- **ID**: automation-1784287880606
- **调度**: FREQ=DAILY;BYHOUR=9;BYMINUTE=0
- **状态**: ACTIVE

### 2. FlowWiki Issue/PR 巡检与回复
- **ID**: automation-1784287892702
- **调度**: FREQ=DAILY;BYHOUR=9,17;BYDAY=MO,TU,WE,TH,FR
- **状态**: ACTIVE

### 3. FlowWiki 每周增长周报
- **ID**: automation-1784287902610
- **调度**: FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0
- **状态**: ACTIVE

## 配置快照

见 `automations.json`。如需恢复，通过 WorkBuddy 的 automation_update 工具重建。

## 监控数据路径

```
~/.workbuddy/monitoring/flowwiki/
├── daily-YYYY-MM-DD.md      # 每日数据报告
├── weekly-YYYY-Www.md        # 每周增长周报
└── draft-reply-<number>.md   # Issue/PR 回复草稿
```
