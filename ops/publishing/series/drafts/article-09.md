# 100 页用 BM25、500 页上 GraphRAG──FlowWiki 的自适应检索策略

> 知识库越大，搜索越烂。这不是运气问题，是检索策略的结构性失效。FlowWiki 用三档自适应切换让检索策略随规模自动进化。

---

## 一、200 页以后，你的知识库开始「找不到东西」

这是我在维护执法督察评查知识库时遇到的真实情况。

前 50 篇文档，用 Obsidian 的 `Cmd+O` 快速搜索，秒出结果。100 篇时，开始出现同一关键词返回 20+ 个结果，需要手动翻找。到 155 篇时，搜"处罚裁量"返回 14 篇，其中前 3 篇跟这个主题只有一句话的相关性──只是因为正文里出现了这四个字。

更麻烦的是**语义搜索完全失效**。搜"监测数据造假"，找不到标题里含有"篡改"的文档──尽管在法律语境中它们指的是同一件事。搜"执法主体资格"，漏掉了讨论"分局是否具有处罚权"的那篇关键论证文章。

这不是 Obsidian 的锅。这是**所有基于关键词的检索引擎在面对领域知识库时都会遇到的「语义鸿沟」**。你知道要查什么，但你的检索工具不知道你在说什么。

更讽刺的是──大多数 AI 知识库项目压根不讨论这个问题。它们默认"用户提问 → 向量搜索 → RAG 回答"这条路径天然成立。但实际上：

| 知识库规模 | 关键词搜索 | 向量搜索 | 实际需求 |
|-----------|-----------|---------|---------|
| < 100 页 | 够用 | 过度设计 | 快就行 |
| 100-500 页 | 噪音爆炸 | 召回率低 | 需要语义理解 |
| 500+ 页 | 完全失效 | 维度灾难 | 需要实体推理 |

**没有一个检索引擎能在所有规模下都表现好。** 这就是 FlowWiki L2 层要解决的核心问题。

---

## 二、检索策略的三重进化

先说一个反直觉的事实：**小规模知识库根本不需要向量数据库。**

Chroma、Pinecone、Weaviate 这些工具的存在有它们的道理。但如果你只有 100 篇文档，每篇 2000 字，总共 200KB 文本──把它们全部嵌成向量放进数据库里，维护一套 embedding pipeline，调参调 chunk size，最后搜索出来的结果可能还不如 `grep`。

这不是向量检索不好，是**规模没到需要它的程度**。

FlowWiki 的设计哲学是：让检索策略随知识库一起成长。

### 阶段一：BM25 + CJK 分词（≤ 100 页）

BM25 是信息检索领域的经典算法，1970 年代提出，经历了几十年的实战检验。它的核心思想非常简单：

- 一个词在文档中出现次数越多，这个文档就越相关（TF：词频）
- 但如果这个词在大多数文档里都出现，那它对区分文档的帮助反而很小（IDF：逆文档频率）
- 文档长度会影响词的密度，长文档需要做归一化（长度惩罚参数 `b`）

对于 100 页以内的知识库，BM25 的击中是精准的──因为文档量少，词频-逆文档频率的统计特性还没有被稀释。加上 CJK 分词（处理中文的二字词切分），基本上可以覆盖 90% 以上的查询场景。

### 阶段二：nano-graphrag（100-500 页）

当文档突破 100 页，BM25 开始暴露问题。同一个实体可能以不同名称出现（"生态环境部" vs "部里" vs "上级部门"），同一个概念可能有不同表述（"违法情节严重" vs "情节恶劣" vs "应当从重处罚"）。

这时候需要的是**实体级别的语义理解**，而不是文档级别的关键词匹配。

nano-graphrag 是一个轻量级的图增强检索框架。它的核心做法是：从文本中抽取实体和关系，构建一个本地知识图谱。当用户查询时，先在图中找到相关实体，再沿着关系边扩展──这样就能把"篡改监测数据"和"数据造假"两个表述不同的术语关联到同一个概念上。

### 阶段三：LightRAG（500+ 页）

到了 500 页以上，问题变成了**维度灾难的实体版**。实体太多、关系太密，图的遍历成本急剧上升。你需要的不只是图谱，还需要向量索引来快速定位图谱中的入口节点。

LightRAG 做的就是这件事：它在图谱之上叠加了向量检索，先用 embedding 快速定位候选实体节点，再在局部子图上进行关系推理。两阶段的「粗筛 → 精排」策略，让检索复杂度从 O(E) 降到 O(log N + K)。

---

## 三、config.toml 驱动的切换机制

FlowWiki 的自适应检索策略是架构设计层面的，而不是代码里硬编码的 `if-else`。核心是 `config.toml` 中的检索配置段：

```toml
[retrieval]
engine = "bm25"                           # 当前使用的检索引擎
fallback_engines = ["nano-graphrag", "lightrag"]  # 自动降级链路

[bm25]
k1 = 1.2                                  # 词频饱和度参数
b = 0.75                                  # 文档长度归一化参数
min_token_length = 2                      # CJK 分词最小字符数

[nano-graphrag]
enabled = true                            # 是否启用图谱检索
max_depth = 3                             # 图谱遍历深度
top_k = 10                                # 返回结果数

[lightrag]
enabled = false                           # 默认关闭（按需启用）
api_key = ""                              # embedding 模型 API key
model = "text-embedding-3-small"          # 向量模型
```

设计上有三个关键决策：

**1. 显式切换，不自动。**

大多数检索系统喜欢做「自动检测规模 → 自动切换引擎」。这看起来很聪明，但不可控。知识库不是只有文档数量一个维度──有些 50 页的法规库由于术语密度极高，需要图谱检索；有些 300 页的技术博客 BM25 就够用。所以 FlowWiki 把这个决策权交给使用者，在 `config.toml` 里显式配置 `engine`。

**2. fallback 链路，不断。**
当主引擎返回结果置信度不足时，系统会自动降级到 fallback 链路。这个设计保证了：即便你配置了 lightrag 但 embedding API 挂了，检索不会直接报错，而是回退到 BM25。

**3. 零依赖启动。**

`lightrag.enabled = false` 是默认值。这意味着 FlowWiki 开箱只需要 BM25（内置实现），不需要装任何向量数据库、不需要申请任何 API key。当你真正需要高级检索能力时，再打开开关。

---

## 四、实战：search_wiki() 的 BM25 实现

下面是 FlowWiki MCP Server 中 BM25 检索的核心实现（`_scripts/mcp_server.py`）：

```python
def search_wiki(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Simple keyword search over wiki pages (BM25-style keyword match)."""
    results: list[dict[str, Any]] = []
    query_lower = query.lower()
    wiki_dir = self.root / "wiki"
    if not wiki_dir.exists():
        return results

    for md_file in wiki_dir.rglob("*.md"):
        if md_file.name in ("README.md", "log.md"):
            continue                          # 跳过索引日志页
        if "meta" in md_file.parts:
            continue                          # 跳过元数据目录
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue
        score = content.lower().count(query_lower)
        if score > 0:
            results.append({
                "path": str(md_file.relative_to(self.root)),
                "title": self._extract_title(content, md_file.name),
                "score": score,
                "preview": content[:300].strip(),
            })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:max_results]
```

几点值得注意的工程考量：

**跳过索引页。** `README.md` 和 `log.md` 是高频词聚集地──"处罚"、"执法"、"案例"这些词在索引中命中 100+ 次，但返回它们作为搜索结果毫无意义。与其依赖 IDF 自然抑制，不如直接过滤。

**跳过元数据目录。** `meta` 目录存放的是知识库自身的结构化元数据（标签、关联、版本），不是正文。混入搜索结果会污染用户体验。

**score = keyword 出现次数。** 这是一个朴素的 BM25 简化实现。真正的 BM25 需要计算 TF-IDF（词频-逆文档频率），但优势在于：它不需要构建倒排索引，不需要预计算文档频率。对 100 页级别的知识库来说，这个简化是「够用」的──精度损失在可接受范围内，换来的是零启动成本。

如果未来接入 nano-graphrag，这个方法会变成这样：

```python
def search_wiki(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
    # 读取 config.toml 选择引擎
    engine = self.config["retrieval"]["engine"]

    if engine == "bm25":
        return self._bm25_search(query, max_results)
    elif engine == "nano-graphrag":
        return self._graphrag_search(query, max_results)
    elif engine == "lightrag":
        return self._lightrag_search(query, max_results)
    else:
        # fallback 链路
        for fallback in self.config["retrieval"]["fallback_engines"]:
            result = self._try_engine(fallback, query, max_results)
            if result:
                return result
```

而 `config.toml` 提供了一个清晰的切换点──**改动一行配置，不需要改代码，不需要重新理解架构。** 这就是「可配置优于可编码」的设计原则。

---

## 五、与竞品对比：其他人怎么处理检索？

| 项目 | 检索方式 | 规模适应 | 切换成本 |
|------|---------|---------|---------|
| **FlowWiki** | BM25 → nano-graphrag → LightRAG 三档自适应 | 显式切换 + fallback 链路 | 改一行 config.toml |
| **llm-wiki-agent** | 无专用检索层，依赖 LLM 逐页读取 | 无 | 无 |
| **atomicstrata/llm-wiki-compiler** | embedding 向量检索（固定方案） | 不可切换 | 改造 pipeline |
| **claude-obsidian** | 依赖 Obsidian 内置搜索 | 无法干预 | 无 |
| **Dify RAG pipeline** | 多检索策略可组合 | 需要手动编排 | 配 pipeline 节点 |

核心差异在于「切换成本」。大多数项目要么绑定一种检索策略（想升级就要改代码），要么让你手动编排（给自由度但不给默认方案）。FlowWiki 的做法是：给出三级路线图，每个阶段切换只需要改一行配置。

**但需要诚实地说：FlowWiki 当前只完整实现了 BM25 阶段。** nano-graphrag 和 LightRAG 的集成是设计层面的规范，代码侧的填充还在进行中。这在开源项目里是常态──先跑通最小可用路径，再按需求逐渐打开能力。

这个策略本身也是一个工程决策：**检索引擎不是越多越好，而是在对的时间用对的工具。** 如果你只有 100 页文档，在一个未完工的 LightRAG 集成上花 3 天，不如花 3 小时优化 BM25 的 CJK 分词。FlowWiki 的 config.toml 设计确保了你可以在需要时平滑升级，而不是一上来就被迫选择。

---

## 六、和前面几篇的关系：检索是信任链条的起点

如果你从系列第一篇一路读过来，你应该能感觉到 FlowWiki 的 7 层架构之间是递进关系：

- **L4 ACE 反思循环**（article-02）确保写入 wiki 的内容正确
- **L4 A-MEM 卡片记忆**（article-03）确保 AI 能跨上下文检索历史
- **L5 Skill 化层**（article-04）确保高频任务不再从零开始
- **L5 双索引**（article-05）确保人类和 AI 都有入口
- **L3 SpecCoding**（article-06）确保变更可追溯
- **L6 多 Agent**（article-07）确保不受单平台绑定
- **L7 场景层**（article-08）确保一套架构多行业复用

而 **L2 检索增强层**──就是这篇文章讨论的内容──是整个信任链条的**起点**。

ACE 再强、卡片再密、Skill 再快，只要第一步「找到对的文档」出错了，后面的所有机制都在处理错误输入。这就像一个精密的质检流水线，但如果原材料进料时就搞混了编号，后面的质检再严格也没有意义。

从这个角度说，FlowWiki 的自适应检索策略是「不追求最优，只追求不丢」。宁可多返回几个候选让 ACE 或用户自己过滤，也不能因为检索策略的切换边界问题漏掉关键文档。这也是为什么 fallback 链路的设计不是「备用方案」，而是「安全网」。

---

## 总结

知识库检索不是一个「选一个引擎然后永远用它」的问题。它随着规模增长而演化──就像你不会用同一把钥匙开所有的锁，也不应该用同一个检索策略应对所有规模的知识库。

FlowWiki 的答案很朴素：**BM25 起步，够用就一直用；发现语义匹配不行了，打开 nano-graphrag；实体关系复杂到图谱也吃力了，再启用 LightRAG。** 每一步切换只改一行配置，不需要重写管线。

**下一篇预告**：从 v0.1.0 到 v0.2.0，FlowWiki 如何从一个「好架构」变成一个「能用的产品」。MCP Server 的 5 工具设计、Docker 一键部署、GitHub Topics 优化──开源项目从 0 到 1 的完整记录。

---

*本文是 FlowWiki 从零到一系列第 9 篇，下一篇：[从 v0.1.0 到 v0.2.0──FlowWiki 是如何让 AI Agent 一句话操作知识库的]*

*系列目录：[第一篇：Karpathy LLM Wiki 构想 + 6 缺口 + FlowWiki 开源首发](#) | [上一篇：L7 场景可插拔设计](#) | [下一篇：v0.1.0 → v0.2.0 进化之路](#)*

*GitHub：[xiejianjun000/FlowWiki](https://github.com/xiejianjun000/FlowWiki)*
