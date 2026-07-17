# Hermes AI 框架与 FlowWiki 集成方案

## 1. 愿景

FlowWiki 作为 Hermes AI 框架的知识引擎层，实现：
- 用户只开发前端 UI，Hermes 作为 AI 基座
- 通过了解用户所属行业，自动按照 FlowWiki 创建完善知识库
- 实现"越用越懂"——任务→知识→Skill 三元组复利

## 2. 核心设计：骨肉分离

### 2.1 原则

```
骨架（L2-L6 + _scripts/_templates/SCHEMA）— 所有行业完全相同，零修改
  ↓ 由 industry.yaml 驱动 ↓
肉（L1 raw/wiki/00_首页/.memory + L7 场景）— 每个行业不同内容
```

### 2.2 架构分层职责

| 层级 | 职责 | 是否通用 |
|------|------|---------|
| L1 知识编译层 | raw/（只读证据）+ wiki/（AI 编译）+ 00_首页/（人类 UX） | ❌ 行业相关 |
| L2 检索增强层 | BM25→nano-graphrag→LightRAG 自适应 | ✅ 通用 |
| L3 Spec-Driven 层 | spec/ 全局设计 + openspec/changes/ 单任务变更 | ✅ 通用 |
| L4 Agent 记忆层 | A-MEM 卡片（Zettelkasten）+ ACE 反思循环 | ✅ 通用 |
| L5 Skill 化层 | 4 操作 skill + 高频任务自动抽象 | ✅ 通用 + 行业专属 |
| L6 多 agent 接手层 | CLAUDE.md + AGENTS.md 双 bootstrap | ✅ 通用 |
| L7 场景层 | 业务外壳，可插拔 | ❌ 行业相关 |

## 3. 行业适配器：industry.yaml

### 3.1 文件位置

```
storage/{industry_slug}/industry.yaml
```

### 3.2 核心字段

| 字段 | 说明 |
|------|------|
| `name/slug/gb_code/domain/subdomain/perspective` | 行业身份标识 |
| `raw_sources.laws/standards/datasets` | 必须入仓的行业资料清单 |
| `wiki_structure.concepts/playbooks/comparisons` | 行业核心知识结构 |
| `scenarios` | L7 场景定义 + trigger + skills |
| `industry_skills` | 行业专属 Skill 路径 |

### 3.3 四个现有行业的适配器

#### 3.3.1 大气溯源

```yaml
name: "大气溯源"
slug: "atmospheric-tracing"
gb_code: "M7461"
domain: "environmental"
subdomain: "atmospheric_tracing"
perspective: "monitoring_station"

raw_sources:
  laws: [环境保护法, 大气污染防治法, 生态环境法典]
  standards: [GB 3095-2012, HJ 633-2012, HJ 663-2013]
  datasets: [CNEMC 实时监测数据, 气象再分析数据, 排放清单]

wiki_structure:
  concepts: [气团后向轨迹, EKMA曲线, O3生成敏感性, PM2.5化学组分重构]
  playbooks: [溯源研判五步法, 市州级溯源工作流, 县域级溯源工作流]
  comparisons: [HYSPLIT vs FLEXPART, WRF-Chem vs CMAQ]

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

#### 3.3.2 执法督察评查

```yaml
name: "执法督察评查"
slug: "law-enforcement-review"
gb_code: "M7821"
domain: "legal"
subdomain: "law_enforcement"
perspective: "regulatory"

raw_sources:
  laws: [行政处罚法, 行政强制法, 生态环境保护综合行政执法事项指导目录]
  standards: [生态环境行政处罚办法, 环境行政执法文书制作规范]
  datasets: [案卷评查标准, 典型案例库, 执法流程模板]

wiki_structure:
  concepts: [程序合法性, 证据链, 自由裁量权, 听证程序]
  playbooks: [案卷评查工作流, 执法全过程记录流程, 重大案件集体讨论]
  comparisons: [一般程序 vs 简易程序, 行政复议 vs 行政诉讼]

scenarios:
  - id: case-review
    name: "案卷评查"
    trigger: "用户上传案卷或询问评查标准"
    skills: [程序审查, 证据审核, 法律适用检查]
  - id: procedure-check
    name: "程序合法性检查"
    trigger: "用户询问执法程序"
    skills: [步骤验证, 时限计算, 文书规范]

industry_skills:
  - name: "程序审查"
    file: ".agents/skills/procedure-review/SKILL.md"
  - name: "证据审核"
    file: ".agents/skills/evidence-review/SKILL.md"
```

#### 3.3.3 环评与排污许可

```yaml
name: "环评与排污许可"
slug: "eia-permit"
gb_code: "M7481"
domain: "environmental"
subdomain: "eia_permit"
perspective: "review_agency"

raw_sources:
  laws: [环境影响评价法, 排污许可管理条例, 建设项目环境保护管理条例]
  standards: [HJ 2.1-2016, HJ 942-2018]
  datasets: [排污许可名录, 环评批复数据库, 排放标准库]

wiki_structure:
  concepts: [环境影响评价, 排污许可证, 达标排放, 总量控制]
  playbooks: [环评审批工作流, 排污许可证核发流程, 许可证后监管]
  comparisons: [环评 vs 排污许可, 报告书 vs 报告表 vs 登记表]

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

#### 3.3.4 企业合规AI管家

```yaml
name: "企业合规AI管家"
slug: "enterprise-compliance"
gb_code: "L7299"
domain: "business"
subdomain: "compliance"
perspective: "enterprise"

raw_sources:
  laws: [公司法, 劳动合同法, 安全生产法, 环境保护法]
  standards: [ISO 19600, GB/T 35770]
  datasets: [合规风险清单, 政策更新库, 行业合规标准]

wiki_structure:
  concepts: [合规管理体系, 风险评估, 合规审计, 合规培训]
  playbooks: [合规清单生成流程, 合规风险评估工作流, 合规检查程序]
  comparisons: [合规 vs 内控, ISO 19600 vs GB/T 35770]

scenarios:
  - id: compliance-checklist
    name: "合规清单生成"
    trigger: "用户询问企业合规要求"
    skills: [法规检索, 风险识别, 清单编制]
  - id: policy-tracking
    name: "政策追踪"
    trigger: "用户询问政策更新"
    skills: [政策监控, 影响分析, 合规建议]

industry_skills:
  - name: "法规检索"
    file: ".agents/skills/regulation-search/SKILL.md"
  - name: "风险识别"
    file: ".agents/skills/risk-identification/SKILL.md"
```

## 4. 「4+1」部署模式

```
FlowWiki 标准版（骨架，git 仓库）
├── storage/
│   ├── atmospheric-tracing/industry.yaml
│   ├── law-enforcement-review/industry.yaml
│   ├── eia-permit/industry.yaml
│   ├── enterprise-compliance/industry.yaml
│   └── {new-industry}/industry.yaml
├── _scripts/
├── _templates/
├── SCHEMA.md
├── config.toml
├── raw/
├── wiki/
├── 00_首页/
├── .memory/
├── 70_Prompt库/
└── .agents/
    ├── skills/
    ├── CLAUDE.md
    └── AGENTS.md
```

## 5. Hermes 冷启动流程

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

## 6. 跨行业切换机制

```
用户切换行业 → 读取新行业的 industry.yaml → 加载对应 raw/wiki 内容 → 切换 L7 场景 → 更新 Skill 索引 → 完成切换
```

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

## 8. "越用越懂"五步闭环

```
用户提问 → Hermes 行业路由 → 读 wiki/index.md + 加载相关页 → 回答用户 → 答案回存 wiki/ + 生成 ZK 卡片 → 高频任务抽象为 skill → 下次同类任务 O(1) 调用
```

## 9. 推进策略

1. **试点改造**：选环评库做试点（差距最小，只缺 5/11）
2. **验证机制**：验证 industry.yaml 机制和骨肉分离设计
3. **推广复制**：推广到大气溯源、执法督察评查、企业合规AI管家
4. **自动冷启动**：实现新行业 Hermes 自动建库

## 10. 验收标准

- industry.yaml 规范完整，可用于 4 个现有知识库的适配
- 骨肉分离设计文档完备，L1-L7 各层职责清晰
- Hermes 冷启动流程可执行，新行业 30 秒内部署完成
- 跨行业切换功能正常，数据隔离有效
- spec/hermes-integration.md 写入 FlowWiki 全局 spec