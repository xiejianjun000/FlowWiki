#!/usr/bin/env python3
"""
ACE Review — FlowWiki 反思循环脚本（v2.0 含内容去重）
Generator → Reflector(含去重) → Curator(含consolidate) → GapLearner

用法:
  python _scripts/ace_review.py --raw <raw_path> [--wiki <wiki_path>] [--verbose]
  python _scripts/ace_review.py --dedup-check <file_path>   # 对已入库文件做去重检查
  python _scripts/ace_review.py --audit-wiki                # 全库去重扫描

四阶段:
  1. Generator:   读 raw 源 → 提取标题/关键词/章节结构
  2. Reflector:   批判检查 + 内容级去重检测（标题匹配 + 文本重叠）
  3. Curator:     决策（入库/待核/consolidate/触发conflict/退回）
  4. GapLearner:  识别知识缺口 → 生成 gap 卡片
"""

import argparse
import json
import os
import re
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
OPS_DIR = MEMORY_DIR / "ops"
WIKI_DIR = KB_ROOT / "wiki"

# 去重阈值
DEDUP_HEADING_OVERLAP_RATIO = 0.3   # 章节标题重叠 ≥30% → 标记潜在重复
DEDUP_TEXT_SIMILARITY = 0.4         # 文本词重叠 ≥40% → 标记高度重复
DEDUP_CONSOLIDATE_THRESHOLD = 0.6   # 文本重叠 ≥60% → Curator 出 consolidate

for d in [ACE_DIR, ZK_DIR, GAP_DIR, CONFLICT_DIR, OPS_DIR]:
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
    parser = argparse.ArgumentParser(description="ACE Review v2 — FlowWiki 反思循环")
    parser.add_argument("--raw", help="raw 源文件路径")
    parser.add_argument("--wiki", default=str(WIKI_DIR), help="wiki 目录路径")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--audit-wiki", action="store_true", help="全库去重扫描模式")
    parser.add_argument("--dedup-check", help="对指定文件做去重检查（不进 ACE 循环）")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki)

    # ── 全库去重模式 ──
    if args.audit_wiki:
        audit_wiki_dedup(wiki_dir)
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

    print(f"\n{'='*50}")
    print(f"  ACE 反思循环 v2 | {raw_path.name}")
    print(f"{'='*50}\n")

    # 阶段一：Generator
    print("📝 [1/4] Generator — 分析源文件...")
    gen_result = phase_generator(raw_path)
    print(f"     标题: {gen_result['title']}")
    print(f"     类型: {gen_result['estimated_type']}")
    print(f"     行数: {gen_result['lines']}")
    print(f"     章节: {', '.join(gen_result.get('headings', []) or [])}")
    if args.verbose:
        print(f"     关键词: {gen_result['keywords']}")

    # 阶段二：Reflector（含去重）
    print("\n🔍 [2/4] Reflector — 批判检查（含内容去重）...")
    issues = phase_reflector(gen_result, wiki_dir)
    dup_count = len([i for i in issues if i["type"] == "content_duplicate"])
    if issues:
        for issue in issues:
            icon = {"error": "🔴", "warning": "🟡", "info": "ℹ️"}.get(issue["severity"], "•")
            print(f"     {icon} [{issue['type']}] {issue['detail']}")
        if dup_count > 0:
            print(f"     → 发现 {dup_count} 处内容重复")
    else:
        print("     ✅ 无 issue")

    # 阶段三：Curator
    print("\n⚖️  [3/4] Curator — 质量评分 + 决策...")
    quality = score_quality(gen_result, issues)
    score = quality["total"]
    det = quality["details"]
    print(f"     质量评分: {score}/10")
    print(f"       信息密度: {det['info_density']}/2 | 结构: {det['structure']}/2 | 溯源: {det['traceability']}/2 | 独特性: {det['uniqueness']}/2 | 可操作: {det['actionability']}/2")
    decision = phase_curator(gen_result, issues)
    decision_map = {
        "accept": "✅ 接受入库",
        "accept_with_notes": "✅ 接受入库（含重复备注）",
        "consolidate": "🔄 建议合并到已有页",
        "label_pending": "🟡 标待核",
        "reject": "🔴 退回 Generator",
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

    # 输出
    print("\n--- 输出 ---")
    write_ace_record(gen_result, issues, decision, gaps, quality)
    if decision in ("accept", "accept_with_notes"):
        print("  📇 ZK 卡片信息已附加至 ACE 记录")
    if gaps:
        write_gap_cards(gaps)
    write_log_entry(str(raw_path), decision)

    print(f"\n{'='*50}")
    print(f"  ACE 完成 | 决策: {decision}")
    print(f"{'='*50}\n")

    result = {
        "status": "completed",
        "decision": decision,
        "issues_count": len(issues),
        "dup_count": dup_count,
        "gaps_count": len(gaps),
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
