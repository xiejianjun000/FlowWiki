# FlowWiki 方法论

## 核心思想

FlowWiki 的核心理念是**知识复利**——让 AI 编译的知识像复利一样积累，让人类像走工作流一样使用，让多 agent 像接力一样接手。

## 三层架构

### L1 知识编译层

```
raw/（只读证据）→ AI 编译 → wiki/（结构化知识）
```

- **raw/**：人类维护，只读，保证证据保真
- **wiki/**：AI 维护，结构化，支持检索

### L2-L6 通用骨架

| 层级 | 功能 | 关键组件 |
|------|------|---------|
| L2 检索增强 | 自适应检索 | BM25→nano-graphrag→LightRAG |
| L3 Spec-Driven | 变更治理 | spec/ + openspec/changes/ |
| L4 Agent 记忆 | 跨会话记忆 | A-MEM 卡片 + ACE 反思循环 |
| L5 Skill 化 | 能力复利 | 4 操作 skill + 高频任务抽象 |
| L6 多 agent | 平台兼容 | CLAUDE.md + AGENTS.md |

### L7 场景层

可插拔的业务外壳，每个行业独立：
- 根因分析场景
- 执法办案场景
- 证照管理场景
- 企业合规场景
- ...任意行业

## 关键机制

### ACE 反思循环

```
Generator → Reflector → Curator
    ↓           ↓           ↓
  生成回答    审查准确性    最终决策
```

- **Generator**：根据 raw 生成 wiki 内容
- **Reflector**：批判性审查，找矛盾/幻觉/过时
- **Curator**：决策是否存入 wiki

### A-MEM 卡片

每个 raw 生成 Zettelkasten 卡片：
- 跨会话可读
- 自动关联
- 支持追溯

### 双索引

| 索引 | 受众 | 形态 |
|------|------|------|
| wiki/index.md | AI agent | 紧凑扁平 |
| 00_首页/ | 人类 | TRAE 风格 MOC |

### 任务→知识→Skill 三元组

```
任务层 → 知识层 → Skill 层
   ↑                    │
   └──── O(1) 调用 ─────┘
```

高频任务自动抽象为 O(1) 调用的 skill。

## 设计原则

1. **物理分离**：raw 只读 / wiki AI 写 / spec 人写
2. **极简优先**：默认零依赖，纯 Markdown + git
3. **双侧友好**：AI 走 index，人类走 6 板块
4. **工作流闭环**：每个任务都走五步，不留孤立操作
5. **防止幻觉永久化**：ACE 三 agent 制约 + 矛盾显式标注
6. **复利飞轮**：raw → wiki → skill → 自动调用 → 新任务 → ...