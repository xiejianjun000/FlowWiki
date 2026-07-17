# FlowWiki 快速开始指南

## 前提条件

- 任意 AI agent 平台（Claude Code / Codex / WorkBuddy / Amp / Gemini CLI）
- Git（用于版本控制）
- Markdown 编辑器（推荐 Obsidian / VS Code）

## 5 分钟上手

### 1. 创建知识库

```bash
# 克隆 FlowWiki 标准版骨架
git clone https://github.com/your-org/flowwiki-template.git my-wiki
cd my-wiki
```

### 2. 选择 Agent Bootstrap

| Agent | 使用文件 |
|-------|---------|
| Claude Code | `.agents/CLAUDE.md` |
| Codex | `.agents/CODEX.md` |
| WorkBuddy | `.agents/WORKBUDDY.md` |
| Amp / Gemini CLI | `.agents/AGENTS.md` |

### 3. 配置行业

编辑 `storage/{your-industry}/industry.yaml`：

```yaml
name: "你的行业"
slug: "your-industry"
gb_code: "XXXXX"
domain: "your-domain"
perspective: "your-perspective"

raw_sources:
  laws: [相关法律]
  standards: [相关标准]
  datasets: [相关数据]

scenarios:
  - id: your-scenario
    name: "你的场景"
    trigger: "触发条件"
    skills: [skill1, skill2]
```

### 4. 入仓第一篇资料

```bash
mkdir -p raw/articles
cp ~/your-first-article.md raw/articles/
```

### 5. 触发 Ingest

在 Agent 中执行：

```
> 请按 ingest skill 把 raw/articles/your-first-article.md 入库
```

Agent 会：
1. 读取 raw/ 文件
2. 运行 ACE 反思循环
3. 编译到 wiki/
4. 生成 A-MEM 卡片
5. 同步双索引

### 6. 查询知识

```
> 查询：你的问题
```

Agent 会：
1. 读取 wiki/index.md
2. 加载相关页面
3. 验证 raw/ 证据
4. 生成回答
5. 回存 wiki/ + 生成 ZK 卡片

## 目录结构速览

```
my-wiki/
├── raw/              # 只读证据层（你维护）
├── wiki/             # AI 编译知识层（AI 维护）
├── 00_首页/          # 人类 UX 入口（你维护）
├── .memory/          # Agent 记忆层（AI 维护）
├── .agents/          # Agent bootstrap
│   ├── CLAUDE.md
│   ├── AGENTS.md
│   ├── CODEX.md
│   └── WORKBUDDY.md
├── storage/          # 行业适配器
│   └── your-industry/
│       └── industry.yaml
├── _scripts/         # 工具脚本
├── _templates/       # 页面模板
├── 70_Prompt库/      # Prompt 管理
├── SCHEMA.md         # 知识库宪法
├── config.toml       # 检索配置
└── spec/             # 全局设计
```

## 下一步

- 阅读 [methodology.md](./methodology.md) 了解理论
- 阅读 [comparison.md](./comparison.md) 了解与现有方法的区别
- 阅读 [examples.md](./examples.md) 查看案例