# FlowWiki 案例集

## 案例 1：大气溯源知识库

**行业**：环境监测
**规模**：1000+ 条判据，160+ 篇微信原文，800+ 文件
**场景**：溯源研判、EKMA 分析、区域传输

### 改造前

- 缺乏 SpecCoding 变更治理
- 无 ACE 反思循环
- 无 A-MEM 卡片
- 仅 WorkBuddy 可用

### 改造后（FlowWiki 标准版）

- ✅ SpecCoding 七阶段变更治理
- ✅ ACE 反思循环
- ✅ A-MEM 卡片记忆
- ✅ 多 agent 兼容（Claude Code/Codex/WorkBuddy）
- ✅ 双索引同步
- ✅ 行业专属 Skill（判据匹配、O3 敏感性诊断等）

## 案例 2：环评与排污许可知识库

**行业**：环保审批
**规模**：38 份原始资料，30+ wiki 页面
**场景**：环评审查、许可证分析、两证衔接

### 改造前

- 已有 raw/ + wiki/ + 4 操作 skill
- 有 CLAUDE.md + AGENTS.md
- 缺失：SCHEMA.md、70_Prompt库/、.memory/、00_首页/

### 改造后（FlowWiki 标准版）

- ✅ 完整 SCHEMA.md 知识库宪法
- ✅ 70_Prompt库/ Prompt 统一管理
- ✅ .memory/ A-MEM 卡片层
- ✅ 00_首页/ 人类 UX 入口
- ✅ storage/eia-permit/industry.yaml 行业适配器
- ✅ 4 大场景页（环评审查/许可证分析/两证衔接/执法检查）
- ✅ 6 个行业专属 Skill

### 验证结果

```bash
$ python3 _scripts/ingest_pipeline.py
INFO:__main__:Starting EIA-permit ingest pipeline...
INFO:__main__:Found 37 raw files
INFO:__main__:Industry: 环评与排污许可
INFO:__main__:Updated wiki/index.md
INFO:__main__:Ingest pipeline completed
```

## 案例 3：执法督察评查知识库

**行业**：行政执法
**规模**：案卷评查标准、典型案例库
**场景**：案卷评查、程序合法性检查

### FlowWiki 改造

- ✅ 程序审查 Skill
- ✅ 证据审核 Skill
- ✅ 法律适用检查 Skill
- ✅ 步骤验证 Skill
- ✅ 时限计算 Skill
- ✅ 文书规范 Skill

## 案例 4：企业合规 AI 管家

**行业**：企业合规
**规模**：合规风险清单、政策更新库
**场景**：合规清单生成、政策追踪

### FlowWiki 改造

- ✅ 法规检索 Skill
- ✅ 风险识别 Skill
- ✅ 清单编制 Skill
- ✅ 政策监控 Skill
- ✅ 影响分析 Skill
- ✅ 合规建议 Skill

## 快速复制

基于以上案例，你可以快速复制到任意行业：

1. 编写 `storage/{industry}/industry.yaml`
2. 拷贝 FlowWiki 骨架
3. 入仓行业资料
4. 运行 ingest
5. 验证场景

详见 [getting-started.md](./getting-started.md)。