# AGENTS.md — FlowWiki 多 Agent 架构

## 概述

FlowWiki 采用多 Agent 协作架构，每个 Agent 负责特定功能，通过 CLAUDE.md 协调。

## Agent 列表

### 1. Generator
- **职责**：根据用户提问和知识库内容生成回答
- **输入**：用户问题、wiki 索引、raw 证据
- **输出**：初步回答
- **约束**：回答必须引用 raw/ 原始证据

### 2. Reflector
- **职责**：审查 Generator 输出的准确性和完整性
- **输入**：Generator 输出、raw 证据、wiki 知识
- **输出**：审查结果（通过/拒绝/修改建议）
- **约束**：严格验证证据链，拒绝无证据内容

### 3. Curator
- **职责**：最终决策是否将回答存入 wiki/
- **输入**：Reflector 审查结果、Generator 输出
- **输出**：决策（存入/不存入/修改后存入）
- **约束**：人类可 override 决策

### 4. Ingestor
- **职责**：将 raw/ 资料编译到 wiki/
- **输入**：raw/ 新文件
- **输出**：wiki/ 新页面
- **约束**：遵循 wiki/ 页面模板

### 5. Researcher
- **职责**：深度研究任务，跨知识库检索
- **输入**：研究问题
- **输出**：研究报告
- **约束**：多来源验证，引用权威资料

### 6. Linter
- **职责**：检查知识库健康度
- **输入**：知识库状态
- **输出**：健康报告（问题清单、修复建议）
- **约束**：定期自动运行，发现问题及时通知

### 7. MemoryManager
- **职责**：管理 A-MEM 卡片库
- **输入**：新回答、新知识
- **输出**：ZK 卡片
- **约束**：遵循 Zettelkasten 格式，自动去重

### 8. SkillManager
- **职责**：管理和加载 Skill
- **输入**：行业配置、Skill 定义
- **输出**：可用 Skill 列表
- **约束**：动态加载，按需卸载

## Agent 协作流程

### ACE 反思循环
```
Generator → Reflector → Curator
    ↓           ↓           ↓
  生成回答    审查准确性    最终决策
    ↓           ↓           ↓
   raw证据     证据验证     存入wiki
```

### 知识入仓流程
```
人类入仓 → Ingestor 编译 → ACE 审查 → wiki/ 写入 → MemoryManager 生成卡片
```

### 查询回答流程
```
用户提问 → Generator 生成 → Reflector 审查 → Curator 决策 → 回答用户 → MemoryManager 生成卡片
```

## Agent 通信协议

### 消息格式
```json
{
  "agent": "{agent_name}",
  "action": "{action}",
  "payload": {...},
  "timestamp": "{ISO 8601}",
  "trace_id": "{UUID}"
}
```

### 消息类型
- **request**：请求执行任务
- **response**：任务执行结果
- **notification**：状态通知
- **error**：错误信息

## Agent 扩展

### 新增 Agent
1. 创建 `.agents/agents/{agent_name}.md`
2. 定义 Agent 职责、输入输出、约束
3. 在 AGENTS.md 中注册
4. 在 CLAUDE.md 中添加调用逻辑

### 行业专属 Agent
根据行业需求，在 `.agents/agents/{industry_slug}/` 目录下创建行业专属 Agent。

## 监控与日志

- 每个 Agent 独立日志文件
- 统一 trace_id 追踪跨 Agent 调用
- 定期健康检查报告