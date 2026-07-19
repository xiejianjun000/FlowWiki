# Fulltext Skill — 按需加载 raw/ 全文

## 功能

根据 wiki/ 页面"## 原文指针"段中给出的路径，按需 read raw/ 原文全文。

**设计背景**：宪法 SCHEMA §1.3 / §4.2 规定 wiki/ 主体只存摘要 + 判断要点，禁止搬运全文。
当 AI 或人类需要逐字引用法条 / 标准 / 细则原文时，通过本 skill 加载 raw/ 全文。

## 触发场景

- AI 在 query 流程中需要逐字引用法条原文（引用到条/款/项）
- 用户问"这条法条原文怎么说"
- 评查报告需要精确引用原文条款
- ACE Reflector 检查"幻觉"时需要回查 raw 原文验证

## 输入

```json
{
  "pointer_path": "../raw/laws/生态环境法典.md",
  "section": "第X章 第X条（可选，定位到具体条款）",
  "quote_intent": "逐字引用|概括转述|事实核查"
}
```

也可接收 wiki/ 页面路径，自动从"## 原文指针"段解析：
```json
{
  "wiki_page": "wiki/concepts/xxx.md",
  "auto_parse_pointer": true
}
```

## 输出

```json
{
  "status": "success|failed",
  "raw_path": "raw/laws/生态环境法典.md",
  "section_found": "第123条",
  "full_text": "（原文片段）",
  "quote_format": "「第123条 ……」（《生态环境法典》）",
  "backlink": "wiki/concepts/xxx.md"
}
```

## 执行流程

1. 解析 pointer_path，定位 raw/ 文件
2. 若提供 section，在原文中查找定位（正则 + 模糊匹配）
3. 提取目标段落全文
4. 生成符合法条引用规范的 quote_format
5. 回链来源 wiki 页面

## 约束

- 路径必须以 `../raw/` 或 `raw/` 开头，禁止跨库读取
- 若 raw 文件不存在，返回 failed 并提示"指针悬空，需 Curator 修复"
- section 未命中时返回整篇全文 + warning
- 引用必须标注来源（《XX法》第X条）+ 回链 wiki 页面
- **绝不修改 raw/ 文件**（SCHEMA §6.1 只读铁律）

## 关联

- 宪法依据：[SCHEMA.md §1.3 原文指针铁律](../../SCHEMA.md)
- 入仓时由 [ingest skill](./ingest/SKILL.md) 调用 ACE 生成指针段
- 由 [lint skill](./lint/SKILL.md) 定期检查指针是否悬空
