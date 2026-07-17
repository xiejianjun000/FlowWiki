# FlowWiki SCHEMA — 知识库宪法

## 1. 核心原则

### 1.1 CIC 工作流
- **Collect（收集）**：人类负责收集原始资料到 raw/，保证证据保真
- **Compile（编译）**：AI 负责将 raw/ 编译到 wiki/，生成结构化知识
- **Compound（复利）**：人和 AI 共用 wiki/，知识持续增长

### 1.2 骨肉分离
- **骨架**（L2-L6）：所有行业完全相同，零修改
- **肉**（L1 + L7）：每个行业不同内容
- **驱动**：industry.yaml 连接骨架与肉

### 1.3 证据链完整
- 所有 wiki/ 内容必须能追溯到 raw/ 原始证据
- 禁止无证据的 AI 编造内容进入 wiki/
- ACE 反思循环确保错误知识不进 wiki

## 2. 文件结构规范

### 2.1 L1 知识编译层

```
raw/                    # 只读证据层，人类维护
  ├── laws/             # 法律文件
  ├── standards/        # 标准文件
  ├── reports/          # 报告文件
  ├── datasets/         # 数据集
  └── README.md         # raw 索引

wiki/                   # AI 编译知识层，AI 维护
  ├── index.md          # wiki 总索引
  ├── concepts/         # 核心概念
  ├── playbooks/        # 操作手册
  ├── comparisons/      # 对比分析
  ├── entities/         # 实体定义
  ├── sources/          # 源解析
  └── synthesis/        # 综合研判

00_首页/                # 人类 UX 入口
  ├── 01_知识图谱/
  ├── 02_判据体系/
  ├── 03_实战场景/
  ├── 04_进化学习/
  ├── 05_采集记录/
  ├── 06_系统运维/
  └── README.md
```

### 2.2 L2 检索增强层

```
config.toml             # 检索配置
```

### 2.3 L3 Spec-Driven 层

```
spec/                   # 全局设计
  ├── design.md
  ├── requirements.md
  ├── structure.md
  ├── tasks.md
  └── hermes-integration.md

openspec/               # 变更治理
  ├── changes/          # 活跃变更
  └── archive/          # 归档变更
```

### 2.4 L4 Agent 记忆层

```
.memory/                # A-MEM 卡片库
  ├── cards/            # Zettelkasten 卡片
  ├── ace/              # ACE 反思记录
  └── README.md
```

### 2.5 L5 Skill 化层

```
.agents/skills/         # Skill 登记册
  ├── ingest/           # 入仓
  ├── query/            # 查询
  ├── lint/             # 检查
  ├── research/         # 研究
  └── {industry_slug}/  # 行业专属
```

### 2.6 L6 多 agent 接手层

```
.agents/
  ├── CLAUDE.md         # CLAUDE bootstrap
  └── AGENTS.md         # AGENTS bootstrap
```

### 2.7 L7 场景层

```
00_首页/03_实战场景/
  ├── {industry_slug}/
  │   ├── README.md
  │   ├── playbooks.md
  │   ├── cases.md
  │   └── skills.md
```

### 2.8 基础设施

```
storage/                # 行业适配器
  └── {industry_slug}/
      └── industry.yaml

_scripts/               # 工具脚本
  ├── ingest_pipeline.py
  ├── gen_criteria_pages.py
  └── build_match_index.py

_templates/             # 模板
  ├── wiki_page.md.j2
  ├── raw_index.md.j2
  └── memory_card.md.j2

70_Prompt库/            # Prompt 管理
  ├── system/
  ├── task/
  ├── retrieval/
  └── output/
```

## 3. 命名规范

### 3.1 文件命名
- 使用小写字母、数字和连字符
- 中文文件名使用拼音或英文描述
- 避免空格和特殊字符

### 3.2 目录命名
- 行业目录：`{industry-slug}` 格式
- 场景目录：`{scenario-id}` 格式
- 概念目录：`{concept-name}` 格式

### 3.3 链接规范
- 使用相对路径
- 链接到 raw/ 文件时使用 `../raw/` 前缀
- 链接到 wiki/ 文件时使用 `../wiki/` 前缀

## 4. 内容规范

### 4.1 raw/ 规范
- 文件必须是原始证据，未经 AI 修改
- 文件名应包含来源、日期和主题
- 每个文件应有元数据注释（来源、日期、版本）

### 4.2 wiki/ 规范
- 所有内容必须能追溯到 raw/
- 使用 Markdown 格式
- 遵循 wiki/ 页面模板
- 禁止无证据的 AI 编造内容

### 4.3 .memory/ 规范
- 卡片使用 Zettelkasten 格式
- 每条记录包含：ID、日期、内容、来源、标签
- ACE 反思记录包含：Generator 输出、Reflector 审查、Curator 决策

## 5. 操作规范

### 5.1 入仓流程
1. 人类收集原始资料 → 写入 raw/
2. 运行 ingest_pipeline.py → AI 编译到 wiki/
3. ACE 反思循环审查 → 确认无误后进入 wiki/
4. 生成 A-MEM 卡片 → 存入 .memory/

### 5.2 查询流程
1. 用户提问 → Hermes 行业路由
2. 读取 wiki/index.md → 加载相关页面
3. 查询 raw/ 原始证据 → 验证准确性
4. 生成回答 → 回存 wiki/ + 生成 ZK 卡片

### 5.3 变更流程
1. 创建 openspec/changes/{change-name}/
2. 编写 proposal.md → design.md → specs/ → plan.md
3. 执行变更 → 验证 → archive

## 6. 安全规范

### 6.1 访问控制
- raw/ 目录只读，禁止 AI 直接修改
- wiki/ 目录由 ACE 循环控制写入
- .memory/ 目录由 Agent 自动维护

### 6.2 内容审核
- 所有 wiki/ 内容必须经过 ACE 反思循环审查
- 人类可否决 AI 生成的内容
- 错误内容必须回退到上一版本

### 6.3 数据隔离
- 每个行业的数据完全隔离
- 通过 slug 作为命名空间标识
- 检索时自动限定在当前行业范围内

## 7. 版本控制

### 7.1 Git 规范
- 使用 Git 进行版本控制
- 每次变更创建独立分支
- 变更完成后合回主分支

### 7.2 变更记录
- 每次变更记录在 openspec/changes/
- 归档后移入 openspec/changes/archive/
- 更新 CHANGELOG.md

## 8. 验收标准

- 文件结构符合规范
- 命名规范统一
- 内容规范执行到位
- 操作流程顺畅
- 安全机制有效
- 版本控制完整