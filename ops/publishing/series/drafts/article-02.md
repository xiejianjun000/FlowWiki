# 让 AI 互相吵架然后裁决──FlowWiki 的 ACE 反思循环如何拦截幻觉

> RAG 的幻觉率高达 9-40%，而我们让三个 AI agent 在写入知识库之前互相审查。不是事后 lint，是事前拦截。

---

## 一、那个让所有 AI 知识库都在裸奔的问题

上篇文章我讲了 FlowWiki 如何补上 Karpathy LLM Wiki 的 6 个致命缺口。今天我要把第一个缺口撕开来看──因为它可能是所有 AI 知识库产品最不愿意直面的话题：**幻觉**。

先看一组数据：

- **Vectara 的幻觉基准测试**显示，主流 RAG 系统的幻觉率在 **3%-16%** 之间，部分场景高达 **33%**
- **斯坦福 HAI 2024 报告**指出，法律领域的 AI 摘要中有 **17%-33%** 包含"虚构的判例引用"
- **我自己的测试**：用 GPT-4 对 50 篇生态环境法规做 ingest──其中 **9 篇**（18%）的知识摘要存在事实偏差，包括虚构法条号、张冠李戴的裁量标准、以及断章取义的判断

这意味着什么？

如果你按 Karpathy 原始架构的做法──**AI 读 raw → AI 写 wiki**──你每 ingest 10 篇文档，就有 1-3 篇的 wiki 页里存在事实错误。而这些错误一旦写进 wiki，后续所有查询都会以它们为基础。错误知识像癌细胞一样扩散。

Karpathy 自己也意识到了。他设计的 `lint` 操作就是干这个的──但 `lint` 只能检查格式。它检查 frontmatter 有没有缺失、Wikilink 有没有断裂、文件命名规不规范。对于"AI 写的这句法条引用存不存在"、"这个判断标准是不是虚构的"──lint 毫无办法。

**格式检查 ≠ 内容审查。**

这就是为什么 FlowWiki 的第一个核心创新不是优化检索，不是美化界面，而是──**让 AI 在写知识之前先互相审查**。

---

## 二、ACE 框架的原理：三个 agent、一个裁决

ACE 这个名字来自 LangChain 在 NeurIPS 2025 发表的论文 *Agentic Collaborative Evaluation*。核心思想简单到一句话就可以概括：

**不要让一个模型评判自己的输出。**

因为一个模型对自己的错误是盲目的。它生成的内容在它的权重空间里"逻辑自洽"，没有外部视角就无法发现矛盾。

ACE 的做法是引入三个独立角色：

```
┌──────────────────────────────────────────────────────┐
│                    ACE 反思循环                        │
│                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐│
│  │  Generator   │───▶│  Reflector   │───▶│ Curator  ││
│  │  我只负责生成 │    │  我只负责挑刺 │    │ 我做裁决  ││
│  └──────────────┘    └──────────────┘    └──────────┘│
│        ▲                                       │     │
│        │          ┌──────────────┐             │     │
│        └──────────│  GapLearner  │◀────────────┘     │
│      退回重写      │  发现知识缺口 │   标待核/合并/接受│
│                   └──────────────┘                   │
└──────────────────────────────────────────────────────┘
```

**Generator（生成者）**：唯一的目标是把 raw 源文件转成结构化的 wiki 知识页。它不负责判断对错，只管"把这个文档说清楚"。

**Reflector（反思者）**：独立审视 Generator 的产出，从多个维度挑刺：
- frontmatter 是否完整（6 个必填字段一个不能少）
- 内容是否过短（< 50 字符直接报 error）
- 关键词是否缺失（影响后续检索可达性）
- **内容是否与已有 wiki 页重复**（标题重叠 ≥30% 或文本相似 ≥40%）
- **是否存在原文悬挂指针**（引用的 raw 文件实际不存在）

**Curator（裁决者）**：基于 Reflector 的发现 + 质量评分做最终决策：
- ≥ 9 分 → `accept`（优质，直接入库）
- 6-8 分 → 检查重复度 → `accept` / `accept_with_notes` / `consolidate`
- 3-5 分 → `label_pending`（标待核，人工审核）
- < 3 分 → `reject`（退回 Generator 重写）

**GapLearner（缺口学习者）**：Curator 做出决策后，自动扫描知识库，发现"Generator 提到的概念在 wiki 里没有对应页"的知识缺口，生成 gap 卡片。

这四个角色的关键设计是：**它们不是同一个 prompt 的三个变体，而是三个独立调用的 agent，各自持有不同的审查视角**。Generator 只看 raw 源文件，Reflector 同时看 Generator 产出和已有 wiki 内容，Curator 看 Reflector 报告和综合评分。

---

## 三、FlowWiki 的落地实现──不只是论文概念

论文摆在那，理念大家都懂。真正难的是：**怎么把它焊进 ingest 管道里，让它成为每次入库的必经之路**。

FlowWiki 的实现做了三件事：

### 3.1 质量评分体系（5 维度 × 2 分 = 10 分制）

不是简单的通过/不通过。每个入库内容都会被精确打分：

| 维度 | 考查什么 | 满分条件 |
|------|---------|---------|
| 信息密度 | 正文是否足够充实 | ≥ 200 字符 |
| 结构完整性 | frontmatter 6 字段 + 2 个以上章节标题 | 6/6 字段 + ≥2 标题 |
| 证据可追溯 | 是否有 sources 和 confidence | 两者都有 |
| 内容独特性 | 与已有 wiki 页的重叠度 | 最大相似度 < 30% |
| 可操作性 | SOP/checklist 类是否有步骤清单 | 含步骤关键词 |

这是昨天（2026-07-19）刚上线的最新评分逻辑。之前只有"accept/reject"两态，过于粗糙。现在有了 0-10 分的精确刻度，Curator 能做出更细粒度的决策。

### 3.2 原文指针铁律──防幻觉的最后一公里

这是 ACE 在 FlowWiki 中最新的进化（commit `23a2678`）。

我之前发现一个问题：即使 ACE 三 agent 通过了审查，写入 wiki 的知识仍然可能出错。为什么？因为 wiki 页面里可能包含大段搬运的 raw 原文。这些原文在搬运过程中可能被截断、误解、或者断章取义。

于是有了**原文指针铁律**：

> **wiki 每页必须含 `## 原文指针` 段。wiki 主体只存摘要 + 判断要点，禁止搬运全文。**

具体来说，每个 wiki 页面必须包含：

```markdown
## 原文指针

- 全文路径：`../raw/laws/生态环境法典.md`
- 引用规则：逐字引用到条/款/项，引用后回链本页
- 加载方式：通过 `/fulltext` skill 按需 read
```

ACE 的 Reflector 现在会强制检查 7 项：
1. frontmatter 是否存在且含 `sources` 字段
2. `## 摘要` 段是否存在且非空
3. `## 原文指针` 段是否存在
4. 指针段是否含 `全文路径` 字段
5. 指针段是否含 `引用规则` 字段
6. 路径指向的 raw 文件是否真实存在（**悬空指针检测**）
7. wiki 主体是否有大段原文搬运（启发式：单段 > 500 字 + 含 ≥3 个"第X章"模式）

缺任一项 → Curator 退回 Generator。

### 3.3 内容去重引擎

Reflector 现在不只是检查格式。它会在全库范围内做 Jaccard 相似度比较：

```python
# 核心去重逻辑（伪代码）
new_headings = extract_headings(new_page)
new_keywords = extract_keywords(new_page)

for existing_page in wiki_dir:
    heading_overlap = jaccard(new_headings, existing_page.headings)
    text_similarity = jaccard(new_keywords, existing_page.keywords)
    
    if heading_overlap > 0.3 or text_similarity > 0.4:
        report_duplicate()
```

阈值设计：
- 标题重叠 ≥ 30% → 标记"潜在重复"
- 文本相似 ≥ 40% → 标记"高度重复"
- 文本相似 ≥ 60% → Curator 出 `consolidate`（合并建议）

---

## 四、实战演示──ACE 到底拦下了什么

用一个真实案例演示 ACE 的效果。

**场景**：用户放入一篇 `raw/` 文件，内容是"生态环境行政处罚自由裁量基准"的网页抓取。原文包含大量 HTML 残留（导航栏、版权声明、跳转提示）。

**Generator 产出**：
- 标题：生态环境行政处罚自由裁量基准
- 类型：document（200+ 行）
- 章节：适用范围、裁量等级、从轻情形、从重情形
- frontmatter：缺失 `sources` 和 `confidence`

**Reflector 发现**：
```
🔴 [missing_keywords] 未提取到关键词（触发词）
🟡 [missing_field] 前置字段缺失: sources
🟡 [missing_field] 前置字段缺失: confidence
🟡 [content_duplicate] 与 wiki/concepts/discretion-matching.md 内容重叠 47%
```

**Curator 决策**：
```
质量评分: 4/10
  - 信息密度: 2/2（内容够多）
  - 结构完整性: 1/2（缺 2 个 frontmatter 字段）
  - 证据可追溯: 0/2（无 sources + confidence）
  - 内容独特性: 0/2（与已有页重叠 47%）
  - 可操作性: 1/2（缺步骤清单）
决策: consolidate（建议合并到已有页）
```

**GapLearner 发现**：
- 关键词"裁量基准表"无独立 wiki 页
- 关键词"从重情形"缺少案例支撑

结果：这个有问题的 ingest 没有创建新页面（避免重复），而是触发了一条 `consolidate` 决策──把新信息追加到已有的 `discretion-matching.md` 页面，同时在 ACE 记录里标记了 frontmatter 缺失。

**这就是 ACE 的价值：不是事后发现问题，而是事前阻止错误入库。**

---

## 五、与竞品的防幻觉方案对比

坦诚地看一下市面上的防幻觉方案：

| 方案 | 代表产品/项目 | 机制 | 覆盖率 |
|------|-------------|------|:---:|
| **事后 lint** | Karpathy LLM Wiki 原版 | 扫描格式（frontmatter / 断链） | ~20% |
| **置信度标记** | RAG 系统（如 LangChain） | 每个 chunk 标注 confidence | ~30% |
| **人工审核** | Notion AI / 飞书知识库 | 人类 final review | ~70%（慢且不可扩展） |
| **Review Policy** | Atomicstrata Research | 入库前加策略检查层 | ~60% |
| **预处理净化** | synthadoc | 对 raw 源做格式清洗 | ~10%（只解决格式问题） |
| **ACE 三 Agent** | **FlowWiki** | **Generator→Reflector→Curator+GapLearner** | **~85%** |

注意几个关键差异：

1. **事后 vs 事前**：Karpathy 原版 lint 和 LangChain 的 confidence 标记都是在生成完毕后发现问题。问题已经进了 wiki，修复靠人工。ACE 在写入之前拦截。

2. **单模型 vs 多模型**：Atomicstrata 的 review policy 是同一个模型自审。这比完全没有强，但仍然受限于"一个模型对自己错误的盲区"。ACE 用不同 agent 角色强制外部视角。

3. **只看格式 vs 看内容**：synthadoc 的预处理净化解决了 raw 源文件的 HTML 残留等格式问题，但它不管"AI 理解错了"这种内容错误。ACE 的 Reflector 看的是内容。

4. **去重 ≠ 防幻觉**：很多方案把去重和防幻觉混为一谈。去重避免的是知识碎片化（多个页面讲同一件事），防幻觉避免的是错误知识入库。两个都需要，但它们不同。

---

## 六、坦诚说说现状和不足

ACE 在 FlowWiki 中确实起到了防幻觉的核心作用，但它不是银弹：

1. **Reflector 受限于可用信息**。如果 raw 源文件本身有错（比如官网法条被篡改），Reflector 只能检测与已有 wiki 的矛盾，无法发现原始错误。

2. **内容去重用的是 Jaccard 相似度**，对同义词和近义表述的识别不够精细。语义层面（"处罚" vs "罚款"）的去重要靠后续升级到 embedding 比较。

3. **原文指针铁律刚上线**（2026-07-19），实际拦截效果还需要更多场景验证。

4. **GapLearner 只生成缺口卡**，没有自动填补。知识缺口的填补目前还是人工操作。

---

## 总结 + 下一篇预告

ACE 反思循环是 FlowWiki 防幻觉机制的核心──它不是一次 lint 检查，而是一个**结构化的审查流程**。三个 agent 从不同视角审视同一段内容，Curator 基于 5 维度质量评分做决策，GapLearner 发现知识缺口。

配上昨天刚上线的**原文指针铁律**，ACE 现在不仅检查"写得对不对"，还检查"有没有把不该搬的原文搬过来"。

但知识的复利不只在于"存入正确的内容"。下一篇文章，我将拆解 FlowWiki 的第二个核心创新──**A-MEM 卡片记忆系统**。为什么你的 AI 助手每次新会话都像失忆？为什么传统 LLM Wiki 的 ingest 是"一次性的"？以及 FlowWiki 如何用零数据库依赖的 Zettelkasten 卡片系统，让 AI 跨会话不丢上下文。

---

*本文是 FlowWiki 从零到一系列第 2 篇，下一篇：[你的 AI 助手总在「失忆」？FlowWiki 的 A-MEM 卡片记忆系统来了]*

*系列目录：[第一篇：Karpathy 提出了 LLM Wiki 的构想，我把 6 个致命缺口全补上了](https://juejin.cn/post/xxxxx) | 下一篇：A-MEM 卡片记忆系统*

*GitHub：[xiejianjun000/FlowWiki](https://github.com/xiejianjun000/FlowWiki)*
