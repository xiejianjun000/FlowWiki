# Wiki 操作日志

> 追加式日志，记录知识库所有变更操作。

## 格式

每条记录包含：时间 | 操作类型 | 操作者 | 文件路径 | 结果

---

## 2026-07-17

| 时间 | 操作 | 操作者 | 路径 | 结果 |
|------|------|--------|------|------|
| 10:25 | ingest | AI (Generator) | raw/test.md → wiki/concepts/ | ✅ 通过 ACE |
| 10:31 | ingest | AI (Generator) | raw/ekma-curve.md → wiki/concepts/ekma曲线.md | ✅ 通过 ACE |
| 10:32 | ingest | AI (Generator) | raw/o3-sensitivity.md → wiki/concepts/o3生成敏感性.md | ✅ 通过 ACE |
| 10:49 | query | AI (Generator) | 测试查询 | ✅ approved (confidence: 0.85) |
| 10:49 | sync | sync_dual_index.py | wiki/index.md + 00_首页/README.md | ✅ 双索引同步 |
| 10:50 | ingest | AI (Generator) | raw/backward-trajectory.md → wiki/concepts/气团后向轨迹.md | ✅ 通过 ACE |
| 10:50 | ingest | AI (Generator) | raw/pm25-reconstruction.md → wiki/concepts/pm2.5化学组分重构.md | ✅ 通过 ACE |
| 16:29 | lint | Claw (WorkBuddy) | 全库体检 | ✅ 补齐缺失文件 |

---

## 操作类型说明

| 类型 | 说明 | 触发方式 |
|------|------|---------|
| ingest | 新资料入库 | 用户投放 raw/ |
| query | 知识查询 | 用户提问 |
| lint | 知识体检 | 定时或手动 |
| research | 深度研究 | 用户发起 |
| sync | 索引同步 | ingest/query 后自动 |
| conflict | 矛盾记录 | ACE Reflector 发现 |
| archive | 归档操作 | 里程碑完成 |
