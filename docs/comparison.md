# FlowWiki 与现有方法对比

## 对比维度

| 维度 | Karpathy LLM Wiki | TRAE Work | 传统 RAG | **FlowWiki** |
|------|------------------|-----------|---------|------------|
| 知识复利 | ✅ | ❌ | ❌ | ✅ |
| 人类 UX | ❌ | ✅ | ❌ | ✅ 双索引 |
| AI 接手友好 | 🟡 仅 Claude | ❌ | ❌ | ✅ 5 家 agent |
| 防幻觉 | ❌ lint 只扫结构 | N/A | ❌ | ✅ ACE 三 agent |
| 跨会话记忆 | ❌ | ❌ | 🟡（向量库） | ✅ A-MEM 卡片 |
| 变更追溯 | ❌ | ❌ | ❌ | ✅ SpecCoding |
| 业务可插拔 | ❌ | ❌ | ❌ | ✅ L7 场景外壳 |
| 规模上限 | 200 页 | 无限（但人工） | 万页 | 自适应 |

## 详细对比

### vs Karpathy LLM Wiki

**FlowWiki 增强：**
- ACE 反思循环（Karpathy 只有单 agent 生成）
- A-MEM 卡片记忆（Karpathy 无记忆层）
- 双索引（Karpathy 只有机器索引）
- SpecCoding 变更治理（Karpathy 无变更管理）
- 多 agent 兼容（Karpathy 仅 Claude Code）
- L7 场景可插拔（Karpathy 业务硬编码）

### vs TRAE Work

**FlowWiki 增强：**
- 知识复利（TRAE 知识不复利）
- AI 自动编译（TRAE 人工维护）
- 跨会话记忆（TRAE 无记忆层）
- 多 agent 兼容（TRAE AI 无法接手）

### vs 传统 RAG

**FlowWiki 增强：**
- 知识积累（RAG 每次重算）
- 证据链完整（RAG 不追溯来源）
- 防幻觉（RAG 无审查机制）
- 人类 UX（RAG 无人类入口）

## 适用场景

### 适合 FlowWiki

- 个人/团队知识库（100-10000 页）
- AI agent 长期维护的专业领域知识库
- 多 agent 接手的协作型知识库
- 业务领域可插拔的多场景知识库

### 不适合 FlowWiki

- 单次查询的临时知识需求（用 RAG）
- 必须用云服务的多租户 SaaS（FlowWiki 本地优先）
- 必须图形界面（FlowWiki 依赖 Obsidian 等第三方）
- 万页以上且需秒级查询（用专业向量数据库）