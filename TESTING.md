# FlowWiki 测试说明书

> 本文档供 Claude / Hermes / Codex 等 AI Agent 测试 FlowWiki 知识库时使用。

## 测试用知识库

仓库包含一个预置的测试知识库：**enforcement-review（执法督察评查）**

- raw/enforcement-review/: 153 篇原始资料
- wiki/enforcement-review/: 98 节点编译知识
- storage/enforcement-review/industry.yaml: 行业配置

## 一键引导

```bash
# 从 raw 重新生成 wiki（跳过入仓）
python _scripts/bootstrap.py --source raw/enforcement-review --slug enforcement-review --skip-to 2
```

## 三个验收

| 验收 | 命令 | 通过标准 |
|------|------|----------|
| 一验 lint | 自动在 bootstrap 中执行 | 0 断链、0 缺 frontmatter |
| 二验 graph | `python _scripts/graph.py --format stats --industry enforcement-review` | 0 孤立、密度 ≥ 2.0 |
| 三验 hermes | `python _scripts/hermes_review.py --industry enforcement-review` | pass、评分 ≥ 7.0 |

## 每日全量测试

```bash
python _scripts/daily_test.py --quick
```

## 实战案例测试

用例 1：自动监测异常
```
企业累计超标18次（颗粒物13次、SO2 1次、NOx 4次），涉及工况标记18次（停炉8次、启炉10次），是否违法？如何处罚？
```

用例 2：排污许可合规
```
MF0001/MF0002回转窑采用双碱法脱硫，疑似难以稳定达标排放，如何核查？
```

## 结果查看

| 内容 | 路径 |
|------|------|
| 操作日志 | `.memory/ops/YYYY-MM-DD.jsonl` |
| ACE 反思 | `.memory/ace/` |
| 缺口卡片 | `.memory/gaps/` |
| 人类页面 | `00_首页/01_知识图谱/` ~ `00_首页/06_系统运维/` |
| 测试报告 | `ops/monitoring/` |
| 图谱可视化 | 用 Obsidian 打开仓库根目录，查看图谱视图 |

## 图谱设置

`.obsidian/graph.json` 已配置为紧密圆图（中心引力 1.2、排斥力 0.15、链接距离 50）。

打开 Obsidian → 打开本仓库 → 点左侧图谱图标即可看到 98 节点彩色知识图谱。

## 能力验证清单

- [ ] bootstrap.py 全流程跑通
- [ ] lint 0 断链
- [ ] graph 0 孤立
- [ ] hermes_review pass
- [ ] ops_log 有记录
- [ ] .memory/ace/ 有反思日志
- [ ] 00_首页/ 6 页有 enforcement-review 入口
- [ ] 实战案例可正确回答
- [ ] 知识缺口可检测并创建 gap 卡片
- [ ] Obsidian 图谱可见 98 节点
