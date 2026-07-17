# FlowWiki — 目录结构

> 版本：v0.1（M0 全局设计阶段）
> 维护：顶层目录变动时 AI 自动更新
> 关联文档：[requirements.md](./requirements.md) / [design.md](./design.md) / [tasks.md](./tasks.md)

---

## 完整目录树

```
FlowWiki/
│
├── README.md                       ← 方法论白皮书入口（M7 完善）
├── CLAUDE.md                       ← L6 Claude Code bootstrap（M1）
├── AGENTS.md                       ← L6 通用 agent bootstrap（M1）
├── SCHEMA.md                       ← L1 宪法（M1）
├── LICENSE                         ← MIT（M1）
├── .gitignore                      ← 忽略 .obsidian/ 等
│
├── spec/                           ← L3 全局设计（人工主导）
│   ├── requirements.md             ← 项目整体需求
│   ├── design.md                   ← 架构设计/决策
│   ├── tasks.md                    ← 里程碑任务清单
│   ├── structure.md                ← 本文件
│   └── devlog.md                   ← 开发日志（PR 合并后 AI 追加）
│
├── openspec/                       ← L3 单任务变更
│   └── changes/
│       ├── <active-change>/
│       │   ├── .openspec.yaml
│       │   ├── proposal.md
│       │   ├── design.md
│       │   ├── specs/
│       │   ├── tasks.md
│       │   └── plan.md
│       └── archive/
│           └── <archived-change>/
│
├── raw/                            ← L1 原始资料层（只读）
│   └── <category>/                 ← 按来源/主题分类
│       └── *.md | *.pdf | *.txt
│
├── wiki/                           ← L1 AI 编译层
│   ├── index.md                    ← 机器索引（紧凑扁平）
│   ├── log.md                      ← 操作日志（追加式）
│   ├── concepts/                   ← 概念页（是什么）
│   ├── playbooks/                  ← 操作手册（怎么做）
│   ├── cases/                      ← 案例页（实例）
│   ├── comparisons/                ← 对比页（A vs B）
│   ├── workflows/                  ← 工作流页（流程图）
│   └── meta/                       ← 元文档（设计原则、命名规范）
│
├── 00_首页/                        ← L1 人类索引（TRAE 6 板块）
│   ├── 00_首页.md                  ← 人类入口 + Dataview 看板
│   ├── 01_新手入门/                 ← 第一次使用 / 5 分钟上手 / FAQ
│   ├── 02_方法论教程/               ← 6 层架构讲解 / 4 操作演示 / ACE 原理
│   ├── 03_实战场景/                 ← L7 业务外壳（可插拔）
│   │   ├── README.md               ← 场景注入机制说明
│   │   └── <scenario-name>/        ← 单个场景
│   │       ├── README.md
│   │       ├── playbooks.md
│   │       ├── cases.md
│   │       └── skills.md
│   ├── 04_工具资源/                 ← 命令速查 / 模板下载 / 70_Prompt库 索引
│   └── 05_近期活动/                 ← changelog / 新场景上线 / 用户故事
│
├── 70_Prompt库/                     ← 场景&功能提示词存档（Skill 升级池）
│   ├── README.md                    ← Prompt 索引 + 升级规则说明
│   ├── 01_生成类.md                 ← "生成迎检清单"/"生成监测方案" 等
│   ├── 02_校对类.md                 ← "校对案卷程序"/"校对数据一致性" 等
│   ├── 03_问句类.md                 ← "从执法者视角"/"用企业视角" 等
│   └── 04_拆解类.md                 ← "拆解许可证"/"拆解法规" 等
│
├── .memory/                        ← L4 Agent 记忆层 ★ FlowWiki 独有
│   ├── README.md                   ← 记忆层架构说明
│   ├── zettelkasten/               ← A-MEM 卡片（ZK-YYYY-MM-DD-NNN.md）
│   │   └── README.md
│   ├── episodic/                   ← 跨会话记忆（每次 query 答案回存）
│   │   └── README.md
│   └── conflict/                   ← 矛盾追踪（新旧知识冲突）
│       └── README.md
│
├── .agents/                        ← L5 Skill（通用 agent 格式）
│   └── skills/
│       ├── ingest/SKILL.md
│       ├── query/SKILL.md
│       ├── lint/SKILL.md
│       └── research/SKILL.md
│
├── .claude/                        ← L5 Skill（Claude Code 格式）
│   └── skills/
│       ├── ingest/SKILL.md
│       ├── query/SKILL.md
│       ├── lint/SKILL.md
│       └── research/SKILL.md
│
├── .llm-wiki/                      ← L2 检索增强配置
│   └── config.toml                 ← 检索模式、阈值、lint 规则
│
├── _scripts/                       ← 工程化工具链（Python）
│   ├── reindex.py                  ← 重生成 wiki/index.md
│   ├── normalize.py                ← 补缺失 frontmatter
│   ├── fix_dangling.py             ← 修复悬空双链
│   ├── lint.py                     ← 体检（结构/悬空/孤儿/矛盾）
│   ├── graph.py                    ← 图谱质量分析（连通/可达/枢纽）
│   ├── sync_index.py               ← 双索引同步（机器 ↔ 人类）
│   ├── ace_review.py               ← ★ L4 ACE 三 agent 反思循环
│   └── a_mem_card.py               ← ★ L4 A-MEM ZK 卡片生成
│
└── _templates/                     ← 页面模板
    ├── concept.md
    ├── playbook.md
    ├── case.md
    ├── comparison.md
    ├── workflow.md
    └── source-summary.md
```

---

## 6 层与目录的映射

| 层 | 目录 | 维护者 | 修改频率 |
|----|------|--------|---------|
| L1 知识编译 | `raw/` `wiki/` `00_首页/` `70_Prompt库/` `SCHEMA.md` | raw 只读 / wiki AI / 00_首页+70_Prompt库 LLM+人 | 高 |
| L2 检索增强 | `.llm-wiki/config.toml` | 人工配置 | 低 |
| L3 Spec-Driven | `spec/` `openspec/` | 人工主导 / AI 归档 | 中 |
| L4 Agent 记忆 | `.memory/` | AI 自动 + 人工 review 矛盾 | 高 |
| L5 Skill 化 | `.agents/skills/` `.claude/skills/` | AI 自动抽象 + 人工 review | 中 |
| L6 多 agent 接手 | `CLAUDE.md` `AGENTS.md` | 人工主导 | 低 |
| L7 场景层 | `00_首页/03_实战场景/` | 可插拔，按需启用 | 中 |

---

## 命名规范

### 文件命名

| 类型 | 规范 | 示例 |
|------|------|------|
| wiki 页 | kebab-case | `wiki/concepts/ace-reflection-loop.md` |
| ZK 卡片 | `ZK-YYYY-MM-DD-NNN.md` | `.memory/zettelkasten/ZK-2026-07-17-001.md` |
| episodic 记忆 | `EP-YYYY-MM-DD-NNN.md` | `.memory/episodic/EP-2026-07-17-001.md` |
| conflict 追踪 | `<topic>.md` | `.memory/conflict/o3-sensitivity-source.md` |
| openspec 变更 | `<verb-object>` | `openspec/changes/implement-ace-amem/` |
| Python 脚本 | snake_case | `_scripts/ace_review.py` |

### 目录命名

- 顶层目录：`数字_名称/` 或 `字母_名称/`（如 `00_首页/`、`spec/`）
- 子目录：全小写 kebab-case（如 `wiki/concepts/`）
- 场景目录：`<scenario-name>/`（如 `03_实战场景/执法办案/`）

### frontmatter 强制字段

所有 wiki/ 文件必须包含：
- `type` — 页面类型
- `title` — 标题
- `created` / `updated` — 日期
- `confidence` — high/medium/low
- `sources` — 溯源到 raw
- `tags` — 至少包含 `flow-wiki` + 层级 + 主题
- `status` — draft/reviewed/archived

---

## 与现有 4 个库的目录借鉴关系

| FlowWiki 目录 | 借鉴来源 | 改进点 |
|--------------|---------|--------|
| `spec/` | SpecCoding 模板 | 强制 4 文件齐备 |
| `openspec/changes/` | OpenSpec + SuperSpec | 加 `.openspec.yaml` 配置 |
| `raw/` | Karpathy 原教 + 执法督察评查库 | 保留只读原则 |
| `wiki/` | 环评与排污许可库 | 7 类页面 + confidence |
| `00_首页/` | TRAE Work 6 板块 + 企业合规库 | 双索引，AI 与人各取所需 |
| `.memory/` ★ | A-MEM 论文 + FlowWiki 原创 | 三子目录分工 |
| `.agents/skills/` `.claude/skills/` | 环评与排污许可库 + Claude 官方 | 双格式同步部署 |
| `.llm-wiki/config.toml` | llm-wiki CLI（环评库已用） | 加自适应阈值 |
| `_scripts/` | 执法督察评查库 5 脚本 | 新增 ace_review.py + a_mem_card.py + sync_index.py |
| `_templates/` | 执法督察评查库 | 扩展到 6 类模板 |
| `CLAUDE.md` `AGENTS.md` | 环评与排污许可库 | 双 bootstrap 内容同步 |

---

## 目录演进规则

1. **顶层目录新增**：必须先在 `spec/structure.md` 记录，AI 才能创建
2. **`raw/` 永远只读**：任何脚本都不得修改 raw/ 下文件
3. **`spec/requirements.md` 和 `spec/design.md`**：人工主导，AI 修改前必须明确请示
4. **`spec/tasks.md` 状态**：AI 完成任务后自动勾选（不修改任务内容）
5. **`spec/devlog.md`**：每次 openspec 变更 archive 时，AI 自动追加一条
6. **`.memory/conflict/`**：人工 review 后才能标记"已解决"

---

## 当前实现进度

| 目录 | 状态 |
|------|------|
| `spec/` | ✅ M0 进行中 |
| `openspec/changes/` | ✅ 空目录已建 |
| `raw/` | ⬜ M1 创建 |
| `wiki/` | ⬜ M1 创建 |
| `00_首页/` | ⬜ M1 创建 |
| `.memory/` | ⬜ M3 创建 |
| `.agents/skills/` `.claude/skills/` | ⬜ M2 创建 |
| `.llm-wiki/` | ⬜ M1 创建 |
| `_scripts/` | ⬜ M2 创建 |
| `_templates/` | ⬜ M1 创建 |
| `CLAUDE.md` `AGENTS.md` `SCHEMA.md` | ⬜ M1 创建 |
