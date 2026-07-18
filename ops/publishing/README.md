# publishing/ — 内容发布操作台

## 发布流程

```
写稿 → 审查 → 生成配图 → 平台适配 → 发布 → 监测效果
  │      │       │          │         │        │
  │      │       │          │         │        └→ 查看 GitHub Traffic Referrers
  │      │       │          │         └→ 掘金 agent-browser / 知乎 agent-browser
  │      │       │          └→ 掘金版 juejin.md + 知乎版 zhihu.md
  │      │       └→ ImageGen 生成 4 张配图到 assets/
  │      └→ 发布前检查清单 checklist.md
  └→ article.md 通用版
```

## 文章管理

```
articles/
└── v0.1.0-launch/         # 首发文章
    ├── article.md          # 通用版（可改、可复用）
    ├── juejin.md           # 掘金适配版
    ├── zhihu.md            # 知乎适配版
    └── assets/             # 配图
```

## 回复模板

发布后社区出现 Issue/PR/Discussion，用 `templates/` 下的模板快速回复。

## 关键平台差异

| 特性 | 掘金 | 知乎 |
|------|------|------|
| 代码块 | 标准 Markdown | 不支持嵌套代码块 |
| 标题层级 | 支持 H1-H6 | H1 会被平台覆盖 |
| 封面 | 800×420 必填 | 不支持自定义封面 |
| 标签 | 最多 5 个 | 话题标签 |
| 数学公式 | KaTeX | 不支持 |
| 目录 | 自动生成 | 手动 |
