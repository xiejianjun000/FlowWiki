# Hermes + FlowWiki 集成设计文档

## 1. 核心设计原则

### 1.1 骨肉分离

FlowWiki 标准版的关键设计就一个原则：

```
骨架（L2-L6 + _scripts/_templates/SCHEMA）— 所有行业完全相同，零修改
  ↓ 由 industry.yaml 驱动 ↓
肉（L1 raw/wiki/00_首页/.memory + L7 场景）— 每个行业不同内容
```

### 1.2 架构分层职责

| 层级 | 职责 | 是否通用 |
|------|------|---------|
| L1 知识编译层 | raw/（只读证据）+ wiki/（AI 编译）+ 00_首页/（人类 UX） | ❌ 行业相关 |
| L2 检索增强层 | BM25→nano-graphrag→LightRAG 自适应 | ✅ 通用 |
| L3 Spec-Driven 层 | spec/ 全局设计 + openspec/changes/ 单任务变更 | ✅ 通用 |
| L4 Agent 记忆层 | A-MEM 卡片（Zettelkasten）+ ACE 反思循环 | ✅ 通用 |
| L5 Skill 化层 | 4 操作 skill + 高频任务自动抽象 | ✅ 通用 + 行业专属 |
| L6 多 agent 接手层 | CLAUDE.md + AGENTS.md 双 bootstrap | ✅ 通用 |
| L7 场景层 | 业务外壳，可插拔 | ❌ 行业相关 |

## 2. industry.yaml 规范

### 2.1 文件位置

```
storage/{industry_slug}/industry.yaml
```

### 2.2 完整 schema

```yaml
name: "行业名称"
slug: "industry-slug"
gb_code: "GB/T 4754 行业代码"
domain: "一级领域"
subdomain: "二级子领域"
perspective: "视角（企业/执法局/监测站/审查机构）"

raw_sources:
  laws:
    - 法律名称
  standards:
    - 标准名称
  datasets:
    - 数据源名称

wiki_structure:
  concepts:
    - 核心概念名称
  playbooks:
    - 操作手册名称
  comparisons:
    - 对比分析名称

scenarios:
  - id: 场景ID
    name: "场景名称"
    trigger: "触发条件描述"
    skills: [skill1, skill2]

industry_skills:
  - name: "Skill 名称"
    file: ".agents/skills/{skill-name}/SKILL.md"
```

### 2.3 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 行业中文名称 |
| `slug` | string | 行业英文标识，用于目录命名 |
| `gb_code` | string | GB/T 4754-2017 国民经济行业分类代码 |
| `domain` | string | 一级领域（environmental/legal/business/health 等） |
| `subdomain` | string | 二级子领域 |
| `perspective` | string | 使用视角，影响内容组织方式 |
| `raw_sources.laws` | list | 必须入仓的法律清单 |
| `raw_sources.standards` | list | 必须入仓的标准清单 |
| `raw_sources.datasets` | list | 行业特有数据源 |
| `wiki_structure.concepts` | list | 行业核心概念列表 |
| `wiki_structure.playbooks` | list | 行业操作手册列表 |
| `wiki_structure.comparisons` | list | 行业对比分析列表 |
| `scenarios[].id` | string | 场景唯一标识 |
| `scenarios[].name` | string | 场景名称 |
| `scenarios[].trigger` | string | 触发条件描述 |
| `scenarios[].skills` | list | 场景关联的 Skill 列表 |
| `industry_skills[].name` | string | 行业专属 Skill 名称 |
| `industry_skills[].file` | string | Skill 文件路径 |

## 3. 「4+1」部署模式

### 3.1 目录结构

```
FlowWiki 标准版（骨架，git 仓库）
├── storage/
│   ├── atmospheric-tracing/
│   │   └── industry.yaml
│   ├── law-enforcement-review/
│   │   └── industry.yaml
│   ├── eia-permit/
│   │   └── industry.yaml
│   ├── enterprise-compliance/
│   │   └── industry.yaml
│   └── {new-industry}/
│       └── industry.yaml
├── _scripts/
│   ├── ingest_pipeline.py
│   ├── gen_criteria_pages.py
│   └── build_match_index.py
├── _templates/
│   ├── wiki_page.md.j2
│   ├── raw_index.md.j2
│   └── memory_card.md.j2
├── SCHEMA.md
├── config.toml
├── raw/
├── wiki/
├── 00_首页/
├── .memory/
├── 70_Prompt库/
└── .agents/
    ├── skills/
    │   ├── ingest/
    │   ├── query/
    │   ├── lint/
    │   ├── research/
    │   └── {industry_slug}/
    ├── CLAUDE.md
    └── AGENTS.md
```

### 3.2 四个现有库改造路径

| 库 | 改造动作 | 工作量 |
|----|---------|--------|
| 大气溯源 | ① 拷贝骨架 ② 写 industry.yaml ③ raw/ 内容迁入 ④ wiki/ 内容映射 ⑤ Hermes 跑首次 ingest | 骨架一次性，内容可自动化 |
| 执法督察评查 | 同上，00_首页 和 _scripts 可复用 | 内容迁入自动化 |
| 企业合规AI管家 | 同上，需先跑 fix_dangling 修复 528 悬空链 | 需额外跑一次 lint |
| 环评与排污许可 | 同上，.agents/.claude skills 可直接复用 | 工作量最小 |

## 4. Hermes 冷启动流程

### 4.1 流程详解

```
用户: "我是做食品安全的"
  ↓
Hermes: 识别行业 → 食品制造业 C14（GB/T 4754）
  ↓
Hermes: 创建 storage/food-safety/industry.yaml
  ↓ 自动填充 ↓
  laws: [食品安全法, 农产品质量安全法, 产品质量法]
  standards: [GB 2760, GB 2761, GB 2762, GB 2763, GB 29921...]
  scenarios: [添加剂合规, 污染物限量, 微生物检验, HACCP审计, 标签审核]
  ↓
Hermes: 拷贝 FlowWiki 骨架 → 创建 raw/ wiki/ 00_首页/ .memory/
  ↓
Hermes: 根据 laws+standards 列表 → Web 搜索原文 → 写入 raw/
  ↓
Hermes: 跑 ingest → raw → wiki 编译 + ACE 反思
  ↓
Hermes: 生成 L4 记忆卡片 + L7 场景页 + 行业专属 Skill
  ↓
就绪。用户看到: "你的食品安全合规知识库已就绪，含 5 部法律、12 项国标、5 个场景"
```

### 4.2 冷启动状态机

| 阶段 | 状态 | 动作 |
|------|------|------|
| 1 | idle | 用户输入行业信息 |
| 2 | industry-detect | Hermes 识别行业，匹配 GB/T 4754 |
| 3 | yaml-generate | 生成 industry.yaml |
| 4 | skeleton-copy | 拷贝 FlowWiki 骨架 |
| 5 | raw-ingest | 抓取法律/标准入 raw/ |
| 6 | wiki-compile | 跑 ingest pipeline，生成 wiki/ |
| 7 | memory-generate | 生成 A-MEM 卡片 |
| 8 | scenarios-create | 创建 L7 场景页 |
| 9 | ready | 知识库就绪，通知用户 |

## 5. 行业适配器示例

### 5.1 大气溯源示例

```yaml
name: "大气溯源"
slug: "atmospheric-tracing"
gb_code: "M7461"
domain: "environmental"
subdomain: "atmospheric_tracing"
perspective: "monitoring_station"

raw_sources:
  laws:
    - 环境保护法
    - 大气污染防治法
    - 生态环境法典
  standards:
    - GB 3095-2012 环境空气质量标准
    - HJ 633-2012 空气质量指数技术规定
    - HJ 663-2013 环境空气质量评价技术规范
  datasets:
    - CNEMC 实时监测数据
    - 气象再分析数据
    - 排放清单

wiki_structure:
  concepts:
    - 气团后向轨迹
    - EKMA曲线
    - O3生成敏感性
    - PM2.5化学组分重构
  playbooks:
    - 溯源研判五步法
    - 市州级溯源工作流
    - 县域级溯源工作流
  comparisons:
    - HYSPLIT vs FLEXPART
    - WRF-Chem vs CMAQ

scenarios:
  - id: trace-source
    name: "溯源研判"
    trigger: "用户上传监测数据或描述污染过程"
    skills: [判据匹配, 区域传输分析, 源类指纹识别]
  - id: ekma-analysis
    name: "EKMA敏感性分析"
    trigger: "用户询问O3污染成因"

industry_skills:
  - name: "判据匹配"
    file: ".agents/skills/criteria-match/SKILL.md"
  - name: "O3敏感性诊断"
    file: ".agents/skills/o3-sensitivity/SKILL.md"
```

### 5.2 环评排污许可示例

```yaml
name: "环评与排污许可"
slug: "eia-permit"
gb_code: "M7481"
domain: "environmental"
subdomain: "eia_permit"
perspective: "review_agency"

raw_sources:
  laws:
    - 环境影响评价法
    - 排污许可管理条例
    - 建设项目环境保护管理条例
  standards:
    - HJ 2.1-2016 环境影响评价技术导则 总纲
    - HJ 942-2018 排污许可证申请与核发技术规范
  datasets:
    - 排污许可名录
    - 环评批复数据库
    - 排放标准库

wiki_structure:
  concepts:
    - 环境影响评价
    - 排污许可证
    - 达标排放
    - 总量控制
  playbooks:
    - 环评审批工作流
    - 排污许可证核发流程
    - 许可证后监管
  comparisons:
    - 环评 vs 排污许可
    - 报告书 vs 报告表 vs 登记表

scenarios:
  - id: eia-review
    name: "环评文件审查"
    trigger: "用户上传环评文件"
    skills: [合规审查, 标准匹配, 公众参与核查]
  - id: permit-analysis
    name: "排污许可证分析"
    trigger: "用户上传许可证或询问许可事项"
    skills: [许可证拆解, 达标判定, 变更评估]

industry_skills:
  - name: "合规审查"
    file: ".agents/skills/compliance-review/SKILL.md"
  - name: "许可证拆解"
    file: ".agents/skills/permit-analysis/SKILL.md"
```

## 6. 跨行业切换机制

### 6.1 切换流程

```
用户切换行业 → 读取新行业的 industry.yaml → 加载对应 raw/wiki 内容 → 切换 L7 场景 → 更新 Skill 索引 → 完成切换
```

### 6.2 数据隔离

- 每个行业的 raw/ wiki/ .memory/ 数据完全隔离
- 通过 slug 作为命名空间标识
- 检索时自动限定在当前行业范围内

## 7. 与 Hermes 的交互接口

### 7.1 Hermes → FlowWiki

| 接口 | 用途 |
|------|------|
| `create_wiki(industry_slug)` | 创建新行业知识库 |
| `ingest_raw(source_type, content)` | 入仓原始资料 |
| `compile_wiki()` | 编译 raw 到 wiki |
| `query_wiki(query)` | 查询 wiki 内容 |
| `add_memory_card(content)` | 添加记忆卡片 |
| `execute_scenario(scenario_id)` | 执行场景 |

### 7.2 FlowWiki → Hermes

| 接口 | 用途 |
|------|------|
| `web_search(query)` | Web 搜索法律标准 |
| `industry_identify(text)` | 行业识别 |
| `generate_yaml(industry_info)` | 生成 industry.yaml |
| `send_notification(message)` | 向用户发送通知 |

## 8. 关键技术实现

### 8.1 industry.yaml 解析

```python
import yaml

def load_industry_config(slug: str) -> dict:
    with open(f"storage/{slug}/industry.yaml", "r") as f:
        return yaml.safe_load(f)
```

### 8.2 动态 Skill 加载

```python
def load_industry_skills(slug: str) -> list:
    config = load_industry_config(slug)
    skills = []
    for skill in config.get("industry_skills", []):
        with open(skill["file"], "r") as f:
            skills.append({"name": skill["name"], "content": f.read()})
    return skills
```

### 8.3 行业路由

```python
def route_to_industry(user_input: str) -> str:
    industry_info = hermes.industry_identify(user_input)
    return industry_info["slug"]
```

## 9. 验收标准

- industry.yaml 规范完整，可用于 4 个现有知识库的适配
- 骨肉分离设计文档完备，L1-L7 各层职责清晰
- Hermes 冷启动流程可执行，新行业 30 秒内部署完成
- 跨行业切换功能正常，数据隔离有效
- spec/hermes-integration.md 写入 FlowWiki 全局 spec