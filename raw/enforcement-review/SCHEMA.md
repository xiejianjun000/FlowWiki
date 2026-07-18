---
title: 执法督察评查知识库 · Schema（LLM 维护约定）
layer: 10-元文档
type: schema
触发词: ["schema", "维护约定", "怎么改库", "入库规范", "ingest流程"]
适用场景: LLM 每次 Ingest/Query/Lint 前读取本文件，作为统一维护纪律
关联法条: []
调用skill: [eco-review-kb]
风险等级: 🟡
version: 1.0
status: 现行
ingested: 2026-07-18T00:00:00+08:00

updated: 2026-07-16
tags: [10-元文档, 🟡常规, schema, 现行]

updated: 2026-07-18
---
# 🛠 SCHEMA.md — 知识库维护约定（人与 LLM 的分工契约）

> 本文件是 Karpathy LLM Wiki 方法论的"Schema 层"。LLM 在每次操作本库前必须读它。
> 它替代了散落在 `10_元文档/` 的约定，并固化角色分工。

## 一、三层架构（必须坚守）

1. **Raw 源层（人类策展 / LLM 只读不改）**：权威原始资料的最终真相源。
   - 现行：法律全文、法典原文、案例原文、裁量基准原文、监测条例原文。
   - 标注：`status: 源真`, 不可变；LLM 仅引用，不在此层撰写。
2. **Wiki 层（LLM 拥有 / 全权维护）**：本库 `01_~09_`、`新手入门/`、`工具资源/` 下的全部精炼页、SOP、实战、导航、指针。
   - LLM 在此层创建/更新/链接/体检。
3. **Schema 层（人+LLM 共演化）**：本文件 + `10_元文档/`。约定结构、frontmatter、工作流。

## 二、角色分工（Karpathy 灵魂）

- **人类**：策展源（决定收什么）、提好问题（评查/办案/督察任务）、判断价值、审批 Lint 发现。
- **LLM**：所有记账苦活——摘要、交叉引用、filing、一致性维护、Lint 体检、index/log 更新。
- 原则：*人类 rarely 手写 wiki；wiki 是 LLM 的产出物。*

## 三、frontmatter 统一 Schema（每页必须）

```
---
标题: <页面标题>
layer: <00-导航|01-评查标准|02-法律法规|03-处罚办法|04-案例|05-督察|06-实务|07-新法|10-元文档|99-运营>
type: <moc|index|sop|law|case|concept|tool|schema|doc>
触发词: ["schema", "维护约定", "怎么改库", "入库规范", "ingest流程"]
适用场景: ["新法更新", "撰写报告"]
关联法条: [<法条号>]
调用skill: [eco-review-kb]
风险等级: <🔴一票否决|🟠重点|🟡常规>
version: 1.0
status: <现行|源真|废止待切换|草案>
updated: <YYYY-MM-DD>
tags: [<layer>, <风险>, <type>, <status>]
---
```

## 四、三大操作（Ingest / Query / Lint）

### Ingest（摄取新源 → 编译进 Wiki）
1. 人类把源放入 Raw 层（或指定已有 Raw 文件），告知 LLM。
2. LLM 读源 → **先分析**（实体/概念/与现有 wiki 的链接/矛盾/结构建议）→ **再生成**（不一次性边读边写）。
3. 产出：源摘要页 + 更新相关 Wiki 页（25项/SOP/实战等）+ 更新 `index.md` + 追加 `log.md`。
4. 一篇源应触碰 3~15 个 Wiki 页。人类审核更新、指导侧重。

### Query（基于 Wiki 问答）
- LLM 先读 `index.md` 定位 → 读相关页 → 带引用合成答案。
- **好答案可存回 Wiki**（比较表/分析/新发现）→ 让探索也复利。

### Lint（定期体检，必须可执行）
每轮 Lint 检查：
- 页面间**矛盾**（尤其 8-15 法典切换、废止10法引用）
- **过期主张**（被新源/新法超越的旧结论）
- **孤页**（无入链，degree≤1）
- **漏链**（重要概念被提及但无独立页 / 应链未链）
- **知识缺口**（可由网络检索填补的空白）
- frontmatter 异常（缺字段/层错配）
- 输出 Lint 报告 → 人类审批 → LLM 修复 → 更新 log。

## 五、两个强制文件
- `index.md`：内容目录，LLM 每次先读。**Ingest 后必须更新。**
- `log.md`：时间轴，`## [YYYY-MM-DD] <操作类型> | <对象>` 前缀，可 `grep` 解析。**每次操作必须追加。**

## 六、版本与备份
- 本库为 git 仓库。每次重大操作后 `git add -A && git commit`。
- Raw 层源真：法律原文变更时，旧版标记 `status: 废止待切换`，不物理删除。

## 七、与本库规则的衔接
- 8-15 法典切换：2026-08-15 后新立案禁引废止10法（🔴 一票否决），Lint 重点查。
- 复议条例(7-1施行)、起诉期限解释(已施行) 的告知要素，Lint 查决定书/告知书类页。
- 详见 `10_元文档/` 各专项约定与 `99_持续运营/`。

## 六、入库标准动作（已脚本化，LLM 每次 Ingest/维护后必跑）
- `_scripts/reindex.py`：重生成 index.md（机器目录），Ingest 后必跑。
- `_scripts/normalize_schema.py --apply`：补缺失 frontmatter 字段（layer/type/触发词/风险等级/version/status/updated/tags，无 title 用文件名补）；tags 下的双链标签写法需转纯文本（即 Obsidian 标签式双链写法，形如“双链标签”）。
- `_scripts/fix_dangling.py --apply`：定点修复悬空双链（跨库去括号、真实页修路径、其余转 `#标签`）。
- `_scripts/lint.py`：体检（frontmatter 异常 / 悬空双链 / 孤页 / 旧法红线）。旧法豁免白名单：讲废止/替代/衔接/法典化后/案例原文/反例教学语境均放行。
- 目标：**lint 归零**才算入库达标。Lint 仅诊断，修复由 LLM 在人工审批后执行并 git commit。
