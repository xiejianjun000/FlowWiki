# Karpathy 提出了 LLM Wiki 的构想，我把 6 个致命缺口全补上了——FlowWiki 开源首发

> 让知识像代码一样编译、缓存、复利增长。不是又一个 RAG，而是一个带防幻觉机制的 AI 知识库编译器。

---

## 一、那个让我睡不着的问题

2025 年，Andrej Karpathy 发了条简洁到令人不安的推：

> **Obsidian 是 IDE，LLM 是程序员，Wiki 是代码库。**

他提了一个类比——知识不应该被 AI 反复重新推导，而应该像代码一样**编译一次，随用随取**。三层架构：`raw/`（不可变源文件）→ `wiki/`（LLM 编译维护）→ `schema/`（协同演进配置）。四个操作：`ingest` → `query` → `lint` → `research`。

这个概念点燃了整个社区。GitHub 上很快涌现了 30+ 个 LLM Wiki 项目，累计 30,000+ Stars。大家都在用 AI 构建"自己的维基百科"。

但我盯着这个架构看了三个晚上，发现**6 个致命缺口**。

先想一个问题：如果你让 AI 帮你维护一个 500 页的知识库，一年之后，你敢信里面的任何一句话吗？

我不敢。

因为 LLM Wiki 的原始设计，在这个问题面前完全是裸奔的。

---

## 二、Karpathy 原始构想的 6 个致命缺口

| # | 缺口 | 后果 |
|---|------|------|
| 1 | **无防幻觉机制** | AI 生成的摘要可能包含事实错误，错误知识永久化，越积越深 |
| 2 | **无跨会话记忆** | 每次 ingest 独立执行，不记得上次做了什么，重复劳动 |
| 3 | **无人类入口** | wiki/ 是扁平文件列表，人类找不到东西，技术好但不好用 |
| 4 | **知识不复利到能力** | 高频任务每次都从零开始，效率不随知识增长而提升 |
| 5 | **变更不可追溯** | 改了什么、为什么改，无记录，知识库变成黑箱 |
| 6 | **单平台绑定** | 绑死 Claude Code，换 agent 就丢知识库 |

这四个操作很美，但缺了最关键的工程基础设施。就像有人给了你一套极其优雅的编码范式，但没给你编译器、没给你测试框架、没给你 CI/CD。

所以我花了几个月，把这 6 个缺口一个一个填上了。

---

## 三、FlowWiki 是什么

一句话：**FlowWiki 是站在 Karpathy LLM Wiki 肩膀上的增强版知识库编译器，融合了 AI 协作领域六个最前沿方法论。**

我把 FlowWiki 架构成 7 层：

```
┌─────────────────────────────────────────────────────┐
│ L7 场景层：7 个通用场景，业务外壳可插拔                    │
│    根因分析｜合规审查｜证照管理｜企业合规｜...               │
├─────────────────────────────────────────────────────┤
│ L6 多 Agent 层：CLAUDE.md + AGENTS.md + CODEX.md     │
│    5 家 agent 通吃，换工具不丢知识库                      │
├─────────────────────────────────────────────────────┤
│ L5 Skill 层：高频任务自动抽象为 O(1) 调用的 Skill         │
├─────────────────────────────────────────────────────┤
│ L4 Agent 记忆层 ★ 独有                                 │
│    A-MEM Zettelkasten 卡片 + ACE 三 agent 防幻觉       │
├─────────────────────────────────────────────────────┤
│ L3 Spec-Driven 层：每个变更走 proposal→impl→archive     │
├─────────────────────────────────────────────────────┤
│ L2 检索增强层：BM25 → nano-graphrag → LightRAG 自适应   │
├─────────────────────────────────────────────────────┤
│ L1 知识编译层：raw(只读) + wiki(AI编译) + 首页(人类入口)   │
└─────────────────────────────────────────────────────┘
```

Karpathy 的核心骨架（L1）我没有改，那是这个范式的灵魂。我在上面盖了 6 层工程基础设施——每一层对应一个原始缺口。

---

## 四、三个让你重新考虑"AI 写知识库"这事的创新

### 创新一：ACE 反思循环——错误知识进不了 wiki

这是 FlowWiki 最核心的防幻觉机制。

传统 ingest 流程：AI 读 raw → 写 wiki。如果 AI 理解错了、幻觉了、断章取义了，错误就永久写进了知识库。

FlowWiki 的做法：每次 ingest**必须经过三 agent 交叉审查**：

```
┌──────────────┐
│  Generator   │ ← 根据 raw 生成摘要/概念/操作手册
└──────┬───────┘
       ▼
┌──────────────┐
│  Reflector   │ ← 批判：找矛盾、幻觉、过时信息
└──────┬───────┘
       ▼
┌──────────────┐
│   Curator    │ ← 决策：放行入 wiki / 标"待核" / 触发冲突目录
└──────────────┘
```

原理来自 LangChain 的 ACE 框架（NeurIPS 2025 收录），我把它直接嵌入了 ingest 管道。不是"生成完跑个 lint 检查格式"，而是**三 agent 从不同角度审视同一段内容**——一个负责生成、一个负责挑刺、一个负责裁决。

Karpathy 的 lint 只扫结构不扫内容。ACE 扫内容。

### 创新二：A-MEM Zettelkasten 卡片——跨会话不丢上下文

你有没有过这种体验：今天让 AI 帮你分析了一份文档，下周要追问，AI 完全不记得了？

传统 LLM Wiki 的 ingest 是单次操作——生成 wiki 页后就结束，不留下任何过程记录。下次新开一个会话，AI 不知道上周 ingest 了什么、为什么那么写、有什么争议。

FlowWiki 的 A-MEM 卡片借鉴了 A-MEM 论文的 Zettelkasten 方法：每次 ingest 自动生成一张**记忆卡片**，记录：

- 原始证据（引用 raw/ 中的具体段落）
- 生成结果（wiki/ 里写了什么）
- 关键论点和推理链
- 与前序卡片的关联（`related` 字段）

这些卡片以 Markdown 文件形式存在 `.memory/zettelkasten/` 目录下，零数据库依赖。新会话的 AI 可以直接读取最近的卡片，恢复对知识库"记忆"。

### 创新三：任务 → 知识 → Skill 三元组——知识的复利不止于静态存储

Karpathy 的架构是两层：raw → wiki。知识在 wiki 里躺着，等着下次被 query 检索。

但"复利"不该只停留在"找到信息更快"这个层面。真正的复利是：**知识不仅要能查，还要能自动变成能力。**

FlowWiki 引入了第三层：**Skill 层**。

当一个操作在项目中被执行了 3 次以上，它就不再是"每次从头做的任务"，而是被抽象成一个 Skill——一个可被 agent 直接调用的 O(1) 操作。比如：

- 第一次做"判据匹配"：人一步步告诉 AI 怎么做，花了 20 分钟
- 第二次：AI 识别到同类任务，但仍然需要确认流程
- 第三次：AI 自动调用 `criteria-matching` skill，5 秒完成

这就是知识的复利飞轮：

```
raw → wiki → skill → 自动调用 → 新任务 → 新 raw → wiki 增厚 → skill 增多 → ...
```

---

## 五、坦诚地比一比：FlowWiki vs 市面上的"AI 知识库"

我不是在做一个比谁都强的项目——市面上有 35+ 个 LLM Wiki 项目和无数 AI 知识库产品。**FlowWiki 的差异化不在于"做得更多"，而在于"补了其他人没补的"。**

### vs 竞品（GitHub 项目维度）

| 能力 | FlowWiki | llm-wiki-agent | claude-obsidian | llm-wiki-compiler | synthadoc |
|------|:---:|:---:|:---:|:---:|:---:|
| 防幻觉机制 | ★ ACE 三 agent | ⚠️ 矛盾标记 | ❌ | ❌ | 预处理净化 |
| 跨会话记忆 | ★ A-MEM 卡片 | ❌ | Hot Cache | ❌ | ❌ |
| 多 Agent 兼容 | ★ 5 家 | 3 家 | 仅 Claude | 仅 Claude | 3 家 |
| 人类 UX | ★ 双索引 | ❌ | Obsidian | 桌面 GUI | Web UI |
| 知识复利 → 能力 | ★ Skill 化 | ❌ | ❌ | ❌ | ❌ |
| 变更追溯 | ★ SpecCoding | ❌ | ❌ | ❌ | ❌ |
| 自适应检索 | ★ 三档切换 | ❌ | 混合 | BM25 | 图谱 |

**FlowWiki 是目前唯一同时在防幻觉 + 跨会话记忆 + 知识复利到能力 + 多 Agent + 变更追溯这 5 个维度上补齐的 LLM Wiki 项目。**

公平地说，claude-obsidian 的 Obsidian 原生集成体验更强，llm-wiki-compiler 的桌面 GUI 更直观。如果你只需要一个 Claude 专用+Obsidian 内用的知识库，它们可能是更好的选择。

但如果你需要**跨 agent、长周期维护、错误知识能被拦截**的知识库——FlowWiki 是目前唯一的选择。

---

## 六、一个真实场景演示

假设你是一个技术团队的负责人，团队用飞书记录决策、用 Git 管理代码、用多个 AI 编程助手辅助开发。现在你需要建立一个团队知识库。

**用传统 RAG 的做法**：上传所有文档 → 每次查询靠模型理解 → 回答不一致、无法追溯来源 → 新增内容没有质量保障 → 3 个月后开始出现相互矛盾的答案。

**用 FlowWiki 的做法**：

```bash
# 1. 克隆模板
git clone https://github.com/xiejianjun000/FlowWiki.git team-wiki

# 2. 投入第一批原始资料
#    raw/ 目录放只读源文件（飞书导出、会议纪要、技术文档）
cp ~/docs/*.md team-wiki/raw/docs/

# 3. 让 AI 编译入库（任何支持的 agent 都可以）
#    在 Claude Code / Codex / WorkBuddy 中：
> 请按 ingest skill 把 raw/docs/ 下的文件入库

# AI 自动完成：
#   → Generator 生成摘要和知识卡片
#   → Reflector 审查（发现矛盾会标记）
#   → Curator 决策（通过 / 待核 / 冲突）
#   → 写入 wiki/ + 生成 A-MEM 卡片 + 更新双索引
```

`ingest` 操作的完整效果：

| 产出物 | 路径 | 作用 |
|--------|------|------|
| 知识页面 | `wiki/concepts/` `wiki/playbooks/` | 编译后的结构化知识 |
| 人类入口 | `00_首页/01_知识图谱/` | 适合人类浏览的 MOC 导航页 |
| 机器索引 | `wiki/index.md` | AI agent 的快速导航（1000 页只占 50KB） |
| 记忆卡片 | `.memory/zettelkasten/` | 跨会话上下文的持久化记录 |
| 审查日志 | `.memory/ace/` | ACE 三 agent 的审查记录，可追溯每个决策 |

---

## 七、技术栈与设计哲学

技术栈极简到令人发指：

| 层 | 技术 |
|----|------|
| 知识格式 | Markdown + YAML frontmatter |
| 检索 | BM25 + CJK 分词 → nano-graphrag → LightRAG（按规模自适应） |
| 记忆 | A-MEM Zettelkasten 卡片（纯文件系统） |
| 防幻觉 | ACE Generator→Reflector→Curator 三 agent |
| 变更管理 | SpecCoding 七阶段 + OpenSpec |
| 外部依赖 | **仅 PyYAML** |

设计哲学六条：

1. **物理分离原则**：raw 只读 / wiki AI 写 / spec 人写，三者不交叉
2. **极简优先**：默认零数据库依赖，纯 Markdown + git
3. **双侧友好**：AI 走 index.md，人类走 6 板块，互不干扰
4. **工作流闭环**：每个任务走"接任务 → spec → 执行 → archive → 复利"
5. **防止幻觉永久化**：ACE 三 agent 制约 + 矛盾显式标注
6. **复利飞轮**：raw → wiki → skill → 自动调用 → 更多 raw

---

## 八、坦诚说说当前的不足

任何首发项目都应该坦诚说清楚"现在不擅长什么"。FlowWiki 目前：

1. **没有 Web UI**。人类入口依赖 Obsidian 等第三方编辑器打开 Markdown。如果你需要开箱即用的可视化界面，FlowWiki 目前不适合。
2. **检索不是秒级**。BM25 在小规模下够用，但万页以上需要启用 LightRAG，而 LightRAG 需要额外配置。
3. **社区零起步**。这是首发文章，Star 数、贡献者、issue 讨论都从零开始。
4. **行业适配器只做了结构**。7 个场景的 `industry.yaml` 都有，但具体行业的法规条文、判据库还需要你自己填充。

---

## 九、后续计划

- **Phase 1（短期）**：完善 7 个场景的实例数据，让新用户 clone 后就有可 run 的 demo
- **Phase 2（中期）**：接入 Quartz v4 发布静态站，让知识库可以一键部署为公开网站
- **Phase 3（长期）**：支持多用户协作的 git-based merge 流程，ACE 审查也支持人工干预

---

## 十、一分钟跑起来

```bash
# 最简方式
git clone https://github.com/xiejianjun000/FlowWiki.git my-wiki
cd my-wiki

# 扔一篇文档进去
mkdir -p raw/articles
echo "# 示例文档" > raw/articles/hello.md

# 在任意支持的 AI agent 中执行
> 请按 ingest skill 把 raw/articles/hello.md 入库
```

支持的 agent：
- Claude Code → 读 `CLAUDE.md`
- Codex / Gemini CLI / Amp → 读 `AGENTS.md`
- WorkBuddy → 读 `WORKBUDDY.md`

---

## 最后

如果 Karpathy 的 LLM Wiki 是一套**编码范式**，那 FlowWiki 就是这套范式的**编译器 + 测试框架 + CI/CD**。

它不是替代，是补齐。

项目完全开源（MIT），所有代码、Spec、Skill、模板都在仓库里。如果你在用 AI 维护知识库、或者正打算建一个，不妨来看看。

- [GitHub 仓库](https://github.com/xiejianjun000/FlowWiki)
- 如果觉得有用，点个 Star ⭐ 是对我最大的支持
- Issue / PR / 讨论随时欢迎，尤其欢迎贡献行业适配器和 Skill

让知识的复利，从今天开始。

---

*本文也发布在 [知乎] 和 [掘金]，欢迎转发讨论。*