# ace/ — ACE 反思循环记录

每次 Ingest 经过 ACE 循环后在此记录检查结果。

## 格式

```markdown
# ACE-YYYY-MM-DD-NNN

## 源文件
[[raw/xxx]]

## Generator 产出
- 摘要：<摘要>
- ZK 卡片：[[ZK-YYYY-MM-DD-NNN]]
- 目标 wiki 路径：wiki/<subdir>/<page>

## Reflector 发现
- [ ] 矛盾：<说明>
- [ ] 幻觉：<说明>
- [ ] 过时：<说明>

## Curator 决策
- [ ] 接受入 wiki
- [ ] 标"待核"（confidence=low）
- [ ] 触发 conflict：[[.memory/conflict/<topic>]]
- [ ] 退回 Generator（第 N 轮）

## 最终状态
✅ 已入库 / ⏳ 待核 / 🔄 第 N 轮
```
