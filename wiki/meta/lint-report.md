# Lint 体检报告

> 体检时间：2026-07-17 16:47
> 体检执行者：Claw (WorkBuddy)

## 检查结果汇总

| 检查项 | 状态 | 问题数 |
|--------|------|--------|
| 悬空链（[[xxx]] 无对应文件） | ✅ 通过 | 0 |
| 孤儿页（无人引用的页面） | ✅ 通过 | 0 |
| frontmatter 缺失 | ⚠️ 需修复 | 9 |
| confidence 不匹配 | ✅ 通过 | 0 |
| 矛盾未解决 | ✅ 通过 | 0 |
| .claude/skills vs .agents/skills 一致性 | ✅ 通过 | 0 |
| 27 skill 全部有 SKILL.md | ✅ 通过 | 0 |
| 7 场景全齐 | ✅ 通过 | 0 |
| 7 行业适配器全齐 | ✅ 通过 | 0 |
| 6 板块全齐 | ✅ 通过 | 0 |
| .memory 4 子目录全齐 | ✅ 通过 | 0 |

## 详细问题

### ⚠️ frontmatter 缺失（9 个页面）

以下 wiki 页面缺少 frontmatter（SCHEMA.md 要求所有 wiki 页面必须有 type/title/created/updated/confidence/sources/tags/status 字段）：

| # | 文件 | 类型 | 严重度 |
|---|------|------|--------|
| 1 | wiki/concepts/气团后向轨迹.md | concept | 中 |
| 2 | wiki/concepts/ekma曲线.md | concept | 中 |
| 3 | wiki/concepts/o3生成敏感性.md | concept | 中 |
| 4 | wiki/concepts/pm2.5化学组分重构.md | concept | 中 |
| 5 | wiki/playbooks/县域级溯源工作流.md | playbook | 中 |
| 6 | wiki/playbooks/市州级溯源工作流.md | playbook | 中 |
| 7 | wiki/playbooks/溯源研判五步法.md | playbook | 中 |
| 8 | wiki/comparisons/hysplit-vs-flexpart.md | comparison | 中 |
| 9 | wiki/comparisons/wrf-chem-vs-cmaq.md | comparison | 中 |

**修复建议**：为每个页面添加标准 frontmatter，可使用 `_templates/concept.md.j2` / `playbook.md.j2` / `comparison.md.j2` 模板。

## 脚本测试结果

| 脚本 | 测试结果 | 输出 |
|------|---------|------|
| ace_review.py | ✅ 通过 | ACE 日志写入 .memory/ace/ |
| a_mem_card.py | ✅ 通过 | ZK 卡片写入 .memory/zettelkasten/ |
| sync_dual_index.py | ✅ 通过 | wiki/index.md + 00_首页/README.md 同步 |
| ingest_pipeline.py | ✅ 通过 | 索引生成（4 concepts, 3 playbooks, 2 comparisons） |
| build_match_index.py | ✅ 通过 | 匹配索引构建（1 raw, 13 wiki） |
| gen_criteria_pages.py | ✅ 通过 | 生成化学组分.md + 气象条件.md |

## 结论

知识库整体健康度良好。唯一待修复项是 9 个 wiki 页面缺少 frontmatter，不影响功能但影响 lint 合规性。
