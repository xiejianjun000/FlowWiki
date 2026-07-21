#!/usr/bin/env python3
"""
ACE Review — FlowWiki 反思循环脚本（v3.1 含 VERIFY-BEFORE-WRITE）

Generator → Reflector(含去重+矛盾检测) → Verifier(引用验证) → Curator(含少数派覆盖) → GapLearner

v3.1 新增 (2026-07-22):
  - VERIFY-BEFORE-WRITE 引用验证（Ekgardt/llm-wiki 模式）：
    写入 wiki/ 前逐条验证 source 引用是否可追溯到 raw/ 原始文件
    验证失败的内容自动隔离到 wiki/_quarantine/
    支持 --no-verify-references 跳过验证

v3.0 新增:
  - 少数派分支（伴侣式记忆 §5.7）：矛盾检测 + 缓冲积累 + 阈值晋升
  - git-snapshot 防御性写入（Ar9av v2026.07.6）：写入前 stash + 失败回滚

用法:
  python _scripts/ace_review.py --raw <raw_path>
  python _scripts/ace_review.py --raw <raw_path> --no-verify-references  # 跳过引用验证
  python _scripts/ace_review.py --raw <raw_path> --no-snapshot  # 跳过 snapshot
  python _scripts/ace_review.py --dedup-check <file_path>
  python _scripts/ace_review.py --audit-wiki
  python _scripts/ace_review.py --audit-quarantine  # 审查隔离区
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter

# ── 配置 ──────────────────────────────────────────────
KB_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = KB_ROOT / ".memory"
ACE_DIR = MEMORY_DIR / "ace"
ZK_DIR = MEMORY_DIR / "zettelkasten"
GAP_DIR = MEMORY_DIR / "gaps"
CONFLICT_DIR = MEMORY_DIR / "conflict"
MINORITY_DIR = MEMORY_DIR / "minority"    # 少数派分支（伴侣式记忆 §5.7）
OPS_DIR = MEMORY_DIR / "ops"
WIKI_DIR = KB_ROOT / "wiki"

# 去重阈值
DEDUP_HEADING_OVERLAP_RATIO = 0.3   # 章节标题重叠 ≥30% → 标记潜在重复
DEDUP_TEXT_SIMILARITY = 0.4         # 文本词重叠 ≥40% → 标记高度重复
DEDUP_CONSOLIDATE_THRESHOLD = 0.6   # 文本重叠 ≥60% → Curator 出 consolidate

QUARANTINE_DIR = WIKI_DIR / "_quarantine"  # 隔离区（VERIFY-BEFORE-WRITE 失败内容）
RAW_DIR = KB_ROOT / "raw"

for d in [ACE_DIR, ZK_DIR, GAP_DIR, CONFLICT_DIR, MINORITY_DIR, OPS_DIR, QUARANTINE_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ── 辅助函数 ──────────────────────────────────────────

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def next_seq(dir_path: Path) -> int:
    prefix = today().replace("-", "")
    max_n = 0
    if dir_path.exists():
        for f in dir_path.iterdir():
            m = re.search(rf"{prefix}(\d{{3}})", f.stem)
            if m:
                n = int(m.group(1))
                if n > max_n:
                    max_n = n
    return max_n + 1


def write_log(op: str, obj: str, result: str, ref: list = None):
    log_file = OPS_DIR / f"{today()}.jsonl"
    entry = {
        "time": datetime.now().isoformat(),
        "op": op,
        "object": obj,
        "result": result,
        "actor": "ai",
        "ref": ref or [],
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"<读取出错: {e}>"


def extract_frontmatter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip("\"'")
    return fm


def strip_frontmatter(text: str) -> str:
    """移除 frontmatter，只保留正文"""
    return re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, flags=re.DOTALL)


def extract_headings(text: str, level: str = "##") -> list:
    """提取指定级别的标题"""
    result = []
    for line in text.split("\n"):
        if line.startswith(level) and not line.startswith("###"):
            clean = re.sub(r"^#{1,5}\s*", "", line).strip()
            clean = re.sub(r"（.*）", "", clean).strip()  # 去除括号内的补充说明
            if clean:
                result.append(clean)
    return result


def extract_keywords(text: str) -> set:
    """从正文中提取有意义的词作为关键词集合（用于相似度比较）"""
    stripped = strip_frontmatter(text)
    # 去除标点和数字引用的干扰
    words = re.findall(r"[一-鿿\w]{2,}", stripped)
    # 过滤掉纯数字和单字
    significant = {w for w in words if len(w) >= 2 and not w.isdigit()}
    return significant


def compute_jaccard_similarity(set_a: set, set_b: set) -> float:
    """Jaccard 相似度：交集/并集"""
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def find_similar_pages(new_file_text: str, wiki_dir: Path, source_path: str = "") -> list:
    """
    核心去重函数：
    对新文件与所有已有 wiki 页做标题匹配 + 文本相似度比较
    返回排序后的相似页列表
    """
    new_body = strip_frontmatter(new_file_text)
    new_headings = extract_headings(new_body)
    new_keywords = extract_keywords(new_body)

    if not new_headings and not new_keywords:
        return []

    matches = []

    for existing in sorted(wiki_dir.rglob("*.md")):
        # 排除自己
        if str(existing) == source_path:
            continue
        # 排除 .memory/ 和 _templates/ 和根目录文件
        if ".memory" in existing.parts or "_templates" in existing.parts:
            continue
        if existing.parent == KB_ROOT:
            continue

        try:
            existing_text = existing.read_text(encoding="utf-8")
        except Exception:
            continue

        existing_body = strip_frontmatter(existing_text)
        existing_headings = extract_headings(existing_body)

        # 标题重叠度
        heading_overlap = 0.0
        if new_headings and existing_headings:
            new_set = set(h.strip() for h in new_headings)
            exist_set = set(h.strip() for h in existing_headings)
            heading_overlap = compute_jaccard_similarity(new_set, exist_set)

        # 文本相似度
        existing_keywords = extract_keywords(existing_body)
        text_sim = compute_jaccard_similarity(new_keywords, existing_keywords)

        if heading_overlap > DEDUP_HEADING_OVERLAP_RATIO or text_sim > DEDUP_TEXT_SIMILARITY:
            rel = existing.relative_to(KB_ROOT)
            matches.append({
                "file": str(rel),
                "heading_overlap": round(heading_overlap, 3),
                "text_similarity": round(text_sim, 3),
                "overlapping_headings": list(set(new_headings) & set(existing_headings)),
            })

    # 按相似度从高到低排序
    matches.sort(key=lambda x: max(x["heading_overlap"], x["text_similarity"]), reverse=True)
    return matches


# ── 格式清洗函数（raw→wiki 编译）────────────────────

def clean_raw_html(raw_text: str) -> str:
    """清洗 raw 源中的网页残留（导航/版权/跳转提示/空白）"""
    text = raw_text

    # 删除 "您访问的链接即将离开" 类跳转提示
    text = re.sub(r"您访问的链接即将离开.*?(是否继续|继续访问)", "", text)

    # 删除常见网页框架元素
    text = re.sub(r"首页\s*[>›》]\s*政务公开\s*[>›》].*", "", text)
    text = re.sub(r"来源：.*?(日期|发布时间)", "", text)
    text = re.sub(r"【字体：[大小]+\s*(默认|放大|缩小)】", "", text)
    text = re.sub(r"版权所有[©\s\d\-–—.年]*(XXX|网站|所有).*", "", text)
    text = re.sub(r"相关阅读|推荐阅读|下一篇|上一篇", "", text)

    # 删除 HTML 残留标签
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<![CDATA\[.*?\]\]>", "", text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # 删除裸露 HTML 标签（保留 <br> 换行转义）
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)

    # 压缩连续空行（最多1个）
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 删除行首行尾空白
    lines = text.split("\n")
    lines = [line.strip() for line in lines]
    text = "\n".join(lines)

    # 删除纯空行后的多余换行
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def detect_and_convert_tables(raw_text: str) -> str:
    """识别网页中的表格结构并转为 markdown 表格"""
    # 尝试识别 HTML <table>
    table_pattern = re.compile(r"<table[^>]*>(.*?)</table>", re.DOTALL)
    tables_found = table_pattern.findall(raw_text)

    result = raw_text
    for table_html in tables_found:
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, re.DOTALL)
        md_rows = []
        for row in rows:
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.DOTALL)
            if cells:
                cleaned = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
                md_rows.append("| " + " | ".join(cleaned) + " |")

        if md_rows:
            md_table = "\n".join(md_rows)
            # 分隔线（在第一行后加）
            parts = md_table.split("\n")
            col_count = parts[0].count("|") - 1
            separator = "|" + "---|" * col_count
            parts.insert(1, separator)
            md_table = "\n".join(parts)
            result = result.replace(table_html, "\n\n" + md_table + "\n\n", 1)

    return result


def format_wiki_body(raw_text: str, title: str) -> str:
    """
    raw→wiki 正文编译主函数
    按 wiki/meta/入库文档格式标准.md 执行清洗+格式化
    """
    text = clean_raw_html(raw_text)
    text = detect_and_convert_tables(text)

    # 规范化标题层级（去掉正文中的 # 标题，从 ## 开始）
    lines = text.split("\n")
    formatted = []
    for line in lines:
        # 正文 # 改为 ##（正文不从 # 开始）
        if line.startswith("# ") and not line.startswith("## "):
            line = "## " + line[2:]
        # 保持 #### 以内
        if line.startswith("#####"):
            line = "#### " + line[5:].strip()
        formatted.append(line)

    return "\n".join(formatted)


# ── 防御性写入（引自 Ar9av v2026.07.6 git-snapshot）───

def git_snapshot_guard(description: str = "ace-review") -> str:
    """在 ACE 写入前创建 git stash 快照。

    写入成功后验证 lint，若 lint 报错则可 git stash pop 回滚。

    返回 snapshot 引用，失败时返回空字符串。
    """
    try:
        result = subprocess.run(
            ["git", "stash", "push", "-m", f"snapshot: {description} ({today()})"],
            cwd=str(KB_ROOT), capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and "No local changes" not in result.stdout:
            return f"stash: {description}"
        elif "No local changes" in result.stdout:
            return ""  # 无可暂存变更，无需 snapshot
        else:
            print(f"  ⚠️  git stash 失败: {result.stderr.strip()}")
            return ""
    except Exception as e:
        print(f"  ⚠️  git snapshot 异常: {e}")
        return ""


def git_snapshot_pop() -> bool:
    """回滚到最近的 git stash snapshot。"""
    try:
        result = subprocess.run(
            ["git", "stash", "pop"],
            cwd=str(KB_ROOT), capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0
    except Exception:
        return False


# ── 少数派分支（引自伴侣式记忆 §5.7）─────────────────

# 矛盾检测阈值
CONTRADICTION_HINT_WORDS = [
    "但是", "然而", "相反", "推翻", "不同", "不对", "矛盾", "修正",
    "实际上", "不同于", "不适用", "不成立",
]

MINORITY_EVIDENCE_THRESHOLD = 3  # 积累 ≥3 条独立证据后触发重审


def phase_minority_check(gen_result: dict, wiki_dir: Path) -> list:
    """检测新内容是否与已有 wiki 页面存在实质性矛盾。

    与 phase_reflector 的去重检测不同：
    - 去重检测 → 相似性（信息重复）
    - 矛盾检测 → 对立性（断言冲突）

    矛盾不直接拒绝 → 缓存到 .memory/minority/ 分支
    积累多源证据后触发 Curator 重审（冲突路由 V4→V5）
    """
    contradictions = []
    new_text = gen_result.get("full_content", "")
    new_body = strip_frontmatter(new_text)
    new_title = gen_result.get("title", "")

    if not wiki_dir.exists():
        return []

    for existing in sorted(wiki_dir.rglob("*.md")):
        if ".memory" in existing.parts:
            continue

        try:
            existing_text = existing.read_text(encoding="utf-8")
        except Exception:
            continue

        existing_body = strip_frontmatter(existing_text)
        fm = extract_frontmatter(existing_text)

        # 跳过已归档或衰减的页面（不参与矛盾检测）
        status = fm.get("status", "")
        if status in ("archived", "decaying"):
            continue

        # 粗粒度：检查是否关于同一主题
        title_overlap = False
        new_words = set(re.findall(r"[\w\u4e00-\u9fff]{2,}", new_title))
        for line in existing_body.split("\n"):
            if line.startswith("# "):
                exist_words = set(re.findall(r"[\w\u4e00-\u9fff]{2,}", line))
                jaccard = len(new_words & exist_words) / max(1, len(new_words | exist_words))
                if jaccard > 0.3:
                    title_overlap = True
                    break

        if not title_overlap:
            continue

        # 细粒度：检测可能的矛盾断言（含矛盾提示词）
        contradiction_hints = []
        for hint in CONTRADICTION_HINT_WORDS:
            if hint in new_body:
                contradiction_hints.append(hint)

        if contradiction_hints:
            rel = existing.relative_to(KB_ROOT)
            existing_confidence = fm.get("confidence", "unknown")
            contradictions.append({
                "existing_page": str(rel),
                "existing_confidence": existing_confidence,
                "existing_status": status,
                "hints": contradiction_hints,
                "new_title": new_title,
            })

    return contradictions


def write_minority_branch(gen_result: dict, contradictions: list,
                           raw_path: str) -> list:
    """将矛盾证据写入少数派分支。

    分支文件格式：
    - 每条矛盾一条记录
    - 记录源文件、矛盾描述、现有页面引用
    - 记录时间戳（用于多周期缓冲压力计算）
    """
    branch_files = []
    for i, contra in enumerate(contradictions):
        seq = next_seq(MINORITY_DIR)
        branch_file = MINORITY_DIR / f"minority-{today()}-{seq:03d}.md"

        content = f"""# Minority Branch — {gen_result.get('title', 'unknown')}

## 矛盾描述
- **新来源**: [[{raw_path}]]
- **标题**: {gen_result.get('title', 'unknown')}
- **冲突页面**: [[{contra['existing_page']}]]
- **冲突提示词**: {', '.join(contra['hints'])}
- **现有页置信度**: {contra['existing_confidence']}

## 新证据摘要
{gen_result.get('full_content', '')[:800]}

## 状态
status: open
created: {now()}
cycle: 1

---
> 少数派分支（伴侣式记忆 §5.7）
> 不静默关闭。积累 ≥{MINORITY_EVIDENCE_THRESHOLD} 条独立证据后触发 Curator 重审。
"""
        branch_file.write_text(content, encoding="utf-8")
        branch_files.append(branch_file)
        print(f"  🌿 少数派分支: {branch_file.relative_to(KB_ROOT)} → "
              f"冲突于 {contra['existing_page']}")

    return branch_files


def check_minority_accumulation(existing_page: str) -> dict:
    """检查针对特定页面的少数派证据是否达到晋升阈值。

    扫描 .memory/minority/ 中所有引用此页面的分支文件。
    """
    if not MINORITY_DIR.exists():
        return {"accumulated": False, "count": 0}

    hits = []
    for branch_file in MINORITY_DIR.glob("minority-*.md"):
        try:
            content = branch_file.read_text(encoding="utf-8")
        except Exception:
            continue
        if existing_page in content:
            # 提取 cycle 数
            cycle_match = re.search(r"cycle:\s*(\d+)", content)
            cycle = int(cycle_match.group(1)) if cycle_match else 1
            hits.append({
                "file": str(branch_file.relative_to(KB_ROOT)),
                "cycle": cycle,
            })

    accumulated = len(hits) >= MINORITY_EVIDENCE_THRESHOLD
    return {
        "accumulated": accumulated,
        "count": len(hits),
        "files": hits,
        "threshold": MINORITY_EVIDENCE_THRESHOLD,
    }


# ── 阶段 1.5: VERIFY-BEFORE-WRITE 引用验证（Ekgardt 模式）───

# 引用模式：从内容中提取的所有可能引用形式
REFERENCE_PATTERNS = [
    # [[wikilink]] 格式
    (re.compile(r"\[\[([^\]]+)\]\]"), "wikilink"),
    # raw/ 路径引用
    (re.compile(r"raw/([^\s\)\]\n,]+\.md)"), "raw_path"),
    # ../raw/ 相对路径
    (re.compile(r"\.\./raw/([^\s\)\]\n,]+\.md)"), "relative_raw_path"),
    # "参见 xxx" 等引用句式
    (re.compile(r"(?:参见|参考|详见|引用|来源)[：:]\s*([^\n，。,\.]{3,80})"), "explicit_ref"),
    # sources: 字段中的文件引用
    (re.compile(r"sources?[：:]\s*\[([^\]]+)\]"), "sources_field"),
]

# 虚构引用模式：检测 LLM 可能编造的"看起来像真实"的引用
FABRICATED_PATTERNS = [
    # 无中生有的法规编号（如"《XX法》第Y条"模式下找不到原文）
    re.compile(r"《([^》]{2,30})》第([\d一二三四五六七八九十百]+)条"),
    # URL 指向不存在的页面
    re.compile(r"https?://[^\s\)\]\n]+"),
    # 外部文档引用（非 raw/ 路径）
    re.compile(r"([\w-]+\.(?:pdf|docx?|xlsx?))\s*(?:中|所述|记载)"),
]

# 参考验证的最低通过分数（0-1 之间）
MIN_VERIFICATION_SCORE = 0.6


def extract_references(content: str) -> list:
    """从生成内容中提取所有声称的引用。

    返回引用列表，每项包含引用文本、类型和位置（行号）。
    """
    refs = []
    lines = content.split("\n")
    text = content

    for pattern, ref_type in REFERENCE_PATTERNS:
        for match in pattern.finditer(text):
            ref_text = match.group(1).strip()
            if ref_text and len(ref_text) > 2:
                # 计算大致行号
                pos = match.start()
                line_num = text[:pos].count("\n") + 1
                refs.append({
                    "text": ref_text,
                    "type": ref_type,
                    "line": line_num,
                    "full_match": match.group(0),
                })

    # 去重
    seen = set()
    unique_refs = []
    for r in refs:
        key = (r["text"][:80], r["type"])
        if key not in seen:
            seen.add(key)
            unique_refs.append(r)

    return unique_refs


def verify_reference(ref: dict, raw_dir: Path) -> dict:
    """验证单个引用是否可追溯到 raw/ 源文件。

    验证策略：
    1. 如果是 raw/ 文件路径 → 直接检查文件是否存在
    2. 如果是 wikilink → 检查 wiki/ 中是否存在对应页面
    3. 如果是显式引用 → 在 raw/ 中全文搜索匹配内容
    4. 如果是 sources 字段 → 逐条检查列出的源文件
    """
    result = {
        "ref": ref,
        "verified": False,
        "source_file": None,
        "method": "none",
        "confidence": 0.0,
    }

    text = ref["text"]
    ref_type = ref["type"]

    if ref_type in ("raw_path", "relative_raw_path"):
        # 直接文件路径验证
        raw_file = raw_dir / text
        if raw_file.exists():
            result["verified"] = True
            result["source_file"] = str(raw_file.relative_to(KB_ROOT))
            result["method"] = "direct_file"
            result["confidence"] = 1.0
        else:
            result["verified"] = False
            result["method"] = "file_missing"

    elif ref_type == "wikilink":
        # wikilink → 检查 wiki/ 或 raw/ 是否存在对应页面
        page_path = None
        wiki_candidate = WIKI_DIR / f"{text}.md"
        raw_candidate = raw_dir / f"{text}.md"
        if wiki_candidate.exists():
            page_path = wiki_candidate
            result["method"] = "wiki_page"
        elif raw_candidate.exists():
            page_path = raw_candidate
            result["method"] = "raw_page"

        if page_path:
            result["verified"] = True
            result["source_file"] = str(page_path.relative_to(KB_ROOT))
            result["confidence"] = 0.9  # wikilink 存在但内容可能不匹配

    elif ref_type == "explicit_ref":
        # 显式引用 → 在 raw/ 中全文搜索
        keywords = [w for w in text[:60].split() if len(w) >= 2]
        if keywords:
            search_term = " ".join(keywords[:3])  # 取前3个关键词
            raw_files = list(raw_dir.rglob("*.md"))
            for raw_file in raw_files:
                try:
                    file_content = raw_file.read_text(encoding="utf-8")
                    if search_term in file_content:
                        result["verified"] = True
                        result["source_file"] = str(raw_file.relative_to(KB_ROOT))
                        result["method"] = "content_search"
                        result["confidence"] = 0.7  # 粗匹配，中等置信度
                        break
                except Exception:
                    continue

    elif ref_type == "sources_field":
        # sources 字段中的文件列表
        source_files = [s.strip().strip('"').strip("'") for s in text.split(",")]
        verified_sources = []
        for sf in source_files:
            if not sf:
                continue
            raw_file = raw_dir / sf.lstrip("/")
            if raw_file.exists():
                verified_sources.append(sf)
        if verified_sources:
            result["verified"] = True
            result["source_file"] = ", ".join(verified_sources)
            result["method"] = "sources_field"
            result["confidence"] = 1.0 if len(verified_sources) == len(source_files) else 0.5

    return result


def detect_fabricated_references(content: str) -> list:
    """检测 LLM 可能编造的虚构引用。

    关注模式：
    - 法规条文引用（无对应 raw/ 文件）
    - 外部 URL（可能已失效）
    - 看起来像文件名但实际不存在的引用
    """
    fabricated = []

    for pattern in FABRICATED_PATTERNS:
        for match in pattern.finditer(content):
            fabricated.append({
                "text": match.group(0),
                "pattern_type": pattern.pattern[:50],
                "line": content[:match.start()].count("\n") + 1,
            })

    return fabricated


def phase_verify_references(gen_result: dict, raw_dir: Path,
                            min_score: float = MIN_VERIFICATION_SCORE) -> dict:
    """VERIFY-BEFORE-WRITE: 在写入 wiki/ 之前验证所有引用。

    这是 FlowWiki v3.1 的核心防御层，引自 Ekgardt/llm-wiki 的
    "确定性引用验证" 模式 + swarmvault 的 "边来源标签" 思路。

    返回:
        {
            "status": "pass" | "quarantine" | "partial",
            "score": 0.0-1.0,
            "references": [...],
            "fabricated": [...],
            "quarantine_reason": str or None,
        }
    """
    content = gen_result.get("full_content", "")
    title = gen_result.get("title", "")
    fm = gen_result.get("frontmatter", {})

    # 1. 提取所有引用
    refs = extract_references(content)

    # 2. 逐条验证
    verified = []
    failed = []
    for ref in refs:
        vr = verify_reference(ref, raw_dir)
        if vr["verified"]:
            verified.append(vr)
        else:
            failed.append(vr)

    # 3. 检测虚构引用
    fabricated = detect_fabricated_references(content)

    # 4. 计算验证分数
    total_refs = len(refs)
    if total_refs == 0:
        # 没有引用也不算问题——可能只是元页面
        score = 0.5  # 中性分数
        status = "partial"
    else:
        verified_count = len(verified)
        score = verified_count / total_refs if total_refs > 0 else 0.0

        if score >= min_score:
            status = "pass"
        elif score >= 0.3:
            status = "partial"
        else:
            status = "quarantine"

    # 5. 如果 frontmatter 有 sources 但都不存在 → 强制 quarantine
    sources = fm.get("sources", "")
    if sources and sources not in ("[]", ""):
        source_list = [s.strip().strip('"[]\'') for s in sources.split(",")]
        all_missing = True
        for s in source_list:
            if (raw_dir / s.lstrip("/")).exists() or (raw_dir / "root-cause" / s).exists():
                all_missing = False
                break
        if all_missing and source_list:
            status = "quarantine"
            fabricated.append({
                "text": f"frontmatter sources 全部不存在: {sources}",
                "pattern_type": "frontmatter_sources",
                "line": 1,
            })

    reason = None
    if status == "quarantine":
        reasons = []
        if failed:
            reasons.append(f"{len(failed)}/{total_refs} 引用无法验证")
        if fabricated:
            reasons.append(f"{len(fabricated)} 处疑似虚构引用")
        reason = "; ".join(reasons) if reasons else "引用验证失败"

    return {
        "status": status,
        "score": round(score, 3),
        "total_refs": total_refs,
        "verified_count": len(verified),
        "failed_count": len(failed),
        "verified_refs": verified,
        "failed_refs": failed,
        "fabricated": fabricated,
        "quarantine_reason": reason,
    }


def write_quarantine(gen_result: dict, verify_result: dict,
                     raw_path: str) -> Path:
    """将验证失败的内容写入隔离区 wiki/_quarantine/。

    隔离内容保留完整正文，添加验证报告头，
    等待人工审核后手动移动到正式 wiki/ 目录。
    """
    title = gen_result.get("title", "untitled")
    slug = re.sub(r"[^\w\s-]", "", title).strip().lower()
    slug = re.sub(r"[-\s]+", "-", slug)[:60]
    seq = next_seq(QUARANTINE_DIR)
    quarantine_file = QUARANTINE_DIR / f"q-{today()}-{seq:03d}-{slug}.md"

    # 构建隔离报告
    report = f"""# 🚫 QUARANTINED: {title}

> **状态**: 隔离中 — 引用验证未通过，等待人工审核
> **日期**: {today()}
> **验证分数**: {verify_result['score']:.0%} ({verify_result['verified_count']}/{verify_result['total_refs']})
> **隔离原因**: {verify_result.get('quarantine_reason', '引用验证失败')}

## 引用验证报告

### 已验证的引用 ({verify_result['verified_count']})
"""
    for vr in verify_result.get("verified_refs", []):
        ref = vr["ref"]
        report += f"- ✅ `{ref['text'][:60]}` → {vr.get('source_file', 'N/A')} ({vr['method']}, 置信度 {vr['confidence']:.0%})\n"

    report += f"""
### 验证失败的引用 ({verify_result['failed_count']})
"""
    for fr in verify_result.get("failed_refs", []):
        ref = fr["ref"]
        report += f"- ❌ `{ref['text'][:60]}` → 未找到 ({ref['method']})\n"

    if verify_result.get("fabricated"):
        report += f"""
### ⚠️ 疑似虚构引用 ({len(verify_result['fabricated'])})
"""
        for fab in verify_result["fabricated"]:
            report += f"- 🔍 `{fab['text'][:80]}` (行 {fab['line']})\n"

    report += f"""
---
## 原始内容

> 以下为生成内容原文，待审核后决定是否入库。

"""
    report += gen_result.get("full_content", "")

    report += f"""

---
> 隔离于 {now()} | 源文件: {raw_path}
> 操作: 手动审核后执行 `mv` 到 wiki/ 目录，或 `rm` 删除
"""

    quarantine_file.write_text(report, encoding="utf-8")
    print(f"  🚫 隔离: {quarantine_file.relative_to(KB_ROOT)}")
    write_log("quarantine", f"{raw_path} → {quarantine_file.name}",
              "quarantined", [str(quarantine_file)])

    return quarantine_file


def audit_quarantine() -> list:
    """审查隔离区：列出所有待审核的隔离内容及其状态。"""
    if not QUARANTINE_DIR.exists():
        print("  ✅ 隔离区为空")
        return []

    items = sorted(QUARANTINE_DIR.glob("q-*.md"))
    if not items:
        print("  ✅ 隔离区为空")
        return []

    print(f"\n{'='*55}")
    print(f"  隔离区审查 | {len(items)} 项待审核")
    print(f"{'='*55}\n")

    results = []
    for item in items:
        try:
            text = item.read_text(encoding="utf-8")
        except Exception:
            continue

        # 提取关键信息
        title_match = re.search(r"# 🚫 QUARANTINED: (.+)", text)
        score_match = re.search(r"验证分数\*\*: (\d+%?)", text)
        reason_match = re.search(r"隔离原因\*\*: (.+)", text)

        title = title_match.group(1).strip() if title_match else item.stem
        score = score_match.group(1) if score_match else "?"
        reason = reason_match.group(1).strip() if reason_match else "未知"

        results.append({
            "file": str(item.relative_to(KB_ROOT)),
            "title": title,
            "score": score,
            "reason": reason,
            "size": len(text),
        })

        icon = "🔴" if "0%" in score else "🟡"
        print(f"  {icon} {title[:50]}")
        print(f"     分数: {score} | 原因: {reason[:60]}")
        print(f"     路径: {item.relative_to(KB_ROOT)}")
        print()

    if not results:
        print("  ✅ 隔离区为空")
    else:
        print(f"  共 {len(results)} 项待审核。")
        print(f"  操作建议: 手动审核每项后移入 wiki/ 或删除。")

    return results


# ── 阶段一：Generator ─────────────────────────────────

def phase_generator(raw_path: Path) -> dict:
    content = read_file(raw_path)
    fm = extract_frontmatter(content)
    title = fm.get("标题") or fm.get("title") or raw_path.stem

    categories = []
    rel_path = raw_path.relative_to(KB_ROOT) if raw_path.is_relative_to(KB_ROOT) else raw_path
    if "执法" in str(rel_path) or "eco" in str(rel_path).lower():
        categories.append("enforcement-review")
    if "法律" in str(rel_path) or "law" in str(rel_path).lower():
        categories.append("legal")

    lines = content.count("\n") + 1
    has_frontmatter = bool(fm)
    estimated_type = "article"
    if lines > 200:
        estimated_type = "document"
    elif lines < 20:
        estimated_type = "note"

    keywords = []
    if "触发词" in fm:
        keywords = [k.strip().strip('"[]') for k in fm["触发词"].split(",")]

    # 提取章节结构
    body = strip_frontmatter(content)
    headings = extract_headings(body)

    return {
        "raw_path": str(raw_path),
        "title": title,
        "frontmatter": fm,
        "has_frontmatter": has_frontmatter,
        "categories": categories,
        "lines": lines,
        "estimated_type": estimated_type,
        "keywords": keywords,
        "headings": headings,
        "full_content": content,
        "generated_at": now(),
    }


# ── 阶段二：Reflector（含内容去重）─────────────────────

def phase_reflector(gen_result: dict, wiki_dir: Path) -> list:
    """Reflector 阶段：完整性检查 + 去重 + 矛盾检测"""
    issues = []
    title = gen_result["title"]
    fm = gen_result["frontmatter"]

    # 1. frontmatter 完整性
    required = ["标题", "layer", "type", "触发词", "风险等级", "status"]
    for field in required:
        if field not in fm:
            issues.append({
                "severity": "warning",
                "type": "frontmatter",
                "detail": f"缺少前置字段: {field}",
            })

    # 2. 同名页检查
    if wiki_dir.exists():
        for existing in wiki_dir.rglob(f"*.md"):
            existing_fm = extract_frontmatter(read_file(existing))
            existing_title = existing_fm.get("标题") or existing_fm.get("title") or existing.stem
            if existing_title == title and existing != gen_result.get("raw_path"):
                issues.append({
                    "severity": "info",
                    "type": "potential_conflict",
                    "detail": f"同名页已存在: {existing.relative_to(KB_ROOT)}",
                })

    # 3. 内容质量
    preview = gen_result.get("full_content", "")
    if len(preview.strip()) < 50:
        issues.append({
            "severity": "error",
            "type": "content_too_short",
            "detail": "内容过短(<50字符)，可能不完整",
        })

    if not gen_result.get("keywords"):
        issues.append({
            "severity": "warning",
            "type": "missing_keywords",
            "detail": "未提取到关键词（触发词）",
        })

    # 4. ★ 内容级去重检测
    content = gen_result.get("full_content", "")
    if content and wiki_dir.exists():
        similar = find_similar_pages(content, wiki_dir, str(gen_result.get("raw_path", "")))
        for dup in similar[:5]:  # 最多报告 Top5
            max_sim = max(dup["heading_overlap"], dup["text_similarity"])
            if dup["overlapping_headings"]:
                detail = (f"与 {dup['file']} 内容重复"
                          f"（标题重叠 {dup['heading_overlap']:.0%}，"
                          f"文本相似 {dup['text_similarity']:.0%}），"
                          f"重叠主题：{', '.join(dup['overlapping_headings'][:3])}")
            else:
                detail = (f"与 {dup['file']} 内容相似"
                          f"（文本相似 {dup['text_similarity']:.0%}）")

            severity = "error" if max_sim >= DEDUP_CONSOLIDATE_THRESHOLD else "warning"
            issues.append({
                "severity": severity,
                "type": "content_duplicate",
                "detail": detail,
                "dup_file": dup["file"],
                "similarity": max_sim,
            })

    return issues


# ── 阶段三：Curator（含质量评分 + consolidate）─────────

CONSOLIDATE_THRESHOLD = 0.6

# 质量评分标准（对应 wiki/meta/入库质量标准.md）
def score_quality(gen_result: dict, issues: list) -> dict:
    """
    对入库内容进行 5 维度质量评分（满分 10 分）
    """
    content = gen_result.get("full_content", "")
    body = strip_frontmatter(content) if content else ""
    fm = gen_result.get("frontmatter", {})
    lines = gen_result.get("lines", 0)

    # 1. 信息密度 (0-2)
    body_chars = len(body.strip())
    if body_chars >= 200:
        info_score = 2
    elif body_chars >= 50:
        info_score = 1
    else:
        info_score = 0

    # 2. 结构完整性 (0-2)
    required = ["标题", "layer", "type", "触发词", "风险等级", "status"]
    fm_present = sum(1 for f in required if f in fm)
    headings = gen_result.get("headings", [])
    if fm_present == 6 and len(headings) >= 2:
        struct_score = 2
    elif fm_present >= 5 and len(headings) >= 1:
        struct_score = 1
    else:
        struct_score = 0

    # 3. 证据可追溯 (0-2)
    has_sources = bool(fm.get("sources", "")) and fm["sources"] not in ("[]", "")
    has_confidence = bool(fm.get("confidence", ""))
    if has_sources and has_confidence:
        trace_score = 2
    elif has_sources or has_confidence:
        trace_score = 1
    else:
        trace_score = 0

    # 4. 内容独特性 (0-2)
    dup_issues = [i for i in issues if i["type"] == "content_duplicate"]
    dup_similarities = [i["similarity"] for i in dup_issues]
    max_dup = max(dup_similarities) if dup_similarities else 0.0
    if max_dup >= 0.6:
        uniq_score = 0
    elif max_dup >= 0.3:
        uniq_score = 1
    else:
        uniq_score = 2

    # 5. 可操作性 (0-2, SOP/checklist 类必检)
    page_type = fm.get("type", "")
    is_sop = page_type.lower() in ("sop", "checklist", "playbook", "")
    if is_sop:
        # 检查是否有步骤/清单关键词
        step_indicators = ["步骤", "1.", "①", "流程", "核验", "检查", "清单"]
        has_steps = any(indicator in body for indicator in step_indicators)
        action_score = 2 if has_steps else (1 if len(body) > 200 else 0)
    else:
        action_score = 2  # 非 SOP 默认满分

    total = info_score + struct_score + trace_score + uniq_score + action_score

    return {
        "total": total,
        "details": {
            "info_density": info_score,
            "structure": struct_score,
            "traceability": trace_score,
            "uniqueness": uniq_score,
            "actionability": action_score,
        },
        "max_duplication": max_dup,
    }


def phase_curator(gen_result: dict, issues: list, max_rounds: int = 3) -> str:
    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    # 质量评分
    quality = score_quality(gen_result, issues)
    score = quality["total"]

    # 决策逻辑：评分优先，异常次之
    if score >= 9:
        return "accept"  # 优质 → 自动入库
    elif score >= 6:
        # 合格，但检查重复
        dup_issues = [i for i in issues if i["type"] == "content_duplicate"]
        dup_similarities = [i["similarity"] for i in dup_issues]
        max_dup_sim = max(dup_similarities) if dup_similarities else 0.0
        if max_dup_sim >= CONSOLIDATE_THRESHOLD:
            return "consolidate"
        elif dup_issues:
            return "accept_with_notes"
        return "accept"
    elif score >= 3 and len(errors) == 0:
        return "label_pending"
    else:
        return "reject"


# ── 阶段四：GapLearner ────────────────────────────────

def phase_gap_learner(gen_result: dict, wiki_dir: Path) -> list:
    gaps = []
    keywords = gen_result.get("keywords", [])

    if wiki_dir.exists():
        existing_pages = set()
        for f in wiki_dir.rglob("*.md"):
            existing_pages.add(f.stem)

        for kw in keywords:
            if kw and not any(kw in p for p in existing_pages):
                gaps.append({
                    "keyword": kw,
                    "detail": f"关键词 '{kw}' 无独立 wiki 页",
                })

    skill_dir = KB_ROOT / ".agents" / "skills" / "enforcement-review"
    if not skill_dir.exists():
        gaps.append({
            "keyword": "skills",
            "detail": "执法评查行业 skill 目录未创建",
        })

    return gaps


# ── 输出生成 ──────────────────────────────────────────

def write_ace_record(gen_result: dict, issues: list, curator_decision: str, gaps: list, quality_score: dict = None):
    seq = next_seq(ACE_DIR)
    ace_file = ACE_DIR / f"ace-{today()}-{seq:03d}.md"
    title = gen_result["title"]
    raw_path = gen_result["raw_path"]

    content = f"""# ACE-{today()}-{seq:03d}

## 源文件
[[{raw_path}]]

## Generator 产出
- 标题：{title}
- 类型：{gen_result.get("estimated_type", "unknown")}
- 行数：{gen_result.get("lines", 0)}
- 章节：{', '.join(gen_result.get("headings", []) or [])}
- 关键词：{', '.join(gen_result.get("keywords", []) or [])}

## Reflector 发现
"""
    if issues:
        for i, issue in enumerate(issues, 1):
            icon = {"error": "🔴", "warning": "🟡", "info": "ℹ️"}.get(issue["severity"], "•")
            content += f"{i}. {icon} **{issue['type']}**: {issue['detail']}\n"
    else:
        content += "无 issue，通过全部检查。\n"

    if quality_score:
        q = quality_score
        d = q["details"]
        content += f"""
## 质量评分
**总分**: {q['total']}/10

| 维度 | 得分 | 满分 |
|------|:----:|:----:|
| 信息密度 | {d['info_density']} | 2 |
| 结构完整性 | {d['structure']} | 2 |
| 证据可追溯 | {d['traceability']} | 2 |
| 内容独特性 | {d['uniqueness']} | 2 |
| 可操作性 | {d['actionability']} | 2 |

"""

    content += f"""
## Curator 决策
**动作**: {curator_decision}

"""
    decisions = {
        "accept": "- ✅ 接受入库 → 生成 ZK 卡片 + 写入 wiki/",
        "accept_with_notes": "- ✅ 接受入库（含重复备注）→ 在页面顶部标注'内容与 XXX 重叠'",
        "consolidate": "- 🔄 建议合并 → 不新建独立页，改为追加到已有页面 + 加时间戳链接",
        "label_pending": "- 🟡 标'待核'（confidence=low）→ 等待人工审核",
        "reject": "- 🔴 退回 Generator → 需重新生成",
    }
    content += decisions.get(curator_decision, f"- {curator_decision}") + "\n"

    if gaps:
        content += """
## GapLearner 发现的知识缺口
"""
        for g in gaps:
            content += f"- 📋 **{g['keyword']}**: {g['detail']}\n"

    content += f"""
## 最终状态
✅ 已完成 ACE 反思循环（{now()}）

---
_由 _scripts/ace_review.py v2.0 自动生成_
"""
    ace_file.write_text(content, encoding="utf-8")
    write_log("ace", f"{raw_path} → {ace_file.name}", "success", [str(ace_file)])
    print(f"  ✅ ACE 记录: {ace_file}")
    return ace_file


def write_gap_cards(gaps: list):
    cards = []
    for gap in gaps:
        seq = next_seq(GAP_DIR)
        gap_file = GAP_DIR / f"gap-{today()}-{seq:03d}.md"
        content = f"""# GAP-{today()}-{seq:03d}

## 缺口描述
{gap['detail']}

## 发现场景
- 触发：ace_review
- 关键词：{gap['keyword']}

## 状态
⬜ 待填补
"""
        gap_file.write_text(content, encoding="utf-8")
        cards.append(gap_file)
        print(f"  📋 Gap 卡片: {gap_file}")
    return cards


def write_log_entry(raw_path: str, result: str):
    log_file = KB_ROOT / "wiki" / "log.md"
    if log_file.exists():
        content = log_file.read_text(encoding="utf-8")
    else:
        content = "# Wiki Operation Log\n\n> 追加式日志\n\n"
    entry = f"## [{today()}] ace_review | {raw_path} | {result}\n"
    log_file.write_text(content + entry, encoding="utf-8")


# ── 全库去重审计模式 ─────────────────────────────────

def audit_wiki_dedup(wiki_dir: Path):
    """扫描全库，找出所有内容重叠的页面对"""
    print(f"\n{'='*55}")
    print("  全库去重扫描")
    print(f"{'='*55}\n")

    all_files = sorted(wiki_dir.rglob("*.md"))
    # 排除 .memory/ 和 _templates/
    all_files = [f for f in all_files if ".memory" not in f.parts and "_templates" not in f.parts]

    dup_pairs = []
    checked = set()

    for i, f1 in enumerate(all_files):
        if f1.parent == KB_ROOT:
            continue
        for f2 in all_files[i + 1:]:
            if f2.parent == KB_ROOT:
                continue
            pair_key = f"{f1.stem}<->{f2.stem}"
            if pair_key in checked:
                continue
            checked.add(pair_key)

            try:
                text1 = f1.read_text(encoding="utf-8")
                text2 = f2.read_text(encoding="utf-8")
            except Exception:
                continue

            keywords1 = extract_keywords(text1)
            keywords2 = extract_keywords(text2)
            sim = compute_jaccard_similarity(keywords1, keywords2)

            headings1 = set(extract_headings(strip_frontmatter(text1)))
            headings2 = set(extract_headings(strip_frontmatter(text2)))
            heading_overlap = compute_jaccard_similarity(headings1, headings2)

            if sim > DEDUP_TEXT_SIMILARITY or heading_overlap > DEDUP_HEADING_OVERLAP_RATIO:
                dup_pairs.append({
                    "file1": str(f1.relative_to(KB_ROOT)),
                    "file2": str(f2.relative_to(KB_ROOT)),
                    "text_sim": round(sim, 3),
                    "heading_overlap": round(heading_overlap, 3),
                    "shared_headings": list(headings1 & headings2)[:3],
                })

    dup_pairs.sort(key=lambda x: max(x["text_sim"], x["heading_overlap"]), reverse=True)

    print(f"  扫描文件: {len(all_files)} 篇")
    print(f"  发现重复对: {len(dup_pairs)}\n")

    if dup_pairs:
        print("  ┌─────┬──────────────────────────────────┬────────┬────────┐")
        print("  │  #  │ 文件对                            │ 文本   │ 标题   │")
        print("  ├─────┼──────────────────────────────────┼────────┼────────┤")
        for i, pair in enumerate(dup_pairs[:20], 1):  # Top20
            f1_short = pair["file1"].split("/")[-1][:20]
            f2_short = pair["file2"].split("/")[-1][:20]
            print(f"  │ {i:3d} │ {f1_short:20s} ↔ {f2_short:20s} │ {pair['text_sim']:.0%}   │ {pair['heading_overlap']:.0%}   │")
        print("  └─────┴──────────────────────────────────┴────────┴────────┘")

    return dup_pairs


# ── 主流程 ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ACE Review v3.1 — FlowWiki 反思循环（含 VERIFY-BEFORE-WRITE）")
    parser.add_argument("--raw", help="raw 源文件路径")
    parser.add_argument("--wiki", default=str(WIKI_DIR), help="wiki 目录路径")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--audit-wiki", action="store_true", help="全库去重扫描模式")
    parser.add_argument("--audit-quarantine", action="store_true", help="审查隔离区（_quarantine/）")
    parser.add_argument("--dedup-check", help="对指定文件做去重检查（不进 ACE 循环）")
    parser.add_argument("--no-snapshot", action="store_true", help="跳过 git snapshot（默认开启）")
    parser.add_argument("--no-verify-references", action="store_true",
                        help="跳过引用验证（默认开启 VERIFY-BEFORE-WRITE）")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki)

    # ── 全库去重模式 ──
    if args.audit_wiki:
        audit_wiki_dedup(wiki_dir)
        return

    # ── 隔离区审查模式 ──
    if args.audit_quarantine:
        audit_quarantine()
        return

    # ── 单文件去重检查模式 ──
    if args.dedup_check:
        check_path = Path(args.dedup_check)
        if not check_path.is_absolute():
            check_path = KB_ROOT / check_path
        if not check_path.exists():
            print(f"❌ 文件不存在: {check_path}")
            sys.exit(1)
        content = read_file(check_path)
        rel = check_path.relative_to(KB_ROOT)
        print(f"\n{'='*50}")
        print(f"  去重检查 | {rel}")
        print(f"{'='*50}\n")
        similar = find_similar_pages(content, wiki_dir, str(check_path))
        if similar:
            print(f"  发现 {len(similar)} 个潜在重复:\n")
            for dup in similar[:10]:
                flag = "🔴" if max(dup["heading_overlap"], dup["text_similarity"]) >= 0.6 else "🟡"
                print(f"  {flag} {dup['file']}")
                print(f"      标题重叠: {dup['heading_overlap']:.0%}  文本相似: {dup['text_similarity']:.0%}")
                if dup["overlapping_headings"]:
                    print(f"      重叠主题: {', '.join(dup['overlapping_headings'][:3])}")
                print()
        else:
            print("  ✅ 未发现内容重复")
        return

    # ── 标准 ACE 循环模式 ──
    if not args.raw:
        parser.print_help()
        sys.exit(1)

    raw_path = Path(args.raw)
    if not raw_path.exists():
        print(f"❌ raw 文件不存在: {raw_path}")
        sys.exit(1)

    # ═══════════════════════════════════════════════════
    # 防御性写入：git snapshot（引自 Ar9av v2026.07.6）
    # ═══════════════════════════════════════════════════
    snapshot_ref = ""
    if not args.no_snapshot:
        snapshot_ref = git_snapshot_guard(f"ace-{raw_path.name}")
        if snapshot_ref:
            print(f"\n🛡️  Git snapshot: {snapshot_ref}")

    print(f"\n{'='*50}")
    print(f"  ACE 反思循环 v3 | {raw_path.name}")
    print(f"{'='*50}\n")

    # 阶段一：Generator
    print("📝 [1/4] Generator — 分析源文件...")
    gen_result = phase_generator(raw_path)
    print(f"     标题: {gen_result['title']}")
    print(f"     类型: {gen_result['estimated_type']}")
    print(f"     行数: {gen_result['lines']}")
    if args.verbose:
        print(f"     关键词: {gen_result['keywords']}")

    # 阶段二：Reflector（含去重 + 矛盾检测）
    print("\n🔍 [2/4] Reflector — 批判检查（含去重 + 矛盾检测）...")
    issues = phase_reflector(gen_result, wiki_dir)
    dup_count = len([i for i in issues if i["type"] == "content_duplicate"])

    # ═══ 少数派分支检测（伴侣式记忆 §5.7）═══
    contradictions = phase_minority_check(gen_result, wiki_dir)
    if contradictions:
        print(f"     🌿 发现 {len(contradictions)} 处潜在矛盾:")
        for contra in contradictions:
            print(f"        → 与 [[{contra['existing_page']}]] 冲突 "
                  f"(提示词: {', '.join(contra['hints'])})")
        # 路由 V4：单源矛盾 → Buffer（缓存到少数派分支）
        branch_files = write_minority_branch(gen_result, contradictions, str(raw_path))

        # 检查是否有页面达到了晋升阈值
        for contra in contradictions:
            acc = check_minority_accumulation(contra["existing_page"])
            if acc["accumulated"]:
                status = "accumulated"  # 标记以达到阈值
                print(f"     ⚡ [[{contra['existing_page']}]] 少数派证据已积累 "
                      f"{acc['count']}/{MINORITY_EVIDENCE_THRESHOLD} → 触发 Curator 重审")
                # 路由 V5：多源多周期 → Compensate（待 Curator 整合）
            else:
                status = "cached"
                print(f"     📥 缓存至少数派分支 ({acc['count']}/{MINORITY_EVIDENCE_THRESHOLD})")
    else:
        print("     ✅ 未检测到矛盾")

    if issues:
        for issue in issues:
            icon = {"error": "🔴", "warning": "🟡", "info": "ℹ️"}.get(issue["severity"], "•")
            print(f"     {icon} [{issue['type']}] {issue['detail']}")
        if dup_count > 0:
            print(f"     → 发现 {dup_count} 处内容重复")
    else:
        print("     ✅ 无 issue")

    # 阶段三：VERIFY-BEFORE-WRITE — 引用验证（v3.1 新增）
    print("\n🔬 [2.5/4] Verifier — 引用溯源验证（VERIFY-BEFORE-WRITE）...")
    verify_result = None
    quarantine_file = None
    if not args.no_verify_references:
        verify_result = phase_verify_references(gen_result, RAW_DIR)
        score_pct = f"{verify_result['score']:.0%}"
        print(f"     验证分数: {score_pct} "
              f"({verify_result['verified_count']}/{verify_result['total_refs']} 通过)")
        if verify_result["status"] == "pass":
            print(f"     ✅ 引用验证通过 → 继续 Curator")
        elif verify_result["status"] == "partial":
            print(f"     ⚠️  部分通过 → 降低置信度至 medium，继续入库")
            # 标记 frontmatter 置信度降低
            gen_result["frontmatter"]["confidence"] = "medium"
            if verify_result["failed_refs"]:
                print(f"     ❌ 失败引用: {len(verify_result['failed_refs'])} 条")
        else:  # quarantine
            print(f"     🚫 引用验证失败 → 隔离到 wiki/_quarantine/")
            print(f"     原因: {verify_result.get('quarantine_reason', '未知')}")
            quarantine_file = write_quarantine(gen_result, verify_result, str(raw_path))
            if verify_result.get("fabricated"):
                for fab in verify_result["fabricated"][:3]:
                    print(f"     🔍 疑似虚构: {fab['text'][:60]} (行 {fab['line']})")
    else:
        print(f"     ⏭️  跳过引用验证 (--no-verify-references)")

    # 阶段四：Curator（如果已被隔离则跳过）
    if quarantine_file:
        decision = "quarantined"
        score = verify_result["score"] * 10 if verify_result else 0
        quality = {"total": int(score), "details": {
            "info_density": 0, "structure": 0, "traceability": 0,
            "uniqueness": 0, "actionability": 0
        }}
        print("\n⚖️  [3/4] Curator — 跳过（内容已隔离）")
    else:
        print("\n⚖️  [3/4] Curator — 质量评分 + 决策...")
        quality = score_quality(gen_result, issues)
        score = quality["total"]
        det = quality["details"]
        print(f"     质量评分: {score}/10")
        print(f"       信息密度: {det['info_density']}/2 | 结构: {det['structure']}/2 | "
              f"溯源: {det['traceability']}/2 | 独特性: {det['uniqueness']}/2 | "
              f"可操作: {det['actionability']}/2")
        decision = phase_curator(gen_result, issues)

    # 少数派分支可能覆盖决策：如果矛盾证据已积累至阈值 → 强制重审
    minority_override = False
    if not quarantine_file:
        for contra in contradictions:
            acc = check_minority_accumulation(contra["existing_page"])
            if acc["accumulated"] and decision == "reject":
                decision = "label_pending"
                minority_override = True
                print(f"     ⚡ 少数派分支覆盖: reject → label_pending (证据积累 {acc['count']}/{MINORITY_EVIDENCE_THRESHOLD})")

    decision_map = {
        "accept": "✅ 接受入库",
        "accept_with_notes": "✅ 接受入库（含重复备注）",
        "consolidate": "🔄 建议合并到已有页",
        "label_pending": "🟡 标待核",
        "reject": "🔴 退回 Generator",
        "quarantined": "🚫 已隔离至 _quarantine/（引用验证失败）",
    }
    print(f"     决策: {decision_map.get(decision, decision)}")

    # 阶段四：GapLearner
    print("\n📋 [4/4] GapLearner — 知识缺口...")
    gaps = phase_gap_learner(gen_result, wiki_dir)
    if gaps:
        for g in gaps:
            print(f"     📋 {g['keyword']}: {g['detail']}")
    else:
        print("     无新缺口")

    # ── 输出（在 snapshot 保护下） ──
    print("\n--- 输出 ---")
    try:
        if quarantine_file:
            print(f"  🚫 内容已隔离: {quarantine_file.relative_to(KB_ROOT)}")
        else:
            write_ace_record(gen_result, issues, decision, gaps, quality)
            if decision in ("accept", "accept_with_notes"):
                print("  📇 ZK 卡片信息已附加至 ACE 记录")
            if gaps:
                write_gap_cards(gaps)
            write_log_entry(str(raw_path), decision)
            # 写入成功后 snapshot 自动保留（git stash 不 pop）
    except Exception as e:
        print(f"  ❌ 写入失败: {e}")
        if snapshot_ref:
            print(f"  🔄 回滚 git snapshot: {snapshot_ref}")
            if git_snapshot_pop():
                print(f"  ✅ 已回滚")
            else:
                print(f"  ⚠️  回滚失败，请手动: git stash pop")
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"  ACE 完成 | 决策: {decision}")
    if snapshot_ref:
        print(f"  🛡️  Git snapshot 已保留（通过 git stash pop 回滚）")
    if contradictions:
        print(f"  🌿 少数派分支: {len(contradictions)} 条矛盾缓存")
    if minority_override:
        print(f"  ⚡ 已触发少数派覆盖")
    if verify_result:
        print(f"  🔬 引用验证: {verify_result['score']:.0%} "
              f"({verify_result['verified_count']}/{verify_result['total_refs']})")
        if verify_result.get("fabricated"):
            print(f"  🔍 疑似虚构引用: {len(verify_result['fabricated'])} 处")
    if quarantine_file:
        print(f"  🚫 已隔离: {quarantine_file.relative_to(KB_ROOT)}")
    print(f"{'='*50}\n")

    result = {
        "status": "completed",
        "decision": decision,
        "issues_count": len(issues),
        "dup_count": dup_count,
        "gaps_count": len(gaps),
        "contradictions_cached": len(contradictions),
        "minority_override": minority_override,
        "snapshot": snapshot_ref if snapshot_ref else None,
        "verify_references": {
            "score": verify_result["score"] if verify_result else None,
            "verified": verify_result["verified_count"] if verify_result else 0,
            "total": verify_result["total_refs"] if verify_result else 0,
            "fabricated": len(verify_result.get("fabricated", [])) if verify_result else 0,
            "status": verify_result["status"] if verify_result else "skipped",
        } if verify_result else {"status": "skipped"},
        "quarantine": str(quarantine_file.relative_to(KB_ROOT)) if quarantine_file else None,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
