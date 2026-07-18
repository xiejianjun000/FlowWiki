> 让知识像代码一样编译、缓存、复利增长。不是又一个 RAG，而是一个带防幻觉机制的 AI 知识库编译器。

如果你让 AI 帮你维护一个 500 页的知识库，一年之后，你敢信里面的任何一句话吗？

我不敢。

---

## 一、那个让我睡不着的问题

2025 年，Andrej Karpathy 发了一条简洁到令人不安的推：

> **Obsidian 是 IDE，LLM 是程序员，Wiki 是代码库。**

他提了一个类比——知识不应该被 AI 反复重新推导，而应该像代码一样**编译一次，随用随取**。三层架构，四个操作。

这个概念点燃了整个社区。GitHub 上很快涌现了 30+ 个 LLM Wiki 项目，累计 30,000+ Stars。

但我盯着这个架构看了三个晚上，发现**6 个致命缺口**。

---

## 二、原始构想的 6 个缺口

我画了个表，一目了然：

- **无防幻觉机制**：AI 的摘要可能有事实错误，错了就永久写进知识库，越积越深
- **无跨会话记忆**：每次 ingest 独立执行，不记得上次做了什么
- **无人类入口**：wiki/ 是扁平文件列表，人类根本找不到东西
- **知识不复利到能力**：高频任务每次都从零开始
- **变更不可追溯**：改了什么、为什么改，全无记录
- **单平台绑定**：绑死 Claude Code，换 agent 就丢知识库

就像有人给了你一套极其优雅的编码范式，但没给你编译器、没给你测试框架、没给你 CI/CD。

---

## 三、FlowWiki：补上所有缺口的 LLM Wiki 增强版

我把解决方案架构成 **7 层**。Karpathy 的核心骨架（L1）没动，那是最优雅的部分。我在上面盖了 6 层工程基础设施。

核心是这三个创新：

### 1. ACE 反思循环——错误知识进不了 wiki

传统流程：AI 读 raw → 写 wiki。理解错了就永久错了。

FlowWiki 每条知识入库必须走三 agent 交叉审查：一个生成、一个挑刺、一个裁决。来自 LangChain ACE 框架（NeurIPS 2025），直接嵌入 ingest 管道。

### 2. A-MEM 卡片——跨会话不丢上下文

每次 ingest 自动生成一张记忆卡片，记录原始证据、推理链、与前序卡片的关联。下次新开会话，AI 可以直接读这些卡片恢复"记忆"。零数据库依赖，纯 Markdown 文件。

### 3. 任务 → 知识 → Skill 三元组——复利不止于存储

同一任务执行 3 次以上 → 自动抽象为 Skill → 下次同类任务 O(1) 秒级完成。

```
raw → wiki → skill → 自动调用 → 新任务 → 更多 raw → ...
```

---

## 四、坦诚比一比

市面上 35+ 个 LLM Wiki 项目，FlowWiki 是目前唯一同时在防幻觉 + 跨会话记忆 + 知识复利到能力 + 多 Agent 兼容 + 变更追溯这 5 个维度补齐的。

诚实地讲：claude-obsidian 的 Obsidian 集成更好，llm-wiki-compiler 的 GUI 更直观。但如果你需要跨 agent、长周期、有防幻觉机制的知识库——FlowWiki 是目前唯一的选择。

---

## 五、实际效果

一个真实场景：技术团队用飞书记决策、Git 管代码、多个 AI 助手辅助开发。建一个团队知识库：

```bash
git clone https://github.com/xiejianjun000/FlowWiki.git team-wiki
cp ~/docs/*.md team-wiki/raw/docs/
# 在任何 AI agent 中说：
> 请按 ingest skill 把 raw/docs/ 下的文件入库
```

ingest 一次，产出 5 样东西：知识页面、人类导航页、机器索引、记忆卡片、审查日志。全部可追溯。

---

## 六、技术栈

极简到只剩 PyYAML 一个外部依赖。其他全是 Markdown + YAML frontmatter + git + 纯 Python 脚本。BM25 → nano-graphrag → LightRAG 按规模自适应切换。

---

## 七、不足

不藏着掖着：

- 没有 Web UI（人类入口依赖 Obsidian）
- 检索不是秒级（万页以上要配 LightRAG）
- 社区零起步
- 行业适配器只搭了框架

---

## 八、一分钟跑起来

```bash
git clone https://github.com/xiejianjun000/FlowWiki.git my-wiki
cd my-wiki
mkdir -p raw/articles
echo "# 示例" > raw/articles/hello.md
# 让 AI 执行：请按 ingest skill 入库
```

支持 Claude Code / Codex / Gemini CLI / Amp / WorkBuddy 五家 agent。

---

如果 Karpathy 的 LLM Wiki 是一套**编码范式**，FlowWiki 就是它的**编译器 + 测试框架 + CI/CD**。

项目完全开源（MIT），欢迎 Star、Issue、PR。

**GitHub**：https://github.com/xiejianjun000/FlowWiki

---

*发布于 知乎 · 话题：人工智能、开源项目、知识管理*
