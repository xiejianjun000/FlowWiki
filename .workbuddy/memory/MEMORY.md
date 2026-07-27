# FlowWiki 项目记忆

## 项目概述
FlowWiki 是一个 AI 与人类协同复利的知识库方法论，融合 Karpathy LLM Wiki、TRAE Work、ACE 反思循环、A-MEM 卡片记忆和 SpecCoding 七阶段。

## 7 层架构
- L1 知识编译层：raw/ + wiki/ + 00_首页/
- L2 检索增强层：config.toml（BM25 → nano-graphrag → LightRAG 自适应）
- L3 Spec-Driven 层：spec/ + openspec/
- L4 Agent 记忆层：.memory/（zettelkasten + episodic + conflict + ace）
- L5 Skill 化层：.agents/skills/ + .claude/skills/（双格式部署）
- L6 多 agent 接手层：CLAUDE.md + AGENTS.md + CODEX.md + WORKBUDDY.md
- L7 场景层：00_首页/03_实战场景/（7 场景可插拔）

## 关键约定
- raw/ 只读，AI 绝不修改
- wiki/ 写入必须经过 ACE 反思循环
- 所有知识必须可追溯到 raw/ 原始证据
- .agents/skills/ 和 .claude/skills/ 必须保持同步
- config.toml 同时存在于根目录和 .llm-wiki/

## 🚨 核心定位：方法论，不是项目
- **FlowWiki 是 Obsidian 上运行的方法论**，不是独立应用
- 首要目标：让 Obsidian 知识库按 FlowWiki 方法组织、验证、生长
- **图谱可视化 = Obsidian 原生 graph view + FlowWiki 配置**，不自己造渲染引擎
- 所有脚本的产出物必须 Obsidian 可读（.md 文件、Wikilink、Dataview 查询）
- 不做独立 Web 界面、不做独立图表引擎、不做独立数据库
- 判断标准："这个功能能在 Obsidian 里用吗？"如果答案是"不能"，就是跑偏

## 🚨 知识库质量：Hermes 核验标准
- 结构完备 ≠ 内容可达。frontmatter 有三空字段（触发词/适用场景/关联法条）→ 文件存在但 LLM 找不到
- 数值红线：可路由率 ≥ 85% 才及格
- 知识库文件绝对不能损坏——修改 raw 文件时必须保留原 frontmatter、只替换正文
- 运营看板待办项必须逐项关闭并标记日期

## 执法督察评查知识库保护规则
- 这是一个真实存在的 Obsidian vault，包含155篇生态环境执法领域的专业文档
- 任何修改必须保留原有的 frontmatter 结构
- 删除或覆盖文件前必须先备份
- 源文件真实路径：/Users/mac/执法督察评查知识库/ 和 /Users/mac/Desktop/FlowWiki/raw/enforcement-review/

## 🚨 路径铁律（2026-07-18 教训）
- **FlowWiki 仓库** = `/Users/mac/Desktop/FlowWiki/`（方法论 + 参考实现）
- **用户知识库** = `/Users/mac/执法督察评查知识库/`（真实 Obsidian vault，155+ 篇）
- 两个路径完全不同，绝不混淆
- 任何涉及"用户知识库"的操作，第一步必须是 `ls /Users/mac/执法督察评查知识库/` 确认当前状态
- 在反驳用户之前，先确认自己看的是正确的东西

## 里程碑状态（2026-07-18 更新）
- M0-M7 全部标记完成
- v0.2.0 发布：MCP Server（5 工具）+ Docker 部署 + 竞品对比表 + GitHub Topics
- 文件统计：27 skill（双部署）、7 场景、7 行业适配器、7 模板、13 脚本
- 新增文件：Dockerfile, docker-compose.yml, .dockerignore, requirements.txt, .mcp.json, docs/mcp-integration.md, _scripts/mcp_server.py

## 里程碑状态（2026-07-23 更新）
- M0-M7 全部标记完成
- v0.5.0 发布：OKF 兼容层（okf_export.py + okf_import.py）+ VERIFY-BEFORE-WRITE 独立工具（verify_before_write.py）
- 文件统计：27 skill（双部署）、7 场景、7 行业适配器、7 模板、16 脚本
- 新增脚本：okf_export.py, okf_import.py, verify_before_write.py
- OKF 对齐 atomicstrata/llm-wiki-compiler v1.1.0 + Google Cloud 标准

## 开发时间线
- 2026-07-17 上午：M0-M7 骨架搭建（约 10:00-10:53）
- 2026-07-17 下午：gap 补齐（16:26-16:40，由 WorkBuddy/Claw 执行）
- 2026-07-17 下午：git init + 端到端测试 + GitHub 发布（16:44-16:56）
- 2026-07-18 凌晨：竞品监控 + 差距自动修复 → v0.2.0（MCP Server + Docker + README 更新）

## GitHub 仓库
- URL: https://github.com/xiejianjun000/FlowWiki
- 可见性：Public
- 账号：xiejianjun000
