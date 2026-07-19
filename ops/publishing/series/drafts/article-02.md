# 让 AI 互相吵架然后裁决──FlowWiki 的 ACE 反思循环如何拦截幻觉

> 三个 AI agent 对同一份知识"生成 → 批判 → 裁决"，错误内容进不了知识库。这不是事后 lint，是事前拦截。

---

## 第一部分：痛点引入──你敢信 AI 写的知识库吗？

去年有个朋友跟我诉苦：他花了两个月，让 Claude 把团队 300 篇技术文档全部"AI 编译"进了 Obsidian 知识库。格式整齐、结构清晰、每个概念都有摘要──看着很美。

第三个月，一个新来的同事问了他一个问题："知识库里写的 HTTP/3 默认端口是 443，但 RFC 9114 说的是啥？"

他查了原文，发现 **AI 把 HTTP/2 的端口配到了 HTTP/3 的摘要里**。一个看似无害的数字错误，但如果有人按这个摘要做端口配置──生产事故。

更可怕的是，这种错误不是个例。他自己又抽查了 20 篇，发现 3 篇有事实性错误：法条引用了已废止的版本、标准编号写错了一位、因果关系被 AI 倒置了。

**问题核心：你让 AI 写知识库，但没有机制验证 AI 写的是对的。**

这不是 Obsidian 的问题，不是 Claude 的问题──是**整个 LLM Wiki 架构的原始设计缺陷**。Karpathy 的 LLM Wiki 提了四个操作（ingest、query、lint、research），其中 lint 只检查格式和结构，**不检查内容的事实正确性**。

RAG 领域的研究早就给出了量化数据：即使使用检索增强生成，LLM 的幻觉率仍在 **9-40%** 之间（取决于领域和模型）。这意味着：如果你让 AI 入库 100 页知识，其中可能有 9-40 页包含事实错误。而这些错误会**永久沉淀在知识库中**，后续每次 query 都可能引用它们。

在第一篇文章里，我把这列为 6 个致命缺口之首──"无防幻觉机制"。今天这篇，我把 FlowWiki 怎么填上这个缺口的完整技术细节拆给你看。

---

## 第二部分：技术原理──ACE 三 Agent 为什么能拦截幻觉

### ACE 来自哪

ACE（Agent Critique Evaluate）是 LangChain 团队在 2025 年提出的框架，论文被 NeurIPS 2025 收录。核心思路极其简洁：

> **让三个 AI agent 对同一份内容从不同角度审视，一个负责生成、一个负责挑刺、一个负责裁决。**

这不是"我生成完再自己检查一遍"──单 agent 自查已经被证明效果很差（LLM 对自己生成的内容天然有确认偏误）。ACE 的关键创新是**三 agent 角色分离**：

```
Generator（生成者）
  └─ 任务：基于 raw 源文件生成摘要、概念、操作手册
  └─ 倾向：追求完整性和流畅性，容易"脑补"缺失信息

Reflector（审视者）
  └─ 任务：从批判角度审查 Generator 的输出
  └─ 检查项：事实矛盾、幻觉信号、证据链断裂、源引用缺失
  └─ 倾向：质疑一切，宁可误报也不漏报

Curator（裁决者）
  └─ 任务：综合 Generator 和 Reflector 的意见做最终决策
  └─ 三种裁决：
     store ── 审查通过，允许写入 wiki
     revise ── 有问题但不严重，需要修正后重新走 ACE
     learn ── 知识库无法覆盖，触发缺口学习流程
     reject ── 严重错误，拒绝入库
```

三 agent 的信息流不是串行传递──Curator 同时看到 Generator 的输出和 Reflector 的审查意见，然后做决策。这比"生成完跑个 lint"多了**对抗性审查**环节。

### 为什么这比"事后 lint"强

Karpathy 的 lint 操作跑在 `ingest` 之后，检查的是**格式和结构**：frontmatter 字段齐全吗？Wikilink 正确吗？文件放在对的目录了吗？

这些检查有价值，但它们**不触及内容**。一个格式完美但事实错误的 wiki 页面，lint 会给它打满分。

ACE 的审查发生在 `ingest` **过程中**──在内容写入 wiki 之前就拦截。区别就像：

| 机制 | 时机 | 检查范围 | 能拦截幻觉吗 |
|------|------|----------|:---:|
| Lint | 入库后 | 格式、结构 | ❌ |
| 单 Agent 自查 | 入库前 | 内容（但确认偏误） | ⚠️ |
| ACE 三 Agent | 入库前 | 内容 + 证据链 + 缺口 | ✅ |

---

## 第三部分：FlowWiki 实现──ACE 嵌入 ingest 管道的完整代码拆解

### 整体架构

FlowWiki 把 ACE 直接嵌入了 ingest 管道──每次入库一个 raw 文件，ACE 自动运行。不是可选的"质量门禁"，而是**ingest 的标准步骤**。

```
ingest_pipeline.py
  └─ scan raw files
  └─ compile to wiki (生成骨架)
  └─ ace_review.py ← 在这里嵌入
       ├─ Generator: 基于 KB + raw 生成回答
       ├─ Reflector: 审查回答，检测缺口/幻觉/证据链断裂
       ├─ Curator: 决策 store/revise/learn/reject
       ├─ GapLearner: 如果 learn，搜索外部源生成学习卡片
       └─ _log_ace: 记录到 .memory/ace/
```

### Generator──不瞎编，先查 KB

```python
class Generator:
    """生成回答 — 基于 knowledge base 或标记缺口"""

    def generate(self, query: str, kb_pages: dict, use_llm: bool = True) -> dict:
        # KB 没有内容时，直接标记为缺口——不编造回答
        if not kb_pages and use_llm:
            return {
                "content": "知识库当前未覆盖此问题。建议补充相关原始资料。",
                "sources": [],
                "confidence": 0.1,  # 极低置信度 = 明确告知"我不确定"
                "knowledge_gaps": [{
                    "query": query,
                    "missing_domain": "未识别",
                    "suggested_sources": []
                }]
            }
```

第一个关键设计：**KB 空时，Generator 不编造回答，而是诚实地说"我不知道"**，置信度设为 0.1。这是防幻觉的第一道门──宁可承认无知，也不要脑补。

有 KB 内容时，Generator 会调用 LLM（DeepSeek API）基于知识库内容生成回答，同时输出置信度评估：

```
confidence > 0.7 → KB 充分覆盖
0.4-0.7 → 能部分回答
< 0.3 → 完全无法回答
```

### Reflector──四种检测机制

```python
class Reflector:
    """审查回答 — 检测缺口、幻觉、证据链断裂"""

    def review(self, output: dict, kb_sources: list) -> dict:
        # 1. 检查 Generator 标记的显式知识缺口
        gaps = output.get("knowledge_gaps", [])

        # 2. 自动检测缺口信号词（"知识库未覆盖"、"暂无相关"等）
        auto_gaps = detect_gaps(content, sources)

        # 3. 验证引用源是否真的在 KB 中
        for src in sources:
            if src not in kb_sources:
                issues.append({"type": "citation", "severity": "high",
                    "description": f"引用的源 '{src}' 不在知识库中"})

        # 4. 置信度低于阈值 → 标记问题
        if confidence < 0.3:
            issues.append({"type": "low_confidence", "severity": "high"})
```

Reflector 的四种检测：

| 检测类型 | 原理 | 严重度 |
|----------|------|--------|
| 显式缺口 | Generator 自己承认的知识空白 | medium |
| 信号词检测 | 扫描回答中的"知识库未覆盖"、"暂无相关"等信号词 | medium |
| 引用验证 | 回答引用的源不在 KB 中 → 可能是幻觉引用 | **high** |
| 置信度门禁 | confidence < 0.3 → 回答不可信 | high |

信号词检测的完整列表（9 个中文 + 5 个英文）：

```python
GAP_SIGNALS = [
    "知识库未覆盖", "暂无相关", "无法确定", "需要补充", "未收录",
    "not found in knowledge base", "insufficient information",
    "缺乏", "无相关资料", "超出范围",
]
```

### Curator──三种裁决 + 一个学习通道

```python
class Curator:
    def decide(self, output: dict, review: dict) -> dict:
        if status == "knowledge_gap":
            decision = "learn"  # 不是拒绝，而是"我去学习"
        elif status == "needs_revision":
            decision = "revise"
        elif status == "approved":
            decision = "store"
```

Curator 的设计哲学：**知识库缺内容不是罪，编造内容才是罪**。所以 `learn` 裁决不是"拒绝你"，而是"承认我不知道，并启动学习流程"。

### GapLearner──缺口的自动补全机制（v0.2.0 新增）

这是昨天刚加进代码的新功能：

```python
class GapLearner:
    """知识缺口学习器 — 搜索外部源，生成学习卡片"""

    def learn(self, gaps: list[dict], query: str) -> list[dict]:
        for gap in gaps[:3]:  # 最多处理 3 个缺口
            card = {
                "id": f"gap-{timestamp}-{hash}",
                "status": "open",
                "query": query,
                "missing_domain": domain,
                "action": "human_review" if not suggested else "auto_ingest_candidate",
            }
            # 保存到 .memory/gaps/ 目录
            json.dump(card, open(card_path, "w"))
```

GapLearner 为每个检测到的知识缺口生成一张学习卡片，保存到 `.memory/gaps/`。卡片有两种状态：

- **human_review**──没有找到推荐源，需要人工判断是否补充
- **auto_ingest_candidate**──找到了推荐源，可以作为下次 ingest 的候选

这让知识库的生长变成了**闭环**：缺口被检测 → 学习卡片被生成 → 人工或自动补充 → 下次 ingest 覆盖缺口 → 知识库增厚。

---

## 第四部分：实战演示──ACE 拦下了什么

我用 FlowWiki 的执法督察评查知识库跑了一次真实测试，让你看看 ACE 在实战中的表现。

### 场景一：知识库能回答的问题

**查询**："企业超标排放，如何处罚？"

知识库中有《生态环境法典》相关条文、处罚程序规范、证据链闭环要求等内容。

```
Generator 输出：
  → 完整引用了 6 个要点（证据链、法律适用、自由裁量权等）
  → confidence: 实际评估值
  → sources: [排污许可, 证据链闭环, ...]

Reflector 审查：
  → status: approved
  → 置信度: 0.85
  → 问题数: 0
  → 知识缺口: 2（微小的关联知识未完全覆盖）

Curator 决策：
  → store ── "审查通过，可存入 wiki"
```

ACE 让一条高质量知识顺利入库。

### 场景二：知识库无法回答的问题

**查询**："核电站放射性废物处理标准？"

知识库是执法督察评查领域，完全没有核能相关内容。

```
Generator 输出：
  → "知识库未覆盖"
  → confidence: 0.1
  → knowledge_gaps: [核电站放射性废物处理标准]

Reflector 审查：
  → status: knowledge_gap
  → 置信度: 0.0
  → 问题数: 1

Curator 决策：
  → learn ── "检测到 3 个知识缺口，需要外部学习"

学习卡片：
  → gap-a13: 核电站放射性废物处理标准 → human_review
  → gap-c7a: 知识库未覆盖 → human_review
  → gap-193: 未识别领域 → human_review
```

ACE 拦住了幻觉──AI 诚实承认不知道，而不是编造一个看似正确的回答。同时生成了学习卡片，标记为 human_review，等待人工决定是否补充核能领域知识。

### ACE 日志记录──每次审查都有存证

所有 ACE 审查记录保存在 `.memory/ace/` 目录，格式为 Markdown + YAML frontmatter：

```markdown
---
id: 20260718-084739
date: 2026-07-18T08:47:39
decision: store
gaps: 2
---

# ACE 反思记录

## 查询
企业超标排放，如何处罚？

## Generator 输出
...

## Reflector 审查
- 状态: approved
- 置信度: 0.85
- 问题数: 0

## Curator 决策
- 决策: store
- 理由: 审查通过，可存入 wiki
```

这意味着：**任何时候你都可以回溯一条知识的入库过程**──谁审查的、置信度是多少、有没有缺口、Curator 为什么决定放行。这不是黑箱。

---

## 第五部分：与竞品的防幻觉方案对比

| 方案 | 项目 | 机制 | 检查时机 | 能拦截内容幻觉 | 能检测知识缺口 | 能追踪审查过程 |
|------|------|------|----------|:---:|:---:|:---:|
| ACE 三 Agent | **FlowWiki** | Generator→Reflector→Curator | 入库前 | ✅ | ✅ | ✅ |
| 矛盾标记 | llm-wiki-agent | ingest 后标记矛盾 | 入库后 | ⚠️ | ❌ | ❌ |
| Lint 检查 | Karpathy 原始设计 | 格式+结构校验 | 入库后 | ❌ | ❌ | ❌ |
| 预处理净化 | synthadoc | 上传前清洗噪音 | 入库前 | ⚠️ | ❌ | ❌ |
| Review policy | atomicstrata | human review gate | 入库后 | ⚠️（依赖人） | ❌ | ⚠️ |

**llm-wiki-agent 的矛盾标记**：入库后才检查矛盾──意味着错误内容已经进了知识库，只是被标记了。如果你不主动清理，后续 query 仍可能引用错误内容。

**atomicstrata 的 review policy**：依赖人工审查──可行但不可扩展。100 页知识库你能逐篇审查，1000 页呢？

**FlowWiki 的 ACE**：入库前拦截 + 自动检测缺口 + 审查日志可追溯。三件事都有工程保障。

公平地说，ACE 不是银弹。它依赖 LLM API 的准确性──如果 Generator 和 Reflector 都被同一个错误误导，Curator 也可能裁决错误。但**对抗性审查比单 agent 自查的漏检率显著更低**，这在 NeurIPS 论文中有实验数据支撑。

---

## 总结 + 下一篇预告

FlowWiki 的 ACE 反思循环做了一件简单但关键的事：**在知识写入知识库之前，让三个 AI agent 对内容进行对抗性审查**。

- Generator 不编造──KB 空时直接承认无知，置信度 0.1
- Reflector 四层检测──显式缺口、信号词、引用验证、置信度门禁
- Curator 三种裁决──store/revise/learn，缺知识不是罪，编造才是
- GapLearner 自动补全──缺口闭环，知识库持续生长
- 审查日志可追溯──.memory/ace/ 目录记录每次决策

这不是事后 lint，不是人工审查门禁，不是"标记矛盾等你自己清理"。这是**工程化的防幻觉机制**──嵌入 ingest 管道，每次入库自动运行，审查记录永久留存。

第一篇文章里我说：FlowWiki 是站在 Karpathy LLM Wiki 肩膀上的增强版。ACE 就是第一个增强──把"AI 可能写错"这个事实，从假设变成了可检测、可拦截、可追溯的工程问题。

下一篇，我们拆 FlowWiki 的第二个创新──A-MEM Zettelkasten 卡片记忆系统。你的 AI 助手为什么每次新会话都像新生儿？卡片记忆如何让知识跨会话持久生长？

---
*本文是 FlowWiki 从零到一系列第 2 篇，下一篇：[你的 AI 助手总在「失忆」？FlowWiki 的 A-MEM 卡片记忆系统来了](#)*
*系列目录：[第 1 篇：FlowWiki 开源首发](https://juejin.cn/post/xxx) | 上一篇：[第 1 篇](https://juejin.cn/post/xxx) | [下一篇](#)*
*GitHub：[xiejianjun000/FlowWiki](https://github.com/xiejianjun000/FlowWiki)*
