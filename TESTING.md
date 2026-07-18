---
标题: 执法督察评查知识库 · 测试说明书
layer: 00-导航
type: doc
触发词: ["测试", "验收", "lint", "ace", "三验"]
适用场景: AI Agent 验收本知识库时使用
风险等级: 🟡
version: 1.0
status: 现行
tags: [00-导航, 🟡常规, doc, 现行]
confidence: high
sources: [".scripts/lint.py", ".scripts/graph.py"]
---

# 执法督察评查知识库 · 测试说明书

> 供 AI Agent 验收本知识库时使用。

## 一验：Lint 体检

```bash
python .scripts/lint.py
```
通过标准：0 断链、0 缺 frontmatter

## 二验：图谱质量

```bash
python .scripts/graph.py --format stats
```
通过标准：0 孤立、全可达、密度≥.015

## 三验：ACE 循环

```bash
python .scripts/ace_review.py --raw raw/articles/2026-07-16_TRAE_Work知识库上线_微信原文.md --verbose
```
通过标准：Generator→Reflector→Curator 三阶段均输出合规

## 四验：内存层

- `.memory/zettelkasten/` 有 ZK 卡片
- `.memory/ops/` 有操作日志
- `.memory/ace/` 有 ACE 记录

## 五验：链接完整性

```bash
python .scripts/fix_dangling.py
```
通过标准：无悬空链（模板占位符除外）

## 图谱设置

推荐 `.obsidian/graph.json` 配置：开启 showOrphans、关闭 Tags、中心引力 0.5、斥力 10。

---
> 返回：[[index]] · [[首页/首页]]
